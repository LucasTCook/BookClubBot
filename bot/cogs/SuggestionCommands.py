import sqlite3
import settings
import discord
from discord.ext import commands
from utils import create_leaderboard_embed
from utils import logger

conn = sqlite3.connect(settings.SQL_DB)
cursor = conn.cursor()
conn.commit()

class SuggestionCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # @commands.hybrid_command(name="suggestions", brief="Displays the current suggestions with their voting score")
    # async def suggestions(self, ctx):
    #     try:
    #         logger.info("IN SUGGESTIONS")
    #         embed = await create_leaderboard_embed(ctx)
    #         if embed:
    #             await ctx.send(embed=embed)
    #         else:
    #             await ctx.send("No books have been suggested yet.")
    #     except Exception as e:
    #         logger.error(f"Error in suggestions: {e}")
    #         await ctx.send("An error occurred while fetching suggestions.")

    

async def setup(bot):
    await bot.add_cog(SuggestionCommands(bot))