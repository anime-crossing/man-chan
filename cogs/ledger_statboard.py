import logging
import typing
import json

from discord import Color, Embed, Member, Message
from discord.ext import commands
from discord.ext.commands.context import Context

from main import ManChanBot
from utils.ledger_utils import get_pst_time

from .commandbase import CommandBase


class Ledger_Statboard(CommandBase):
    @staticmethod
    def read_json(param: int) -> int:
        file_path = 'fetcher/statboard_info.json'
        with open(file_path, 'r') as f:
            data = json.load(f)

        return data['message_id'] if param == 1 else data['timestamp']
    
    @staticmethod
    def write_json(message_id: int, timestamp: int):
        file_path = 'fetcher/statboard_info.json'
        with open(file_path, 'r') as f:
            data = json.load(f)

        data['message_id'] = message_id
        data['timestamp'] = timestamp

        with open(file_path, 'w') as f:
            json.dump(data, f)

    @staticmethod
    async def update_board():
        stats = Embed(title="Ledger for *Anime Crossing*", color=Color.blue())
        base_description = f'Tracking financial stats as of <t:{Ledger_Statboard.read_json(2)}:f>'

        open_transactions = f''
        

    @commands.command(aliases=["ils"])
    async def initledgerstats(self, ctx: Context):
        timestamp = get_pst_time()
        stats = Embed(title="Ledger Stats for Anime Crossing", description = f'Tracking financial stats as of <t:{timestamp}:f>', color=Color.blue())

        message = await ctx.send(embed=stats)
        
        print(f'{message.id} {timestamp}')
        self.write_json(message.id, timestamp)


async def setup(bot: ManChanBot):
    if Ledger_Statboard.is_enabled(bot.configs):
        await bot.add_cog(Ledger_Statboard(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.ledger_statboard")
