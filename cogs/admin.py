import discord
from discord.ext import commands, tasks
from utils.ui_colors import ColorPalette
from services.embed_builder import EmbedBuilder
from services.logs_manager import LogsManager
from utils.logger import log
from datetime import time

class Admin(commands.Cog):
    """Admin commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.embed_builder = EmbedBuilder()
        self.logs_manager = LogsManager()
        self.auto_cleanup_logs.start()  # Start the automatic cleanup task
    
    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.auto_cleanup_logs.cancel()
    
    @tasks.loop(time=time(hour=3, minute=0))  # Run at 3:00 AM every day
    async def auto_cleanup_logs(self):
        """Automatically clean up old logs every day"""
        try:
            deleted_count, kept_count = self.logs_manager.clear_old_logs(days_to_keep=7)
            
            if deleted_count > 0:
                log.info(f"🗑️ Auto-cleanup: Deleted {deleted_count} old log files, kept {kept_count}")
            else:
                log.debug(f"✨ Auto-cleanup: All logs are recent ({kept_count} files)")
                
        except Exception as e:
            log.error(f"Error in auto log cleanup: {e}")
    
    @auto_cleanup_logs.before_loop
    async def before_auto_cleanup(self):
        """Wait until bot is ready before starting the task"""
        await self.bot.wait_until_ready()
        log.info("🤖 Auto log cleanup task started (runs daily at 3:00 AM)")
    
    def is_admin():
        """Check if user has administrator permissions"""
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)
    
    @commands.hybrid_command(name="getlogs", description="Get today's global bot log file")
    @is_admin()
    async def getlogs(self, ctx):
        """Send today's global log file"""
        try:
            log_file, file_size = self.logs_manager.get_today_log_file()
            
            if not log_file:
                await ctx.send("❌ No log file found for today!")
                return
            
            filename = log_file.split('/')[-1]
            embed = self.embed_builder.admin_today_logs(filename, file_size)
            embed.add_field(name="Scope", value="🌐 Global Logs", inline=True)
            
            await ctx.send(embed=embed, file=discord.File(log_file))
            log.info(f"{ctx.author} requested today's global logs")
            
        except Exception as e:
            log.error(f"Error getting logs: {e}")
            await ctx.send(f"❌ Error getting logs: {e}")
    
    @commands.hybrid_command(name="getserverlogs", description="Get today's log file for this server")
    @is_admin()
    async def getserverlogs(self, ctx):
        """Send today's log file for current server"""
        try:
            log_file, file_size = self.logs_manager.get_today_log_file(ctx.guild.id)
            
            if not log_file:
                await ctx.send(f"❌ No log file found for this server today!")
                return
            
            filename = log_file.split('/')[-1]
            embed = self.embed_builder.admin_today_logs(filename, file_size)
            embed.add_field(name="Server", value=f"🏠 {ctx.guild.name}", inline=True)
            
            await ctx.send(embed=embed, file=discord.File(log_file))
            log.server_log(ctx.guild.id, ctx.guild.name, f"{ctx.author} requested today's server logs", "INFO")
            
        except Exception as e:
            log.error(f"Error getting server logs: {e}")
            await ctx.send(f"❌ Error getting server logs: {e}")
    
    @commands.hybrid_command(name="getallogs", description="Get all global log files in a zip")
    @is_admin()
    async def getallogs(self, ctx):
        """Send all global log files compressed in a zip"""
        try:
            zip_buffer, stats = self.logs_manager.create_logs_archive()
            
            if not zip_buffer:
                await ctx.send("❌ No log files found!")
                return
            
            embed = self.embed_builder.admin_logs_archive(
                stats['files_count'],
                stats['total_size_kb'],
                stats['zip_size_kb']
            )
            embed.add_field(name="Scope", value="🌐 Global Logs", inline=True)
            
            zip_filename = self.logs_manager.generate_zip_filename()
            
            await ctx.send(
                embed=embed, 
                file=discord.File(fp=zip_buffer, filename=zip_filename)
            )
            log.info(f"{ctx.author} requested all global logs ({stats['files_count']} files)")
            
        except Exception as e:
            log.error(f"Error creating logs archive: {e}")
            await ctx.send(f"❌ Error creating logs archive: {e}")
    
    @commands.hybrid_command(name="getallserverlogs", description="Get all log files for this server in a zip")
    @is_admin()
    async def getallserverlogs(self, ctx):
        """Send all server log files compressed in a zip"""
        try:
            zip_buffer, stats = self.logs_manager.create_logs_archive(ctx.guild.id)
            
            if not zip_buffer:
                await ctx.send(f"❌ No log files found for this server!")
                return
            
            embed = self.embed_builder.admin_logs_archive(
                stats['files_count'],
                stats['total_size_kb'],
                stats['zip_size_kb']
            )
            embed.add_field(name="Server", value=f"🏠 {ctx.guild.name}", inline=True)
            
            zip_filename = self.logs_manager.generate_zip_filename(ctx.guild.id)
            
            await ctx.send(
                embed=embed, 
                file=discord.File(fp=zip_buffer, filename=zip_filename)
            )
            log.server_log(ctx.guild.id, ctx.guild.name, f"{ctx.author} requested all server logs ({stats['files_count']} files)", "INFO")
            
        except Exception as e:
            log.error(f"Error creating server logs archive: {e}")
            await ctx.send(f"❌ Error creating server logs archive: {e}")
    
    @commands.hybrid_command(name="clearlogs", description="Delete old global log files (keeps last 7 days)")
    @is_admin()
    async def clearlogs(self, ctx):
        """Delete global log files older than 7 days"""
        try:
            deleted_count, kept_count = self.logs_manager.clear_old_logs(days_to_keep=7)
            
            if deleted_count == 0 and kept_count == 0:
                await ctx.send("❌ No log files found!")
                return
            
            embed = self.embed_builder.admin_logs_cleanup(deleted_count, kept_count, days_kept=7)
            embed.add_field(name="Scope", value="🌐 Global Logs", inline=True)
            
            await ctx.send(embed=embed)
            log.info(f"{ctx.author} cleaned old global logs: {deleted_count} deleted, {kept_count} kept")
            
        except Exception as e:
            log.error(f"Error clearing logs: {e}")
            await ctx.send(f"❌ Error clearing logs: {e}")
    
    @commands.hybrid_command(name="clearserverlogs", description="Delete old server log files (keeps last 7 days)")
    @is_admin()
    async def clearserverlogs(self, ctx):
        """Delete server log files older than 7 days"""
        try:
            deleted_count, kept_count = self.logs_manager.clear_old_logs(days_to_keep=7, guild_id=ctx.guild.id)
            
            if deleted_count == 0 and kept_count == 0:
                await ctx.send(f"❌ No log files found for this server!")
                return
            
            embed = self.embed_builder.admin_logs_cleanup(deleted_count, kept_count, days_kept=7)
            embed.add_field(name="Server", value=f"🏠 {ctx.guild.name}", inline=True)
            
            await ctx.send(embed=embed)
            log.server_log(ctx.guild.id, ctx.guild.name, f"{ctx.author} cleaned old server logs: {deleted_count} deleted, {kept_count} kept", "INFO")
            
        except Exception as e:
            log.error(f"Error clearing server logs: {e}")
            await ctx.send(f"❌ Error clearing server logs: {e}")
    
    @commands.hybrid_command(name="logsstats", description="View logs statistics")
    @is_admin()
    async def logsstats(self, ctx):
        """Show statistics about log files"""
        try:
            stats = self.logs_manager.get_logs_statistics()
            
            if not stats:
                await ctx.send("❌ No log files found!")
                return
            
            embed = self.embed_builder.admin_logs_statistics(
                stats['total_files'],
                stats['total_size_mb'],
                stats['oldest_log'],
                stats['newest_log']
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            log.error(f"Error getting logs stats: {e}")
            await ctx.send(f"❌ Error getting logs stats: {e}")
    
    @commands.hybrid_command(name="autocleanup", description="View or toggle automatic log cleanup status")
    @is_admin()
    async def autocleanup(self, ctx, action: str = None):
        try:
            if action is None or action.lower() == "status":
                is_running = self.auto_cleanup_logs.is_running()
                next_run = self.auto_cleanup_logs.next_iteration
                
                embed = discord.Embed(
                    title="🤖 Auto Cleanup Status",
                    color=ColorPalette.SUCCESS if is_running else ColorPalette.WARNING
                )
                
                embed.add_field(
                    name="Status", 
                    value="🟢 Running" if is_running else "🔴 Stopped", 
                    inline=True
                )
                embed.add_field(
                    name="Schedule", 
                    value="Daily at 3:00 AM", 
                    inline=True
                )
                embed.add_field(
                    name="Retention", 
                    value="7 days", 
                    inline=True
                )
                
                if is_running and next_run:
                    embed.add_field(
                        name="Next Run", 
                        value=f"<t:{int(next_run.timestamp())}:R>",
                        inline=False
                    )
                
                embed.set_footer(text="💡 Use /autocleanup start|stop|trigger to control")
                await ctx.send(embed=embed)
                
            elif action.lower() == "start":
                if self.auto_cleanup_logs.is_running():
                    await ctx.send("⚠️ Auto cleanup is already running!")
                else:
                    self.auto_cleanup_logs.start()
                    await ctx.send("✅ Auto cleanup has been started!")
                    log.info(f"{ctx.author} started auto log cleanup")
                    
            elif action.lower() == "stop":
                if not self.auto_cleanup_logs.is_running():
                    await ctx.send("⚠️ Auto cleanup is already stopped!")
                else:
                    self.auto_cleanup_logs.cancel()
                    await ctx.send("🛑 Auto cleanup has been stopped!")
                    log.info(f"{ctx.author} stopped auto log cleanup")
                    
            elif action.lower() == "trigger":
                await ctx.send("🔄 Triggering manual cleanup...")
                deleted_count, kept_count = self.logs_manager.clear_old_logs(days_to_keep=7)
                
                embed = self.embed_builder.admin_logs_cleanup(deleted_count, kept_count, days_kept=7)
                await ctx.send(embed=embed)
                log.info(f"{ctx.author} manually triggered auto cleanup: {deleted_count} deleted")
                
            else:
                await ctx.send(f"❌ Invalid action! Use: status, start, stop, or trigger")
                
        except Exception as e:
            log.error(f"Error managing auto cleanup: {e}")
            await ctx.send(f"❌ Error: {e}")
    
    @commands.hybrid_command(name="serverslogs", description="View all servers with logs")
    @is_admin()
    async def serverslogs(self, ctx):
        """List all servers that have log files"""
        try:
            servers = self.logs_manager.get_servers_list()
            
            if not servers:
                await ctx.send("❌ No server logs found!")
                return
            
            embed = discord.Embed(
                title="📁 Servers with Logs",
                color=ColorPalette.INFO,
                description=f"Found logs for **{len(servers)}** servers"
            )
            
            server_list = []
            for guild_id in servers:
                guild = self.bot.get_guild(int(guild_id))
                guild_name = guild.name if guild else "Unknown Server"
                logs_count = len(self.logs_manager.get_server_logs(guild_id))
                server_list.append(f"• **{guild_name}** (`{guild_id}`) - {logs_count} files")
            
            embed.add_field(
                name="Servers",
                value="\n".join(server_list[:10]),  # Limit to 10 to avoid embed size issues
                inline=False
            )
            
            if len(server_list) > 10:
                embed.set_footer(text=f"Showing 10 of {len(server_list)} servers")
            
            await ctx.send(embed=embed)
            log.info(f"{ctx.author} requested servers logs list")
            
        except Exception as e:
            log.error(f"Error getting servers list: {e}")
            await ctx.send(f"❌ Error: {e}")
    

async def setup(bot):
    await bot.add_cog(Admin(bot))
