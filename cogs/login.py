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

with open("login.json") as f:
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

        embed.add_field(
            name = ":orange_circle: Crunchyroll :orange_circle:",
            value = "u: " + config["Crunchyroll"]["login"] + "\np: " + config["Crunchyroll"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":blue_circle: Disney+* :blue_circle:",
            value = "u: " + config["Disney+"]["login"] + "\np: " + config["Disney+"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":black_circle: HBO Max :black_circle:",
            value = "u: " + config["HBO Max"]["login"] + "\np: " + config["HBO Max"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":green_circle: Hulu* :green_circle:",
            value = "u: " + config["Hulu"]["login"] + "\np: " + config["Hulu"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":red_circle: Netflix :red_circle:",
            value = "u: " + config["Netflix"]["login"] + "\np: " + config["Netflix"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":football: NFL+ :football:",
            value = "u: " + config["NFL+"]["login"] + "\np: " + config["NFL+"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":white_circle: Paramount+ :white_circle:",
            value = "u: " + config["Paramount+"]["login"] + "\np: " + config["Paramount+"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":yellow_circle: Peacock :yellow_circle:",
            value = "u: " + config["Peacock"]["login"] + "\np: " + config["Peacock"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":nazar_amulet: Viki (KDramas) :nazar_amulet:",
            value = "u: " + config["Viki"]["login"] + "\np: " + config["Viki"]["password"], 
            inline=True
        )
        embed.add_field(
            name = ":brown_circle: Showtime :brown_circle:",
            value = "u: " + config["Showtime"]["login"] + "\np: " + config["Showtime"]["password"], 
            inline=True
        )

        select = Select(                                        # Select Method that Creates Selection Menu for Embed
            placeholder= "Choose a streaming service...",       # Placeholder Text
            options=[                                           # Selection Options
                discord.SelectOption(
                    label="Crunchyroll", 
                    emoji="🟠", 
                    description="Crunchyroll Login"),
                discord.SelectOption(
                    label="Disney+", 
                    emoji="🔵", 
                    description="Disney+ Login"),
                discord.SelectOption(
                    label="HBO Max", 
                    emoji="⚫", 
                    description="HBO Max Login"),
                discord.SelectOption(
                    label="Hulu", 
                    emoji="🟢", 
                    description="Hulu Login"),          
                discord.SelectOption(
                    label="Netflix", 
                    emoji="🔴", 
                    description="Netflix Login"),
                discord.SelectOption(
                    label="NFL+", 
                    emoji="🏈", 
                    description="NFL+ Login"),
                discord.SelectOption(
                    label="Paramount+", 
                    emoji="🗻", 
                    description="Paramount+ Login"),
                discord.SelectOption(
                    label="Peacock", 
                    emoji="🦚", 
                    description="Peacock Login"),
                discord.SelectOption(
                    label="Viki", 
                    emoji="🧿", 
                    description="Viki Login"),
                discord.SelectOption(
                    label="Showtime", 
                    emoji="🟤", 
                    description="Showtime Login")           
            ]
        )

        async def my_callback(interaction):
            if interaction.user == ctx.author:      # Interaction Author Must be Original Sender
                await interaction.response.send_message(config[select.values[0]]["password"])

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