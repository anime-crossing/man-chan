import logging
from typing import Any, Dict

from discord import Interaction  # type: ignore - Interaction exists
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View  # type: ignore - These libraries exist

from main import ManChanBot

from .commandbase import CommandBase


class Anilist(CommandBase):
    @commands.command()
    async def anime(self, ctx: Context):
        embed = Embed()
        embed.color = Color.blue()

        # Do Stuff to get Query Here
        image_url = "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx130003-5Y8rYzg982sq.png"
        embed.title = "BOCCHI THE ROCK"
        embed.url = "https://anilist.co/anime/130003/Bocchi-the-Rock"
        embed.description = "My anxious gorl"
        embed.set_thumbnail(url=image_url)
        embed.add_field(
            name="Information",
            value="Type: ANIME TV\nStatus: FINISHED\nAIRED: Oct 09, 2022 to Dec 25, 2022\nEpisodes: 12\nScore: 88",
            inline=True,
        )
        embed.add_field(name="Genre", value="Comedy\nMusic\nSlice of Life", inline=True)
        embed.set_footer(text="hi")

        async def magnifying_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                embed.set_thumbnail(url=None)  # type: ignore - None is valid
                embed.set_image(url=image_url)

                stats_button = Button(emoji="📊")
                stats_button.callback = stat_callback
                stat_view = View()
                stat_view.add_item(stats_button)

                await interaction.response.edit_message(embed=embed, view=stat_view)

        async def stat_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                embed.set_image(url=None)  # type: ignore - None is valid
                embed.set_thumbnail(url=image_url)

                await interaction.response.edit_message(embed=embed, view=view)

        magnifying_button = Button(emoji="🔍")
        magnifying_button.callback = magnifying_callback

        view = View()
        view.add_item(magnifying_button)

        await ctx.reply(embed=embed, view=view, mention_author=False)  # type: ignore - View exists

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_ANILIST"]


async def setup(bot: ManChanBot):
    if Anilist.is_enabled(bot.configs):
        await bot.add_cog(Anilist(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.anilist")
