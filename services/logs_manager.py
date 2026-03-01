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
    
    def get_today_log_file(self):
        """Get today's log file path and info"""
        today = datetime.now().strftime("%Y%m%d")
        log_file = f"{self.logs_dir}/bot_{today}.log"
        
        if not os.path.exists(log_file):
            return None, None
        
        file_size = os.path.getsize(log_file) / 1024  # KB
        return log_file, file_size
    
    def get_all_log_files(self):
        """Get all log files in directory"""
        if not os.path.exists(self.logs_dir):
            return []
        
        return [f for f in os.listdir(self.logs_dir) if f.endswith('.log')]
    
    def create_logs_archive(self):
        """Create a zip archive with all log files"""
        log_files = self.get_all_log_files()
        
        if not log_files:
            return None, None
        
        try:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for log_file in log_files:
                    file_path = os.path.join(self.logs_dir, log_file)
                    zip_file.write(file_path, log_file)
            zip_buffer.seek(0)
            
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
    
    def clear_old_logs(self, days_to_keep=7):
        """Delete log files older than specified days"""
        log_files = self.get_all_log_files()
        
        if not log_files:
            return 0, 0
        
        current_date = datetime.now()
        deleted_count = 0
        kept_count = 0
        
        for log_file in log_files:
            try:
                date_str = log_file.split('_')[1].split('.')[0]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                days_old = (current_date - file_date).days
                if days_old > days_to_keep:
                    os.remove(os.path.join(self.logs_dir, log_file))
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
    
    def generate_zip_filename(self):
        """Generate a timestamped filename for logs archive"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"lare_logs_{timestamp}.zip"
