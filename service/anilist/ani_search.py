from __future__ import annotations

import datetime
import re
from operator import itemgetter
from typing import TYPE_CHECKING, Literal, cast

from disnake import Interaction

from db.anilist_users import AnilistUsers
from utils.tools import dig, empty_or_default

from ..basev2 import CustomView, MessageBase
from .api import AnilistAPI, AnilistSearchOptions, AnilistStatus
from .objects import *

if TYPE_CHECKING:
    from typing import Any, Dict, List


class AniSearch(MessageBase):
    async def search_media(
        self, arg: str, mode: Literal["anime", "novel", "manga"]
    ) -> None:
        embed = EmbedSearch.create()
        view = CustomView()
        self.set_embed(embed)
        self.set_view(view)

        self._media_type = self._parse_media_type(mode)
        if self._media_type is None:
            embed.switch_to_error()
            return await self.reply()

        status, response = AnilistAPI.search_anime(arg, self._media_type)

        if status == AnilistStatus.ERROR or status == AnilistStatus.INTERNAL_ERROR:
            embed.switch_to_error()
            return await self.reply()

        search_query: List[Dict[Any, Any]] = dig(response, "data", "Page", "media")  # type: ignore
        if not search_query:
            embed.switch_to_not_found()
            return await self.reply()

        search_query.sort(key=itemgetter("popularity"), reverse=True)

        field_value = ""
        selector_component = SelectSearchOption()
        for i, item in enumerate(search_query, start=1):
            if self._media_type == AnilistSearchOptions.ANIME:
                staff_name = empty_or_default(
                    dig(item, "studios", "nodes", 0, "name"), "Unknown Studio"
                )
            else:
                author_index = (
                    1 if dig(item, "staff", "edges", 0, "role") != "Story & Art" else 0
                )

                staff_name = empty_or_default(
                    dig(item, "staff", "nodes", author_index, "name", "full"),
                    "Unknown Author",
                )

            ani_title: str = dig(item, "title", "romaji")  # type: ignore
            field_value += (
                f"`{i}`.`♡{item['popularity']}` · {staff_name} · **{ani_title}**\n"
            )
            selector_component.put_option(i, ani_title, item["id"], staff_name)

        search_number: int = dig(response, "data", "Page", "pageInfo", "perPage")  # type: ignore
        embed.switch_to_found_list(search_number, field_value)

        selector_component.set_callback(self._callback_selection)
        self.add_item(selector_component)

        self.selector_component = selector_component
        return await self.reply()

    def _parse_media_type(self, mode: str) -> Optional[AnilistSearchOptions]:
        if mode == "anime":
            return AnilistSearchOptions.ANIME
        elif mode == "manga":
            return AnilistSearchOptions.MANGA
        elif mode == "novel":
            return AnilistSearchOptions.NOVEL

        return None

    async def _callback_selection(self, interaction: Interaction[Any]):
        if interaction.user == self.author:
            new_message = _AniSelected(self.ctx).init_args(
                self.selector_component.values[0],
                interaction,
                self._media_type,  # type: ignore
            )
            await self.exit(new_message)


class _AniSelected(MessageBase):
    def init_args(
        self,
        selected_option: str,
        interaction: Interaction[Any],
        media_type: AnilistSearchOptions,
    ) -> _AniSelected:
        self._selected_ani = selected_option
        self._interaction = interaction
        self._media_type = media_type
        return self

    async def enter(self):
        await self.display_selected()

    async def display_selected(self):
        embed = EmbedAniInfo.create()
        view = CustomView()
        self.set_embed(embed)
        self.set_view(view)

        status, response = AnilistAPI.get_anime_info(self._selected_ani)

        if status == AnilistStatus.ERROR or response is None:
            embed.switch_to_error()
            return await self.update_message_send(self._interaction)

        data = dig(response, "data", "Media")
        if data is None:
            embed.switch_to_error()
            return await self.update_message_send(self._interaction)

        image_url = dig(data, "coverImage", "extraLarge")
        title = dig(data, "title", "romaji")
        url = dig(data, "siteUrl")

        re_cleaner = re.compile("<.*?>")  # Removes HTML Formatting <> </> etc
        description = str(re.sub(re_cleaner, "", str(dig(data, "description"))))

        media_type = dig(data, "type")
        format = dig(data, "format")
        status = dig(data, "status")
        episodes = dig(data, "episodes")
        startDate = dig(data, "startDate")
        endDate = dig(data, "endDate")
        chapters = dig(data, "chapters")
        volumes = dig(data, "volumes")
        averageScore = dig(data, "averageScore")
        genres = dig(data, "genres")

        info_string = (
            f"Type: {media_type if format != 'NOVEL' else 'NOVEL'}\nStatus: {status}\n"
        )
        if self._media_type == AnilistSearchOptions.ANIME:
            info_string += f"Aired: {self.convert_date(startDate)} to {self.convert_date(endDate)}\n"  # type: ignore
            info_string += f"Episodes: {episodes if episodes != None else '?'}\n"
        else:
            info_string += f"From: {self.convert_date(startDate)} to {self.convert_date(endDate)}\n"  # type: ignore
            info_string += f"Chapters: {chapters if chapters != None else '?'}\n"
            info_string += f"Volumes: {volumes if volumes != None else '?'}\n"

        info_string += f"Score: {averageScore}"

        embed.set_info(
            title=title,  # type: ignore
            url=url,  # type: ignore
            description=description,
            info=info_string,
            thumbnail=image_url,  # type: ignore
            genres=genres,  # type: ignore
        )

        existing_user = AnilistUsers.get_anilist_id(self.author_id)
        if existing_user is not None:
            score_status, score_response = AnilistAPI.get_score(
                existing_user, self._selected_ani
            )

            if score_status == AnilistStatus.SUCCESS and score_response is not None:
                ani_name = dig(score_response, "user", "name")
                ani_status = dig(score_response, "status")
                ani_progress = dig(score_response, "progress")
                ani_score = dig(score_response, "score")
                embed.add_score(
                    discord_name=self.author_name,
                    anilist_name=ani_name,  # type: ignore
                    status=ani_status,  # type: ignore
                    progress=ani_progress,  # type: ignore
                    score=ani_score,  # type: ignore
                )

        magnifying_button = ButtonMagnifier.create()
        magnifying_button.set_callback(self._callback_magnifier)
        self.add_button(magnifying_button)

        self.add_return_button()

        return await self.update_message_send(self._interaction)

    async def _callback_magnifier(self, interaction: Interaction[Any]):
        if interaction.user == self.author:
            cast(EmbedAniInfo, self.embed).magnify_image()

            stats_button = ButtonStatsSwitch.create()
            stats_button.set_callback(self._callback_stats_view)

            new_view = CustomView()
            self.set_view(new_view)
            self.add_button(stats_button)
            self.add_return_button()

            await self.update_message_send(interaction)

    async def _callback_stats_view(self, interaction: Interaction[Any]):
        if interaction.user == self.author:
            cast(EmbedAniInfo, self.embed).minify_image()

            magnify_button = ButtonMagnifier.create()
            magnify_button.set_callback(self._callback_magnifier)

            new_view = CustomView()
            self.set_view(new_view)
            self.add_button(magnify_button)
            self.add_return_button()

            await self.update_message_send(interaction)

    # Converts Date to Readable Format from Anilist JSON
    def convert_date(self, date: Dict[str, Any]) -> str:
        if date["month"] is None:
            if date["day"] is None:
                return date["year"] if date["year"] != None else "?"
            return "?"

        month_num = str(date["month"])
        datetime_object = datetime.datetime.strptime(month_num, "%m")
        month_name = datetime_object.strftime("%b")

        return f"{month_name} {date['day']}, {date['year']}"
