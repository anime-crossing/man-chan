from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Optional, Set, cast

from disnake import Guild
from disnake.ext.commands import Cog, command

from service.socialcredit import SocialCreditService
from utils.config_mapper import (
    DATABASE_STATUS,
    SOCIAL_CREDIT_DOWNVOTE,
    SOCIAL_CREDIT_ENABLE,
    SOCIAL_CREDIT_TIMELIMIT,
    SOCIAL_CREDIT_UPVOTE,
    SOCIAL_CREDIT_WHITELIST,
)
from utils.context import get_member
from utils.distyping import Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from disnake.raw_models import RawReactionActionEvent

    from utils.distyping import Config, ManChanBot


class ScoreCategory(Enum):
    POSITIVE = 1
    NEGATIVE = -1


class SocialCredit(CommandBase):
    @Cog.listener()
    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        emoji = reaction.emoji
        guild_id = str(reaction.guild_id)

        if guild_id not in self.whitelist:
            return

        if emoji.name == self.upvote:
            await SocialCreditService.process_credit(
                self.bot, reaction, ScoreCategory.POSITIVE, 1, self.timelimit
            )

        if emoji.name == self.downvote:
            await SocialCreditService.process_credit(
                self.bot, reaction, ScoreCategory.NEGATIVE, 1, self.timelimit
            )

    @Cog.listener()
    async def on_raw_reaction_remove(self, reaction: RawReactionActionEvent):
        emoji = reaction.emoji
        guild_id = str(reaction.guild_id)

        if guild_id not in self.whitelist:
            return

        if emoji.name == self.upvote:
            await SocialCreditService.process_credit(
                self.bot, reaction, ScoreCategory.POSITIVE, -1, self.timelimit
            )

        if emoji.name == self.downvote:
            await SocialCreditService.process_credit(
                self.bot, reaction, ScoreCategory.NEGATIVE, -1, self.timelimit
            )

    @command()
    async def score(self, ctx: Context, *args: str):
        """Get self user's score or tag another user to get their score."""
        guild_id = str(cast(Guild, ctx.guild).id)
        if guild_id not in self.whitelist:
            return

        author = ctx.author
        if len(args) > 0:
            member = get_member(ctx, args[0])
            if member:
                author = member

        embed = SocialCreditService.create_user_score_embed(author)
        await ctx.channel.send(embed=embed)

    @command(aliases=["lb"])
    async def leaderboard(self, ctx: Context):
        guild_id = str(cast(Guild, ctx.guild).id)
        if guild_id not in self.whitelist:
            return

        embed = SocialCreditService.create_leaderboard_embed(ctx)
        await ctx.channel.send(embed=embed)

    @property
    def whitelist(self) -> Set[str]:
        return self.configs.get(SOCIAL_CREDIT_WHITELIST, {})

    @property
    def upvote(self) -> str:
        return self.configs.get(SOCIAL_CREDIT_UPVOTE, "")

    @property
    def downvote(self) -> str:
        return self.configs.get(SOCIAL_CREDIT_DOWNVOTE, "")

    @property
    def timelimit(self) -> Optional[int]:
        return self.configs.get(SOCIAL_CREDIT_TIMELIMIT)

    @classmethod
    def is_enabled(cls, configs: Config = {}):
        return (
            configs.get(SOCIAL_CREDIT_ENABLE)
            and configs.get(SOCIAL_CREDIT_UPVOTE)
            and configs.get(SOCIAL_CREDIT_DOWNVOTE)
            and configs.get(DATABASE_STATUS)
        )


def setup(bot: ManChanBot):
    if SocialCredit.is_enabled(bot.configs):
        cleanup_configs(bot)
        bot.add_cog(SocialCredit(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.socialcredit")


def cleanup_configs(bot: ManChanBot):
    bot.configs[SOCIAL_CREDIT_WHITELIST] = (
        set(bot.configs[SOCIAL_CREDIT_WHITELIST])
        if bot.configs.get(SOCIAL_CREDIT_WHITELIST)
        else {}
    )
