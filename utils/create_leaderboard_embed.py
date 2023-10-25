import sqlite3
import settings
import discord
from utils import logger

conn = sqlite3.connect(settings.SQL_DB)
cursor = conn.cursor()
conn.commit()

async def create_leaderboard_embed(ctx):
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
            user = ctx.bot.get_user(user_id)
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