import os
from dotenv import load_dotenv
import discord.ext.commands
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.getLogger('bot')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = discord.ext.commands.Bot(command_prefix='+', intents=discord.Intents.all())

bot.load_extension('cogs.reactions')
bot.load_extension('cogs.embed_sender')
bot.load_extension('cogs.channel_builder')


@bot.event
async def on_ready():
    logging.info(f'------------\nLogged in as: "{bot.user.name}" ({bot.user.id})\n------------')
    # guild = bot.guilds.pop()
    # channel = guild.get_channel(1089895232285462648)

    # And the main code looks like this
    # with open("embed1.json", "r") as file:
    #     temp_ban_embeds = parse_embed_json(file.read())
    #
    # for embed in temp_ban_embeds:
    #     await channel.send(embed=embed, view=MyView())
    #     return


# class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui
#     # Create a button with the label "😎 Click me!" with color Blurple# .View
#     @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎")
#     async def button_callback(self, button, interaction: discord.Interaction):
#         await interaction.response.send_message("You clicked the button!", ephemeral=True) # Send a message when the button is clicked
#
#
# def parse_embed_json(json_file):
#     embeds_json = loads(json_file)['embeds']
#
#     for embed_json in embeds_json:
#         embed = discord.Embed().from_dict(embed_json)
#         yield embed

@bot.command()
async def hello(ctx):
    await ctx.response()

bot.run(BOT_TOKEN)
