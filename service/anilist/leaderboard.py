from enum import Enum

from db.anilist_users import AnilistUsers
from service.anilist.api import AnilistAPI, AnilistStatus
from service.anilist.objects import EmbedLeaderboard
from service.basev2 import MessageBase
from utils.context import get_member
from utils.tools import dig


class _SearchStatus(Enum):
    NOLINK = 0
    NOTFOUND = 1
    SUCCESS = 2
    ERROR = 3


class Leaderboard(MessageBase):
    async def leaderboard(self):
        all_users = AnilistUsers.get_all()
        embed = EmbedLeaderboard.create()

        self.set_embed(embed)

        if len(all_users) == 0:
            embed.switch_to_empty()
            return await self.send()

        result = self._fetch_updated_user_data()
        if result == _SearchStatus.NOTFOUND:
            embed.not_found_error()

        if result == _SearchStatus.ERROR:
            embed.not_general_error()

        anime_field = []
        manga_field = []

        for i, users in enumerate(AnilistUsers.anime_leaderboard(), start=1):
            name = get_member(self.ctx, str(users.id))
            anime_field.append(
                f"{i}. {name.display_name if name else 'Unknown'} - {str(round(int(users.minutes_watched)/float(1440), 2))} Days"  # type: ignore
            )

        for i, users in enumerate(AnilistUsers.manga_leaderboard(), start=1):
            name = get_member(self.ctx, str(users.id))
            manga_field.append(
                f"{i}. {name.display_name if name else 'Unknown'} - {str(users.chapters_read)} Chapters"
            )

        embed.add_field(name="Anime", value="\n".join(anime_field), inline=True)
        embed.add_field(name="Manga", value="\n".join(manga_field), inline=True)

        await self.send()

    def _fetch_updated_user_data(self) -> _SearchStatus:
        current_user = AnilistUsers.get(self.author_id)
        if current_user is None or current_user.anilist_id is None:
            return _SearchStatus.NOLINK

        status, result = AnilistAPI.get_user_info(str(current_user.anilist_id))
        if status == AnilistStatus.NOT_FOUND:
            return _SearchStatus.NOTFOUND

        if status == AnilistStatus.INTERNAL_ERROR or result is None:
            return _SearchStatus.ERROR

        watch_stat = dig(
            result, "data", "User", "statistics", "anime", "minutesWatched"
        )
        read_stat = dig(result, "data", "User", "statistics", "anime", "chaptersRead")

        current_user.update_stats(minutes=watch_stat, chapters=read_stat)  # type: ignore
        return _SearchStatus.SUCCESS
