"""Embed Builder Service - Creates styled embeds for music bot"""
import discord
from utils.ui_colors import ColorPalette


class EmbedBuilder:
    """Service for creating consistent and styled Discord embeds"""
    
    @staticmethod
    def _add_field_if_exists(embed, data, key, name, value_format=None, inline=True):
        value = data.get(key)
        if value:
            if callable(value_format):
                value = value_format(value)
            elif value_format:
                value = value_format.format(value)
            embed.add_field(name=name, value=value, inline=inline)
    
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
            EmbedBuilder._add_field_if_exists(
                embed, 
                {'duration': f"{int(minutes)}:{int(seconds):02d}"}, 
                'duration', 
                "Duration", 
                inline=True
            )
        
        EmbedBuilder._add_field_if_exists(embed, song_info, 'uploader', "Channel", inline=True)
        
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
            EmbedBuilder._add_field_if_exists(
                embed,
                {'duration': f"{int(minutes)}:{int(seconds):02d}"},
                'duration',
                "Duration",
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
        
        EmbedBuilder._add_field_if_exists(embed, card, "hp", "HP", inline=True)
        
        if card.get("types"):
            types_str = " ".join([pokemon_service.get_type_emoji(t) + t for t in card["types"]])
            embed.add_field(name="Type", value=types_str, inline=True)
        
        embed.add_field(
            name="Rarity", 
            value=f"{rarity_emoji} {card.get('rarity', 'Unknown')}", 
            inline=True
        )
        
        EmbedBuilder._add_field_if_exists(embed, card, "set", "Set", inline=True)
        EmbedBuilder._add_field_if_exists(embed, card, "number", "Number", lambda x: f"#{x}", inline=True)
        
        if card.get("artist"):
            embed.set_footer(text=f"Illustrated by {card['artist']}")
        
        image_url = card.get("image_large") or card.get("image")
        if image_url:
            embed.set_image(url=image_url)
        
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
    
    @staticmethod
    def help_menu(bot_cogs, total_commands, bot_avatar_url=None):
        embed = discord.Embed(
            title="📚 Help Menu",
            description="Here are all available commands organized by category:",
            color=ColorPalette.INFO
        )
        
        for cog_name, cog in sorted(bot_cogs.items()):
            cog_commands = cog.get_commands()
            
            if cog_commands:
                commands_list = []
                for command in sorted(cog_commands, key=lambda x: x.name):
                    description = command.description or command.help or "No description"
                    commands_list.append(f"`/{command.name}` - {description}")
                
                if commands_list:
                    cog_desc = cog.__doc__ or cog_name
                    embed.add_field(
                        name=f"__{cog_desc}__",
                        value="\n".join(commands_list),
                        inline=False
                    )
        
        embed.set_footer(text=f"Total commands: {total_commands} | Use /command for details")
        
        if bot_avatar_url:
            embed.set_thumbnail(url=bot_avatar_url)
        
        return embed    
    @staticmethod
    def admin_today_logs(filename, file_size_kb):
        """Create embed for today's log file"""
        embed = discord.Embed(
            title="📄 Today's Log File",
            description="Here's the log file for today:",
            color=ColorPalette.INFO
        )
        embed.add_field(name="📝 Filename", value=f"`{filename}`", inline=False)
        embed.add_field(name="📊 File Size", value=f"{file_size_kb:.2f} KB", inline=True)
        embed.add_field(name="📅 Date", value=f"{filename.split('_')[1].split('.')[0][:4]}-{filename.split('_')[1].split('.')[0][4:6]}-{filename.split('_')[1].split('.')[0][6:]}", inline=True)
        embed.set_footer(text="💡 Tip: Use /getallogs for all logs in a zip")
        return embed
    
    @staticmethod
    def admin_logs_archive(files_count, total_size_kb, zip_size_kb):
        """Create embed for logs archive"""
        compression_ratio = ((total_size_kb - zip_size_kb) / total_size_kb * 100) if total_size_kb > 0 else 0
        
        embed = discord.Embed(
            title="📦 Logs Archive Created",
            description="All log files have been compressed successfully!",
            color=ColorPalette.SUCCESS
        )
        embed.add_field(name="📁 Total Files", value=f"{files_count} files", inline=True)
        embed.add_field(name="📏 Original Size", value=f"{total_size_kb:.2f} KB", inline=True)
        embed.add_field(name="🗜️ Compressed Size", value=f"{zip_size_kb:.2f} KB", inline=True)
        embed.add_field(name="💾 Compression Ratio", value=f"{compression_ratio:.1f}% smaller", inline=False)
        embed.set_footer(text="✨ Archive ready for download!")
        return embed
    
    @staticmethod
    def admin_logs_cleanup(deleted_count, kept_count, days_kept=7):
        """Create embed for logs cleanup results"""
        embed = discord.Embed(
            title="🗑️ Logs Cleanup Complete",
            description=f"Old log files have been cleaned up. Keeping last {days_kept} days.",
            color=ColorPalette.WARNING
        )
        embed.add_field(name="❌ Deleted", value=f"{deleted_count} files", inline=True)
        embed.add_field(name="✅ Kept", value=f"{kept_count} files", inline=True)
        embed.add_field(name="⏱️ Retention", value=f"{days_kept} days", inline=True)
        
        if deleted_count > 0:
            embed.set_footer(text="💡 Freed up disk space!")
        else:
            embed.set_footer(text="✨ All logs are recent!")
        
        return embed
    
    @staticmethod
    def admin_logs_statistics(total_files, total_size_mb, oldest_log, newest_log):
        """Create embed for logs statistics"""
        embed = discord.Embed(
            title="📊 Logs Statistics",
            description="Overview of all log files in the system:",
            color=ColorPalette.ACCENT
        )
        embed.add_field(name="📁 Total Files", value=f"{total_files} files", inline=True)
        embed.add_field(name="💾 Total Size", value=f"{total_size_mb:.2f} MB", inline=True)
        embed.add_field(name="⚡ Avg Size", value=f"{(total_size_mb / total_files):.2f} MB", inline=True)
        embed.add_field(name="📅 Oldest Log", value=oldest_log, inline=True)
        embed.add_field(name="🆕 Newest Log", value=newest_log, inline=True)
        
        try:
            from datetime import datetime
            oldest_date = datetime.strptime(oldest_log, "%Y-%m-%d")
            newest_date = datetime.strptime(newest_log, "%Y-%m-%d")
            days_span = (newest_date - oldest_date).days
            embed.add_field(name="📆 Date Range", value=f"{days_span} days", inline=True)
        except:
            pass
        
        embed.set_footer(text="💡 Use /clearlogs to clean old logs")
        return embed