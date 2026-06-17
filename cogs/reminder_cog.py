import disnake
from disnake.ext import commands, tasks
import dateparser
from datetime import datetime
import json
import logging
import pytz

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.REMINDERS_FILE = 'reminders.json'
        self.reminders = {}
        self.utc = pytz.UTC
        self.pst = pytz.timezone('America/Los_Angeles')
        self.load_reminders()
        self.check_reminders.start()

    def load_reminders(self):
        try:
            with open(self.REMINDERS_FILE, 'r') as f:
                self.reminders = json.load(f)
        except FileNotFoundError:
            self.reminders = {}

    def save_reminders(self):
        with open(self.REMINDERS_FILE, 'w') as f:
            json.dump(self.reminders, f)

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        current_time = datetime.now(self.utc)
        reminders_to_remove = []
        
        for reminder_id, reminder in self.reminders.items():
            reminder_time = datetime.fromisoformat(reminder['time']).replace(tzinfo=self.utc)
            
            if current_time >= reminder_time:
                try:
                    channel = self.bot.get_channel(reminder['channel_id'])
                    user = self.bot.get_user(reminder['user_id'])
                    set_by = self.bot.get_user(reminder['set_by'])
                    
                    if not channel:
                        logging.error(f"Could not find channel with ID {reminder['channel_id']}")
                        continue
                        
                    if not user:
                        logging.error(f"Could not find user with ID {reminder['user_id']}")
                        continue
                        
                    if not set_by:
                        logging.error(f"Could not find user who set reminder with ID {reminder['set_by']}")
                        continue
                    
                    # Check if bot has permission to send messages
                    if not channel.permissions_for(channel.guild.me).send_messages:
                        logging.error(f"Bot does not have permission to send messages in channel {channel.name}")
                        continue
                    
                    # Send the reminder
                    if user.id == reminder['set_by']:
                        await channel.send(f"🔔 {user.mention} Reminder: {reminder['message']}")
                    else:
                        await channel.send(f"🔔 {user.mention} Reminder from {set_by.mention}: {reminder['message']}")
                    
                except Exception as e:
                    logging.error(f"Error sending reminder {reminder_id}: {str(e)}")
                    continue
                
                reminders_to_remove.append(reminder_id)
        
        # Remove sent reminders
        for reminder_id in reminders_to_remove:
            del self.reminders[reminder_id]
        
        if reminders_to_remove:
            self.save_reminders()

    @commands.command(name='remind')
    async def set_reminder(self, ctx, *, reminder_text):
        """
        Set a reminder. Usage: /remind [@user] [time] [message]
        Examples: 
        /remind in 2 hours to take out the trash
        /remind @user in 10 minutes to get on a call
        Times are interpreted in PST (Pacific Time)
        """
        try:
            # Check if the message starts with a user mention
            words = reminder_text.split()
            target_user = None
            
            if words[0].startswith('<@') and words[0].endswith('>'):
                # Extract user ID from mention
                user_id = int(words[0][2:-1].replace('!', ''))
                target_user = self.bot.get_user(user_id)
                if not target_user:
                    await ctx.send("I couldn't find that user. Please make sure to mention a valid user.")
                    return
                # Remove the mention from the reminder text
                reminder_text = ' '.join(words[1:])
            
            # Parse the reminder text to extract time and message
            words = reminder_text.split()
            time_str = ' '.join(words[:3])  # Get first 3 words for time parsing
            message = ' '.join(words[3:])   # Rest is the reminder message
            
            # Parse the time in PST
            reminder_time = dateparser.parse(time_str)
            if not reminder_time:
                await ctx.send("I couldn't understand the time format. Try something like 'in 2 hours' or 'tomorrow at 3pm'")
                return
            
            # Convert to PST if naive datetime
            if reminder_time.tzinfo is None:
                reminder_time = self.pst.localize(reminder_time)
            
            # Convert to UTC for storage
            reminder_time_utc = reminder_time.astimezone(self.utc)
                
            # Store the reminder
            reminder_id = str(ctx.message.id)
            self.reminders[reminder_id] = {
                'channel_id': ctx.channel.id,
                'user_id': target_user.id if target_user else ctx.author.id,
                'message': message,
                'time': reminder_time_utc.isoformat(),
                'set_by': ctx.author.id
            }
            self.save_reminders()
            
            # Create confirmation message in PST
            target = target_user.mention if target_user else "you"
            reminder_time_pst = reminder_time_utc.astimezone(self.pst)
            await ctx.send(f"Reminder set! I'll remind {target} about '{message}' at {reminder_time_pst.strftime('%d-%m-%Y %H:%M:%S %Z')}")
            
        except Exception as e:
            await ctx.send(f"Sorry, I couldn't set that reminder. Error: {str(e)}")

    @commands.command(name='reminders')
    async def list_reminders(self, ctx):
        """List all your active reminders (times shown in PST)"""
        user_reminders = [r for r in self.reminders.values() if r['user_id'] == ctx.author.id]
        
        if not user_reminders:
            await ctx.send("You don't have any active reminders.")
            return
        
        message = "**Your active reminders (PST):**\n"
        for i, reminder in enumerate(user_reminders, 1):
            reminder_time = datetime.fromisoformat(reminder['time']).replace(tzinfo=self.utc)
            reminder_time_pst = reminder_time.astimezone(self.pst)
            message += f"{i}. {reminder['message']} - {reminder_time_pst.strftime('%d-%m-%Y %H:%M:%S %Z')}\n"
        
        await ctx.send(message)

def setup(bot):
    bot.add_cog(ReminderCog(bot)) 