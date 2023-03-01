import random
import string
from datetime import datetime
import pytz

from discord import Color, Embed, Member, ButtonStyle, Interaction   #type: ignore
from discord.ext.commands.context import Context
from discord.ui import Button, View #type: ignore


from db.invoices import Invoice
from db.invoice_participants import Invoice_Participant

def verify_unique(uid: str) -> bool:
    return not Invoice.get(uid)

def gen_uuid(string_length: int) -> str:
    while True:
        charset = string.digits + ''.join(c for c in string.ascii_uppercase if c not in 'AEIOU')
        uuid = ''.join(random.choice(charset) for _ in range(string_length))
        if verify_unique(uuid):
            return uuid
        
def create_confirmation_buttons(ctx: Context, member: Member, embed: Embed, param: int, confirm: Button) -> View:   # type: ignore
    async def x_callback(interaction: Interaction): # type: ignore
        if interaction.user == ctx.author or interaction.user == member:
            if param == 1:
                embed.description = "Bill Cancelled.  Please re-run commands to fix errors if they exist." 
            elif param in [2,3]:
                embed.description = "Payment Cancelled.  Please re-run commands to fix errors if they exist." 
            embed.color = Color.red()
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.defer()

    async def check_callback(interaction: Interaction):         # type: ignore
        if interaction.user == member: 
            embed.color = Color.gold()
            check_button.disabled = True
            view.add_item(confirm)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.defer()

    x_button = Button(emoji='❌')
    x_button.callback = x_callback
    check_button = Button(emoji='☑️')
    check_button.callback = check_callback

    view = View()
    view.add_item(x_button)
    view.add_item(check_button)

    return view

def already_paid(bill: Invoice_Participant) -> Embed:
    already_paid = Embed(
        title="Bill Already Paid!",
        description=f'Invoice from Bill #`{bill.invoice_id}` was already paid by <@{bill.participant_id}> on <t:{bill.paid_on}:D>',
        color=Color.blue()
    )
    return already_paid

def get_pst_time() -> int:
    pst_timezone = pytz.timezone("America/Los_Angeles")
    pst_time = datetime.now(pst_timezone)

    return int(pst_time.timestamp())
