import discord
from discord.ext import commands
import asyncio
import os
import signal
import sys
from dotenv import load_dotenv
from utils.logger import log
from services.http_service import HttpService

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
    cogs_list = ['cogs.music', 'cogs.general', 'cogs.love', 'cogs.pokemon', 'cogs.admin']
    for cog in cogs_list:
        try:
            await bot.load_extension(cog)
            log.success(f'Cog loaded: {cog}')
        except Exception as e:
            log.failed(f'Error loading {cog}: {e}')

async def cleanup():
    """Cleanup resources before shutdown"""
    log.info("🛑 Shutting down gracefully...")
    
    try:
        http_service = HttpService()
        await http_service.close()
        log.success("✅ HTTP sessions closed")
    except Exception as e:
        log.warning(f"Error closing HTTP service: {e}")
    
    try:
        await bot.close()
        log.success("✅ Bot disconnected")
    except Exception as e:
        log.warning(f"Error closing bot: {e}")
    
    log.success("👋 Goodbye!")

async def main():
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        log.info("⚠️  Keyboard interrupt received")
    except Exception as e:
        log.error(f"Unexpected error: {e}")
    finally:
        await cleanup()

def handle_sigterm(signum, frame):
    """Handle SIGTERM signal"""
    log.info("⚠️  SIGTERM received")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("👋 Bot stopped by user")
    except Exception as e:
        log.error(f"Fatal error: {e}")