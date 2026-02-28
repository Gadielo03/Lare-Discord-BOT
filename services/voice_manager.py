"""Voice Channel Manager Service - Handles voice channel operations"""
import discord
import asyncio
from utils.logger import log


class VoiceManager:
    """Manages voice channel connections and audio playback"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def connect_to_channel(self, channel):
        """Connect to a voice channel"""
        try:
            log.info(f'Connecting to voice channel: {channel.name}')
            voice_client = await channel.connect()
            log.success(f'Successfully connected to {channel.name}')
            return voice_client
        except Exception as e:
            log.error(f'Failed to connect to voice channel: {e}')
            raise
    
    async def disconnect(self, guild_id):
        """Disconnect from voice channel"""
        guild = self.bot.get_guild(guild_id)
        if guild and guild.voice_client:
            log.info(f'Disconnecting from voice channel in {guild.name}')
            await guild.voice_client.disconnect()
    
    def get_voice_client(self, guild_id):
        """Get the voice client for a guild"""
        guild = self.bot.get_guild(guild_id)
        return guild.voice_client if guild else None
    
    def is_connected(self, guild_id):
        """Check if bot is connected to voice channel"""
        voice_client = self.get_voice_client(guild_id)
        return voice_client is not None and voice_client.is_connected()
    
    def is_playing(self, guild_id):
        """Check if audio is currently playing"""
        voice_client = self.get_voice_client(guild_id)
        return voice_client is not None and voice_client.is_playing()
    
    def is_paused(self, guild_id):
        """Check if audio is paused"""
        voice_client = self.get_voice_client(guild_id)
        return voice_client is not None and voice_client.is_paused()
    
    def pause(self, guild_id):
        """Pause audio playback"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            log.info(f'Audio paused in guild {guild_id}')
            return True
        return False
    
    def resume(self, guild_id):
        """Resume audio playback"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            log.info(f'Audio resumed in guild {guild_id}')
            return True
        return False
    
    def stop(self, guild_id):
        """Stop audio playback"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            log.info(f'Audio stopped in guild {guild_id}')
            return True
        return False
    
    def play_audio(self, guild_id, audio_source, after_callback=None):
        """Play audio in voice channel"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_connected():
            voice_client.play(audio_source, after=after_callback)
            return True
        return False
    
    async def ensure_connection(self, ctx):
        """Ensure bot is connected to user's voice channel"""
        if not ctx.author.voice:
            log.warning(f'User {ctx.author} not in voice channel')
            return None, "❌ You need to be in a voice channel to play music!"
        
        channel = ctx.author.voice.channel
        
        if not ctx.voice_client:
            try:
                voice_client = await self.connect_to_channel(channel)
                return voice_client, None
            except Exception as e:
                return None, f"❌ Could not connect to voice channel: {e}"
        
        return ctx.voice_client, None
