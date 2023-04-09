import logging
from typing import Optional

from discord import ButtonStyle  # type: ignore
from discord import Interaction  # type: ignore
from discord import Color, Embed, Member  # type: ignore - These libraries also exist
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import (  # type: ignore - These libraries exist
    Button,
    Modal,
    TextInput,
    View,
)

from db.alias import Aliases
from main import ManChanBot

from .commandbase import CommandBase


class Alias(CommandBase):
    def format_name(self, name: str) -> str:
        return name.lower().capitalize()

    async def save_alias(self, discord_id: int, alias: Optional[str]):
        table_entry = Aliases.get(discord_id)

        if not table_entry:
            table_entry = Aliases.create(discord_id)

        table_entry.set_alias(alias)

    async def create_alias(self, ctx: Context, member: Optional[Member], interaction: Interaction, alias: str):  # type: ignore
        alias = self.format_name(alias)
        embed = Embed(
            title="Confirm Alias",
            description=f"Alias Chosen: `{alias}`",
        )

        async def no_callback(interaction: Interaction):  # type: ignore
            embed.title = "Alias setup cancelled"
            embed.color = Color.red()

            await interaction.response.edit_message(embed=embed, view=None)

        async def yes_callback(interaction: Interaction):  # type: ignore
            embed.title = "Alias Saved."
            embed.color = Color.green()

            discord_id = ctx.author.id if member is None else member.id

            await self.save_alias(ctx.author.id, str(alias).lower())
            await interaction.response.edit_message(embed=embed, view=None)

        no_button = Button(emoji="❌")
        no_button.callback = no_callback
        yes_button = Button(emoji="✅")
        yes_button.callback = yes_callback

        view = View()
        view.add_item(no_button)
        view.add_item(yes_button)

        await interaction.response.edit_message(embed=embed, view=view)

    @commands.command()
    async def alias(self, ctx: Context):
        alias_embed = Embed(
            title="Set name for Alias",
            description="The bot will use this name during certain commands so that it doesn't need to constantly @ you or require you to type out full mention.\n\nBe sure to make your alias something common like just your name:\n\nEx: `Manny, Ivan, Chai, Jose, Bhrayan, Tony`",
            color=Color.blue(),
        )

        prompt = Modal(title="Enter preferred Alias")
        answer = TextInput(label="alias")

        async def modal_callback(interaction: Interaction):  # type: ignore
            await self.create_alias(ctx, None, interaction, answer)

        prompt.add_item(answer)
        prompt.on_submit = modal_callback

        async def entry_callback(interaction: Interaction):  # type: ignore
            if interaction.user == ctx.author:
                await interaction.response.send_modal(prompt)

        answer_button = Button(emoji="✏️")
        answer_button.callback = entry_callback

        view = View()
        view.add_item(answer_button)

        if Aliases.get(ctx.author.id) is None:
            await ctx.send(embed=alias_embed, view=view)  # type: ignore
            return

        async def remove_callback(interaction: Interaction):  # type: ignore
            if interaction.user == ctx.author:
                change_alias.title = "Alias Removed"
                change_alias.description = "Associated Alias has been removed from database, please re-run `!alias` to setup your alias."
                change_alias.color = Color.red()

                await self.save_alias(ctx.author.id, None)

        change_alias = Embed(
            title="Alias already set!",
            description="To bypass and change your alias, please use the button below.",
            color=Color.blue(),
        )

        repeat_button = Button(emoji="🔁")
        repeat_button.callback = entry_callback
        remove_button = Button(emoji="🗑️", style=ButtonStyle.danger)
        remove_button.callback = remove_button

    @commands.command(aliases=["sal"])
    async def setalias(self, ctx: Context, member: Member, arg: str):
        if ctx.author.guild_permissions.administrator:  # type: ignore
            alias = self.format_name(arg)
            await self.save_alias(member.id, alias)
            embed = Embed(
                title="Member Alias Saved",
                description=f"Member Alias saved as: `{alias}`",
                color=Color.green(),
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            await ctx.reply("You must be an admin to run this command!")

    @commands.command(aliases=["sid"])
    async def setid(self, ctx: Context, member: int, arg: str):
        if ctx.author.guild_permissions.administrator:  # type: ignore
            alias = self.format_name(arg)
            await self.save_alias(member, alias)
            embed = Embed(
                title="Member Alias Saved",
                description=f"Member Alias saved as: `{alias}`",
                color=Color.green(),
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            await ctx.reply("You must be an admin to run this command!")


async def setup(bot: ManChanBot):
    if Alias.is_enabled(bot.configs):
        await bot.add_cog(Alias(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.alias")
