import logging
from enum import Enum
from typing import Any, Dict, cast

from discord import Color, Embed, Guild
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.raw_models import RawReactionActionEvent

from db.socialcredit import UserCredit
from main import ManChanBot
from utils.context import get_member, get_message

from .commandbase import CommandBase


class ScoreCategory(Enum):
    POSITIVE = 1
    NEGATIVE = -1


class SocialCredit(CommandBase):
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        print(reaction)
        message = get_message(reaction.message_id)
        print(reaction.message_id)
        emoji = reaction.emoji
        guild_id = str(reaction.guild_id)

        if guild_id not in self.configs["SOCIAL_WHITELIST"]:
            return

        if emoji.name == self.configs["UPVOTE_EMOJI_NAME"]:
            await self._process_credit(reaction, ScoreCategory.POSITIVE, 1)

        if emoji.name == self.configs["DOWNVOTE_EMOJI_NAME"]:
            await self._process_credit(reaction, ScoreCategory.NEGATIVE, 1)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: RawReactionActionEvent):
        print(reaction)
        emoji = reaction.emoji
        guild_id = str(reaction.guild_id)

        if guild_id not in self.configs["SOCIAL_WHITELIST"]:
            return

        if emoji.name == self.configs["UPVOTE_EMOJI_NAME"]:
            await self._process_credit(reaction, ScoreCategory.POSITIVE, -1)

        if emoji.name == self.configs["DOWNVOTE_EMOJI_NAME"]:
            await self._process_credit(reaction, ScoreCategory.NEGATIVE, -1)

    @commands.command()
    async def score(self, ctx: Context, *args: str):
        guild_id = str(cast(Guild, ctx.guild).id)
        if guild_id not in self.configs["SOCIAL_WHITELIST"]:
            return

        author = ctx.author
        if len(args) > 0:
            member = get_member(ctx, args[0])
            if member:
                author = member

        embed = Embed()
        embed.title = author.display_name

        user_score = UserCredit.get(author.id)
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

        await ctx.channel.send(embed=embed)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx: Context):
        guild_id = str(cast(Guild, ctx.guild).id)
        if guild_id not in self.configs["SOCIAL_WHITELIST"]:
            return

        result = UserCredit.leaderboard()

        embed = Embed()
        embed.title = "Leaderboard"

        if len(result) == 0:
            embed.description = "No users have been scored yet!"
            return await ctx.channel.send(embed=embed)

        score_fields = []

        for num, user in enumerate(result, start=1):
            name = get_member(ctx, str(user.id))
            score_fields.append(
                f"{num}. [{str(user.current_score)}] {name.display_name if name else 'Unknown'}"
            )

        embed.add_field(
            name="Ranking [Score] User", value="\n".join(score_fields), inline=True
        )
        await ctx.channel.send(embed=embed)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return (
            configs["ENABLE_SOCIAL_CREDIT"]
            and configs["UPVOTE_EMOJI_NAME"]
            and configs["DOWNVOTE_EMOJI_NAME"]
            and configs["db_on"]
        )

    async def get_message_author_id(self, channel_id: int, message_id: int) -> int:
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)  # type: ignore
        return message.author.id

    async def _process_credit(
        self,
        reaction: RawReactionActionEvent,
        direction: ScoreCategory,
        weight: int = 1,
    ):
        """The weight is how much we will add to the points, can be negative or positive."""
        discord_id = await self.get_message_author_id(
            reaction.channel_id, reaction.message_id
        )

        if discord_id == reaction.user_id:
            return

        credit_score = UserCredit.get(discord_id)
        if not credit_score:
            credit_score = UserCredit.create(discord_id)

        if direction == ScoreCategory.POSITIVE:
            credit_score.increase_score(weight)
        else:
            credit_score.decrease_score(weight)


async def setup(bot: ManChanBot):
    if SocialCredit.is_enabled(bot.configs):
        cleanup_configs(bot)
        await bot.add_cog(SocialCredit(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.socialcredit")


def cleanup_configs(bot: ManChanBot):
    bot.configs["SOCIAL_WHITELIST"] = (
        set(bot.configs["SOCIAL_WHITELIST"]) if bot.configs["SOCIAL_WHITELIST"] else {}
    )
