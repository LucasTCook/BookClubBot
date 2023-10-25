# External Libraries
import requests
import sqlite3
import json
import random
import asyncio
import os
import random
from dotenv import load_dotenv
# from utils import create_leaderboard_embed

# Discord Libraries
import discord
from discord.ext import commands
from discord.ext.commands import Converter, command
from discord import app_commands
# from discord_components import DiscordComponents, Button  # This is commented out as you mentioned not using it

# Local Modules
import settings
# from ui import buttons
from database import db_setup
from handlers import *
# from bot.views.group_buttons import JoinGroupButton


load_dotenv()
logger = settings.logging.getLogger("bot")

# Initialize the bot with a prefix
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Define a dictionary to map message IDs to suggestion IDs
suggestion_message_ids = {}

FIND_A_GROUP_CHANNEL_ID = settings.FIND_A_GROUP_CHANNEL_ID
VOTE_CHANNEL_ID = settings.VOTE_CHANNEL_ID
RESULT_CHANNEL_ID = settings.RESULT_CHANNEL_ID
HOME_CATEGORY_ID = settings.HOME_CATEGORY_ID
GOOGLE_BOOKS_API_KEY = settings.GOOGLE_BOOKS_API_KEY

BOT_REMOVING_REACTION = False

conn = sqlite3.connect(settings.SQL_DB)
cursor = conn.cursor()
conn.commit()

db_setup.verify_and_create_tables()


@bot.event
async def on_ready():
    await startup_logs()
    # await startup_extension_sync()

    # bot.tree.copy_global_to(guild=settings.GUILDS_ID)
    # synced = await bot.tree.sync()
    # synced_local = await bot.tree.sync(guild=settings.GUILDS_ID)
    # logger.info(f"Synced Global{str(len(synced))}")
    # logger.info(f"Synced Local{str(len(synced_local))}")



# async def startup_extension_sync():
    # for cmd_file in settings.CMDS_DIR.glob("*.py"):
    #     if cmd_file.name != "__init__.py":
    #         await bot.load_extension(f"bot.cmds.{cmd_file.name[:-3]}")

    # for filename in os.listdir(settings.COGS_DIR):
    #     if filename.endswith(".py") and filename != "__init__.py":
    #         path_without_extension = filename[:-3]
    #         await bot.load_extension(f"bot.cogs.{path_without_extension}")

async def startup_logs():
    logger.info(f'Logged in as {bot.user.name}')
    logger.info(f"User: {bot.user} (ID: {bot.user.id})")
    logger.info(f"Guild ID: {settings.GUILD_ID_INT}")
    logger.info(f"Vote Channel ID: {VOTE_CHANNEL_ID}")
    logger.info(f"Leaderboard Channel ID: {RESULT_CHANNEL_ID}")
    logger.info(f"Home Category ID: {HOME_CATEGORY_ID}")
    logger.info(f"Find a Group Channel ID: {FIND_A_GROUP_CHANNEL_ID}")
    logger.info(f"Google API KEY: {GOOGLE_BOOKS_API_KEY}")
    logger.info(f"CMD DIR: {settings.COGS_DIR}")
    logger.info(f"CMD DIR: {settings.CMDS_DIR}")


async def is_owner(ctx):
    return ctx.author.id == ctx.guild.owner.id

@bot.command(name="suggest",brief="Suggest a book")
async def suggest(ctx, *args):

    def is_book_duplicate(title):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM suggested_books WHERE title=?", (title,))
        count = cursor.fetchone()[0]
        return count > 0

    if VOTE_CHANNEL_ID:
        user_id = ctx.author.id  # Get the Discord user ID of the person who submitted the suggestion

        # Check how many suggestions the user has made
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM suggested_books WHERE user_id = ?", (user_id,))
        suggestion_count = cursor.fetchone()[0]

        if suggestion_count >= 3:
            await ctx.send("You've already made three suggestions. Modify your suggestions using !mysuggestions")
            return

        
        book_name = " ".join(args)  # Join all provided words into a single string

        if GOOGLE_BOOKS_API_KEY is None:
            await ctx.send("⚠️ Google Books API not configured")
            return

        # Make a request to the Google Books API
        url = f'https://www.googleapis.com/books/v1/volumes?q={book_name}&key={GOOGLE_BOOKS_API_KEY}'
        response = requests.get(url)
        data = response.json()

        if 'items' in data:
            # Filter the results to select the most relevant entry
            selected_entry = None
            for entry in data['items']:
                if entry['volumeInfo'].get('title', '').lower() == book_name.lower():
                    selected_entry = entry
                    break  # Found an exact title match, break the loop

            # If no exact title match was found, use the first entry as a fallback
            if selected_entry is None:
                selected_entry = data['items'][0]

            book = selected_entry['volumeInfo']

            title = book.get('title', 'Title not found')
            author = book.get('authors', ['Author not found'])[0]
            description = book.get('description', 'Description not found')
            image_url = book.get('imageLinks', {}).get('thumbnail', '')

            # Check if the book has already been suggested
            if is_book_duplicate(title):
                await ctx.send("This book has already been suggested.")
                return
            else:
                genre_emoji = "📖"
                embed = discord.Embed(title=title, description=description)
                embed.set_author(name=author)
                embed.set_thumbnail(url=image_url)

                embed.add_field(name="keywords", value= book_name, inline=False)


                # Include additional book details in the embed
                embed.add_field(name="Submitted By", value= ctx.author.name, inline=False)

                embed.add_field(name="Instructions: ", value = "Thank you for your book suggestion! 📖  \n\nTo approve, click ✅ and your book will be sent to #suggestion-voting. \n To reject, click 🚫", inline=False)

                # Send a private message to the user with book details and emoji reactions
                # private_message = await ctx.author.send("")
                suggestion_message = await ctx.author.send(embed=embed)


                # Add Green check (✅) and 🚫 emoji reactions to the private message
                await suggestion_message.add_reaction("✅")
                await suggestion_message.add_reaction("🚫")


        else:
            await ctx.send("Book not found.")

        # Delete the user's command message
        # await ctx.message.delete()
        # view=buttons.Buttons()
        # await ctx.send(f"{title} has been suggested and is pending approval.",view=view)
        await ctx.send(f"{title} has been suggested and is pending approval.")
        
    else:
        await ctx.send("Voting channel has not been configured.")

@bot.command(name="mysuggestions", brief="View and Remove your suggestions")
async def my_suggestions(ctx):
    # Get the user's ID
    user_id = ctx.author.id

    # Fetch the user's suggestions from the database
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, desc, cover FROM suggested_books WHERE user_id = ?", (user_id,))
    user_suggestions = cursor.fetchall()

    if user_suggestions:
        for suggestion in user_suggestions:
            title, author, desc, cover = suggestion

            # Create an embed for each suggestion using the retrieved data
            embed = discord.Embed(title=title, description=desc, color=discord.Color.blue())
            embed.set_author(name=author)
            embed.set_thumbnail(url=cover)

            # Send the embed to the user
            message = await ctx.author.send(embed=embed)

            # Add a reaction (❌ emoji) to allow the user to delete their suggestion
            await message.add_reaction("❌")

            # Store the suggestion message ID in the dictionary for future reference
            suggestion_message_ids[message.id] = title  # Use message ID as the key
    else:
        await ctx.author.send("You haven't made any suggestions yet.")

@bot.command(name="suggestions",brief="Displays current suggestoins")
async def leaderboard(ctx):
    embed = await create_leaderboard_embed()
    if embed:
        await ctx.send(embed=embed)
    else:
        await ctx.send("No books have been suggested yet.")

async def create_winner_channels(selected_suggestion):
    if HOME_CATEGORY_ID:
        # Find the Book Club category by ID
        home_category = bot.get_channel(HOME_CATEGORY_ID)

        if home_category and isinstance(home_category, discord.CategoryChannel):
            # Create text channels within the specified category
            await home_category.create_text_channel(f"📖{selected_suggestion}-progress")
            await home_category.create_text_channel(f"📣{selected_suggestion}-announcements")
            await home_category.create_text_channel(f"🚫{selected_suggestion}-spoiler")
            await home_category.create_text_channel(f"🆓{selected_suggestion}-spoiler-free")
            

@commands.check(is_owner)
@bot.command(name="lottery", brief="Entries based on positive vote karma.")
async def lottery(ctx,type="",countdown = 10):
    # logger.info(f"In lottery")
    if countdown == 0:
        await ctx.send(":x: **Error:** Countdown duration was not passed. Use `!strawpick (duration)` to set it.")
        return

    books_votes = retrieve_book_votes()

    # logger.info(f"Book Votes: {books_votes}")

    # Create the lottery set
    lottery_pool = []
    covers = {}
    descriptions = {}
    authors = {}
    for title, author, user_id, upvotes, downvotes, keywords, cover, desc in books_votes:
        if (upvotes - downvotes) > 0:
            lottery_pool.extend([title] * (upvotes - downvotes))
            covers[title] = cover
            descriptions[title] = desc
            authors[title] = author

    # logger.info("Lottery 2")

    embed = discord.Embed()

    formatted_list = [f"{book}" for book in lottery_pool]
    # logger.info("Lottery")
    embed.description = "\n".join(formatted_list)

    countdown_message = ":tada: **LET THE LOTTERY BEGIN!** :tada:"
    message = await ctx.send(content=countdown_message, embed=embed)
    await asyncio.sleep(3)

    # Start the countdown
    countdown_message = await message.edit(content="", embed=embed)
    for remaining_time in range(countdown, -1, -1):
        selected_suggestion = random.choice(lottery_pool)


        # Create a bulleted list as a string with random bold text
        formatted_list = [f"**{book}**" if book == selected_suggestion else f"~~{book}~~" for book in lottery_pool]

        embed.title = f":hourglass: **Time Left:** {remaining_time} seconds :hourglass:"
        embed.description = "\n".join(formatted_list)
        embed.set_thumbnail(url=covers[selected_suggestion])     
        countdown_message = await message.edit(embed=embed)
            
        if(remaining_time == 0):
            countdown_message = await message.edit(content="", embed=embed)
            embed = discord.Embed()
            embed.title = f":trophy: WINNER :trophy:\n **{selected_suggestion}** *{authors[selected_suggestion]}* "
            embed.description=descriptions[selected_suggestion]
            embed.set_thumbnail(url=covers[selected_suggestion])
            await ctx.send(embed=embed)

            await create_winner_channels(selected_suggestion)
        else:
            # If in LMS mode, remove the selected suggestion
            if type == 'lms':
                lottery_pool.remove(selected_suggestion)
            await asyncio.sleep(1)

# @commands.check(is_owner)
@bot.command(name="strawpick", brief="Pick a suggestion tied for first randomly.")
async def strawpick(ctx, top_placements=3,countdown = 10):
    # logger.info("In strawpick")
    if countdown == 0:
        await ctx.send(":x: **Error:** Countdown duration was not passed. Use `!strawpick (duration)` to set it.")
        return

    books_votes = retrieve_book_votes()

    if not books_votes:
        await ctx.send("No suggested books found!")
        return
    
    # logger.info("In strawpick 2")
    lottery_pool = []
    covers = {}
    descriptions = {}
    authors = {}

    # Sort the books based on net votes
    sorted_books = sorted(books_votes, key=lambda x: x[3] - x[4], reverse=True)
    # logger.info("In strawpick 3")
    # Determine the net votes of the nth book (where n = number_of_placements)
    threshold_votes = None  # default value
    top_placements=int(top_placements)
    if len(sorted_books) >= int(top_placements):
        threshold_votes = sorted_books[top_placements - 1][3] - sorted_books[top_placements - 1][4]
    # logger.info("In strawpick 4")
    candidates = []
    for book in sorted_books:
        if book[3] - book[4] >= threshold_votes:
            candidates.append(book)
    # logger.info("In strawpick 5")
    for title, author, user_id, upvotes, downvotes, keywords, cover, desc in candidates:
        lottery_pool.extend([title])
        covers[title] = cover
        descriptions[title] = desc
        authors[title] = author

    embed = discord.Embed()

    formatted_list = [f"{book}" for book in lottery_pool]
    # logger.info(formatted_list)

    embed.description = "\n".join(formatted_list)

    countdown_message = ":tada: **LET THE STRAWPICK BEGIN!** :tada:"
    message = await ctx.send(content=countdown_message, embed=embed)
    await asyncio.sleep(3)

    countdown_message = await message.edit(content="", embed=embed)
    for remaining_time in range(countdown, -1, -1):
        embed.title = f":hourglass: **Time Left:** {remaining_time} seconds :hourglass:"
        selected_suggestion = random.choice(lottery_pool)
        formatted_list = [f"**{book}**" if book == selected_suggestion else f"~~{book}~~" for book in lottery_pool]
        embed.description = "\n".join(formatted_list)
        embed.set_thumbnail(url=covers[selected_suggestion])
        await message.edit(embed=embed)
        
        if(remaining_time == 0):
            
            embed = discord.Embed()
            embed.title = f":trophy: WINNER :trophy:\n **{selected_suggestion}** *{authors[selected_suggestion]}* "
            embed.description=descriptions[selected_suggestion]
            embed.set_thumbnail(url=covers[selected_suggestion])
            await ctx.send(embed=embed)
        else:
            await asyncio.sleep(1)

    await create_winner_channels(selected_suggestion)

def retrieve_book_votes():
    logger.info("In retrieve books")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, user_id, upvotes, downvotes, keywords, cover, desc FROM suggested_books ORDER BY (upvotes - downvotes) DESC")
        suggested_books = cursor.fetchall()
        return suggested_books
    except:
        logger.error("Error retrieving votes")

async def create_leaderboard_embed():
    logger.info("IN create leaderboard")

    cursor = conn.cursor()
    cursor.execute("SELECT title, user_id, upvotes, downvotes, keywords, author, cover, pageCount FROM suggested_books ORDER BY (upvotes - downvotes) DESC")
    suggested_books = cursor.fetchall()

    if suggested_books:
        embed = discord.Embed(title="Vote Results", color=discord.Color.gold())
        details = ""
        first_place_points = suggested_books[0][2] - suggested_books[0][3]
        next_placement = 0
        pin_thumbnail = False  # Track if we should pin the thumbnail

        for i, (title, user_id, upvotes, downvotes, keywords, author, cover, pageCount) in enumerate(suggested_books):
            user = bot.get_user(user_id)
            if user is not None:
                user_name = user.name
            else:
                user_name = "Unknown User"

            # Determine medal
            score = upvotes - downvotes
            # medal = "🥇" if score == first_place_points else (next_placement if score == previous_score else (i+1))

            if score == first_place_points:
                medal = "🥇"
            elif score == previous_score: 
                medal = next_placement
            else:
                # medal = (i+1)

                if (i+1) == 2:
                    medal = "2nd"
                elif (i+1) == 3:
                    medal = "3rd"
                else:
                    medal = f"{(i+1)}th"
                next_placement = medal
                

            # if score != first_place_points and score != previous_score:
            #     next_placement += 1  # Increment the placement for ties in the score
            details += f"{medal} **{title}**\n *{author}* \n" \
                       f"**Total Points**: *{upvotes-downvotes}*\n" \
                       f"**Page Count**: {pageCount}\n" \
                       f"**Suggested By**: {user_name}\n\n"

            previous_score = score

            # If it's the first place suggestion, add the cover as an inline image
            if medal == "🥇" and cover and not pin_thumbnail:
                embed.set_thumbnail(url=cover)
                pin_thumbnail = True  # Set to True after the first-place suggestion's image is added

        # Set the details in the embed's description
        embed.description = details

        return embed
    else:
        return None


@bot.event
async def on_reaction_add(reaction, user):
    print("Adding reaction...")
    print(reaction)
    
    channel_id = reaction.message.channel.id  # Correct way to obtain the channel_id

    # Check if the reaction is not from the bot (to avoid triggering on bot's own reactions)
    if user.bot:
        return
    
    if channel_id == VOTE_CHANNEL_ID:
        await populate_results()

    if isinstance(reaction.message.channel, discord.DMChannel):
        print("IS DM...")
        message = reaction.message

        if reaction.emoji == "❌" and not user.bot:
            # Retrieve the suggestion identifier from the dictionary
            suggestion_id = suggestion_message_ids.get(message.id)

            if suggestion_id:
                # Delete the suggestion from the user's DM
                await message.delete()

                # Delete the corresponding suggestion message in the voting channel
                voting_channel = bot.get_channel(VOTE_CHANNEL_ID)
                async for message in voting_channel.history():
                    if message.author == bot.user and message.embeds[0].title == suggestion_id:
                        await message.delete()

                # Delete the suggestion from the database
                cursor = conn.cursor()
                cursor.execute("DELETE FROM suggested_books WHERE title = ?", (suggestion_id,))
                conn.commit()

                # Delete messages in RESULT_CHANNEL_ID
                result_channel = bot.get_channel(RESULT_CHANNEL_ID)
                async for message in result_channel.history():
                    await message.delete()

                leaderboard_embed = await create_leaderboard_embed()
                if leaderboard_embed:
                    await bot.get_channel(RESULT_CHANNEL_ID).send(embed=leaderboard_embed)
        if reaction.emoji == "🚫" and not user.bot:
            await reset_chat(reaction)
        if reaction.emoji == "✅" and not user.bot:
            await approve_suggestion(reaction,user)


@bot.event
async def on_raw_reaction_add(reaction):
    global BOT_REMOVING_REACTION
    user_id = reaction.user_id
    user = await bot.fetch_user(user_id)
    channel_id = reaction.channel_id

    # Exit early if the bot is the one adding the reaction
    if user.bot:
        return

    if channel_id == VOTE_CHANNEL_ID:
        message_id = reaction.message_id
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        suggestion_title = message.embeds[0].title 
        cursor = conn.cursor()

        # If the upvote emoji was added by the user
        if str(reaction.emoji) == "👍":  
            # Increment the upvote in the database
            cursor.execute("UPDATE suggested_books SET upvotes = upvotes + 1 WHERE title = ?", (suggestion_title,))
            conn.commit()

            # If the user has previously downvoted, decrement the downvote in the database
            for r in message.reactions:
                if str(r.emoji) == "👎":
                    users = [u async for u in r.users()]  # Collect users into a list using async list comprehension
                    if user in users:  # Check if the current user is in that list
                        # Decrement the downvote in the database
                        cursor.execute("UPDATE suggested_books SET downvotes = downvotes - 1 WHERE title = ?", (suggestion_title,))
                        conn.commit()
                        BOT_REMOVING_REACTION = True
                        await message.remove_reaction("👎", user)  # Remove the downvote reaction from the user
                        BOT_REMOVING_REACTION = False
                        break

        # If the downvote emoji was added by the user
        elif str(reaction.emoji) == "👎":  
            # Increment the downvote in the database
            cursor.execute("UPDATE suggested_books SET downvotes = downvotes + 1 WHERE title = ?", (suggestion_title,))
            conn.commit()

            # If the user has previously upvoted, decrement the upvote in the database
            for r in message.reactions:
                if str(r.emoji) == "👍":
                    users = [u async for u in r.users()]  # Collect users into a list using async list comprehension
                    if user in users:  # Check if the current user is in that list
                        # Decrement the downvote in the database
                        cursor.execute("UPDATE suggested_books SET upvotes = upvotes - 1 WHERE title = ?", (suggestion_title,))
                        conn.commit()
                        BOT_REMOVING_REACTION = True
                        await message.remove_reaction("👍", user)  # Remove the downvote reaction from the user
                        BOT_REMOVING_REACTION = False
                        break

        await populate_results()


@bot.event
async def on_raw_reaction_remove(reaction):
    global BOT_REMOVING_REACTION
    if BOT_REMOVING_REACTION:
        return
    channel_id = reaction.channel_id
    user_id = reaction.user_id  # Get the user's ID who added the reaction

    # Fetch the message using the channel and message IDs
    user = await bot.fetch_user(user_id) 
    channel = bot.get_channel(channel_id)

    # Check if the reaction is not from the bot (to avoid triggering on bot's own reactions)
    if user.bot:
        return
    # Check if the reaction is removed from a message in your voting channel
    if channel_id == VOTE_CHANNEL_ID:
        message_id = reaction.message_id
        message = await channel.fetch_message(message_id)
        # Check the emoji used for upvoting and downvoting (use your custom emoji if available)
        if str(reaction.emoji) == "👍":  # Replace with your upvote emoji
            suggestion_title = message.embeds[0].title  # Adjust this based on your embed structure

            # Then, update the database by decrementing the downvote count for this suggestion
            cursor = conn.cursor()
            cursor.execute("UPDATE suggested_books SET upvotes = upvotes - 1 WHERE title = ?", (suggestion_title,))
            conn.commit()
        elif str(reaction.emoji) == "👎":  # Replace with your downvote emoji
            suggestion_title = message.embeds[0].title  # Adjust this based on your embed structure

            # Then, update the database by decrementing the downvote count for this suggestion
            cursor = conn.cursor()
            cursor.execute("UPDATE suggested_books SET downvotes = downvotes - 1 WHERE title = ?", (suggestion_title,))
            conn.commit()

        # Delete messages in RESULT_CHANNEL_ID
        result_channel = bot.get_channel(RESULT_CHANNEL_ID)
        async for message in result_channel.history():
            await message.delete()

        await populate_results()

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        # Check if it's a button interaction
        if interaction.data["component_type"] == discord.ComponentType.button.value:
            # Handle based on custom_id
            if interaction.data["custom_id"].startswith("join_"):
                await handle_join_group(interaction)


async def reset_chat(reaction):
    # async for message in reaction.message.channel.history():
    #     await message.delete()
    await reaction.message.delete()


@commands.check(is_owner)
@bot.command(name="remove-all", brief="Remove all suggestions", hidden= True)
async def removeAll(ctx):
    try:
        # Delete all suggestions from the database
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suggested_books")
        conn.commit()

        # Delete the bot's messages in the voting channel
        voting_channel = bot.get_channel(VOTE_CHANNEL_ID)
        if voting_channel:
            async for message in voting_channel.history():
                if message.author == bot.user:
                    if message.reference:
                        # If the message is part of a thread, delete the thread
                        thread = await voting_channel.fetch_message(message.reference.message_id)
                        await thread.delete()
                    await message.delete()

        # Delete messages in RESULT_CHANNEL_ID
        result_channel = bot.get_channel(RESULT_CHANNEL_ID)
        async for message in result_channel.history():
            await message.delete()

        await ctx.send("All suggestions and bot messages have been cleared.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
# async def populate_results():
#     # Delete messages in RESULT_CHANNEL_ID
#     result_channel = bot.get_channel(RESULT_CHANNEL_ID)
#     async for message in result_channel.history():
#         await message.delete()

#     leaderboard_embed = await create_leaderboard_embed()
#     if leaderboard_embed:
#         await bot.get_channel(RESULT_CHANNEL_ID).send(embed=leaderboard_embed)

# async def populate_results():
#     # Get messages in RESULT_CHANNEL_ID
#     result_channel = bot.get_channel(RESULT_CHANNEL_ID)
#     last_message = None

#     messages = [msg async for msg in result_channel.history(limit=1)]


#     # If there are messages in the history
#     if messages:
#         last_message = messages[0]

#     leaderboard_embed = await create_leaderboard_embed()

#     # Check if there's a message to edit
#     if last_message:
#         logger.info("Found last message")
#         # Edit the existing message with the new embed
#         await last_message.edit(embed=leaderboard_embed)
#     else:
#         logger.info("No result found")
#         # If there's no previous message, send a new one
#         await result_channel.send(embed=leaderboard_embed)

async def populate_results():
    logger.info("IN POPULATE RESULTS")
    # Get messages in RESULT_CHANNEL_ID
    result_channel = bot.get_channel(RESULT_CHANNEL_ID)

    # Fetch the last message from the channel's history
    messages = [msg async for msg in result_channel.history(limit=1)]

    leaderboard_embed = await create_leaderboard_embed()

    # If there are messages in the history and there's an embed to update with
    if messages and leaderboard_embed:
        last_message = messages[0]
        try:
            # Attempt to edit the embed of the last message
            await last_message.edit(embed=leaderboard_embed)
            logger.info("Successfully updated embed of the last message.")
        except discord.NotFound:
            logger.warning("Message not found or could not edit the message.")
    else:
        logger.warning("No result found or no embed to update with.")
        try:
            # Attempt to edit the embed of the last message
            await result_channel.send(embed=leaderboard_embed)
            logger.info("Successfully sent new embed.")
        except discord.NotFound:
            logger.warning("Message not found or could not edit the message.")






async def approve_suggestion(reaction,user):

    user_id = user.id

    def is_book_duplicate(title):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM suggested_books WHERE title=?", (title,))
        count = cursor.fetchone()[0]
        return count > 0

    def add_suggested_book(title, user_id,author,keywords,desc,pageCount):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO suggested_books (title, user_id, author, cover,keywords,desc,pageCount) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, user_id, author, image_url, keywords, desc, pageCount))
        conn.commit()


    for field in reaction.message.embeds[0].fields:
        if field.name == "keywords":
            keywords = field.value

    # Make a request to the Google Books API
    url = f'https://www.googleapis.com/books/v1/volumes?q={keywords}&key={GOOGLE_BOOKS_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        # Filter the results to select the most relevant entry
        selected_entry = None
        for entry in data['items']:
            if entry['volumeInfo'].get('title', '').lower() == keywords.lower():
                selected_entry = entry
                break  # Found an exact title match, break the loop

        # If no exact title match was found, use the first entry as a fallback
        if selected_entry is None:
            selected_entry = data['items'][0]

        book = selected_entry['volumeInfo']

        title = book.get('title', 'Title not found')
        author = book.get('authors', ['Author not found'])[0]
        description = book.get('description', 'Description not found')
        image_url = book.get('imageLinks', {}).get('thumbnail', '')
        pageCount = book.get('pageCount', 0)

        # Check if the book has already been suggested
        if is_book_duplicate(title):
            await user.send("This book has already been suggested.")
        else:
            genre_emoji = "📖"
            embed = discord.Embed(title=title, description=description)
            embed.set_author(name=author)
            embed.set_thumbnail(url=image_url)

            # Include additional book details in the embed
            embed.add_field(name="Page Count: ", value= pageCount, inline=False)
            embed.add_field(name="Submitted By", value= user.name, inline=False)

            # Post the suggestion in your specified channel (BROADCAST_CHANNEL_ID)
            message = await bot.get_channel(VOTE_CHANNEL_ID).send(embed=embed)            
            await message.create_thread(name=title, auto_archive_duration=False)

            #trigger leaderboard

            # Add upvote and downvote reactions
            await message.add_reaction("👍")
            await message.add_reaction("👎")

            # Add the book to the database to prevent duplicates and store the user ID
            add_suggested_book(title, user_id, author,keywords, description, pageCount)

    await populate_results()
    # async for message in reaction.message.channel.history():
    #     await reset_chat(reaction)

    await reaction.message.delete()

def fetch_book_info(book_title, api_key):
    # Define the Google Books API URL
    api_url = f'https://www.googleapis.com/books/v1/volumes?q={book_title}&key={api_key}'

    # Make a request to the Google Books API
    response = requests.get(api_url)
    data = response.json()

    # Check if the API response contains book information
    if 'items' in data:
        book = data['items'][0]['volumeInfo']

        book_info = {
            'title': book.get('title', 'Unknown Title'),
            'author': book.get('authors', ['Unknown Author']),
            'pageCount': book.get('pageCount', 'Unknown Page Count'),
            'publishedDate': book.get('publishedDate', 'Unknown Published Date'),
            'description': book.get('description', 'No Description Available'),
            'categories': book.get('categories', ['Uncategorized']),
            'imageLink': book.get('imageLinks', {}).get('thumbnail', 'No Image Available')
        }

        return book_info
    else:
        # Return default values if book information is not found
        return {
            'title': 'Unknown Title',
            'author': ['Unknown Author'],
            'pageCount': 'Unknown Page Count',
            'publishedDate': 'Unknown Published Date',
            'description': 'No Description Available',
            'categories': ['Uncategorized'],
            'imageLink': 'No Image Available'
        }

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CheckFailure):
        with open("resources/permission-denied-responses.json", "r") as file:
            witty_responses = json.load(file)

        await ctx.send(random.choice(witty_responses), ephemeral=True)
    else:
        print(error)




# Run the bot with your token
bot.run(settings.DISCORD_API_SECRET, root_logger=True)
