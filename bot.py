import os
from dotenv import load_dotenv
import discord
import discord.ext.commands
from discord.utils import get
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bot')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = discord.ext.commands.Bot(command_prefix='+', intents=discord.Intents.all())

@client.event
async def on_ready():
    logger.info("Logged in as %s (%s)", client.user.name, client.user.id)

client.run(BOT_TOKEN)
