"""
Unit tests for Device Detector
"""

import unittest
from unittest.mock import Mock, patch
from src.core.device_detector import DeviceDetector, DeviceInfo, DeviceConnectionType


class TestDeviceDetector(unittest.TestCase):
    """Test cases for DeviceDetector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = DeviceDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(len(self.detector.devices), 0)
    
    def test_device_detection_callback(self):
        """Test device detection callback registration"""
        callback_called = []
        
        def test_callback(device):
            callback_called.append(device)
        
        self.detector.register_detection_callback(test_callback)
        self.assertIn(test_callback, self.detector.detection_callbacks)
    
    def test_device_removal_callback(self):
        """Test device removal callback registration"""
        callback_called = []
        
        def test_callback(udid):
            callback_called.append(udid)
        
        self.detector.register_removal_callback(test_callback)
        self.assertIn(test_callback, self.detector.removal_callbacks)


if __name__ == '__main__':
    unittest.main()


