"""
File Utility Functions
Helper functions for file operations, validation, and formatting
"""

import os
from pathlib import Path
from typing import Optional, List
import logging

from src.utils.logger import get_logger

logger = get_logger(__name__)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    Args:
        size_bytes: Size in bytes
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


def ensure_directory(path: str) -> bool:
    """
    Ensure directory exists, create if necessary
    Args:
        path: Directory path
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension (lowercase, without dot)"""
    return Path(filename).suffix.lower().lstrip('.')


def is_supported_photo_format(filename: str) -> bool:
    """Check if file is a supported photo format"""
    photo_extensions = {'.heic', '.heif', '.jpg', '.jpeg', '.png', '.raw', '.cr2', '.nef', '.arw'}
    return get_file_extension(filename) in photo_extensions


def is_supported_video_format(filename: str) -> bool:
    """Check if file is a supported video format"""
    video_extensions = {'.mov', '.mp4', '.m4v', '.avi', '.mkv'}
    return get_file_extension(filename) in video_extensions


def is_supported_document_format(filename: str) -> bool:
    """Check if file is a supported document format"""
    doc_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.7z'}
    return get_file_extension(filename) in doc_extensions


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for Windows filesystem
    Removes invalid characters
    """
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    return sanitized


def get_available_drives() -> List[dict]:
    """
    Get list of available drives (internal and external)
    Returns:
        List of dicts with 'path', 'label', 'type', 'free_space', 'total_space'
    """
    drives = []
    
    try:
        import psutil
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drives.append({
                    'path': partition.mountpoint,
                    'label': partition.device,
                    'type': 'removable' if 'removable' in partition.opts else 'fixed',
                    'free_space': usage.free,
                    'total_space': usage.total
                })
            except PermissionError:
                continue
    except Exception as e:
        logger.error(f"Failed to get drive list: {e}")
    
    return drives


