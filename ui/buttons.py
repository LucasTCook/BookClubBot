import discord
from discord.ext import commands
from discord.ui import view, Button

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Click Me",style=discord.ButtonStyle.blurple)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.edit_message(content=f"This is an edited button response!")

    # @discord.ui.button(label="Gray Button",style=discord.ButtonStyle.gray) # or .secondary/.grey
    # async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.edit_message(view=self)

    # @discord.ui.button(label="Green Button",style=discord.ButtonStyle.green) # or .success
    # async def green_button(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.edit_message(view=self)

    # @discord.ui.button(label="Red Button",style=discord.ButtonStyle.red) # or .danger
    # async def red_button(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.edit_message(view=self)

    # @discord.ui.button(label="Change All",style=discord.ButtonStyle.success)
    # async def color_changing_button(self,child:discord.ui.Button,interaction:discord.Interaction):
    #     for child in self.children:
    #         child.disabled=True
    #     await interaction.response.edit_message(view=self)