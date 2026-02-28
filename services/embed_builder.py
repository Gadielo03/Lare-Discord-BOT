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
    def queue_empty():
        """Create embed for empty queue"""
        embed = discord.Embed(
            title="📭 Queue Empty",
            description="No more songs in the queue.\nAdd more songs with `/play`!",
            color=ColorPalette.EMPTY
        )
        embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGg5Njk0NHBtOGRmMHhsNGE4NDF4ZTFmZDJ5aGJvNGprZm1rYWRhbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hEc4k5pN17GZq/giphy.gif")
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
