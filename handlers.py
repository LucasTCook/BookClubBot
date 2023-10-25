import sqlite3
import discord
import settings


async def handle_join_group(interaction):
    group_id = interaction.data["custom_id"].split("_")[-1] 

    with sqlite3.connect(settings.SQL_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT users_in_group, group_name, home_channel_id, group_creator FROM reading_group WHERE group_id = ?", (group_id,))
        row = cursor.fetchone()

        users = []
        group_name = ""
        home_channel_id = None
        group_creator = None

        if row:
            if row[0]:
                users = row[0].split(',')
            group_name = row[1]
            home_channel_id = row[2]
            group_creator = row[3]
        else:
            await interaction.response.send_message("Error: Group not found.")
            return


        # Add the user to the group
        if str(interaction.user.id) not in users:
            users.append(str(interaction.user.id))
            cursor.execute("UPDATE reading_group SET users_in_group = ? WHERE group_id = ?", (','.join(users), group_id,))
            conn.commit()

            # Add the user to the role
            guild = interaction.guild
            print(group_name)
            role = discord.utils.get(guild.roles, name=group_name)
            if role:
                member = guild.get_member(interaction.user.id)
                await member.add_roles(role)
            await interaction.response.send_message(f"You've joined the {group_name} reading group!", ephemeral=True)
        else:
            await interaction.response.send_message("You're already in this reading group!", ephemeral=True)