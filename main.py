import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} Connected in Servers:\n')
    for server in bot.guilds:
        print(f'{server.name} (id: {server.id})')
    
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'❌ Error syncing commands: {e}')
    
    print('\n✅ Bot Hot N Ready!')

@bot.event
async def on_message(message):
    """Message Logger"""
    if message.author != bot.user:
        print(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message)

async def load_cogs():
    """Cog Loader"""
    cogs_list = ['cogs.music', 'cogs.general']
    for cog in cogs_list:
        try:
            await bot.load_extension(cog)
            print(f'Loaded: {cog}')
        except Exception as e:
            print(f'Error loading {cog}: {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())