"""
Configuration Management System
Loads and manages application configuration from YAML files
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration manager"""
    
    _instance: Optional['Config'] = None
    _config_data: Optional[Dict[str, Any]] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config_data is not None:
            return
        
        config_path = Path("config/config.yaml")
        if not config_path.exists():
            logger.warning(f"Config file not found at {config_path}, using defaults")
            self._config_data = self._get_default_config()
        else:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config_data = yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Failed to load config: {e}, using defaults")
                self._config_data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'app': {
                'name': 'BouabidTransfer',
                'version': '1.0.0',
                'log_level': 'INFO'
            },
            'transfer': {
                'buffer_size': 1048576,
                'max_parallel_transfers': 4,
                'enable_checksum': True
            },
            'usb': {'enabled': True},
            'wifi': {'enabled': True},
            'bluetooth': {'enabled': True}
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('transfer.buffer_size')
        """
        keys = key_path.split('.')
        value = self._config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self._config_data
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    @classmethod
    def get_instance(cls) -> 'Config':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_config() -> Config:
    """Convenience function to get config instance"""
    return Config.get_instance()


