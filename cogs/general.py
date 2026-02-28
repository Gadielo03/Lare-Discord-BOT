import discord
from discord.ext import commands
from utils.ui_colors import ColorPalette

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

    @commands.hybrid_command(name="helpme", description="Provides a list of available commands")
    async def helpme(self, ctx):
        """Provides a list of available commands - automatically generated"""
        embed = discord.Embed(
            title="📚 Help Menu",
            description="Here are all available commands organized by category:",
            color=ColorPalette.INFO
        )
        
        for cog_name, cog in sorted(self.bot.cogs.items()):
            cog_commands = cog.get_commands()
            
            if cog_commands:
                commands_list = []
                for command in sorted(cog_commands, key=lambda x: x.name):
                    description = command.description or command.help or "No description"
                    commands_list.append(f"`/{command.name}` - {description}")
                
                if commands_list:
                    cog_desc = cog.__doc__ or cog_name
                    embed.add_field(
                        name=f"__{cog_desc}__",
                        value="\n".join(commands_list),
                        inline=False
                    )
        
        embed.set_footer(text=f"Total commands: {len(list(self.bot.commands))} | Use /command for details")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user.avatar else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
