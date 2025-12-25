"""
Data Integrity Module
Handles checksum calculation, verification, and transfer validation
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Dict
import json
import logging

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class DataIntegrityManager:
    """Manages data integrity verification for transfers"""
    
    def __init__(self):
        self.config = get_config()
        self.algorithm = self.config.get('transfer.checksum_algorithm', 'sha256')
        self.buffer_size = self.config.get('transfer.buffer_size', 1048576)
        self.checksum_cache: Dict[str, str] = {}
    
    def calculate_checksum(self, file_path: str) -> str:
        """
        Calculate checksum for a file
        Args:
            file_path: Path to file
        Returns:
            Hexadecimal checksum string
        """
        if file_path in self.checksum_cache:
            return self.checksum_cache[file_path]
        
        try:
            hash_obj = hashlib.new(self.algorithm)
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.buffer_size):
                    hash_obj.update(chunk)
            
            checksum = hash_obj.hexdigest()
            self.checksum_cache[file_path] = checksum
            return checksum
            
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            raise
    
    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """
        Verify file checksum
        Args:
            file_path: Path to file
            expected_checksum: Expected checksum value
        Returns:
            True if checksum matches, False otherwise
        """
        try:
            actual_checksum = self.calculate_checksum(file_path)
            match = actual_checksum.lower() == expected_checksum.lower()
            
            if not match:
                logger.warning(
                    f"Checksum mismatch for {file_path}\n"
                    f"Expected: {expected_checksum}\n"
                    f"Actual: {actual_checksum}"
                )
            
            return match
            
        except Exception as e:
            logger.error(f"Failed to verify checksum for {file_path}: {e}")
            return False
    
    def save_checksum(self, file_path: str, checksum: str, checksum_file: Optional[str] = None):
        """
        Save checksum to a file
        Args:
            file_path: Original file path
            checksum: Checksum value
            checksum_file: Optional path to checksum file (default: file_path + .checksum)
        """
        if checksum_file is None:
            checksum_file = f"{file_path}.checksum"
        
        try:
            data = {
                'file': file_path,
                'algorithm': self.algorithm,
                'checksum': checksum
            }
            
            with open(checksum_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved checksum to {checksum_file}")
            
        except Exception as e:
            logger.error(f"Failed to save checksum: {e}")
    
    def load_checksum(self, checksum_file: str) -> Optional[str]:
        """
        Load checksum from file
        Args:
            checksum_file: Path to checksum file
        Returns:
            Checksum value or None if not found
        """
        try:
            with open(checksum_file, 'r') as f:
                data = json.load(f)
                return data.get('checksum')
        except Exception as e:
            logger.debug(f"Failed to load checksum from {checksum_file}: {e}")
            return None
    
    def verify_file_integrity(self, file_path: str, checksum_file: Optional[str] = None) -> bool:
        """
        Verify file integrity using checksum file
        Args:
            file_path: Path to file
            checksum_file: Optional path to checksum file
        Returns:
            True if file is valid, False otherwise
        """
        if checksum_file is None:
            checksum_file = f"{file_path}.checksum"
        
        if not os.path.exists(checksum_file):
            logger.warning(f"Checksum file not found: {checksum_file}")
            return False
        
        expected_checksum = self.load_checksum(checksum_file)
        if not expected_checksum:
            return False
        
        return self.verify_checksum(file_path, expected_checksum)


