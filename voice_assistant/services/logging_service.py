"""
Logging service implementation.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from ..config.settings import ConfigManager


class LoggingService:
    """Service for managing application logging."""
    
    def __init__(self, config_manager: ConfigManager, log_dir: str = "logs"):
        self.config_manager = config_manager
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        try:
            # Get log level from config
            log_level = getattr(
                logging,
                self.config_manager.config.settings.log_level.upper(),
                logging.INFO
            )
            
            # Create root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(log_level)
            
            # Clear any existing handlers
            root_logger.handlers.clear()
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            simple_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            
            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "voice_assistant.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(detailed_formatter)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(simple_formatter)
            
            # Add handlers to root logger
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)
            
            # Create application-specific logger
            app_logger = logging.getLogger('voice_assistant')
            app_logger.info("Logging service initialized successfully")
            
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            raise
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance with the specified name."""
        return logging.getLogger(name)
    
    def set_log_level(self, level: str) -> None:
        """Set logging level dynamically."""
        try:
            log_level = getattr(logging, level.upper(), logging.INFO)
            
            # Update all handlers
            root_logger = logging.getLogger()
            root_logger.setLevel(log_level)
            
            for handler in root_logger.handlers:
                handler.setLevel(log_level)
            
            # Update config
            self.config_manager.config.settings.log_level = level.upper()
            self.config_manager.save_config()
            
            logger = logging.getLogger('voice_assistant')
            logger.info(f"Log level changed to: {level.upper()}")
            
        except Exception as e:
            logger = logging.getLogger('voice_assistant')
            logger.error(f"Failed to set log level: {e}")
    
    def add_file_handler(self, filename: str, level: Optional[str] = None) -> logging.FileHandler:
        """Add an additional file handler."""
        try:
            file_path = self.log_dir / filename
            handler = logging.FileHandler(file_path, encoding='utf-8')
            
            # Set level
            if level:
                handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            else:
                handler.setLevel(logging.INFO)
            
            # Set formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            # Add to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            
            logger = logging.getLogger('voice_assistant')
            logger.info(f"Added file handler: {filename}")
            
            return handler
            
        except Exception as e:
            logger = logging.getLogger('voice_assistant')
            logger.error(f"Failed to add file handler: {e}")
            raise
    
    def get_log_files(self) -> list[dict]:
        """Get list of log files with their information."""
        try:
            log_files = []
            
            for log_file in self.log_dir.glob("*.log*"):
                stat = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024*1024), 2),
                    'modified': stat.st_mtime
                })
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            
            return log_files
            
        except Exception as e:
            logger = logging.getLogger('voice_assistant')
            logger.error(f"Failed to get log files: {e}")
            return []
    
    def cleanup_old_logs(self, days_old: int = 30) -> int:
        """Clean up log files older than specified days."""
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            logger = logging.getLogger('voice_assistant')
            logger.info(f"Cleaned up {deleted_count} log files older than {days_old} days")
            
            return deleted_count
            
        except Exception as e:
            logger = logging.getLogger('voice_assistant')
            logger.error(f"Failed to cleanup old logs: {e}")
            return 0
    
    def tail_log(self, lines: int = 50) -> list[str]:
        """Get the last N lines from the main log file."""
        try:
            log_file = self.log_dir / "voice_assistant.log"
            
            if not log_file.exists():
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return [line.rstrip() for line in all_lines[-lines:]]
                
        except Exception as e:
            logger = logging.getLogger('voice_assistant')
            logger.error(f"Failed to tail log: {e}")
            return []