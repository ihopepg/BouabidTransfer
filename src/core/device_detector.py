"""
iPhone Device Detection Module
Detects and manages iPhone connections via USB, Wi-Fi, and Bluetooth
"""

import threading
import time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class DeviceConnectionType(Enum):
    """Device connection types"""
    USB = "usb"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    """iPhone device information"""
    udid: str  # Unique Device Identifier
    name: str
    model: str
    ios_version: str
    connection_type: DeviceConnectionType
    is_trusted: bool
    is_locked: bool
    battery_level: Optional[int] = None
    storage_total: Optional[int] = None  # bytes
    storage_free: Optional[int] = None  # bytes
    last_seen: float = 0.0
    
    def __post_init__(self):
        if self.last_seen == 0.0:
            self.last_seen = time.time()


class DeviceDetector:
    """
    Main device detection and management class
    Monitors for iPhone connections across all available channels
    """
    
    def __init__(self):
        self.config = get_config()
        self.devices: Dict[str, DeviceInfo] = {}
        self.detection_callbacks: List[Callable[[DeviceInfo], None]] = []
        self.removal_callbacks: List[Callable[[str], None]] = []
        self._running = False
        self._detection_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Channel-specific detectors
        self.usb_detector = None
        self.wifi_detector = None
        self.bluetooth_detector = None
        
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize channel-specific detection modules"""
        try:
            if self.config.get('usb.enabled', True):
                from src.channels.usb_detector import USBDetector
                self.usb_detector = USBDetector()
                logger.info("USB detector initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize USB detector: {e}")
        
        try:
            if self.config.get('wifi.enabled', True):
                from src.channels.wifi_detector import WiFiDetector
                self.wifi_detector = WiFiDetector()
                logger.info("WiFi detector initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize WiFi detector: {e}")
        
        try:
            if self.config.get('bluetooth.enabled', False):  # Default to False
                from src.channels.bluetooth_detector import BluetoothDetector
                self.bluetooth_detector = BluetoothDetector()
                logger.info("Bluetooth detector initialized")
            else:
                logger.debug("Bluetooth disabled in configuration")
        except Exception as e:
            logger.debug(f"Bluetooth detector not available: {e}")
    
    def start_detection(self):
        """Start continuous device detection"""
        if self._running:
            return
        
        self._running = True
        self._detection_thread = threading.Thread(
            target=self._detection_loop,
            daemon=True,
            name="DeviceDetection"
        )
        self._detection_thread.start()
        logger.info("Device detection started")
    
    def stop_detection(self):
        """Stop device detection"""
        self._running = False
        if self._detection_thread:
            self._detection_thread.join(timeout=5.0)
        logger.info("Device detection stopped")
    
    def _detection_loop(self):
        """Main detection loop running in background thread"""
        interval = self.config.get('transfer.device_detection_interval', 2)
        
        while self._running:
            try:
                self._scan_devices()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(interval)
    
    def _scan_devices(self):
        """Scan all channels for connected devices"""
        detected_devices = {}
        
        # Scan USB
        if self.usb_detector:
            try:
                usb_devices = self.usb_detector.scan()
                for device in usb_devices:
                    detected_devices[device.udid] = device
            except Exception as e:
                # USB errors are handled internally by USBDetector
                # Only log unexpected errors here
                error_str = str(e).lower()
                if "backend" not in error_str:
                    logger.debug(f"USB scan error: {e}")
        
        # Scan Wi-Fi
        if self.wifi_detector:
            try:
                wifi_devices = self.wifi_detector.scan()
                for device in wifi_devices:
                    if device.udid in detected_devices:
                        # Update existing device with additional connection
                        detected_devices[device.udid].connection_type = DeviceConnectionType.USB
                    else:
                        detected_devices[device.udid] = device
            except Exception as e:
                logger.debug(f"WiFi scan error: {e}")
        
        # Scan Bluetooth (only if enabled)
        if self.bluetooth_detector and self.config.get('bluetooth.enabled', False):
            try:
                bt_devices = self.bluetooth_detector.scan()
                for device in bt_devices:
                    if device.udid not in detected_devices:
                        detected_devices[device.udid] = device
            except Exception as e:
                logger.debug(f"Bluetooth scan error: {e}")
        
        # Update device list and notify callbacks
        with self._lock:
            current_udids = set(self.devices.keys())
            new_udids = set(detected_devices.keys())
            
            # New devices
            for udid in new_udids - current_udids:
                device = detected_devices[udid]
                self.devices[udid] = device
                self._notify_device_added(device)
            
            # Removed devices
            for udid in current_udids - new_udids:
                del self.devices[udid]
                self._notify_device_removed(udid)
            
            # Updated devices
            for udid in new_udids & current_udids:
                old_device = self.devices[udid]
                new_device = detected_devices[udid]
                if self._device_changed(old_device, new_device):
                    self.devices[udid] = new_device
                    self._notify_device_added(new_device)
    
    def _device_changed(self, old: DeviceInfo, new: DeviceInfo) -> bool:
        """Check if device information has changed significantly"""
        return (
            old.is_trusted != new.is_trusted or
            old.is_locked != new.is_locked or
            old.connection_type != new.connection_type or
            abs(old.last_seen - new.last_seen) > 10
        )
    
    def _notify_device_added(self, device: DeviceInfo):
        """Notify callbacks about new/updated device"""
        for callback in self.detection_callbacks:
            try:
                callback(device)
            except Exception as e:
                logger.error(f"Error in device detection callback: {e}")
    
    def _notify_device_removed(self, udid: str):
        """Notify callbacks about device removal"""
        for callback in self.removal_callbacks:
            try:
                callback(udid)
            except Exception as e:
                logger.error(f"Error in device removal callback: {e}")
    
    def register_detection_callback(self, callback: Callable[[DeviceInfo], None]):
        """Register callback for device detection events"""
        self.detection_callbacks.append(callback)
    
    def register_removal_callback(self, callback: Callable[[str], None]):
        """Register callback for device removal events"""
        self.removal_callbacks.append(callback)
    
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of currently connected devices"""
        with self._lock:
            return list(self.devices.values())
    
    def get_device(self, udid: str) -> Optional[DeviceInfo]:
        """Get specific device by UDID"""
        with self._lock:
            return self.devices.get(udid)


