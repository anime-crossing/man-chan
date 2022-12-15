import logging
from typing import Any, Dict, cast

import discord
from discord.ui import Select, View
from discord import Color, Embed, Guild
from discord.ext import commands
from discord.ext.commands.context import Context


from main import ManChanBot

from .commandbase import CommandBase

import json

def get_password(data: Any, site: str) -> str:
    entries = list(filter(lambda entry: entry['site'] == site, data['login_info']))
    return entries[0]['password']

with open("login.json", "r") as f:
        config = json.load(f)

class Login(CommandBase):
    @commands.command()
    async def login(self, ctx: Context):
        # Create Embed with Python, reads from json config file
        embed=Embed()
        embed.title = "Various Login Information"
        embed.description = "Please do not share this information with anyone else!"
        embed.set_footer(text="For Mobile Friendly, copy the password using the Selection Menu below")
        embed.color = Color.blue()
        
        select = Select(                                        # Select Method that Creates Selection Menu for Embed
            placeholder= "Choose a streaming service..."       # Placeholder Text
        )

        for i in config['login_info']: 
            embed.add_field(
                name = i["emoji_text"] + i["site"] + i["emoji_text"],
                value = "u: " + i["email"] + "\np: " + i["password"],
                inline=True
            )

            select.add_option(
                label=i["site"],
                emoji=None,
                description=i["site"] + " Login"
            )

        async def my_callback(interaction):
            if interaction.user == ctx.author:      # Interaction Author Must be Original Sender
                await interaction.response.send_message(get_password(config, select.values[0]))

        select.callback = my_callback
        view = View(timeout=15)             # Disables after  15 Second
        view.add_item(select)
        await ctx.channel.send(embed=embed, view=view)
    
    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return (
            configs["ENABLE_LOGIN"]
        )

async def setup(bot: ManChanBot):
    if Login.is_enabled(bot.configs):
        await bot.add_cog(Login(bot))
    else:
        logging.warn("SKIPPING: cogs.login")