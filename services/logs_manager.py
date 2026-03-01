"""Logs Manager Service - Manages log files operations"""
import os
import zipfile
from datetime import datetime
import io
from utils.logger import log


class LogsManager:
    """Service for managing log files operations"""
    
    def __init__(self, logs_dir="Lare_Logs"):
        self.logs_dir = logs_dir
        self.servers_dir = f"{logs_dir}/servers"
    
    def get_today_log_file(self, guild_id=None):
        """Get today's log file path and info"""
        today = datetime.now().strftime("%Y%m%d")
        
        if guild_id:
            log_file = f"{self.servers_dir}/{guild_id}_{today}.log"
        else:
            log_file = f"{self.logs_dir}/bot_{today}.log"
        
        if not os.path.exists(log_file):
            return None, None
        
        file_size = os.path.getsize(log_file) / 1024  # KB
        return log_file, file_size
    
    def get_all_log_files(self, include_servers=False):
        """Get all log files in directory"""
        if not os.path.exists(self.logs_dir):
            return []
        
        main_logs = [f for f in os.listdir(self.logs_dir) if f.endswith('.log')]
        
        if include_servers and os.path.exists(self.servers_dir):
            server_logs = [f"servers/{f}" for f in os.listdir(self.servers_dir) if f.endswith('.log')]
            return main_logs + server_logs
        
        return main_logs
    
    def create_logs_archive(self, guild_id=None):
        """Create a zip archive with all log files"""
        if guild_id:
            log_files = self.get_server_logs(guild_id)
            base_dir = self.servers_dir
        else:
            log_files = self.get_all_log_files(include_servers=True)
            base_dir = self.logs_dir
        
        if not log_files:
            return None, None
        
        try:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for log_file in log_files:
                    file_path = os.path.join(base_dir if not guild_id else base_dir, log_file.replace('servers/', ''))
                    if guild_id:
                        zip_file.write(file_path, log_file.replace('servers/', ''))
                    else:
                        file_path = os.path.join(self.logs_dir, log_file)
                        zip_file.write(file_path, log_file)
            zip_buffer.seek(0)
            
            if guild_id:
                total_size = sum(
                    os.path.getsize(os.path.join(self.servers_dir, f))
                    for f in log_files
                ) / 1024  # KB
            else:
                total_size = sum(
                    os.path.getsize(os.path.join(self.logs_dir, f)) 
                    for f in log_files
                ) / 1024  # KB
            
            zip_size = len(zip_buffer.getvalue()) / 1024  # KB
            
            stats = {
                'files_count': len(log_files),
                'total_size_kb': total_size,
                'zip_size_kb': zip_size
            }
            
            return zip_buffer, stats
            
        except Exception as e:
            log.error(f"Error creating logs archive: {e}")
            return None, None
    
    def clear_old_logs(self, days_to_keep=7, guild_id=None):
        """Delete log files older than specified days"""
        if guild_id:
            log_files = self.get_server_logs(guild_id)
            base_dir = self.servers_dir
        else:
            log_files = self.get_all_log_files(include_servers=True)
            base_dir = self.logs_dir
        
        if not log_files:
            return 0, 0
        
        current_date = datetime.now()
        deleted_count = 0
        kept_count = 0
        
        for log_file in log_files:
            try:
                date_str = log_file.split('_')[-1].split('.')[0]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                days_old = (current_date - file_date).days
                if days_old > days_to_keep:
                    if guild_id:
                        os.remove(os.path.join(self.servers_dir, log_file))
                    else:
                        file_path = os.path.join(self.logs_dir, log_file)
                        os.remove(file_path)
                    deleted_count += 1
                    log.debug(f"Deleted old log: {log_file} ({days_old} days old)")
                else:
                    kept_count += 1
            except Exception as e:
                log.warning(f"Could not process file {log_file}: {e}")
                kept_count += 1
        
        return deleted_count, kept_count
    
    def get_logs_statistics(self):
        """Get statistics about log files"""
        log_files = self.get_all_log_files()
        
        if not log_files:
            return None
        
        try:
            total_size = sum(
                os.path.getsize(os.path.join(self.logs_dir, f)) 
                for f in log_files
            ) / (1024 * 1024)  # MB
            
            dates = []
            for log_file in log_files:
                try:
                    date_str = log_file.split('_')[1].split('.')[0]
                    dates.append(datetime.strptime(date_str, "%Y%m%d"))
                except:
                    pass
            
            if dates:
                oldest = min(dates).strftime("%Y-%m-%d")
                newest = max(dates).strftime("%Y-%m-%d")
            else:
                oldest = newest = "Unknown"
            
            return {
                'total_files': len(log_files),
                'total_size_mb': total_size,
                'oldest_log': oldest,
                'newest_log': newest
            }
            
        except Exception as e:
            log.error(f"Error calculating statistics: {e}")
            return None
    
    def get_server_logs(self, guild_id):
        """Get all log files for a specific server"""
        if not os.path.exists(self.servers_dir):
            return []
        
        return [f for f in os.listdir(self.servers_dir) if f.startswith(f"{guild_id}_") and f.endswith('.log')]
    
    def get_servers_list(self):
        """Get list of all servers with logs"""
        if not os.path.exists(self.servers_dir):
            return []
        
        servers = set()
        for filename in os.listdir(self.servers_dir):
            if filename.endswith('.log'):
                guild_id = filename.split('_')[0]
                servers.add(guild_id)
        
        return list(servers)
    
    def generate_zip_filename(self, guild_id=None):
        """Generate a timestamped filename for logs archive"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if guild_id:
            return f"lare_logs_{guild_id}_{timestamp}.zip"
        return f"lare_logs_{timestamp}.zip"
