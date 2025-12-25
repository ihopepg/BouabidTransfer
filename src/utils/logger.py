"""
Advanced Logging System for BouabidTransfer
Production-grade logging with file rotation and colored output
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
import colorlog


class BouabidLogger:
    """Centralized logging system with file and console handlers"""
    
    _instance: Optional['BouabidLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_file = self.log_dir / "bouabidtransfer.log"
        self.logger = logging.getLogger("BouabidTransfer")
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        self._setup_handlers()
        BouabidLogger._initialized = True
    
    def _setup_handlers(self):
        """Configure file and console handlers"""
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s%(reset)s - %(name)s - %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self, name: str = "BouabidTransfer") -> logging.Logger:
        """Get a logger instance for a specific module"""
        return logging.getLogger(name)
    
    @classmethod
    def get_instance(cls) -> 'BouabidLogger':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_logger(name: str = "BouabidTransfer") -> logging.Logger:
    """Convenience function to get a logger"""
    logger_instance = BouabidLogger.get_instance()
    return logger_instance.get_logger(name)



