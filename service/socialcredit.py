from __future__ import annotations
from db import UserCredit

from typing import TYPE_CHECKING, cast, Union, Optional
from disnake import Embed, Color
from utils.context import get_member, get_message_no_context
from datetime import datetime, timezone

if TYPE_CHECKING:
    from disnake import User, Member, RawReactionActionEvent
    from utils.distyping import Context, ManChanBot
    from cogs.socialcredit import ScoreCategory
    from disnake import Message


class SocialCreditService:
    @classmethod
    async def process_credit(
        cls,
        bot: ManChanBot,
        reaction: RawReactionActionEvent,
        direction: ScoreCategory,
        weight: int = 1,
        timelimit: Optional[int] = None,
    ):
        """The weight is how much we will add to the points, can be negative or positive."""
        from cogs.socialcredit import ScoreCategory

        message = await get_message_no_context(
            bot, reaction.channel_id, reaction.message_id
        )
        if not message:
            return

        discord_id = message.author.id
        if discord_id == reaction.user_id:
            return

        if await cls._is_passed_time_limit(timelimit, message):
            return

        credit_score = UserCredit.get(discord_id)
        if not credit_score:
            credit_score = UserCredit.create(discord_id)

        if direction == ScoreCategory.POSITIVE:
            credit_score.increase_score(weight)
        else:
            credit_score.decrease_score(weight)

    @classmethod
    def create_user_score_embed(cls, author: Union[User, Member]) -> Embed:
        user_score = UserCredit.get(author.id)

        embed = Embed()
        embed.title = author.display_name
        embed.set_thumbnail(author.display_avatar.url)

        if not user_score:
            embed.description = "You have no score yet :)"
        else:
            embed.color = (
                Color.green()
                if cast(int, user_score.current_score) >= 0
                else Color.red()
            )

            embed.add_field(
                name="Current Score",
                value=cast(str, user_score.current_score),
                inline=False,
            )
            embed.add_field(
                name="Positives", value=cast(str, user_score.positives), inline=True
            )
            embed.add_field(
                name="Negatives", value=cast(str, user_score.negatives), inline=True
            )

        return embed

    @classmethod
    def create_leaderboard_embed(cls, ctx: Context) -> Embed:
        result = UserCredit.leaderboard()

        embed = Embed()
        embed.title = "Leaderboard"

        if len(result) == 0:
            embed.description = "No users have been scored yet!"
            return embed

        score_fields = []
        for num, user in enumerate(result, start=1):
            name = get_member(ctx, str(user.id))
            score_fields.append(
                f"{num}. [{str(user.current_score)}] {name.display_name if name else 'Unknown'}"
            )

        embed.add_field(
            name="Ranking [Score] User", value="\n".join(score_fields), inline=True
        )

        return embed

    @staticmethod
    async def _is_passed_time_limit(timelimit: Optional[int], message: Message) -> bool:
        if not timelimit or type(timelimit) is not int:
            return False

        # Discord messages supposed to be in UTC, but still returns in PST time.
        message_time = (
            message.created_at.replace(tzinfo=timezone.utc).timestamp() + 28800
        )
        return message_time < (datetime.utcnow().timestamp() - timelimit)
