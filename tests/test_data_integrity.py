"""
Unit tests for Data Integrity Manager
"""

import unittest
import tempfile
import os
from src.core.data_integrity import DataIntegrityManager


class TestDataIntegrityManager(unittest.TestCase):
    """Test cases for DataIntegrityManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = DataIntegrityManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_calculate_checksum(self):
        """Test checksum calculation"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Hello, World!")
        
        checksum = self.manager.calculate_checksum(test_file)
        self.assertIsNotNone(checksum)
        self.assertIsInstance(checksum, str)
        self.assertEqual(len(checksum), 64)  # SHA-256 produces 64 char hex string
    
    def test_verify_checksum(self):
        """Test checksum verification"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Hello, World!")
        
        checksum = self.manager.calculate_checksum(test_file)
        self.assertTrue(self.manager.verify_checksum(test_file, checksum))
        self.assertFalse(self.manager.verify_checksum(test_file, "invalid_checksum"))


if __name__ == '__main__':
    unittest.main()


