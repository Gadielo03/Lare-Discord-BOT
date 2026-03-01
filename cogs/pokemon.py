import discord
from discord.ext import commands
import asyncio
from services.pokemon_service import PokemonService
from services.embed_builder import EmbedBuilder
from utils.logger import log


class Pokemon(commands.Cog):
    """Pokemon TCG commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.pokemon_service = PokemonService()
        self.embed_builder = EmbedBuilder()
    
    @commands.hybrid_command(name="openpack", description="Open a Pokemon TCG booster pack!")
    async def openpack(self, ctx, pack_size: int = 10):
        """Open a Pokemon card pack with random cards"""
        try:
            log.server_log(ctx.guild.id, ctx.guild.name, f"{ctx.author} is opening a Pokemon pack (size: {pack_size})", "INFO")
            
            if pack_size < 1 or pack_size > 15:
                await ctx.send("❌ Pack size must be between 1 and 15 cards!")
                return
            
            opening_embed = self.embed_builder.pokemon_pack_opening(ctx.author.display_name)
            await ctx.send(embed=opening_embed)
            await asyncio.sleep(2)
            cards, set_info = await self.pokemon_service.open_pack(pack_size)
            
            if not cards:
                await ctx.send("❌ Failed to open pack. Try again!")
                return
            
            log.success(f"Pack opened with {len(cards)} cards for {ctx.author}")
            
            set_embed = self.embed_builder.pokemon_set_info(set_info)
            await ctx.send(embed=set_embed)
            await ctx.send("🎴 **Revealing your cards...**")
            
            for i, card in enumerate(cards, 1):
                await asyncio.sleep(1.5)
                card_embed = self.embed_builder.pokemon_card(card, self.pokemon_service)
                card_embed.set_author(name=f"Card {i}/{len(cards)}")
                if set_info.get('symbol'):
                    card_embed.set_footer(text=set_info.get('name', 'Unknown Set'), icon_url=set_info.get('symbol'))
                
                await ctx.send(embed=card_embed)
            
            await asyncio.sleep(1)
            summary_embed = self.embed_builder.pokemon_pack_summary(
                cards, 
                ctx.author.display_name, 
                self.pokemon_service
            )
            if set_info.get('logo'):
                summary_embed.set_thumbnail(url=set_info['logo'])
            await ctx.send(embed=summary_embed)
            
        except Exception as e:
            log.error(f"Error in openpack command: {e}")
            await ctx.send(f"❌ Error opening pack: {e}")
    
    @commands.hybrid_command(name="quickpack", description="Open a pack and see summary only (faster)")
    async def quickpack(self, ctx, pack_size: int = 10):
        """Open a pack but only show the summary (faster)"""
        try:
            log.info(f"{ctx.author} is opening a quick pack")
            
            if pack_size < 1 or pack_size > 15:
                await ctx.send("❌ Pack size must be between 1 and 15 cards!")
                return
            
            opening_embed = self.embed_builder.pokemon_pack_opening(ctx.author.display_name)
            msg = await ctx.send(embed=opening_embed)
            
            cards, set_info = await self.pokemon_service.open_pack(pack_size)
            
            if not cards:
                await ctx.send("❌ Failed to open pack. Try again!")
                return
            
            log.success(f"Quick pack opened with {len(cards)} cards for {ctx.author}")
            
            await asyncio.sleep(2)
            summary_embed = self.embed_builder.pokemon_pack_summary(
                cards, 
                ctx.author.display_name, 
                self.pokemon_service
            )
            if set_info.get('logo'):
                summary_embed.set_thumbnail(url=set_info['logo'])
            summary_embed.description = f"**Set:** {set_info.get('name', 'Unknown')}\n" + (summary_embed.description or '')
            await msg.edit(embed=summary_embed)
            
            rarest_card = max(cards, key=lambda c: self.pokemon_service._get_rarity_value(c.get("rarity", "Common")))
            
            await asyncio.sleep(1)
            await ctx.send("✨ **Your best card:**")
            card_embed = self.embed_builder.pokemon_card(rarest_card, self.pokemon_service)
            await ctx.send(embed=card_embed)
            
        except Exception as e:
            log.error(f"Error in quickpack command: {e}")
            await ctx.send(f"❌ Error opening pack: {e}")
    
    @commands.hybrid_command(name="searchcard", description="Search for a specific Pokemon card")
    async def searchcard(self, ctx, *, card_name: str):
        """Search for a Pokemon card by name"""
        try:
            log.info(f"{ctx.author} is searching for card: {card_name}")
            await ctx.send(f"🔍 Searching for **{card_name}**...")
            card = await self.pokemon_service.search_card(card_name)
            
            if not card:
                await ctx.send(f"❌ Could not find card: **{card_name}**")
                return
            
            card_embed = self.embed_builder.pokemon_card(card, self.pokemon_service)
            await ctx.send(embed=card_embed)
            log.success(f"Found card {card['name']} for {ctx.author}")
            
        except Exception as e:
            log.error(f"Error in searchcard command: {e}")
            await ctx.send(f"❌ Error searching card: {e}")


async def setup(bot):
    await bot.add_cog(Pokemon(bot))
