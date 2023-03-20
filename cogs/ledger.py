import logging
import random
import typing
from typing import List, Optional, Union

from discord import ButtonStyle  # type: ignore
from discord import Interaction  # type: ignore
from discord import Color, Embed, Member, Message
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View  # type: ignore

from db.alias import Aliases
from db.invoice_participants import Invoice_Participant
from db.invoices import Invoice
from main import ManChanBot
from utils.context import get_member
from utils.ledger_utils import *

from .commandbase import CommandBase


class Ledger(CommandBase):
    @staticmethod
    def create_bill(uuid: str, pay_id: int, cost: float, arg: str, timestamp: int, multi: bool):  # type: ignore
        table_entry = Invoice.get(uuid)

        if not table_entry:
            table_entry = Invoice.create(uuid)

        table_entry.set_values(pay_id, cost, arg, timestamp, multi)

        return table_entry

    @staticmethod
    def handle_transaction(
        invoice: Invoice,
        participant_ids: Union[int, List[int]],
        splits: Optional[List[float]],
        param: int,
    ):
        if not isinstance(participant_ids, list):
            participant_ids = [participant_ids]

        if splits is None:  # Traditional 1-on-1 Transacation !bill
            participant_entry = Invoice_Participant.create(
                invoice.id, participant_ids[0], float(invoice.total_cost)
            )
        else:  # Split Transactions from !bm
            for participant, split in zip(participant_ids, splits):
                participant_entry = Invoice_Participant.create(
                    invoice.id, participant, split
                )

    @staticmethod
    def select_random_member(ctx: Context, participants: List[int]) -> Optional[Member]:
        random_member_id = random.choice(participants)
        return get_member(ctx, random_member_id)
    
    @commands.command()
    async def bill(self, ctx: Context, member: Member, amount: float, *, description: str = None):  # type: ignore
        if description is None:
            error_embed = Embed(
                title="Re-run command with a valid description",
                description=f"Example: `!bill @chai 1.23 Starbucks`",
            )
            await ctx.reply(embed=error_embed, mention_author=False)
        if len(description) > 25:
            await ctx.reply("The description must be 25 characters or less")
            return

        if ctx.author == member:
            fraud_embed = Embed(
                title="Fraud Warning",
                description="The authorities are on their way.  Stop trying to charge yourself!",
                color=Color.red(),
            )
            return await ctx.reply(embed=fraud_embed, mention_author=False)

        amount = round(amount, 2)
        if amount < 0:
            await ctx.reply("The amount cannot be negative")
            return

        bill_id = gen_uuid(4)
        formatted_amount = "{:.2f}".format(amount)
        timestamp = get_pst_time()
        bill_embed = Embed(
            title="New Bill",
            description=f"Bill ID: `{bill_id}`\nDate: <t:{timestamp}:D>\n\nReason: **{description}**\n\nPay to {ctx.author.mention}\nBill to{member.mention}\n\nTotal Bill: **${formatted_amount}**",
            color=Color.blue(),
        )
        message = f"{member.mention} please confirm the bill from {ctx.author.mention}"

        async def confirm_callback(interaction: Interaction):  # type: ignore
            if interaction.user == member:
                bill_embed.color = Color.green()
                bill_embed.set_footer(
                    text=f"Bill confirmed. Charge was added into database with ID #{bill_id}"
                )

                bill = Ledger.create_bill(
                    bill_id, ctx.author.id, amount, str(description), timestamp, False
                )
                Ledger.handle_transaction(bill, member.id, None, 1)
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        confirm_button = Button(emoji="☑", style=ButtonStyle.success)
        confirm_button.callback = confirm_callback

        view = create_confirmation_buttons(ctx, member, bill_embed, 1, confirm_button)

        await ctx.reply(content=message, embed=bill_embed, view=view, mention_author=False)  # type: ignore

    @commands.command(aliases=["ii"])
    async def invoiceinfo(self, ctx: Context, *, arg: str = None):  # type: ignore
        if arg is None:
            bill = Invoice_Participant.get_latest(ctx.author.id, False)
            if bill is None and Invoice_Participant.get_latest(ctx.author.id, True):
                await ctx.reply("All Associated Invoices Already Paid for.  Good Job!")
                return
        else:
            bill = Invoice_Participant.get(ctx.author.id, arg.upper())

        async def button_callback(interaction: Interaction):  # type: ignore
            if interaction.user == ctx.author:
                if bill.paid:  # type: ignore - Bill will not be empty checked later
                    return await interaction.response.edit_message(embed=already_paid(bill), view=None)  # type: ignore - Bill will not be empty checked later
                else:
                    await interaction.response.defer()
                    await ctx.invoke(ctx.bot.get_command('pay'), arg=bill.invoice_id)   # type: ignore - It will never be none
            else:
                await interaction.response.defer()

        pay_button = Button(label="Pay Bill", emoji="💸", style=ButtonStyle.success)
        pay_button.callback = button_callback

        pay_view = View()
        pay_view.add_item(pay_button)

        if bill is not None:
            invoice_info = Invoice.get(bill.invoice_id)
            member = get_member(ctx, invoice_info.payer_id)  # type: ignore - Bill will not be empty checked later
            member = typing.cast(Member, member)
            base_description = f"`{bill.invoice_id}` · `${bill.amount_owed}`\n\nReason: **{invoice_info.desc}**\n\n"  # type: ignore - Bill will not be empty checked later
            unpaid_description = base_description + f"Pay to: <@{invoice_info.payer_id}>\n\nBilled: <t:{invoice_info.open_date}:f>"  # type: ignore - Bill will not be empty checked later
            if invoice_info is not None:
                bill_embed = Embed(title="Bill Info")
                if bill.paid:
                    bill_embed.color = Color.green()
                    paid_description = unpaid_description.replace("Pay", "Paid", 1)
                    paid_description += f"\nPaid: <t:{bill.paid_on}:f>"
                    bill_embed.description = paid_description
                    await ctx.reply(embed=bill_embed, view=None, mention_author=False)  # type: ignore
                else:
                    bill_embed.color = Color.red()
                    bill_embed.description = unpaid_description
                    await ctx.reply(embed=bill_embed, view=pay_view, mention_author=False)  # type: ignore
            else:
                await ctx.reply(
                    "Invalid Code. Please re-run command", mention_author=False
                )
        else:
            await ctx.reply("No Associated Invoices.")
            return

    @commands.command(aliases=["ic", "invoices", "inc"])
    async def invoicecollection(self, ctx: Context):
        collection_embed = Embed(title="Invoice Collection")
        collection = Invoice_Participant.get_all(ctx.author.id)

        if len(collection) == 0:
            collection_embed.description = "No Invoices Associated with User."
            return await ctx.send(embed=collection_embed)

        description = f"Invoices owed by {ctx.author.mention}\n\n"

        for invoice in collection:
            emoji = "✔️" if invoice.paid else "⭕"
            parent_invoice = Invoice.get(invoice.invoice_id)
            invoice_desc = parent_invoice.desc  # type: ignore
            owed_id = parent_invoice.payer_id  # type: ignore
            description += f"{emoji}  `{invoice.invoice_id}`  ·  `${invoice.amount_owed: .2f}` · **{invoice_desc}** · Pay to <@{owed_id}>\n"

        collection_embed.description = description

        await ctx.reply(embed=collection_embed, mention_author=False)

    @commands.command(aliases=["bi", "billi"])
    async def billinfo(self, ctx: Context, *, arg: str = None):  # type: ignore
        if arg is None:
            bill = Invoice.get_latest(ctx.author.id, False)
            if bill is None and Invoice.get_latest(ctx.author.id, True):
                await ctx.reply("All Issued bills have been paid and closed")
                return
        else:
            bill = Invoice.get(arg.upper())
        
        async def close_callback(interaction: Interaction):     # type: ignore
            pass

        async def open_callback(interaction: Interaction):      # type: ignore
            pass

        async def remind_callback(interaction: Interaction):    #type: ignore
            await ctx.invoke(ctx.bot.get_command('remindbill'), arg=bill.id)   # type: ignore - It will never be none
            await interaction.response.defer()

        open_button = Button(label='Re-open Bill', emoji='⭕')
        open_button.callback = open_callback

        close_button = Button(label='Close Bill', emoji='❌')
        close_button.callback = close_callback

        remind_button = Button(label='Remind People!', emoji='🗣️')
        remind_button.callback = remind_callback

        action_view = View()

        if bill is not None:
            bill_embed = Embed(title='Bill Info')
            base_description=f'`{bill.id}` · `{bill.total_cost}`\n\nReason: **{bill.desc}**\n\nPaid by: <@{bill.payer_id}>\n\nParticipants:\n'

            participants = Invoice_Participant.get_participants(bill.id)

            if participants is not None:
                for participant in participants:
                    emoji = '⭕' if participant.paid else '❌'
                    base_description += f'{emoji} `${participant.amount_owed: .2f}` · <@{participant.participant_id}>\n'

            base_description += f'\nBill opened: <t:{bill.open_date}:f>'

            if bill.closed:
                bill_embed.color = Color.green()
                closed_description = f'{base_description}\nBill closed: <t:{bill.close_date}:f>'
                bill_embed.description = closed_description
                action_view.add_item(open_button)
                await ctx.reply(embed=bill_embed, view=action_view, mention_author=False)
            else:
                bill_embed.color = Color.red()
                bill_embed.description = base_description
                action_view.add_item(remind_button)
                action_view.add_item(close_button)
                await ctx.reply(embed=bill_embed, view=action_view, mention_author=False)
        else:
            await ctx.reply("Invalid Code Entered.  Please re-run command", mention_author=False)

    @commands.command(aliases=["bc", "billc"])
    async def billcollection(self, ctx: Context, *, arg: str = None): #type: ignore
        pass
    
    @commands.command()
    async def pay(self, ctx: Context, *, arg: str = None):  # type: ignore
        if arg is None:
            bill = Invoice_Participant.get_latest(ctx.author.id, False)
            if bill is None and Invoice_Participant.get_latest(ctx.author.id, True):
                await ctx.reply("All Associated Invoices paid for! Good Job!")
                return
        else:
            bill = Invoice_Participant.get(ctx.author.id, arg.upper())

        async def confirm_callback(interaction: Interaction):  # type: ignore
            if interaction.user == member:
                if not bill.paid:  # type: ignore - Won't be none
                    timestamp = get_pst_time()
                    bill_embed.color = Color.green()
                    bill_embed.set_footer(
                        text=f"Bill paid. Charge was updated in database."
                    )
                    bill.set_paid(timestamp)  # type: ignore - Bill will not be empty checked later
                    if bill.get_status(bill.invoice_id):
                        invoice = Invoice.get(bill.invoice_id)
                        invoice.close_bill(get_pst_time())
                    paid_description = unpaid_description.replace("Pay", "Paid", 1)
                    paid_description += f"\nPaid: <t:{timestamp}:f>"
                    bill_embed.description = paid_description
                    await interaction.response.edit_message(embed=bill_embed, view=None)
                else:
                    paid_embed = already_paid(bill)  # type: ignore - Won't be none
                    await interaction.response.edit_message(embed=paid_embed, view=None)
            else:
                await interaction.response.defer()

        confirm_button = Button(emoji="☑", style=ButtonStyle.success)
        confirm_button.callback = confirm_callback

        if bill is not None:
            if bill.paid:
                return await ctx.reply(embed=already_paid(bill), mention_author=False)
            invoice_info = Invoice.get(bill.invoice_id)
            member = get_member(ctx, invoice_info.payer_id)  # type: ignore - Bill will not be empty checked later
            member = typing.cast(Member, member)
            if invoice_info is not None:
                unpaid_description = f"Reason: **{invoice_info.desc}**\n\nPay to: {member.mention}\nAmount: **${bill.amount_owed: .2f}**\n\nBilled: <t:{invoice_info.open_date}:f>"
                bill_embed = Embed(
                    title=f"Pay Bill `{bill.invoice_id}`?",
                    description=unpaid_description,
                )
                content = (
                    f"{member.mention} please confirm payment from {ctx.author.mention}"
                )
                view = create_confirmation_buttons(
                    ctx, member, bill_embed, 2, confirm_button
                )
                await ctx.reply(content=content, embed=bill_embed, view=view, mention_author=False)  # type: ignore
        else:
            await ctx.reply("Invalid Code. Please re-run command", mention_author=False)

    @commands.command(aliases=["billm", "bm"])
    async def billmultiple(self, ctx: Context, total: float, *, arg: str = None):  # type: ignore
        bill_id = gen_uuid(4)
        timestamp = get_pst_time()
        participants = []
        cost_array = []
        multi_embed = Embed(title="New Multi-Bill")
        embed_description = f"Bill ID: `{bill_id}`\nDate: <t:{timestamp}:D>\n\nReason: {arg}\n\nPay to {ctx.author.mention}\n\nTotal Bill: **${total: .2f}**\n"
        multi_embed.description = embed_description

        group_list = Aliases.get_list()
        select = Select(
            placeholder="Select people to bill",
            min_values=1,
            max_values=len(group_list) - 1,
        )

        for member in group_list:
            if member.id != int(ctx.author.id):
                select.add_option(label=member.alias, value=member.id)

        async def select_callback(interaction: Interaction):  # type: ignore
            nonlocal embed_description, participants
            if interaction.user == ctx.author:
                invoice = "Bill the following people: \n"
                participants = select.values
                for participant in participants:
                    invoice += f"- <@{participant}>\n"
                embed_description += invoice
                multi_embed.description = embed_description
                await interaction.response.edit_message(
                    embed=multi_embed, view=split_view
                )

        select.callback = select_callback

        view = View()
        view.add_item(select)

        async def even_callback(interaction: Interaction):  # type: ignore
            if interaction.user == ctx.author:
                if not participants:
                    await interaction.response.send_message(
                        "Participants not being filled somehow or updating"
                    )
                else:
                    nonlocal embed_description, cost_array
                    n = len(participants) + 1
                    per_value = round(total / n, 2)
                    embed_description += f"Each participant will pay $**{per_value: .2f}**. (Owner of Bill Included in Splits)"
                    cost_array = [per_value] * (n - 1)
                    multi_embed.description = embed_description
                    view = create_confirmation_buttons(ctx, ctx.author, multi_embed, 2, confirm_button)  # type: ignore - Won't be none
                    await interaction.response.edit_message(
                        embed=multi_embed, view=view
                    )
            else:
                await interaction.response.defer()

        async def split_callback(interaction: Interaction):  # type: ignore
            if interaction.user == ctx.author:
                nonlocal embed_description, cost_array
                cost_message = None

                temp_description = (
                    embed_description
                    + "\nPlease enter bill in format `1.99, 11.14, 41.11` according to members selected.\n\n**Note, the first entry should be how much YOU paid.**  If you paid 10, and Steven and Tony paid 12, each, please type `10, 12, 12`.\n\nWhole numbers are okay!\n\nPress Checkmark when complete.  Message will timeout in 60 seconds.\n"
                )
                multi_embed.description = temp_description

                async def lock_callback(interaction: Interaction):  # type: ignore
                    nonlocal embed_description, cost_array
                    embed_description += f"\nYou paid: **${cost_array[0]: .2f}**\n"
                    
                    cost_array = cost_array[1:]

                    embed_description += f"\nParticipant Price Breakdown:\n"

                    for participant, cost in zip(participants, cost_array):
                        embed_description += f"- <@{participant}>: **${cost: .2f}**\n"
                        print(f"Cost Parsed: {cost}")

                    multi_embed.description = embed_description

                    view = create_confirmation_buttons(ctx, ctx.author, multi_embed, 2, confirm_button)  # type: ignore

                    await interaction.response.edit_message(
                        embed=multi_embed, view=view
                    )

                lock_button = Button(emoji="🔒")
                lock_button.callback = lock_callback

                view = create_confirmation_buttons(ctx, ctx.author, multi_embed, 2, confirm_button)  # type: ignore - Won't be none
                await interaction.response.edit_message(embed=multi_embed, view=view)

                def check(message: Message) -> bool:
                    return ctx.author == message.author

                while cost_message is None:
                    message = await ctx.bot.wait_for(
                        "message", timeout=60.0, check=check
                    )
                    if check_usd_format(str(message.content), len(participants)):
                        cost_message = str(message.content)
                    else:
                        await ctx.send("String parsed incorrectly. Please try again")

                cost_array = [float(x) for x in cost_message.split(", ")]

                for participant, cost in zip(participants, cost_array):
                    temp_description += f"- Bill <@{participant}> **${cost: .2f}**?\n"
                multi_embed.description = temp_description

                view = create_confirmation_buttons(ctx, ctx.author, multi_embed, 2, lock_button)  # type: ignore - Won't be none
                await interaction.message.edit(embed=multi_embed, view=view)

            else:
                await interaction.response.defer()

        split_evenly = Button(
            emoji="🟰", label="Split Evenly", style=ButtonStyle.success
        )
        split_evenly.callback = even_callback
        split_specific = Button(emoji="🔢", label="Split Specific")
        split_specific.callback = split_callback

        split_view = View()
        split_view.add_item(split_evenly)
        split_view.add_item(split_specific)

        async def confirm_callback(interaction: Interaction):  # type: ignore
            if interaction.user == ctx.author:
                bill = Ledger.create_bill(bill_id, ctx.author.id, total, arg, timestamp, True)
                Ledger.handle_transaction(bill, participants, cost_array, 2)
                multi_embed.set_footer(
                    text=f"New Multi-bill confirmed.  Charges were added into the database with ID #{bill_id}"
                )
                multi_embed.color = Color.green()
                await interaction.response.edit_message(embed=multi_embed, view=None)
            else:
                await interaction.response.defer()

        confirm_button = Button(emoji="☑", style=ButtonStyle.success)
        confirm_button.callback = confirm_callback

        await ctx.reply(embed=multi_embed, view=view, mention_author=False)  # type: ignore

    @commands.command(aliases=["tc"])
    async def test_confirm(self, ctx: Context, member: Member, param: int):
        embed = Embed(
            title="Test Embed", description="Creates a test embed to attach views to"
        )

        async def confirm_callback(interaction: Interaction):  # type: ignore
            await interaction.response.edit_message(
                content="Button works", embed=None, view=None
            )

        confirm_button = Button(emoji="☑️")
        confirm_button.callback = confirm_callback

        view = create_confirmation_buttons(ctx, member, embed, param, confirm_button)

        await ctx.reply(embed=embed, view=view)  # type: ignore

    @commands.command(aliases=['rb'])
    async def remindbill(self, ctx: Context, *, arg: str = None):
        if arg is None:
            return await ctx.reply("Please provide the bill id of the bill you wish to remind people of.  Example: `!rb br14`")
        
        participants = Invoice_Participant.get_participants(arg.upper())

        if participants is None:
            return await ctx.reply("Unable to find the associated bill.  Double check the bill is in your inventory with `!bc` and then re-run the command.")
        
        message = ''

        for participant in participants:
            if not participant.paid:
                message += f'<@{participant.participant_id}> '
        
        message += f'\n\nThis is your reminder to pay the owner of Bill `{arg.upper()}`. Please pay promptly via their method of choice.  To confirm payment, please either run `!pay {arg}` or `!ii {arg}`'

        return await ctx.reply(content=message, mention_author=False)


async def setup(bot: ManChanBot):
    if Ledger.is_enabled(bot.configs):
        await bot.add_cog(Ledger(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.ledger")
