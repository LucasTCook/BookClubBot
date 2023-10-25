import sqlite3
import settings
import discord
from discord.ext import commands
from ..views import group_buttons
from discord import Interaction

logger = settings.logging.getLogger("bot")
conn = sqlite3.connect(settings.SQL_DB)
cursor = conn.cursor()
conn.commit()

FIND_A_GROUP_CHANNEL_ID = settings.FIND_A_GROUP_CHANNEL_ID
VOTE_CHANNEL_ID = settings.VOTE_CHANNEL_ID
RESULT_CHANNEL_ID = settings.RESULT_CHANNEL_ID
HOME_CATEGORY_ID = settings.HOME_CATEGORY_ID

async def is_owner(ctx):
    return ctx.author.id == ctx.guild.owner.id


class AdminCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.check(is_owner)
    @commands.command(name="delete-all-suggestions", brief="Remove all suggestions", hidden= True)
    async def deleteAll(self, ctx):
        try:
            # Delete all suggestions from the database
            cursor = conn.cursor()
            cursor.execute("DELETE FROM suggested_books")
            conn.commit()

            # Delete the bot's messages in the voting channel
            voting_channel = self.bot.get_channel(VOTE_CHANNEL_ID)
            if voting_channel:
                async for message in voting_channel.history():
                    if message.author == self.bot.user:
                        if message.reference:
                            # If the message is part of a thread, delete the thread
                            thread = await voting_channel.fetch_message(message.reference.message_id)
                            await thread.delete()
                        await message.delete()

            # Delete messages in RESULT_CHANNEL_ID
            result_channel = self.bot.get_channel(RESULT_CHANNEL_ID)
            async for message in result_channel.history():
                await message.delete()

            await ctx.send("All suggestions and bot messages have been cleared.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    
    # Delete the user's command message
    # await ctx.message.delete()

    
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))