import discord
from discord.ext import commands
from discord.ui import View, Button
import yt_dlp
import asyncio
from collections import deque
import random
from logger import log
from ui_colors import ColorPalette

class MusicControlView(View):
    """Interactive music control buttons"""
    
    def __init__(self, cog, ctx):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.cog = cog
        self.ctx = ctx
    
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary, emoji="⏸️")
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        voice_client = self.ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            button.label = "Resume"
            button.emoji = "▶️"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("⏸️ Music paused", ephemeral=True)
        elif voice_client and voice_client.is_paused():
            voice_client.resume()
            button.label = "Pause"
            button.emoji = "⏸️"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("▶️ Music resumed", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No music is playing", ephemeral=True)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        voice_client = self.ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped to next song", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No music is playing", ephemeral=True)
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        voice_client = self.ctx.voice_client
        if voice_client:
            queue = self.cog.get_queue(self.ctx.guild.id)
            queue.clear()
            await voice_client.disconnect()
            await interaction.response.send_message("⏹️ Music stopped and queue cleared", ephemeral=True)
            # Disable all buttons
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message("❌ Bot is not in a voice channel", ephemeral=True)
    
    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, emoji="🔀")
    async def shuffle_button(self, interaction: discord.Interaction, button: Button):
        queue = self.cog.get_queue(self.ctx.guild.id)
        if len(queue) < 2:
            await interaction.response.send_message("❌ Not enough songs to shuffle", ephemeral=True)
        else:
            random.shuffle(queue)
            await interaction.response.send_message(f"🔀 Shuffled {len(queue)} songs", ephemeral=True)
    
    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, emoji="📜")
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        queue = self.cog.get_queue(self.ctx.guild.id)
        if len(queue) == 0:
            await interaction.response.send_message("📭 Queue is empty", ephemeral=True)
        else:
            queue_list = "\n".join([f"`{i+1}.` **{song['title']}**" for i, song in enumerate(list(queue)[:10])])
            if len(queue) > 10:
                queue_list += f"\n\n*...and {len(queue) - 10} more*"
            embed = discord.Embed(
                title="🎵 Current Queue",
                description=queue_list,
                color=ColorPalette.QUEUE
            )
            embed.set_footer(text=f"Total: {len(queue)} songs")
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{song_info['title']}**",
                    color=ColorPalette.NOW_PLAYING
                )
                
                # Add thumbnail if available
                if 'thumbnail' in song_info and song_info['thumbnail']:
                    embed.set_thumbnail(url=song_info['thumbnail'])
                
                # Add duration if available
                if 'duration' in song_info and song_info['duration']:
                    minutes, seconds = divmod(song_info['duration'], 60)
                    embed.add_field(name="Duration", value=f"{int(minutes)}:{int(seconds):02d}", inline=True)
                
                # Add channel if available
                if 'uploader' in song_info and song_info['uploader']:
                    embed.add_field(name="Channel", value=song_info['uploader'], inline=True)
                
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                view = MusicControlView(self, ctx)
                await ctx.send(embed=embed, view=view)
        else:
            log.debug(f'Queue empty in {ctx.guild.name}, starting inactivity timer')
            embed = discord.Embed(
                title="📭 Queue Empty",
                description="No more songs in the queue.\nAdd more songs with `/play`!",
                color=ColorPalette.EMPTY
            )
            # Add animated GIF for empty queue
            embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGg5Njk0NHBtOGRmMHhsNGE4NDF4ZTFmZDJ5aGJvNGprZm1rYWRhbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hEc4k5pN17GZq/giphy.gif")
            await ctx.send(embed=embed)
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
                                        'title': entry['title'],
                                        'thumbnail': song_info.get('thumbnail'),
                                        'duration': song_info.get('duration'),
                                        'uploader': song_info.get('uploader')
                                    })
                                    songs_added += 1
                        
                        log.success(f'Added {songs_added} songs from playlist to queue in {ctx.guild.name}')
                        embed = discord.Embed(
                            title="📑 Playlist Added",
                            description=f"Added **{songs_added}** songs to the queue!",
                            color=ColorPalette.ADDED
                        )
                        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                        await ctx.send(embed=embed)
                        
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
                    thumbnail = info.get('thumbnail')
                    duration = info.get('duration')
                    uploader = info.get('uploader')
                else:
                    info = ydl.extract_info(f"ytsearch:{param}", download=False)
                    entry = info['entries'][0]
                    url = entry['url']
                    title = entry['title']
                    thumbnail = entry.get('thumbnail')
                    duration = entry.get('duration')
                    uploader = entry.get('uploader')
                    
            queue = self.get_queue(ctx.guild.id)
            queue.append({
                'url': url,
                'title': title,
                'thumbnail': thumbnail,
                'duration': duration,
                'uploader': uploader
            })
            log.info(f'Song added to queue: "{title}" (Position: {len(queue)}) in {ctx.guild.name}')
            
            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                await self.play_next(ctx)
            else:
                embed = discord.Embed(
                    title="➕ Added to Queue",
                    description=f"**{title}**",
                    color=ColorPalette.ADDED
                )
                
                # Add thumbnail
                if thumbnail:
                    embed.set_thumbnail(url=thumbnail)
                
                # Add duration if available
                if duration:
                    minutes, seconds = divmod(duration, 60)
                    embed.add_field(name="Duration", value=f"{int(minutes)}:{int(seconds):02d}", inline=True)
                
                embed.add_field(name="Position", value=f"#{len(queue)}", inline=True)
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                view = MusicControlView(self, ctx)
                await ctx.send(embed=embed, view=view)
                
        except Exception as e:
            log.error(f'Error adding to queue: {e} (User: {ctx.author}, Query: {param})')
            await ctx.send(f"❌ Error Adding to queue {e}")
    
    @commands.hybrid_command(name="queue", description="Show the current music queue")
    async def queue(self, ctx):
        """Show the current music queue"""
        queue = self.get_queue(ctx.guild.id)
        log.debug(f'User {ctx.author} requested queue in {ctx.guild.name} ({len(queue)} songs)')
        
        if len(queue) == 0:
            embed = discord.Embed(
                title="📭 Queue Empty",
                description="No songs in the queue. Use `/play` to add some!",
                color=ColorPalette.EMPTY
            )
            await ctx.send(embed=embed)
            return
        
        queue_list = "\n".join([f"`{i+1}.` **{song['title']}**" for i, song in enumerate(queue)])
        embed = discord.Embed(
            title="🎵 Current Music Queue",
            description=queue_list,
            color=ColorPalette.QUEUE
        )
        embed.set_footer(text=f"Total songs: {len(queue)}")
        view = MusicControlView(self, ctx)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="skip", description="Skip to the next song")
    async def skip(self, ctx):
        """Skip to the next song"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            log.info(f'User {ctx.author} skipped song in {ctx.guild.name}')
            ctx.voice_client.stop()
            embed = discord.Embed(
                title="⏭️ Song Skipped",
                description="Moving to the next song...",
                color=ColorPalette.INFO
            )
            await ctx.send(embed=embed)
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
            embed = discord.Embed(
                title="⏸️ Music Paused",
                description="Use `/resume` to continue playing",
                color=ColorPalette.WARNING
            )
            await ctx.send(embed=embed)
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
            embed = discord.Embed(
                title="▶️ Music Resumed",
                description="Playback has been resumed",
                color=ColorPalette.SUCCESS
            )
            await ctx.send(embed=embed)
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
            embed = discord.Embed(
                title="⏹️ Music Stopped",
                description="Disconnected from voice channel and cleared the queue",
                color=ColorPalette.ERROR
            )
            await ctx.send(embed=embed)
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
        embed = discord.Embed(
            title="🔀 Queue Shuffled",
            description=f"Randomized {len(queue)} songs in the queue",
            color=ColorPalette.SECONDARY
        )
        await ctx.send(embed=embed)

async def setup(bot):
    log.debug('Setting up Music cog')
    await bot.add_cog(Music(bot))
