import logging

from discord import Color, Embed, Member, ButtonStyle, Interaction   #type: ignore
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, View #type: ignore

from main import ManChanBot
from utils.ledger_utils import gen_uuid
from utils.context import get_member
from db.invoices import Invoice
from db.invoice_participants import Invoice_Participant

from .commandbase import CommandBase

class Ledger(CommandBase):
    @staticmethod
    def store_in_database(uuid: str, pay_id: int, payee_id: int, cost: float, arg: str):
        table_entry = Invoice.get(uuid)

        if not table_entry:
            table_entry = Invoice.create(uuid)
        
        table_entry.set_values(pay_id, cost, arg)

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
            
        amount = round(amount, 2)
        if amount < 0:
            await ctx.reply("The amount cannot be negative")
            return
        
        bill_id = gen_uuid(4)
        formatted_amount = "{:.2f}".format(amount)
        bill_embed = Embed(
            title="New Bill",
            description=f"Bill ID: `{bill_id}`\nDate: `02/28/2023`\n\nReason: **{description}**\n\nPaid by {ctx.author.mention}\nBill to{member.mention}\nTotal Bill: **${formatted_amount}**",
            color=Color.blue()
        )
        message = f'{member.mention} please confirm the bill from {ctx.author.mention}'
        
        async def x_callback(interaction: Interaction):  #type: ignore
            if interaction.user == ctx.author or interaction.user == member:
                bill_embed.description="Bill Cancelled.  Please re-run commands to fix errors if they exist"
                bill_embed.color = Color.red()
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        async def check_callback(interaction: Interaction): #type: ignore
            if interaction.user == member:
                bill_embed.color = Color.gold()
                check_button.disabled = True
                view.add_item(confirm_button)
                await interaction.response.edit_message(embed=bill_embed, view=view)
            else:
                await interaction.response.defer()

        async def confirm_callback(interaction: Interaction): #type: ignore
            if interaction.user == member:
                bill_embed.color = Color.green()
                bill_embed.set_footer(text=f'Bill confirmed. Charge was added into database with ID #{bill_id}')
                Ledger.store_in_database(bill_id, ctx.author.id, member.id, amount, str(description))
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

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
    
    @commands.command(aliases=["bi"])
    async def billinfo(self, ctx: Context, *, arg: str = None): #type: ignore
        if arg is None:
            bill = Invoice_Participant.get_latest(ctx.author.id)
        else:
            bill = Invoice_Participant.get(ctx.author.id, arg.upper())

        async def button_callback(interaction: Interaction):
            if interaction.user == ctx.author:
                bill_embed.title = f'Pay Bill `{bill.invoice_id}`?'
                bill_embed.color = Color.blue()
                content = f'{get_member(ctx, invoice_info.payer_id).mention} please confirm payment from {ctx.author.mention}'

                await interaction.response.edit_message(content=content, embed=bill_embed, view=confirm_view)

            else:
                await interaction.response.defer()

        pay_button = Button(label="Pay Bill", emoji='💸', style=ButtonStyle.success)
        pay_button.callback = button_callback

        pay_view = View()
        pay_view.add_item(pay_button)

        async def x_callback(interaction: Interaction):  #type: ignore
            if interaction.user == ctx.author or interaction.user == get_member(ctx, invoice_info.payer_id):
                bill_embed.description="Payment Cancelled.  Please re-run commands to fix errors if they exist"
                bill_embed.color = Color.red()
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        async def check_callback(interaction: Interaction): #type: ignore
            if interaction.user == get_member(ctx, invoice_info.payer_id):
                bill_embed.color = Color.gold()
                check_button.disabled = True
                confirm_view.add_item(confirm_button)
                await interaction.response.edit_message(embed=bill_embed, view=confirm_view)
            else:
                await interaction.response.defer()

        async def confirm_callback(interaction: Interaction): #type: ignore
            if interaction.user == get_member(ctx, invoice_info.payer_id):
                bill_embed.color = Color.green()
                bill_embed.set_footer(text=f'Bill paid. Charge was updated in database')
                bill.set_paid()
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        x_button = Button(emoji="❌")
        x_button.callback = x_callback
        check_button = Button(emoji="☑")
        check_button.callback = check_callback
        confirm_button = Button(emoji="☑", style = ButtonStyle.success)
        confirm_button.callback = confirm_callback

        confirm_view = View()
        confirm_view.add_item(x_button)
        confirm_view.add_item(check_button)

        if bill is not None:
            invoice_info = Invoice.get(bill.invoice_id)
            if invoice_info is not None:
                bill_embed = Embed(
                    title="Bill Info",
                    description=f'`{bill.invoice_id}` · `02/28/23`\n\nReason: **{invoice_info.desc}**\n\nPay to: <@{invoice_info.payer_id}>\nAmount: **${bill.amount_owed: .2f}**'
                )
                bill_embed.color = Color.green() if bill.paid == True else Color.red()
                await ctx.reply(embed=bill_embed, view=pay_view, mention_author=False)
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

        async def x_callback(interaction: Interaction):  #type: ignore
            if interaction.user == ctx.author or interaction.user == get_member(ctx, invoice_info.payer_id):
                bill_embed.description="Payment Cancelled.  Please re-run commands to fix errors if they exist"
                bill_embed.color = Color.red()
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        async def check_callback(interaction: Interaction): #type: ignore
            if interaction.user == get_member(ctx, invoice_info.payer_id):
                bill_embed.color = Color.gold()
                check_button.disabled = True
                view.add_item(confirm_button)
                await interaction.response.edit_message(embed=bill_embed, view=view)
            else:
                await interaction.response.defer()

        async def confirm_callback(interaction: Interaction): #type: ignore
            if interaction.user == get_member(ctx, invoice_info.payer_id):
                bill_embed.color = Color.green()
                bill_embed.set_footer(text=f'Bill paid. Charge was updated in database')
                bill.set_paid()
                await interaction.response.edit_message(embed=bill_embed, view=None)
            else:
                await interaction.response.defer()

        x_button = Button(emoji="❌")
        x_button.callback = x_callback
        check_button = Button(emoji="☑")
        check_button.callback = check_callback
        confirm_button = Button(emoji="☑", style = ButtonStyle.success)
        confirm_button.callback = confirm_callback

        view = View()
        view.add_item(x_button)
        view.add_item(check_button)

        if bill is not None:
            invoice_info = Invoice.get(bill.invoice_id)
            if invoice_info is not None:
                bill_embed = Embed(
                    title=f"Pay Bill `{bill.invoice_id}`?",
                    description=f'Reason: **{invoice_info.desc}**\n\nPay to: <@{invoice_info.payer_id}>\nAmount: **${bill.amount_owed: .2f}**'
                )
                content = f'{get_member(ctx, invoice_info.payer_id).mention} please confirm payment from {ctx.author.mention}' 
                await ctx.reply(content=content, embed=bill_embed, view=view, mention_author=False)
        else:
            await ctx.reply("Invalid Code. Please re-run command", mention_author=False)

async def setup(bot: ManChanBot):
    if Ledger.is_enabled(bot.configs):
        await bot.add_cog(Ledger(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.ledger")