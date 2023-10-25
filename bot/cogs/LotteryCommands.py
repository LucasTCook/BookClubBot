import random
import sqlite3
import settings
import discord
import asyncio
from discord.ext import commands
from utils import logger
from utils import create_leaderboard_embed

conn = sqlite3.connect(settings.SQL_DB)
cursor = conn.cursor()
conn.commit()

class LotteryCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.HOME_CATEGORY_ID = settings.HOME_CATEGORY_ID
        self.countdown = 10

    def is_owner(ctx):
        return ctx.author.id == ctx.guild.owner.id

    # @commands.check(is_owner)
    # @commands.hybrid_command(name="lottery", brief="Entries based on positive vote karma.")
    # async def lottery(self, ctx):
    #     if self.countdown == 0:
    #         await ctx.send(":x: **Error:** Countdown duration was not passed. Use `!strawpick (duration)` to set it.")
    #         return

    #     books_votes = self.retrieve_book_votes()

    #     # Create the lottery set
    #     lottery_pool = []
    #     covers = {}
    #     descriptions = {}
    #     authors = {}
    #     for title, author, user_id, upvotes, downvotes, keywords, cover, desc in books_votes:
    #         if (upvotes - downvotes) > 0:
    #             lottery_pool.extend([title] * (upvotes - downvotes))
    #             covers[title] = cover
    #             descriptions[title] = desc
    #             authors[title] = author

    #     embed = discord.Embed()

    #     formatted_list = [f"{book}" for book in lottery_pool]

    #     embed.description = "\n".join(formatted_list)

    #     countdown_message = ":tada: **LET THE LOTTERY BEGIN!** :tada:"
    #     message = await ctx.send(content=countdown_message, embed=embed)
    #     await asyncio.sleep(3)

    #     # Start the countdown
    #     countdown_message = await message.edit(content="", embed=embed)
    #     for remaining_time in range(self.countdown, -1, -1):
    #         selected_suggestion = random.choice(lottery_pool)

    #         # Create a bulleted list as a string with random bold text
    #         formatted_list = [f"**{book}**" if book == selected_suggestion else f"~~{book}~~" for book in lottery_pool]

    #         embed.title = f":hourglass: **Time Left:** {remaining_time} seconds :hourglass:"
    #         embed.description = "\n".join(formatted_list)
    #         embed.set_thumbnail(url=covers[selected_suggestion])     
    #         # countdown_message = f":hourglass: **Time Left:** {remaining_time} seconds :hourglass:"
    #         countdown_message = await message.edit(embed=embed)
            
    #         if(remaining_time == 0):
    #             countdown_message = await message.edit(content="", embed=embed)
    #             embed = discord.Embed()
    #             embed.title = f":trophy: WINNER :trophy:\n **{selected_suggestion}** *{authors[selected_suggestion]}* "
    #             embed.description=descriptions[selected_suggestion]
    #             embed.set_thumbnail(url=covers[selected_suggestion])
    #             await ctx.send(embed=embed)
    #         else:
    #             await asyncio.sleep(1)

                

    # @commands.check(is_owner)
    # @commands.hybrid_command(name="strawpick", brief="Pick a suggestion tied for first randomly.")
    # async def strawpick(self,ctx, top_placements):
    #     if self.countdown == 0:
    #         await ctx.send("Countdown duration was not passed. Use !strawpick (duration) (placements) to set it.")
    #         return

    #     books_votes = self.retrieve_book_votes()

    #     if not books_votes:
    #         await ctx.send("No suggested books found!")
    #         return
        

    #     lottery_pool = []
    #     covers = {}
    #     descriptions = {}
    #     authors = {}

    #     # Sort the books based on net votes
    #     sorted_books = sorted(books_votes, key=lambda x: x[3] - x[4], reverse=True)

    #     # Determine the net votes of the nth book (where n = number_of_placements)
    #     threshold_votes = sorted_books[top_placements - 1][3] - sorted_books[top_placements - 1][4] if len(sorted_books) >= top_placements else None

    #     candidates = []
    #     for book in sorted_books:
    #         if book[3] - book[4] >= threshold_votes:
    #             candidates.append(book)

    #     for title, author, user_id, upvotes, downvotes, keywords, cover, desc in candidates:
    #         lottery_pool.extend([title])
    #         covers[title] = cover
    #         descriptions[title] = desc
    #         authors[title] = author

    #     embed = discord.Embed()

    #     formatted_list = [f"{book}" for book in lottery_pool]

    #     embed.description = "\n".join(formatted_list)

    #     countdown_message = ":tada: **LET THE STRAWPICK BEGIN!** :tada:"
    #     message = await ctx.send(content=countdown_message, embed=embed)
    #     await asyncio.sleep(3)

    #     countdown_message = await message.edit(content="", embed=embed)
    #     for remaining_time in range(self.countdown, -1, -1):
    #         embed.title = f":hourglass: **Time Left:** {remaining_time} seconds :hourglass:"
    #         selected_suggestion = random.choice(lottery_pool)
    #         formatted_list = [f"**{book}**" if book == selected_suggestion else book for book in lottery_pool]
    #         embed.description = "\n".join(formatted_list)
    #         embed.set_thumbnail(url=covers[selected_suggestion])
    #         await message.edit(embed=embed)
            
    #         if(remaining_time == 0):
                
    #             embed = discord.Embed()
    #             embed.title = f":trophy: WINNER :trophy:\n **{selected_suggestion}** *{authors[selected_suggestion]}* "
    #             embed.description=descriptions[selected_suggestion]
    #             embed.set_thumbnail(url=covers[selected_suggestion])
    #             await ctx.send(embed=embed)
    #         else:
    #             await asyncio.sleep(1)


    # def retrieve_book_votes(self):
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT title, author, user_id, upvotes, downvotes, keywords, cover, desc FROM suggested_books ORDER BY (upvotes - downvotes) DESC")
    #     suggested_books = cursor.fetchall()
    #     return suggested_books

async def setup(bot):
    await bot.add_cog(LotteryCommands(bot))