import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import random

class Music(commands.Cog):
    """Music commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.inactivity_tasks = {} 
    
    def get_queue(self, guild_id):
        """Retrieve or create the music queue for a guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]
    
    def reset_inactivity_timer(self, guild_id):
        """Reset the inactivity timer"""
        if guild_id in self.inactivity_tasks:
            self.inactivity_tasks[guild_id].cancel()
        
        self.inactivity_tasks[guild_id] = asyncio.create_task(
            self.inactivity_disconnect(guild_id)
        )
    
    async def inactivity_disconnect(self, guild_id, timeout=300):
        """Disconnect bot after inactivity timeout (default 5 minutes)"""
        await asyncio.sleep(timeout)
        
        voice_client = self.bot.get_guild(guild_id).voice_client
        if voice_client and not voice_client.is_playing():
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
                voice_client.play(
                    discord.FFmpegPCMAudio(song_info['url']),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_next(ctx), self.bot.loop
                    )
                )
                await ctx.send(f"Playing: **{song_info['title']}**")
        else:
            await ctx.send("📭 The queue is empty. Add more songs with `/play`!")
            self.reset_inactivity_timer(ctx.guild.id)
    
    @commands.hybrid_command(name="play", description="Play a song from YouTube or add to queue")
    async def play(self, ctx, *, param: str):
        """Add a song to the queue and play it"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to play music!")
            return
        
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            await channel.connect()
            self.reset_inactivity_timer(ctx.guild.id)
        
        await ctx.send(f"🔍 Searching: **{param}**...")
        
        try:
            is_playlist = 'playlist' in param.lower() or 'list=' in param
            
            if is_playlist:
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
                        
                        await ctx.send(f"added **{songs_added}** songs from the playlist to the queue!")
                        
                        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                            await self.play_next(ctx)
                        return
            
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
            
            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                await self.play_next(ctx)
            else:
                await ctx.send(f"Adding to queue: **{title}** (Position: {len(queue)})")
                
        except Exception as e:
            await ctx.send(f"❌ Error Adding to queue {e}")
    
    @commands.hybrid_command(name="queue", description="Show the current music queue")
    async def queue(self, ctx):
        """Show the current music queue"""
        queue = self.get_queue(ctx.guild.id)
        
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
            ctx.voice_client.stop()
            await ctx.send("Skipping to the next song...")
        else:
            await ctx.send("❌ No Song in the queue to skip")
    
    @commands.hybrid_command(name="pause", description="Pause the current song")
    async def pause(self, ctx):
        """Pause the currently playing music"""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Music paused")
        else:
            await ctx.send("❌ No music is currently playing")
    
    @commands.hybrid_command(name="resume", description="Resume the paused song")
    async def resume(self, ctx):
        """Resume the paused music"""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Music resumed")
        else:
            await ctx.send("❌ No music is currently paused")
    
    @commands.hybrid_command(name="stop", description="Stop music and clear the queue")
    async def stop(self, ctx):
        """Stop the music and clear the queue"""
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        
        voice_client = ctx.voice_client
        if voice_client:
            await voice_client.disconnect()
            await ctx.send("Music stopped and queue cleared")
        else:
            await ctx.send("❌ The bot is not in a voice channel")
    
    @commands.hybrid_command(name="shuffle", description="Shuffle the music queue")
    async def shuffle(self, ctx):
        """Shuffle the current music queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if len(queue) < 2:
            await ctx.send("❌ Not enough songs in the queue to shuffle")
            return
        
        random.shuffle(queue)
        await ctx.send("🔀 The queue has been shuffled!")

async def setup(bot):
    await bot.add_cog(Music(bot))
