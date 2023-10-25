import sqlite3
import discord
from discord.ui import View, Button
from discord.ui.button import ButtonStyle
from discord import Interaction
import settings

class JoinGroupButton(View):
    def __init__(self, group_name, id):
        super().__init__()
        self.group_name = group_name
        self.id = id
        self.add_item(Button(label="Join Group", style=ButtonStyle.success, custom_id=f"join_{self.id}"))

    # @discord.ui.button(label="Join Group", style=ButtonStyle.success, custom_id="join_group_placeholder")  # This placeholder will be replaced dynamically
    # async def join_button(self, interaction: Interaction, button: Button):
    #     # Fetch the group details from the database
    #     with sqlite3.connect(settings.SQL_DB) as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT users_in_group FROM reading_group WHERE group_id = ?", (self.id,))
    #         row = cursor.fetchone()

    #         # Check if we got a result
    #         if row:
    #             # Check if users_in_group is not None
    #             if row[0]:
    #                 users = row[0].split(',')
    #             else:
    #                 users = []
    #         else:
    #             await interaction.response.send_message("Error: Group not found.")
    #             return


    #         # Add the user to the group
    #         if str(interaction.user.id) not in users:
    #             users.append(str(interaction.user.id))
    #             cursor.execute("UPDATE reading_group SET users_in_group = ? WHERE group_id = ?", (','.join(users), self.id,))
    #             conn.commit()

    #             # Add the user to the role
    #             guild = interaction.guild
    #             print(self.group_name)
    #             role = discord.utils.get(guild.roles, name=self.group_name)
    #             if role:
    #                 member = guild.get_member(interaction.user.id)
    #                 await member.add_roles(role)
    #             await interaction.response.send_message(f"You've joined the {self.group_name} reading group!", ephemeral=True)
    #         else:
    #             await interaction.response.send_message("You're already in this reading group!")
