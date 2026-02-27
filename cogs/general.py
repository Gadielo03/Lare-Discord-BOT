import discord
from discord.ext import commands

class General(commands.Cog):
    """General commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener for messages to respond to 'ping'"""
        if message.author == self.bot.user:
            return
        if message.content.startswith('ping'):
            await message.channel.send('pong')
    
    @commands.hybrid_command(name="hello", description="Simple command to greet the user")
    async def hello(self, ctx):
        """Simple command to greet the user"""
        await ctx.send('Hello!')

async def setup(bot):
    await bot.add_cog(General(bot))
