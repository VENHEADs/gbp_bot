"""Logging configuration for the Telegram bot."""

import logging
import logging.handlers
import os


def setup_logging(log_file: str = 'bot.log', 
                  console_level: int = logging.INFO,
                  file_level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up logging configuration with console and file handlers.
    
    Args:
        log_file: Path to the log file
        console_level: Logging level for console output
        file_level: Logging level for file output
        
    Returns:
        Configured logger instance
    """
    # Get logger for the main module
    logger = logging.getLogger('__main__')
    
    # Prevent Telethon from flooding logs unless it's an error
    logging.getLogger('telethon').setLevel(logging.ERROR)
    
    # Create formatter
    log_formatter = logging.Formatter(
        '[%(levelname)5s/%(asctime)s] %(name)s: %(message)s'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_level)
    
    # File Handler (Rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5MB per file
        backupCount=2
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(file_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return logger 