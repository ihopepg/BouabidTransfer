"""
Unit tests for Transfer Engine
"""

import unittest
from unittest.mock import Mock, patch
from src.core.transfer_engine import TransferEngine, TransferSession, TransferFile, TransferStatus
from src.core.device_detector import DeviceInfo, DeviceConnectionType


class TestTransferEngine(unittest.TestCase):
    """Test cases for TransferEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = TransferEngine()
        self.test_device = DeviceInfo(
            udid="test_udid",
            name="Test iPhone",
            model="iPhone 15 Pro",
            ios_version="17.0",
            connection_type=DeviceConnectionType.USB,
            is_trusted=True,
            is_locked=False
        )
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.active_sessions), 0)
    
    def test_create_session(self):
        """Test session creation"""
        files = [
            {'source': '/path/to/file1.jpg', 'size': 1024},
            {'source': '/path/to/file2.mp4', 'size': 2048}
        ]
        
        session_id = self.engine.create_session(
            self.test_device,
            files,
            '/destination'
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.engine.active_sessions)
        
        session = self.engine.active_sessions[session_id]
        self.assertEqual(len(session.files), 2)
        self.assertEqual(session.device_udid, self.test_device.udid)


if __name__ == '__main__':
    unittest.main()


