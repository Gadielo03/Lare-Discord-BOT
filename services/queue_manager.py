"""Queue Manager Service - Handles music queue operations"""
from collections import deque
from logger import log


class QueueManager:
    """Manages music queues for different guilds"""
    
    def __init__(self):
        self.queues = {}
    
    def get_queue(self, guild_id):
        """Retrieve or create the music queue for a guild"""
        if guild_id not in self.queues:
            log.debug(f'Creating new queue for guild {guild_id}')
            self.queues[guild_id] = deque()
        return self.queues[guild_id]
    
    def add_song(self, guild_id, song_info):
        """Add a song to the queue"""
        queue = self.get_queue(guild_id)
        queue.append(song_info)
        return len(queue)
    
    def get_next_song(self, guild_id):
        """Get the next song from the queue"""
        queue = self.get_queue(guild_id)
        if len(queue) > 0:
            return queue.popleft()
        return None
    
    def clear_queue(self, guild_id):
        """Clear the queue for a guild"""
        if guild_id in self.queues:
            self.queues[guild_id].clear()
            log.debug(f'Cleared queue for guild {guild_id}')
    
    def shuffle_queue(self, guild_id):
        """Shuffle the queue for a guild"""
        import random
        queue = self.get_queue(guild_id)
        if len(queue) >= 2:
            random.shuffle(queue)
            return True
        return False
    
    def get_queue_size(self, guild_id):
        """Get the size of the queue"""
        return len(self.get_queue(guild_id))
    
    def is_empty(self, guild_id):
        """Check if the queue is empty"""
        return len(self.get_queue(guild_id)) == 0
