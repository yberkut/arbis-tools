import unittest
import os
from luks_key_manager import store_key, retrieve_key, init_db

MASTER_PASSWORD = b"super_secure_password"
TEST_KEY_NAME = "test_key"
TEST_LUKS_KEY = os.urandom(32)  # Random 32-byte LUKS key


class TestLuksKeyManager(unittest.TestCase):

    def setUp(self):
        """Initialize database before each test."""
        init_db()

    def test_store_and_retrieve_key(self):
        """Ensure keys can be stored and retrieved correctly."""
        store_key(TEST_KEY_NAME, TEST_LUKS_KEY, MASTER_PASSWORD)
        retrieved_key = retrieve_key(TEST_KEY_NAME, MASTER_PASSWORD)
        self.assertEqual(TEST_LUKS_KEY, retrieved_key)

    def test_wrong_password(self):
        """Ensure retrieval fails with the wrong password."""
        store_key(TEST_KEY_NAME, TEST_LUKS_KEY, MASTER_PASSWORD)
        with self.assertRaises(Exception):
            retrieve_key(TEST_KEY_NAME, b"wrong_password")


if __name__ == "__main__":
    unittest.main()
