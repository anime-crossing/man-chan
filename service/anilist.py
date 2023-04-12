from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING, Optional, cast

from disnake import Color, Embed
from disnake.ui import Button, Select, View

from db import AnilistUsers
from fetcher.anilist import AnilistApi
from utils.config_mapper import DATABASE_STATUS

from .interaction_base import CallbackBase, InteractionBase

if TYPE_CHECKING:
    from disnake import Interaction

    from utils.distyping import Config, Context


class AnilistAttributes(Enum):
    ANIME = "ANIME"
    MANGA = "MANGA"
    NOVEL = "NOVEL"


class AnilistService(InteractionBase):
    def __init__(self, ctx: Context, configs: Config) -> None:
        super().__init__(ctx)
        self._configs = configs

    async def send_api_search_interaction(
        self,
        media_type: AnilistAttributes,
        query: str,
        format: Optional[AnilistAttributes] = None,
    ):
        """Searches for Anime/Manga/Novel, presents as embed with a selection menu."""
        format_type = None if format is None else format.value
        fetch_results = AnilistApi.fetch_search_results(
            media_type.value, query, format_type
        )

        if len(fetch_results.media) < 1:
            not_found = Embed(
                title="Media not found",
                description="Please re-run the command and refine your search parameters.",
                color=Color.red(),
            )
            await self._ctx.reply(embed=not_found, mention_author=False)
            return

        results = fetch_results.media
        results.sort(key=lambda x: x.popularity, reverse=True)

        selection_embed = Embed()
        selection_embed.title = "Search Results"
        selection_embed.description = "Please select the entry using the menu below."

        field_value = ""
        select = Select(placeholder="Select an entry")
        for i, media in enumerate(results, start=1):
            if media_type == AnilistAttributes.ANIME:
                staff_name = (
                    "Unknown Studio" if len(media.studios) < 1 else media.studios[0]
                )
            else:
                staff_name = (
                    "Unknown Author" if len(media.staff) < 1 else media.staff[0].name
                )

            field_value += (
                f"`{i}`.`♡{media.popularity}` · {staff_name} · **{media.title}**\n"
            )
            select.add_option(
                label=f"{i}. {media.title}",
                value=str(media.id),
                description=staff_name,
            )

        selection_embed.add_field(
            name=f"Showing top {fetch_results.per_page} entries",
            value=field_value,
            inline=True,
        )

        view = View(timeout=45)
        view.add_item(select)

        await _MediaInfo(self, selection_embed, view, select).send()

    async def send_account_setup(self):
        pass

    @classmethod
    async def create_leaderboard_embed(cls, ctx: Context):
        pass


class _MediaInfo(CallbackBase):
    async def send(self):
        self._select.callback = self._callback_media_option_selected
        self._message = await self._ctx.channel.send(
            embed=self._old_embed, view=self._old_view
        )

    async def _callback_media_option_selected(self, interaction: Interaction):
        if interaction.user == self._ctx.author:
            await self._create_media_info_embed(interaction, self._select.values[0])

    # Creates Message after Search is Completed, Combines all Parts (Content + Score)
    async def _create_media_info_embed(self, interaction: Interaction, media_id: str):
        media = AnilistApi.fetch_media_info(media_id)
        self._media = media
        # media_json = self.media_fetch(media_id)

        embed = Embed()
        self._current_embed = embed
        view = View()
        self._current_view = view

        embed.color = Color.blue()

        if media.image:
            embed.set_thumbnail(url=media.image)

        if media.url:
            embed.url = media.url

        embed.title = media.title
        embed.description = re.sub("<.*?>", "", media.description)
        embed.set_footer(text="Stats and information provided by Anilist")

        information_string = f"Type: {media.media_type}\nStatus: {media.status}\n"

        if media.media_type == "ANIME":
            information_string += f"AIRED: {media.start_date.format_to_readable()} to {media.end_date.format_to_readable()}\n"
            information_string += f"Episodes: {media.episodes or '?'}\n"
        else:
            information_string += f"From: {media.start_date.format_to_readable()} to {media.end_date.format_to_readable()}\n"
            information_string += f"Chapters: {media.chapters or '?'}\n"
            information_string += f"Volumes: {media.volumes or '?'}\n"

        information_string += f"Score: {media.avg_score or '-'}"

        embed.add_field(name="Information", value=information_string, inline=True)
        embed.add_field(name="Genre", value=("\n".join(media.genres)), inline=True)

        # Handle retrieving user score if database is on
        if cast(AnilistService, self._service)._configs[DATABASE_STATUS]:
            discord_id = self._ctx.author.id
            anilist_id = AnilistUsers.get_anilist_id(discord_id)

            if anilist_id:
                anilist_stats = AnilistApi.fetch_user_media_score(media_id, anilist_id)

                if anilist_stats is not None:
                    embed.add_field(
                        name=f"{self._ctx.author.display_name} ({anilist_stats.name}) Stats",
                        value=f"Status: {anilist_stats.status}\nProgress: {anilist_stats.progress}\nScore: {anilist_stats.score}",
                        inline=False,
                    )

        magnifying_button = Button(emoji="🔍")
        magnifying_button.callback = self._callback_magnify_image

        self._back_button = Button(emoji="⬅")
        self._back_button.callback = self._callback_previous

        view.add_item(self._back_button)
        view.add_item(magnifying_button)

        await interaction.response.edit_message(embed=embed, view=view)

    async def _callback_magnify_image(self, interaction: Interaction):
        if interaction.user == self._ctx.author:
            self._current_embed.set_thumbnail(url=None)
            self._current_embed.set_image(url=self._media.image)

            stat_view = View()
            stats_button = Button(emoji="📊")
            stats_button.callback = self._callback_statistics
            stat_view.add_item(self._back_button)
            stat_view.add_item(stats_button)

            await interaction.response.edit_message(
                embed=self._current_embed, view=stat_view
            )

    async def _callback_statistics(self, interaction: Interaction):
        if interaction.user == self._ctx.author:
            self._current_embed.set_image(url=None)
            self._current_embed.set_thumbnail(url=self._media.image)

            await interaction.response.edit_message(
                embed=self._current_embed, view=self._current_view
            )

    async def _callback_previous(self, interaction: Interaction):
        if interaction.user == self._ctx.author:
            await interaction.response.edit_message(
                embed=self._old_embed, view=self._old_view
            )
