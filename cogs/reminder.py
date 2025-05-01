import disnake
from disnake.ext import commands, tasks
import dateparser
from datetime import datetime
import json
import logging
import uuid
from typing import Dict, Any

from main import ManChanBot
from .commandbase import CommandBase

logger = logging.getLogger(__name__)

class ReminderCog(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.REMINDERS_FILE = 'reminders.json'
        self.reminders: Dict[str, Any] = {}
        self.load_reminders()
        self.check_reminders.start()

    def load_reminders(self):
        try:
            with open(self.REMINDERS_FILE, 'r') as f:
                self.reminders = json.load(f)
                # Remove any reminders that have already been sent
                self.reminders = {k: v for k, v in self.reminders.items() if not v.get('sent', False)}
        except FileNotFoundError:
            self.reminders = {}

    def save_reminders(self):
        with open(self.REMINDERS_FILE, 'w') as f:
            json.dump(self.reminders, f)

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        current_time = datetime.now()
        reminders_to_remove = []
        
        for reminder_id, reminder in self.reminders.items():
            if reminder.get('sent', False):
                reminders_to_remove.append(reminder_id)
                continue
                
            reminder_time = datetime.fromisoformat(reminder['time'])
            
            if current_time >= reminder_time:
                try:
                    channel = self.bot.get_channel(reminder['channel_id'])
                    user = self.bot.get_user(reminder['user_id'])
                    set_by = self.bot.get_user(reminder['set_by'])
                    
                    if not channel:
                        logger.error(f"Could not find channel with ID {reminder['channel_id']}")
                        continue
                        
                    if not user:
                        logger.error(f"Could not find user with ID {reminder['user_id']}")
                        continue
                        
                    if not set_by:
                        logger.error(f"Could not find user who set reminder with ID {reminder['set_by']}")
                        continue
                    
                    # Check if bot has permission to send messages
                    if not channel.permissions_for(channel.guild.me).send_messages:
                        logger.error(f"Bot does not have permission to send messages in channel {channel.name}")
                        continue
                    
                    # Mark the reminder as sent before sending to prevent race conditions
                    reminder['sent'] = True
                    self.save_reminders()
                    
                    # Send the reminder
                    if user.id == reminder['set_by']:
                        await channel.send(f"🔔 {user.mention} Reminder: {reminder['message']}")
                    else:
                        await channel.send(f"🔔 {user.mention} Reminder from {set_by.mention}: {reminder['message']}")
                    
                    # Add to removal list
                    reminders_to_remove.append(reminder_id)
                    
                except Exception as e:
                    logger.error(f"Error sending reminder {reminder_id}: {str(e)}")
                    # If there was an error, unmark the reminder as sent
                    reminder['sent'] = False
                    continue
        
        # Remove sent reminders and save only once
        if reminders_to_remove:
            for reminder_id in reminders_to_remove:
                del self.reminders[reminder_id]
            self.save_reminders()

    @commands.command(name='remind')
    async def set_reminder(self, ctx: commands.Context, *, reminder_text: str):
        """
        Set a reminder. Usage: /remind [@user] [time] [message]
        Examples: 
        /remind in 2 hours to take out the trash
        /remind @user in 10 minutes to get on a call
        """
        try:
            logger.debug(f"Setting new reminder: {reminder_text}")
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
            
            # Parse the time
            reminder_time = dateparser.parse(time_str)
            if not reminder_time:
                await ctx.send("I couldn't understand the time format. Try something like 'in 2 hours' or 'tomorrow at 3pm'")
                return
                
            # Store the reminder with a unique ID
            reminder_id = str(uuid.uuid4())
            logger.debug(f"Creating new reminder with ID {reminder_id}")
            self.reminders[reminder_id] = {
                'channel_id': ctx.channel.id,
                'user_id': target_user.id if target_user else ctx.author.id,
                'message': message,
                'time': reminder_time.isoformat(),
                'set_by': ctx.author.id,
                'sent': False
            }
            self.save_reminders()
            
            # Create confirmation message
            target = target_user.mention if target_user else "you"
            await ctx.send(f"Reminder set! I'll remind {target} about '{message}' at {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error setting reminder: {str(e)}")
            await ctx.send(f"Sorry, I couldn't set that reminder. Error: {str(e)}")

    @commands.command(name='reminders')
    async def list_reminders(self, ctx: commands.Context):
        """List all your active reminders"""
        user_reminders = [r for r in self.reminders.values() if r['user_id'] == ctx.author.id]
        
        if not user_reminders:
            await ctx.send("You don't have any active reminders.")
            return
        
        message = "**Your active reminders:**\n"
        for i, reminder in enumerate(user_reminders, 1):
            reminder_time = datetime.fromisoformat(reminder['time'])
            message += f"{i}. {reminder['message']} - {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        await ctx.send(message)
        
    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}) -> bool:
        return configs.get("ENABLE_REMINDER_COG", False)

def setup(bot: ManChanBot):
    if ReminderCog.is_enabled(bot.configs):
        bot.add_cog(ReminderCog(bot))
    else:
        logging.warn("SKIPPING: cogs.reminder") 