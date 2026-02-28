import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import random
from logger import log

class Music(commands.Cog):
    """Music commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.inactivity_tasks = {} 
    
    def get_queue(self, guild_id):
        """Retrieve or create the music queue for a guild"""
        if guild_id not in self.queues:
            log.debug(f'Creating new queue for guild {guild_id}')
            self.queues[guild_id] = deque()
        return self.queues[guild_id]
    
    def reset_inactivity_timer(self, guild_id):
        """Reset the inactivity timer"""
        if guild_id in self.inactivity_tasks:
            self.inactivity_tasks[guild_id].cancel()
            log.debug(f'Inactivity timer reset for guild {guild_id}')
        
        self.inactivity_tasks[guild_id] = asyncio.create_task(
            self.inactivity_disconnect(guild_id)
        )
    
    async def inactivity_disconnect(self, guild_id, timeout=300):
        """Disconnect bot after inactivity timeout (default 5 minutes)"""
        await asyncio.sleep(timeout)
        
        voice_client = self.bot.get_guild(guild_id).voice_client
        if voice_client and not voice_client.is_playing():
            log.info(f'Disconnecting due to inactivity in guild {guild_id}')
            await voice_client.disconnect()
            if guild_id in self.queues:
                self.queues[guild_id].clear()
            if guild_id in self.inactivity_tasks:
                del self.inactivity_tasks[guild_id]
    
    
    async def play_next(self, ctx):
        """Play the next song in the queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if len(queue) > 0:
            song_info = queue.popleft()
            voice_client = ctx.voice_client
            
            if voice_client and voice_client.is_connected():
                log.info(f'Playing: {song_info["title"]} in {ctx.guild.name}')
                voice_client.play(
                    discord.FFmpegPCMAudio(song_info['url']),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_next(ctx), self.bot.loop
                    )
                )
                await ctx.send(f"Playing: **{song_info['title']}**")
        else:
            log.debug(f'Queue empty in {ctx.guild.name}, starting inactivity timer')
            await ctx.send("📭 The queue is empty. Add more songs with `/play`!")
            self.reset_inactivity_timer(ctx.guild.id)
    
    @commands.hybrid_command(name="play", description="Play a song from YouTube or add to queue")
    async def play(self, ctx, *, param: str):
        """Add a song to the queue and play it"""
        log.info(f'Play command invoked by {ctx.author} with query: "{param}" in {ctx.guild.name}')
        if not ctx.author.voice:
            log.warning(f'User {ctx.author} not in voice channel in {ctx.guild.name}')
            await ctx.send("❌ You need to be in a voice channel to play music!")
            return
        
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            log.info(f'Connecting to voice channel: {channel.name} in {ctx.guild.name}')
            try:
                await channel.connect()
                log.success(f'Successfully connected to {channel.name}')
                self.reset_inactivity_timer(ctx.guild.id)
            except Exception as e:
                log.error(f'Failed to connect to voice channel: {e}')
                await ctx.send(f"❌ Could not connect to voice channel: {e}")
                return
        
        await ctx.send(f"🔍 Searching: **{param}**...")
        
        try:
            is_playlist = 'playlist' in param.lower() or 'list=' in param
            
            if is_playlist:
                log.info(f'Processing playlist request in {ctx.guild.name}')
                ydl_opts = {
                    'format': 'bestaudio',
                    'noplaylist': False,
                    'playlistend': 10, 
                    'quiet': True,
                    'extract_flat': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(param, download=False)
                    
                    if 'entries' in info:
                        songs_added = 0
                        queue = self.get_queue(ctx.guild.id)
                        
                        for entry in info['entries'][:10]:  
                            if entry:
                                ydl_single = {'format': 'bestaudio', 'quiet': True}
                                with yt_dlp.YoutubeDL(ydl_single) as ydl2:
                                    song_info = ydl2.extract_info(f"https://www.youtube.com/watch?v={entry['id']}", download=False)
                                    queue.append({
                                        'url': song_info['url'],
                                        'title': entry['title']
                                    })
                                    songs_added += 1
                        
                        log.success(f'Added {songs_added} songs from playlist to queue in {ctx.guild.name}')
                        await ctx.send(f"added **{songs_added}** songs from the playlist to the queue!")
                        
                        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                            await self.play_next(ctx)
                        return
            
            log.debug(f'Searching for single song: "{param}" in {ctx.guild.name}')
            ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if param.startswith("http"):
                    info = ydl.extract_info(param, download=False)
                    url = info['url']
                    title = info['title']
                else:
                    info = ydl.extract_info(f"ytsearch:{param}", download=False)
                    url = info['entries'][0]['url']
                    title = info['entries'][0]['title']
                    
            queue = self.get_queue(ctx.guild.id)
            queue.append({'url': url, 'title': title})
            log.info(f'Song added to queue: "{title}" (Position: {len(queue)}) in {ctx.guild.name}')
            
            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                await self.play_next(ctx)
            else:
                await ctx.send(f"Adding to queue: **{title}** (Position: {len(queue)})")
                
        except Exception as e:
            log.error(f'Error adding to queue: {e} (User: {ctx.author}, Query: {param})')
            await ctx.send(f"❌ Error Adding to queue {e}")
    
    @commands.hybrid_command(name="queue", description="Show the current music queue")
    async def queue(self, ctx):
        """Show the current music queue"""
        queue = self.get_queue(ctx.guild.id)
        log.debug(f'User {ctx.author} requested queue in {ctx.guild.name} ({len(queue)} songs)')
        
        if len(queue) == 0:
            await ctx.send("📭 The queue is empty")
            return
        
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(queue)])
        embed = discord.Embed(
            title="🎵 Current Music Queue",
            description=queue_list,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="skip", description="Skip to the next song")
    async def skip(self, ctx):
        """Skip to the next song"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            log.info(f'User {ctx.author} skipped song in {ctx.guild.name}')
            ctx.voice_client.stop()
            await ctx.send("Skipping to the next song...")
        else:
            log.warning(f'User {ctx.author} tried to skip but no song playing in {ctx.guild.name}')
            await ctx.send("❌ No Song in the queue to skip")
    
    @commands.hybrid_command(name="pause", description="Pause the current song")
    async def pause(self, ctx):
        """Pause the currently playing music"""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            log.info(f'User {ctx.author} paused music in {ctx.guild.name}')
            voice_client.pause()
            await ctx.send("Music paused")
        else:
            log.warning(f'User {ctx.author} tried to pause but no music playing in {ctx.guild.name}')
            await ctx.send("❌ No music is currently playing")
    
    @commands.hybrid_command(name="resume", description="Resume the paused song")
    async def resume(self, ctx):
        """Resume the paused music"""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_paused():
            log.info(f'User {ctx.author} resumed music in {ctx.guild.name}')
            voice_client.resume()
            await ctx.send("Music resumed")
        else:
            log.warning(f'User {ctx.author} tried to resume but no music paused in {ctx.guild.name}')
            await ctx.send("❌ No music is currently paused")
    
    @commands.hybrid_command(name="stop", description="Stop music and clear the queue")
    async def stop(self, ctx):
        """Stop the music and clear the queue"""
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        
        voice_client = ctx.voice_client
        if voice_client:
            log.info(f'User {ctx.author} stopped music in {ctx.guild.name}')
            await voice_client.disconnect()
            await ctx.send("Music stopped and queue cleared")
        else:
            log.warning(f'User {ctx.author} tried to stop but bot not in voice channel in {ctx.guild.name}')
            await ctx.send("❌ The bot is not in a voice channel")
    
    @commands.hybrid_command(name="shuffle", description="Shuffle the music queue")
    async def shuffle(self, ctx):
        """Shuffle the current music queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if len(queue) < 2:
            log.warning(f'User {ctx.author} tried to shuffle but only {len(queue)} song(s) in queue in {ctx.guild.name}')
            await ctx.send("❌ Not enough songs in the queue to shuffle")
            return
        
        log.info(f'User {ctx.author} shuffled queue ({len(queue)} songs) in {ctx.guild.name}')
        random.shuffle(queue)
        await ctx.send("🔀 The queue has been shuffled!")

async def setup(bot):
    log.debug('Setting up Music cog')
    await bot.add_cog(Music(bot))
