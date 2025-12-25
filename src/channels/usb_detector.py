"""
USB Device Detection Module
Detects iPhone devices connected via USB
"""

try:
    import usb.core
    import usb.util
    import usb.backend.libusb1
    USB_AVAILABLE = True
except (ImportError, OSError):
    USB_AVAILABLE = False

from typing import List, Optional
import logging

from src.utils.logger import get_logger
from src.core.device_detector import DeviceInfo, DeviceConnectionType

logger = get_logger(__name__)

# Apple Vendor ID
APPLE_VENDOR_ID = 0x05AC

# iPhone Product IDs (common models)
IPHONE_PRODUCT_IDS = {
    0x12A8: "iPhone 6",
    0x12AA: "iPhone 6 Plus",
    0x12AB: "iPhone 6s",
    0x12AC: "iPhone 6s Plus",
    0x12AD: "iPhone SE",
    0x12AE: "iPhone 7",
    0x12AF: "iPhone 7 Plus",
    0x12B0: "iPhone 8",
    0x12B1: "iPhone 8 Plus",
    0x12B2: "iPhone X",
    0x12B3: "iPhone XS",
    0x12B4: "iPhone XS Max",
    0x12B5: "iPhone XR",
    0x12B6: "iPhone 11",
    0x12B7: "iPhone 11 Pro",
    0x12B8: "iPhone 11 Pro Max",
    0x12B9: "iPhone SE (2nd gen)",
    0x12BA: "iPhone 12",
    0x12BB: "iPhone 12 mini",
    0x12BC: "iPhone 12 Pro",
    0x12BD: "iPhone 12 Pro Max",
    0x12BE: "iPhone 13",
    0x12BF: "iPhone 13 mini",
    0x12C0: "iPhone 13 Pro",
    0x12C1: "iPhone 13 Pro Max",
    0x12C2: "iPhone SE (3rd gen)",
    0x12C3: "iPhone 14",
    0x12C4: "iPhone 14 Plus",
    0x12C5: "iPhone 14 Pro",
    0x12C6: "iPhone 14 Pro Max",
    0x12C7: "iPhone 15",
    0x12C8: "iPhone 15 Plus",
    0x12C9: "iPhone 15 Pro",
    0x12CA: "iPhone 15 Pro Max",
    0x12CB: "iPhone 16",
    0x12CC: "iPhone 16 Plus",
    0x12CD: "iPhone 16 Pro",
    0x12CE: "iPhone 16 Pro Max",
    0x12CF: "iPhone 17",
    0x12D0: "iPhone 17 Plus",
    0x12D1: "iPhone 17 Pro",
    0x12D2: "iPhone 17 Pro Max",
}


class USBDetector:
    """Detects iPhone devices via USB"""
    
    def __init__(self):
        self.devices: List[DeviceInfo] = []
        self._backend_warning_logged = False
    
    def scan(self) -> List[DeviceInfo]:
        """
        Scan for USB-connected iPhone devices
        Returns list of detected DeviceInfo objects
        """
        detected_devices = []
        
        # Check if USB is available
        if not USB_AVAILABLE:
            if not self._backend_warning_logged:
                logger.debug("USB library not available. USB detection disabled.")
                self._backend_warning_logged = True
            return detected_devices
        
        try:
            # Check if backend is available
            try:
                backend = usb.backend.libusb1.get_backend()
                if backend is None:
                    if not self._backend_warning_logged:
                        logger.debug("USB backend (libusb) not installed. USB detection disabled.")
                        logger.debug("Note: This is normal. USB detection requires libusb driver.")
                        self._backend_warning_logged = True
                    return detected_devices
            except Exception:
                if not self._backend_warning_logged:
                    logger.debug("USB backend not available. USB detection disabled.")
                    self._backend_warning_logged = True
                return detected_devices
            
            # Find all Apple devices
            devices = usb.core.find(find_all=True, idVendor=APPLE_VENDOR_ID)
            
            for device in devices:
                try:
                    product_id = device.idProduct
                    model = IPHONE_PRODUCT_IDS.get(product_id, f"iPhone (Unknown Model)")
                    
                    # Try to get serial number (UDID)
                    try:
                        # This requires proper USB configuration
                        # For now, use a combination of vendor/product/serial
                        udid = self._get_device_udid(device)
                    except Exception:
                        udid = f"USB_{product_id:04X}_{device.bus}_{device.address}"
                    
                    device_info = DeviceInfo(
                        udid=udid,
                        name=model,
                        model=model,
                        ios_version="Unknown",  # Would need libimobiledevice to get this
                        connection_type=DeviceConnectionType.USB,
                        is_trusted=False,  # Would need to check with device
                        is_locked=False  # Would need to check with device
                    )
                    
                    detected_devices.append(device_info)
                    logger.debug(f"Detected USB device: {model} ({udid})")
                    
                except Exception as e:
                    logger.debug(f"Error processing USB device: {e}")
                    continue
        
        except usb.core.NoBackendError:
            # No USB backend available - expected on Windows without libusb
            if not self._backend_warning_logged:
                logger.debug("USB backend not available. Install libusb for USB device detection.")
                self._backend_warning_logged = True
        except Exception as e:
            # Only log actual errors, not expected "no backend" messages
            error_str = str(e).lower()
            if "backend" not in error_str and "no backend" not in error_str:
                if not self._backend_warning_logged or "backend" not in error_str:
                    logger.debug(f"USB scan: {e}")
        
        self.devices = detected_devices
        return detected_devices
    
    def _get_device_udid(self, device) -> str:
        """
        Get device UDID from USB device
        This is a simplified version - full implementation would use
        libimobiledevice or pymobiledevice3
        """
        try:
            # Try to read device descriptor
            # In production, this would use libimobiledevice
            serial = usb.util.get_string(device, device.iSerialNumber)
            if serial:
                return serial
        except Exception:
            pass
        
        # Fallback: generate UDID from device identifiers
        return f"USB_{device.idVendor:04X}_{device.idProduct:04X}_{device.bus}_{device.address}"

