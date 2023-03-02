import logging
import typing

from discord import Color, Embed, Member, ButtonStyle, Interaction   #type: ignore
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, View, Select #type: ignore
from datetime import datetime

from main import ManChanBot
from utils.ledger_utils import gen_uuid, create_confirmation_buttons, already_paid, get_pst_time
from utils.context import get_member
from db.invoices import Invoice
from db.invoice_participants import Invoice_Participant

from .commandbase import CommandBase

class Ledger(CommandBase):
    @staticmethod
    def store_in_database(uuid: str, pay_id: int, payee_id: int, cost: float, arg: str, timestamp: int):
        table_entry = Invoice.get(uuid)

        if not table_entry:
            table_entry = Invoice.create(uuid)
        
        table_entry.set_values(pay_id, cost, arg, timestamp)

        participant_entry = Invoice_Participant.create(table_entry.id, payee_id, cost, False)

    @commands.command()
    async def bill(self, ctx: Context, member: Member, amount: float, *, description: str = None): #type: ignore
        if description is None:
            error_embed= Embed(
                title="Re-run command with a valid description",
                description=f'Example: `!bill @chai 1.23 Starbucks`'
            )
            await ctx.reply(embed=error_embed, mention_author=False)
        if len(description) > 25:
            await ctx.reply("The description must be 25 characters or less")
            return
        
        if ctx.author == member:
            fraud_embed = Embed(
                title="Fraud Warning",
                description="The authorities are on their way.  Stop trying to charge yourself!",
                color=Color.red()
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
            color=Color.blue()
        )
        message = f'{member.mention} please confirm the bill from {ctx.author.mention}'

        async def confirm_callback(interaction: Interaction): #type: ignore
            if interaction.user == member:
                bill_embed.color = Color.green()
                bill_embed.set_footer(text=f'Bill confirmed. Charge was added into database with ID #{bill_id}')

                Ledger.store_in_database(bill_id, ctx.author.id, member.id, amount, str(description), timestamp)
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        confirm_button = Button(emoji="☑", style = ButtonStyle.success)
        confirm_button.callback = confirm_callback

        view = create_confirmation_buttons(ctx, member, bill_embed, 1, confirm_button)

        await ctx.reply(content=message, embed=bill_embed, view=view, mention_author=False) #type: ignore

    @commands.command()
    async def form(self, ctx: Context):
        form_embed = Embed(
            title="Bill via Google Forms",
            description='[Use this to fill out the information!](https://forms.gle/ckiVkZk92WhqZNRA6)',
            color=Color.purple()
        )
        await ctx.reply(embed=form_embed, mention_author=False)
    
    @commands.command(aliases=["bi"])
    async def billinfo(self, ctx: Context, *, arg: str = None): #type: ignore
        if arg is None:
            bill = Invoice_Participant.get_latest(ctx.author.id)
        else:
            bill = Invoice_Participant.get(ctx.author.id, arg.upper())


        async def button_callback(interaction: Interaction):        # type: ignore
            if interaction.user == ctx.author:               
                if bill.paid:                                   # type: ignore - Bill will not be empty checked later
                    return await interaction.response.edit_message(embed=already_paid(bill), view=None) # type: ignore - Bill will not be empty checked later
                bill_embed.title = f'Pay Bill `{bill.invoice_id}`?'  # type: ignore - Bill will not be empty checked later
                bill_embed.color = Color.blue()
                member = get_member(ctx, invoice_info.payer_id)     # type: ignore - Bill will not be empty checked later
                member = typing.cast(Member, member)
                content = f'{member.mention} please confirm payment from {ctx.author.mention}'
                confirm_view = create_confirmation_buttons(ctx, member, bill_embed, 1, confirm_button)
                await interaction.response.edit_message(content=content, embed=bill_embed, view=confirm_view)

            else:
                await interaction.response.defer()

        pay_button = Button(label="Pay Bill", emoji='💸', style=ButtonStyle.success)
        pay_button.callback = button_callback

        pay_view = View()
        pay_view.add_item(pay_button)

        async def confirm_callback(interaction: Interaction): #type: ignore
            if interaction.user == get_member(ctx, invoice_info.payer_id):  # type: ignore - Bill will not be empty checked later
                bill_embed.color = Color.green()
                bill_embed.set_footer(text=f'Bill paid. Charge was updated in database')
                timestamp = get_pst_time()
                new_description = unpaid_description.replace("Pay", "Paid", 1)
                new_description += f'\nPaid: <t:{timestamp}:f>'
                bill_embed.description = new_description
                bill.set_paid(timestamp)     # type: ignore - Bill will not be empty checked later   
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        confirm_button = Button(emoji="☑", style = ButtonStyle.success)
        confirm_button.callback = confirm_callback

        if bill is not None:            
            invoice_info = Invoice.get(bill.invoice_id)
            member = get_member(ctx, invoice_info.payer_id)     # type: ignore - Bill will not be empty checked later
            member = typing.cast(Member, member)
            base_description = f'`{bill.invoice_id}` · `${bill.amount_owed}`\n\nReason: **{invoice_info.desc}**\n\n' # type: ignore - Bill will not be empty checked later
            unpaid_description = base_description + f"Pay to: <@{invoice_info.payer_id}>\n\nBilled: <t:{invoice_info.date}:f>" # type: ignore - Bill will not be empty checked later
            if invoice_info is not None:
                bill_embed = Embed(title="Bill Info")
                if bill.paid:
                    bill_embed.color = Color.green()
                    paid_description = unpaid_description.replace("Pay", "Paid", 1)
                    paid_description += f'\nPaid: <t:{bill.paid_on}:f>'
                    bill_embed.description = paid_description
                    await ctx.reply(embed=bill_embed, view=None, mention_author=False)      #type: ignore
                else:
                    bill_embed.color = Color.red()
                    bill_embed.description = unpaid_description
                    await ctx.reply(embed=bill_embed, view=pay_view, mention_author=False) #type: ignore
            else:   
                await ctx.reply("Invalid Code. Please re-run command", mention_author=False)

    @commands.command(aliases=["bc", "billc"])
    async def billcollection(self, ctx: Context):
        collection_embed = Embed(title="Invoice Collection")
        collection = Invoice_Participant.get_all(ctx.author.id)
        
        if len(collection) == 0:
            collection_embed.description = "No Invoices Associated with User."
            return await ctx.send(embed=collection_embed)
        
        description=f"Invoices for {ctx.author.mention}\n\n"

        for invoice in collection:
            emoji = '✔️' if invoice.paid else '⭕'
            parent_invoice = Invoice.get(invoice.invoice_id)
            invoice_desc = parent_invoice.desc     # type: ignore
            owed_id = parent_invoice.payer_id   # type: ignore
            description += f'{emoji}  `{invoice.invoice_id}`  ·  `${invoice.amount_owed: .2f}` · **{invoice_desc}** · Pay to <@{owed_id}>\n'
        
        collection_embed.description = description

        await ctx.reply(embed=collection_embed, mention_author=False)

    @commands.command()
    async def pay(self, ctx: Context, *, arg: str = None):  # type: ignore
        if arg is None:
            bill = Invoice_Participant.get_latest(ctx.author.id)
        else:
            bill = Invoice_Participant.get(ctx.author.id, arg.upper())

        async def confirm_callback(interaction: Interaction): #type: ignore
            if interaction.user == member:
                if not bill.paid:                       # type: ignore - Won't be none
                    timestamp = get_pst_time()
                    bill_embed.color = Color.green()
                    bill_embed.set_footer(text=f'Bill paid. Charge was updated in database.')
                    bill.set_paid(timestamp)     # type: ignore - Bill will not be empty checked later
                    paid_description = unpaid_description.replace("Pay", "Paid", 1)
                    paid_description += f'\nPaid: <t:{timestamp}:f>'
                    bill_embed.description = paid_description
                    await interaction.response.edit_message(embed=bill_embed, view=None)
                else:
                    paid_embed = already_paid(bill)    # type: ignore - Won't be none
                    await interaction.response.edit_message(embed=paid_embed, view=None)
            else:
                await interaction.response.defer()

        confirm_button = Button(emoji="☑", style = ButtonStyle.success)
        confirm_button.callback = confirm_callback

        if bill is not None:
            if bill.paid:
                return await ctx.reply(embed=already_paid(bill), mention_author=False)
            invoice_info = Invoice.get(bill.invoice_id)
            member = get_member(ctx, invoice_info.payer_id)     # type: ignore - Bill will not be empty checked later
            member = typing.cast(Member, member)
            if invoice_info is not None:
                unpaid_description = f'Reason: **{invoice_info.desc}**\n\nPay to: {member.mention}\nAmount: **${bill.amount_owed: .2f}**\n\nBilled: <t:{invoice_info.date}:f>'
                bill_embed = Embed(
                    title=f"Pay Bill `{bill.invoice_id}`?",
                    description=unpaid_description
                )
                content = f'{member.mention} please confirm payment from {ctx.author.mention}' 
                view = create_confirmation_buttons(ctx, member, bill_embed, 2, confirm_button)
                await ctx.reply(content=content, embed=bill_embed, view=view, mention_author=False)     #type: ignore
        else:
            await ctx.reply("Invalid Code. Please re-run command", mention_author=False)

    @commands.command(aliases=['billm', 'bm'])
    async def billmultiple(self, ctx: Context, total: float, *, arg: str = None):       # type: ignore
        bill_id = gen_uuid(4)
        timestamp = get_pst_time()
        multi_embed = Embed(title="New Multi-Bill")
        embed_description = f'Bill ID: `{bill_id}`\nDate: <t:{timestamp}:D>\n\nReason: {arg}\n\nPay to {ctx.author.mention}\n\nTotal Bill: **${total}**\n'
        multi_embed.description = embed_description
        select = Select(placeholder="Select people to bill", min_values=1, max_values=3)
        select.add_option(
            label='Test Ape',
            value=1059938083031761007
        )
        select.add_option(
            label='Man-chan',
            value=798958744003149854
        )
        select.add_option(
            label='ChaIvan',
            value=850083935651102720
        )

        async def select_callback(interaction: Interaction):    # type: ignore
            nonlocal embed_description
            if interaction.user == ctx.author:
                invoice = 'Bill the following people: \n'
                for value in select.values:
                    invoice += f'- <@{value}>\n'
                embed_description += invoice
                multi_embed.description = embed_description
                await interaction.response.edit_message(embed=multi_embed, view=split_view)

        select.callback = select_callback

        view = View()
        view.add_item(select)

        split_evenly = Button(emoji='🟰', label='Split Evenly', style=ButtonStyle.success)
        split_specific = Button(emoji='🔢', label='Split Specific')

        split_view = View()
        split_view.add_item(split_evenly)
        split_view.add_item(split_specific)

        await ctx.reply(embed=multi_embed, view=view, mention_author=False)     # type: ignore 

    @commands.command(aliases=['tc'])
    async def test_confirm(self, ctx: Context, member: Member, param: int):
        embed = Embed(
            title="Test Embed",
            description="Creates a test embed to attach views to"
        )

        async def confirm_callback(interaction: Interaction):    # type: ignore
            await interaction.response.edit_message(content="Button works", embed=None, view=None)

        confirm_button = Button(emoji='☑️')
        confirm_button.callback = confirm_callback

        view = create_confirmation_buttons(ctx, member, embed, param, confirm_button)

        await ctx.reply(embed=embed, view=view)     # type: ignore

    @commands.command()
    async def time(self, ctx: Context):
        embed = Embed(title="Time Test")
        timestamp = get_pst_time()
        embed.description = f'<t:{timestamp}:d>'
        await ctx.reply(datetime.utcnow(), embed=embed)

async def setup(bot: ManChanBot):
    if Ledger.is_enabled(bot.configs):
        await bot.add_cog(Ledger(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.ledger")