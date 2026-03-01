import logging
import colorlog
from datetime import datetime
import os


class CustomLogger:
    """
    Custom logger with colors and improved format
    Shows: timestamp, level, module, message
    """
    
    def __init__(self, name="Lare", level=logging.DEBUG):
        self.logger = colorlog.getLogger(name)
        self.logger.setLevel(level)
        
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] [%(levelname)-8s]%(reset)s %(cyan)s[%(name)s]%(reset)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        if not os.path.exists('Lare_Logs'):
            os.makedirs('Lare_Logs')
        
        if not os.path.exists('Lare_Logs/servers'):
            os.makedirs('Lare_Logs/servers')
        
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler = logging.FileHandler(
            f'Lare_Logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """DEBUG level log"""
        self.logger.debug(message)
    
    def info(self, message):
        """INFO level log"""
        self.logger.info(message)
    
    def warning(self, message):
        """WARNING level log"""
        self.logger.warning(message)
    
    def error(self, message):
        """ERROR level log"""
        self.logger.error(message)
    
    def critical(self, message):
        """CRITICAL level log"""
        self.logger.critical(message)
    
    def success(self, message):
        """Log for successful operations (INFO with special format)"""
        self.logger.info(f"✅ {message}")
    
    def failed(self, message):
        """Log for failed operations (ERROR with special format)"""
        self.logger.error(f"❌ {message}")
    
    def server_log(self, guild_id, guild_name, message, level="INFO"):
        """Log message to both main log and server-specific log"""
        formatted_message = f"[Server: {guild_name} ({guild_id})] {message}"
        
        if level == "DEBUG":
            self.logger.debug(formatted_message)
        elif level == "INFO":
            self.logger.info(formatted_message)
        elif level == "WARNING":
            self.logger.warning(formatted_message)
        elif level == "ERROR":
            self.logger.error(formatted_message)
        elif level == "CRITICAL":
            self.logger.critical(formatted_message)
        
        try:
            server_log_file = f'Lare_Logs/servers/{guild_id}_{datetime.now().strftime("%Y%m%d")}.log'
            
            with open(server_log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] [{level.ljust(8)}] {message}\n")
        except Exception as e:
            self.logger.error(f"Failed to write server log: {e}")


log = CustomLogger("Lare")
