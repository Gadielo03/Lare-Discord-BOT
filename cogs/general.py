import discord
from discord.ext import commands
from utils.ui_colors import ColorPalette
from services.embed_builder import EmbedBuilder

class General(commands.Cog):
    """General commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.embed_builder = EmbedBuilder()
    
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

    @commands.hybrid_command(name="helpme", description="Provides a list of available commands")
    async def helpme(self, ctx):
        """Provides a list of available commands - automatically generated"""
        bot_avatar_url = self.bot.user.display_avatar.url if self.bot.user.avatar else None
        
        embed = self.embed_builder.help_menu(
            bot_cogs=self.bot.cogs,
            total_commands=len(list(self.bot.commands)),
            bot_avatar_url=bot_avatar_url
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
