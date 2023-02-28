import logging

from discord import Color, Embed, Member, ButtonStyle, Interaction   #type: ignore
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, View #type: ignore

from main import ManChanBot

from .commandbase import CommandBase

class Ledger(CommandBase):
    @commands.command()
    async def bill(self, ctx: Context, member: Member, amount: float):
        bill_embed = Embed(
            title="Bill",
            description=f"Participants: {member.mention}\nTotal Bill: **${amount}**",
            color=Color.blue()
        )
        message = f'{member.mention} please confirm the bill from {ctx.author.mention}'
        
        async def x_callback(interaction: Interaction):  #type: ignore
            bill_embed.description="Bill Cancelled.  Please re-run commands to fix errors if they exist"
            bill_embed.color = Color.red()
            await interaction.response.edit_message(embed=bill_embed, view=None)

        async def check_callback(interaction: Interaction): #type: ignore
            bill_embed.color = Color.gold()
            check_button.disabled = True
            view.add_item(confirm_button)
            await interaction.response.edit_message(embed=bill_embed, view=view)

        async def confirm_callback(interaction: Interaction): #type: ignore
            bill_embed.color = Color.green()
            bill_embed.set_footer(text='Bill confirmed. Charge was added into database.')
            await interaction.response.edit_message(embed=bill_embed, view=None)

        x_button = Button(emoji="❌")
        x_button.callback = x_callback
        check_button = Button(emoji="☑")
        check_button.callback = check_callback
        confirm_button = Button(emoji="☑", style = ButtonStyle.success)
        confirm_button.callback = confirm_callback

        view = View()
        view.add_item(x_button)
        view.add_item(check_button)

        await ctx.reply(content=message, embed=bill_embed, view=view, mention_author=False) #type: ignore

    @commands.command()
    async def form(self, ctx: Context):
        form_embed = Embed(
            title="Bill via Google Forms",
            description='[Use this to fill out the information!](https://forms.gle/ckiVkZk92WhqZNRA6)',
            color=Color.purple()
        )
        await ctx.reply(embed=form_embed, mention_author=False)

async def setup(bot: ManChanBot):
    if Ledger.is_enabled(bot.configs):
        await bot.add_cog(Ledger(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.ledger")