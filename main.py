import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from utils.logger import log

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    log.info(f'{bot.user} connected to the following servers:')
    for server in bot.guilds:
        log.info(f'  • {server.name} (ID: {server.id})')
    
    try:
        synced = await bot.tree.sync()
        log.success(f'Synced {len(synced)} slash command(s)')
    except Exception as e:
        log.failed(f'Error syncing commands: {e}')
    
    log.success('Bot is Hot N Ready!')

@bot.event
async def on_message(message):
    """Message Logger"""
    if message.author != bot.user:
        log.debug(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message)

async def load_cogs():
    """Cog Loader"""
    cogs_list = ['cogs.music', 'cogs.general']
    for cog in cogs_list:
        try:
            await bot.load_extension(cog)
            log.success(f'Cog loaded: {cog}')
        except Exception as e:
            log.failed(f'Error loading {cog}: {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())