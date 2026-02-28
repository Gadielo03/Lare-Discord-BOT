"""Inactivity Manager - Handles bot disconnection after inactivity"""
import asyncio
from logger import log


class InactivityManager:
    """Manages inactivity timers for voice connections"""
    
    def __init__(self, bot, queue_manager):
        self.bot = bot
        self.queue_manager = queue_manager
        self.inactivity_tasks = {}
    
    def reset_timer(self, guild_id):
        """Reset the inactivity timer"""
        if guild_id in self.inactivity_tasks:
            self.inactivity_tasks[guild_id].cancel()
            log.debug(f'Inactivity timer reset for guild {guild_id}')
        
        self.inactivity_tasks[guild_id] = asyncio.create_task(
            self._disconnect_after_timeout(guild_id)
        )
    
    async def _disconnect_after_timeout(self, guild_id, timeout=300):
        """Disconnect bot after inactivity timeout (default 5 minutes)"""
        await asyncio.sleep(timeout)
        
        guild = self.bot.get_guild(guild_id)
        if guild and guild.voice_client:
            voice_client = guild.voice_client
            if not voice_client.is_playing():
                log.info(f'Disconnecting due to inactivity in guild {guild_id}')
                await voice_client.disconnect()
                self.queue_manager.clear_queue(guild_id)
                if guild_id in self.inactivity_tasks:
                    del self.inactivity_tasks[guild_id]
    
    def cancel_timer(self, guild_id):
        """Cancel the inactivity timer"""
        if guild_id in self.inactivity_tasks:
            self.inactivity_tasks[guild_id].cancel()
            del self.inactivity_tasks[guild_id]
            log.debug(f'Inactivity timer cancelled for guild {guild_id}')
