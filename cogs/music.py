import discord
from discord.ext import commands
import asyncio
from utils.logger import log
from services.queue_manager import QueueManager
from services.youtube_service import YouTubeService
from services.music_controls import MusicControlView
from services.inactivity_manager import InactivityManager
from services.voice_manager import VoiceManager
from services.embed_builder import EmbedBuilder


class Music(commands.Cog):
    """Music commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.queue_manager = QueueManager()
        self.youtube_service = YouTubeService()
        self.voice_manager = VoiceManager(bot)
        self.inactivity_manager = InactivityManager(bot, self.queue_manager)
        self.embed_builder = EmbedBuilder()
    
    
    async def play_next(self, ctx):
        """Play the next song in the queue"""
        song_info = self.queue_manager.get_next_song(ctx.guild.id)
        
        if song_info:
            if self.voice_manager.is_connected(ctx.guild.id):
                log.info(f'Playing: {song_info["title"]} in {ctx.guild.name}')
                
                audio_source = discord.FFmpegPCMAudio(song_info['url'])
                after_callback = lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx), self.bot.loop
                )
                
                self.voice_manager.play_audio(ctx.guild.id, audio_source, after_callback)
                
                embed = self.embed_builder.now_playing(song_info, ctx.author.display_name)
                view = MusicControlView(self, ctx)
                await ctx.send(embed=embed, view=view)
        else:
            log.debug(f'Queue empty in {ctx.guild.name}, starting inactivity timer')
            embed = self.embed_builder.queue_empty()
            await ctx.send(embed=embed)
            self.inactivity_manager.reset_timer(ctx.guild.id)
    
    @commands.hybrid_command(name="play", description="Play a song from YouTube or add to queue")
    async def play(self, ctx, *, param: str):
        """Add a song to the queue and play it"""
        log.info(f'Play command invoked by {ctx.author} with query: "{param}" in {ctx.guild.name}')
        
        voice_client, error = await self.voice_manager.ensure_connection(ctx)
        if error:
            await ctx.send(error)
            return
        
        self.inactivity_manager.reset_timer(ctx.guild.id)
        
        await ctx.send(f"🔍 Searching: **{param}**...")
        
        try:
            if self.youtube_service.is_playlist(param):
                log.info(f'Processing playlist request in {ctx.guild.name}')
                songs = await self.youtube_service.process_playlist(param)
                
                for song in songs:
                    self.queue_manager.add_song(ctx.guild.id, song)
                
                log.success(f'Added {len(songs)} songs from playlist to queue in {ctx.guild.name}')
                embed = self.embed_builder.playlist_added(len(songs), ctx.author.display_name)
                await ctx.send(embed=embed)
                
                if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                    await self.play_next(ctx)
                return
            
            log.debug(f'Searching for single song: "{param}" in {ctx.guild.name}')
            song_info = await self.youtube_service.search_song(param)
            
            position = self.queue_manager.add_song(ctx.guild.id, song_info)
            log.info(f'Song added to queue: "{song_info["title"]}" (Position: {position}) in {ctx.guild.name}')
            
            if not self.voice_manager.is_playing(ctx.guild.id) and not self.voice_manager.is_paused(ctx.guild.id):
                await self.play_next(ctx)
            else:
                embed = self.embed_builder.added_to_queue(song_info, position, ctx.author.display_name)
                view = MusicControlView(self, ctx)
                await ctx.send(embed=embed, view=view)
                
        except Exception as e:
            log.error(f'Error adding to queue: {e} (User: {ctx.author}, Query: {param})')
            await ctx.send(f"❌ Error adding to queue: {e}")
    
    @commands.hybrid_command(name="queue", description="Show the current music queue")
    async def queue(self, ctx):
        """Show the current music queue"""
        log.debug(f'User {ctx.author} requested queue in {ctx.guild.name}')
        
        if self.queue_manager.is_empty(ctx.guild.id):
            embed = self.embed_builder.queue_empty()
            await ctx.send(embed=embed)
            return
        
        queue = self.queue_manager.get_queue(ctx.guild.id)
        queue_list = "\n".join([f"`{i+1}.` **{song['title']}**" for i, song in enumerate(queue)])
        embed = self.embed_builder.queue_display(queue_list, len(queue))
        view = MusicControlView(self, ctx)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="skip", description="Skip to the next song")
    async def skip(self, ctx):
        """Skip to the next song"""
        if self.voice_manager.stop(ctx.guild.id):
            log.info(f'User {ctx.author} skipped song in {ctx.guild.name}')
            embed = self.embed_builder.song_skipped()
            await ctx.send(embed=embed)
        else:
            log.warning(f'User {ctx.author} tried to skip but no song playing in {ctx.guild.name}')
            await ctx.send("❌ No Song in the queue to skip")
    
    @commands.hybrid_command(name="pause", description="Pause the current song")
    async def pause(self, ctx):
        """Pause the currently playing music"""
        if self.voice_manager.pause(ctx.guild.id):
            log.info(f'User {ctx.author} paused music in {ctx.guild.name}')
            embed = self.embed_builder.music_paused()
            await ctx.send(embed=embed)
        else:
            log.warning(f'User {ctx.author} tried to pause but no music playing in {ctx.guild.name}')
            await ctx.send("❌ No music is currently playing")
    
    @commands.hybrid_command(name="resume", description="Resume the paused song")
    async def resume(self, ctx):
        """Resume the paused music"""
        if self.voice_manager.resume(ctx.guild.id):
            log.info(f'User {ctx.author} resumed music in {ctx.guild.name}')
            embed = self.embed_builder.music_resumed()
            await ctx.send(embed=embed)
        else:
            log.warning(f'User {ctx.author} tried to resume but no music paused in {ctx.guild.name}')
            await ctx.send("❌ No music is currently paused")
    
    @commands.hybrid_command(name="stop", description="Stop music and clear the queue")
    async def stop(self, ctx):
        """Stop the music and clear the queue"""
        self.queue_manager.clear_queue(ctx.guild.id)
        
        if self.voice_manager.is_connected(ctx.guild.id):
            log.info(f'User {ctx.author} stopped music in {ctx.guild.name}')
            await self.voice_manager.disconnect(ctx.guild.id)
            embed = self.embed_builder.music_stopped()
            await ctx.send(embed=embed)
        else:
            log.warning(f'User {ctx.author} tried to stop but bot not in voice channel in {ctx.guild.name}')
            await ctx.send("❌ The bot is not in a voice channel")
    
    @commands.hybrid_command(name="shuffle", description="Shuffle the music queue")
    async def shuffle(self, ctx):
        """Shuffle the current music queue"""
        if self.queue_manager.shuffle_queue(ctx.guild.id):
            queue_size = self.queue_manager.get_queue_size(ctx.guild.id)
            log.info(f'User {ctx.author} shuffled queue ({queue_size} songs) in {ctx.guild.name}')
            embed = self.embed_builder.queue_shuffled(queue_size)
            await ctx.send(embed=embed)
        else:
            log.warning(f'User {ctx.author} tried to shuffle but not enough songs in {ctx.guild.name}')
            await ctx.send("❌ Not enough songs in the queue to shuffle")
    
    @commands.hybrid_command(name="generate", description="Generate a playlist based on genre or topic")
    async def generate(self, ctx, genre: str, count: int = 10):
        """Generate a playlist based on music genre or topic"""
        log.info(f'Generate playlist command invoked by {ctx.author} for genre: "{genre}" in {ctx.guild.name}')
        
        voice_client, error = await self.voice_manager.ensure_connection(ctx)
        if error:
            await ctx.send(error)
            return
        
        self.inactivity_manager.reset_timer(ctx.guild.id)
        
        count = max(5, min(count, 15))
        
        await ctx.send(f"🎲 Generating {count} songs for **{genre}**... This may take a moment.")
        
        try:
            songs = await self.youtube_service.generate_playlist_by_genre(genre, count)
            
            if not songs:
                await ctx.send(f"❌ Could not find songs for genre: {genre}")
                return
            
            for song in songs:
                self.queue_manager.add_song(ctx.guild.id, song)
            
            log.success(f'Generated playlist with {len(songs)} songs for {genre} in {ctx.guild.name}')
            
            embed = self.embed_builder.playlist_generated(genre, len(songs), ctx.author.display_name)
            await ctx.send(embed=embed)
            
            if not self.voice_manager.is_playing(ctx.guild.id) and not self.voice_manager.is_paused(ctx.guild.id):
                await self.play_next(ctx)
                
        except Exception as e:
            log.error(f'Error generating playlist: {e} (User: {ctx.author}, Genre: {genre})')
            await ctx.send(f"❌ Error generating playlist: {e}")

async def setup(bot):
    log.debug('Setting up Music cog')
    await bot.add_cog(Music(bot))
