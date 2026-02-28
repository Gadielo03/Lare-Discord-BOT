import discord
from discord.ext import commands
from ui_colors import ColorPalette

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
        embed = discord.Embed(
            title="👋 Hello!",
            description=f"Hi {ctx.author.mention}! I'm here to help you.",
            color=ColorPalette.PRIMARY
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
