"""Embed Builder Service - Creates styled embeds for music bot"""
import discord
from utils.ui_colors import ColorPalette


class EmbedBuilder:
    """Service for creating consistent and styled Discord embeds"""
    
    @staticmethod
    def now_playing(song_info, requester):
        """Create embed for now playing"""
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{song_info['title']}**",
            color=ColorPalette.NOW_PLAYING
        )
        
        if song_info.get('thumbnail'):
            embed.set_thumbnail(url=song_info['thumbnail'])
        
        if song_info.get('duration'):
            minutes, seconds = divmod(song_info['duration'], 60)
            embed.add_field(
                name="Duration", 
                value=f"{int(minutes)}:{int(seconds):02d}", 
                inline=True
            )
        
        if song_info.get('uploader'):
            embed.add_field(name="Channel", value=song_info['uploader'], inline=True)
        
        embed.set_footer(text=f"Requested by {requester}")
        return embed
    
    @staticmethod
    def added_to_queue(song_info, position, requester):
        """Create embed for song added to queue"""
        embed = discord.Embed(
            title="➕ Added to Queue",
            description=f"**{song_info['title']}**",
            color=ColorPalette.ADDED
        )
        
        if song_info.get('thumbnail'):
            embed.set_thumbnail(url=song_info['thumbnail'])
        
        if song_info.get('duration'):
            minutes, seconds = divmod(song_info['duration'], 60)
            embed.add_field(
                name="Duration", 
                value=f"{int(minutes)}:{int(seconds):02d}", 
                inline=True
            )
        
        embed.add_field(name="Position", value=f"#{position}", inline=True)
        embed.set_footer(text=f"Requested by {requester}")
        return embed
    
    @staticmethod
    def playlist_added(song_count, requester):
        """Create embed for playlist added"""
        embed = discord.Embed(
            title="📑 Playlist Added",
            description=f"Added **{song_count}** songs to the queue!",
            color=ColorPalette.ADDED
        )
        embed.set_footer(text=f"Requested by {requester}")
        return embed
    
    @staticmethod
    def queue_empty(gif_url=None):
        """Create embed for empty queue"""
        embed = discord.Embed(
            title="📭 Queue Empty",
            description="No more songs in the queue.\nAdd more songs with `/play`!",
            color=ColorPalette.EMPTY
        )
        if gif_url:
            embed.set_image(url=gif_url)
        return embed
    
    @staticmethod
    def queue_display(queue_list, total_songs):
        """Create embed for queue display"""
        embed = discord.Embed(
            title="🎵 Current Music Queue",
            description=queue_list,
            color=ColorPalette.QUEUE
        )
        embed.set_footer(text=f"Total songs: {total_songs}")
        return embed
    
    @staticmethod
    def song_skipped():
        """Create embed for song skipped"""
        embed = discord.Embed(
            title="⏭️ Song Skipped",
            description="Moving to the next song...",
            color=ColorPalette.INFO
        )
        return embed
    
    @staticmethod
    def music_paused():
        """Create embed for music paused"""
        embed = discord.Embed(
            title="⏸️ Music Paused",
            description="Use `/resume` to continue playing",
            color=ColorPalette.WARNING
        )
        return embed
    
    @staticmethod
    def music_resumed():
        """Create embed for music resumed"""
        embed = discord.Embed(
            title="▶️ Music Resumed",
            description="Playback has been resumed",
            color=ColorPalette.SUCCESS
        )
        return embed
    
    @staticmethod
    def music_stopped():
        """Create embed for music stopped"""
        embed = discord.Embed(
            title="⏹️ Music Stopped",
            description="Disconnected from voice channel and cleared the queue",
            color=ColorPalette.ERROR
        )
        return embed
    
    @staticmethod
    def queue_shuffled(song_count):
        """Create embed for queue shuffled"""
        embed = discord.Embed(
            title="🔀 Queue Shuffled",
            description=f"Randomized {song_count} songs in the queue",
            color=ColorPalette.SECONDARY
        )
        return embed
    
    @staticmethod
    def error(message):
        """Create embed for error messages"""
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=ColorPalette.ERROR
        )
        return embed
    
    @staticmethod
    def success(title, message):
        """Create embed for success messages"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=message,
            color=ColorPalette.SUCCESS
        )
        return embed
    
    @staticmethod
    def playlist_generated(genre, song_count, requester):
        """Create embed for generated playlist"""
        embed = discord.Embed(
            title="🎲 Playlist Generated",
            description=f"Added **{song_count}** {genre} songs to the queue!",
            color=ColorPalette.SECONDARY
        )
        embed.add_field(name="Genre/Topic", value=genre, inline=True)
        embed.add_field(name="Songs Added", value=song_count, inline=True)
        embed.set_footer(text=f"Generated by {requester}")
        return embed
    
    @staticmethod
    def hug(author, member, gif_url):
        """Create embed for hug command with GIF"""
        embed = discord.Embed(
            title="🤗 Warm Hug!",
            description=f"{author.mention} gives a warm hug to {member.mention}!",
            color=ColorPalette.LOVE
        )
        if gif_url:
            embed.set_image(url=gif_url)
        return embed
    
    @staticmethod
    def pokemon_pack_opening(username):
        """Create embed for pack opening start"""
        embed = discord.Embed(
            title="🎴 Opening Pokemon Card Pack!",
            description=f"**{username}** is opening a booster pack...\n✨ Good luck!",
            color=ColorPalette.PRIMARY
        )
        return embed
    
    @staticmethod
    def pokemon_card(card, pokemon_service):
        """Create embed for individual Pokemon card"""
        rarity_emoji = pokemon_service.get_rarity_emoji(card.get("rarity", "Common"))
        
        embed = discord.Embed(
            title=f"{rarity_emoji} {card.get('name', 'Unknown Card')}",
            color=ColorPalette.ACCENT
        )
        
        if card.get("hp"):
            embed.add_field(name="HP", value=card["hp"], inline=True)
        
        if card.get("types"):
            types_str = " ".join([pokemon_service.get_type_emoji(t) + t for t in card["types"]])
            embed.add_field(name="Type", value=types_str, inline=True)
        
        embed.add_field(name="Rarity", value=f"{rarity_emoji} {card.get('rarity', 'Unknown')}", inline=True)
        
        if card.get("set"):
            embed.add_field(name="Set", value=card["set"], inline=True)
        
        if card.get("number"):
            embed.add_field(name="Number", value=f"#{card['number']}", inline=True)
        
        if card.get("artist"):
            embed.set_footer(text=f"Illustrated by {card['artist']}")
        
        if card.get("image_large"):
            embed.set_image(url=card["image_large"])
        elif card.get("image"):
            embed.set_image(url=card["image"])
        
        return embed
    
    @staticmethod
    def pokemon_pack_summary(cards, username, pokemon_service):
        """Create embed summarizing all cards in pack"""
        embed = discord.Embed(
            title=f"🎴 {username}'s Pack Summary",
            description="Here's what you got!",
            color=ColorPalette.SUCCESS
        )
        
        rarity_groups = {}
        for card in cards:
            rarity = card.get("rarity", "Common")
            if rarity not in rarity_groups:
                rarity_groups[rarity] = []
            rarity_groups[rarity].append(card["name"])
        
        for rarity, card_names in sorted(rarity_groups.items(), 
                                         key=lambda x: pokemon_service._get_rarity_value(x[0])):
            emoji = pokemon_service.get_rarity_emoji(rarity)
            cards_list = "\n".join([f"• {name}" for name in card_names])
            embed.add_field(name=f"{emoji} {rarity}", value=cards_list, inline=False)
        
        embed.set_footer(text=f"Total cards: {len(cards)}")
        return embed
    
    @staticmethod
    def pokemon_set_info(set_info):
        """Create embed for Pokemon set information"""
        embed = discord.Embed(
            title=f"🎴 {set_info.get('name', 'Unknown Set')}",
            description=f"**Set ID:** {set_info.get('id')}\n**Release Date:** {set_info.get('release_date')}\n**Total Cards:** {set_info.get('card_count', {}).get('official', '?')}",
            color=ColorPalette.PRIMARY
        )
        if set_info.get('logo'):
            embed.set_thumbnail(url=set_info['logo'])
        if set_info.get('serie'):
            serie = set_info['serie']
            if isinstance(serie, dict):
                embed.add_field(name="Series", value=serie.get('name', 'Unknown'), inline=True)
        return embed

    @staticmethod
    def kiss(author, member, gif_url):
        """Create embed for kiss command with GIF"""
        embed = discord.Embed(
            title="😘 Sweet Kiss!",
            description=f"{author.mention} sends a sweet kiss to {member.mention}!",
            color=ColorPalette.LOVE
        )
        if gif_url:
            embed.set_image(url=gif_url)
        return embed
