import discord
from discord.ext import commands
from services.embed_builder import EmbedBuilder
from services.gif_service import GifService
from utils.logger import log

class Love(commands.Cog):
    """Love commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.gif_service = GifService()
    
    @commands.hybrid_command(name="hug", description="Express love to someone or something")
    async def hug(self, ctx, member: discord.Member = None):
        """Express love to someone or something"""
        try:
            if member is None:
                member = ctx.author
            
            log.debug(f"Hug command: {ctx.author} -> {member}")
            
            gif_url = await self.gif_service.get_random_gif("hug")
            log.debug(f"Got GIF URL: {gif_url}")
            
            embed = EmbedBuilder.hug(ctx.author, member, gif_url)
            log.debug("Embed created, sending...")
            
            await ctx.send(embed=embed)
            log.success(f"Hug sent from {ctx.author} to {member}")
        except Exception as e:
            log.error(f"Error in hug command: {e}")
            await ctx.send("Sorry, something went wrong while trying to send the hug! 😢")    


    @commands.hybrid_command(name="kiss", description="Send a kiss to someone or something")
    async def kiss(self, ctx, member: discord.Member = None):
        """Send a kiss to someone or something"""
        try:
            if member is None:
                member = ctx.author
            
            log.debug(f"Kiss command: {ctx.author} -> {member}")
            
            gif_url = await self.gif_service.get_random_gif("kiss")
            log.debug(f"Got GIF URL: {gif_url}")
            
            embed = EmbedBuilder.kiss(ctx.author, member, gif_url)
            log.debug("Embed created, sending...")
            
            await ctx.send(embed=embed)
            log.success(f"Kiss sent from {ctx.author} to {member}")
        except Exception as e:
            log.error(f"Error in kiss command: {e}")
            await ctx.send("Sorry, something went wrong while trying to send the kiss! 😢")        

async def setup(bot):
    await bot.add_cog(Love(bot))
