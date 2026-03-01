"""Music Control View - Interactive buttons for music control"""
import discord
from discord.ui import View, Button
from utils.ui_colors import ColorPalette


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
            queue_manager = self.cog.queue_manager
            queue_manager.clear_queue(self.ctx.guild.id)
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
        queue_manager = self.cog.queue_manager
        if queue_manager.shuffle_queue(self.ctx.guild.id):
            queue_size = queue_manager.get_queue_size(self.ctx.guild.id)
            await interaction.response.send_message(f"🔀 Shuffled {queue_size} songs", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Not enough songs to shuffle", ephemeral=True)
    
    @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, emoji="📜")
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        queue_manager = self.cog.queue_manager
        queue = queue_manager.get_queue(self.ctx.guild.id)
        
        if queue_manager.is_empty(self.ctx.guild.id):
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
