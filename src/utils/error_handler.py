"""
Comprehensive Error Handling System
Provides user-friendly error messages and error recovery
"""

from typing import Optional, Dict, Callable
from enum import Enum
import logging

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorCategory(Enum):
    """Error categories for classification"""
    DEVICE_CONNECTION = "device_connection"
    FILE_ACCESS = "file_access"
    TRANSFER_FAILURE = "transfer_failure"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    DATA_INTEGRITY = "data_integrity"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Centralized error handling with user-friendly messages"""
    
    # Error message mappings
    ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
        ErrorCategory.DEVICE_CONNECTION.value: {
            "default": "Unable to connect to your iPhone. Please ensure:\n"
                      "- Your iPhone is connected via USB\n"
                      "- You have trusted this computer on your iPhone\n"
                      "- Your iPhone is unlocked",
            "not_trusted": "Your iPhone is not trusted. Please unlock your iPhone and tap 'Trust This Computer' when prompted.",
            "locked": "Your iPhone is locked. Please unlock your iPhone and try again.",
            "not_found": "iPhone not detected. Please check the USB connection and try again.",
        },
        ErrorCategory.FILE_ACCESS.value: {
            "default": "Unable to access the file. The file may be:\n"
                      "- Protected by iOS\n"
                      "- Currently in use\n"
                      "- Not accessible on this device",
            "permission_denied": "Permission denied. This file may require special access permissions.",
            "not_found": "File not found on the device.",
        },
        ErrorCategory.TRANSFER_FAILURE.value: {
            "default": "Transfer failed. This may be due to:\n"
                      "- Connection interruption\n"
                      "- Insufficient storage space\n"
                      "- File corruption\n\n"
                      "You can try resuming the transfer.",
            "connection_lost": "Connection lost during transfer. The transfer can be resumed.",
            "insufficient_space": "Not enough storage space on the destination drive.",
            "corrupted": "File appears to be corrupted. Please try transferring again.",
        },
        ErrorCategory.PERMISSION_DENIED.value: {
            "default": "Permission denied. Please check:\n"
                      "- File permissions on your iPhone\n"
                      "- Write permissions on the destination folder",
        },
        ErrorCategory.NETWORK_ERROR.value: {
            "default": "Network error occurred. Please check:\n"
                      "- Wi-Fi connection\n"
                      "- Network settings\n"
                      "- Firewall configuration",
        },
        ErrorCategory.DATA_INTEGRITY.value: {
            "default": "Data integrity check failed. The transferred file may be corrupted.\n"
                      "Please try transferring again.",
            "checksum_mismatch": "File checksum verification failed. The file may be corrupted.",
        },
    }
    
    @staticmethod
    def categorize_error(error: Exception) -> ErrorCategory:
        """Categorize an error based on its type and message"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        if "trust" in error_str or "permission" in error_str:
            return ErrorCategory.PERMISSION_DENIED
        elif "connection" in error_str or "connect" in error_str:
            return ErrorCategory.DEVICE_CONNECTION
        elif "file" in error_str or "access" in error_str:
            return ErrorCategory.FILE_ACCESS
        elif "network" in error_str or "wifi" in error_str:
            return ErrorCategory.NETWORK_ERROR
        elif "checksum" in error_str or "integrity" in error_str:
            return ErrorCategory.DATA_INTEGRITY
        elif "transfer" in error_str:
            return ErrorCategory.TRANSFER_FAILURE
        else:
            return ErrorCategory.UNKNOWN
    
    @staticmethod
    def get_user_message(error: Exception, specific_key: Optional[str] = None) -> str:
        """
        Get user-friendly error message
        Args:
            error: Exception object
            specific_key: Optional specific error key
        Returns:
            User-friendly error message
        """
        category = ErrorHandler.categorize_error(error)
        category_messages = ErrorHandler.ERROR_MESSAGES.get(category.value, {})
        
        if specific_key and specific_key in category_messages:
            return category_messages[specific_key]
        
        return category_messages.get("default", f"An error occurred: {str(error)}")
    
    @staticmethod
    def handle_error(error: Exception, context: Optional[str] = None) -> str:
        """
        Handle an error and return user-friendly message
        Args:
            error: Exception object
            context: Optional context information
        Returns:
            User-friendly error message
        """
        # Log the error
        logger.error(f"Error occurred{f' in {context}' if context else ''}: {error}", exc_info=True)
        
        # Get user-friendly message
        user_message = ErrorHandler.get_user_message(error)
        
        return user_message
    
    @staticmethod
    def is_recoverable(error: Exception) -> bool:
        """Check if an error is recoverable (can be retried)"""
        category = ErrorHandler.categorize_error(error)
        recoverable_categories = [
            ErrorCategory.TRANSFER_FAILURE,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.DEVICE_CONNECTION,
        ]
        return category in recoverable_categories


