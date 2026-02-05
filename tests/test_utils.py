"""
Tests for Stark Secure Agent Common Utilities

These tests validate the core utility functions.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from common.utils import (
    generate_auth_token,
    hash_password,
    verify_password,
    AgentMessage,
    get_legal_banner
)


class TestSecurityUtils(unittest.TestCase):
    """Test security utility functions"""
    
    def test_generate_auth_token(self):
        """Test token generation"""
        token1 = generate_auth_token()
        token2 = generate_auth_token()
        
        # Tokens should be strings
        self.assertIsInstance(token1, str)
        self.assertIsInstance(token2, str)
        
        # Tokens should be unique
        self.assertNotEqual(token1, token2)
        
        # Default length should be 64 chars (32 bytes in hex)
        self.assertEqual(len(token1), 64)
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "SecurePassword123!"
        
        # Hash the password
        pwd_hash, salt = hash_password(password)
        
        # Hash should be a string
        self.assertIsInstance(pwd_hash, str)
        self.assertIsInstance(salt, str)
        
        # Verify correct password
        self.assertTrue(verify_password(password, pwd_hash, salt))
        
        # Verify incorrect password fails
        self.assertFalse(verify_password("WrongPassword", pwd_hash, salt))
    
    def test_password_hashing_with_same_salt(self):
        """Test that same password and salt produce same hash"""
        password = "TestPassword"
        salt = "fixed_salt_for_testing"
        
        hash1, _ = hash_password(password, salt)
        hash2, _ = hash_password(password, salt)
        
        self.assertEqual(hash1, hash2)


class TestAgentMessage(unittest.TestCase):
    """Test agent message formatting"""
    
    def test_create_message(self):
        """Test message creation"""
        msg = AgentMessage.create(
            AgentMessage.MSG_TYPES['PING'],
            {'status': 'ok'},
            'agent-123'
        )
        
        self.assertIn('type', msg)
        self.assertIn('agent_id', msg)
        self.assertIn('timestamp', msg)
        self.assertIn('data', msg)
        
        self.assertEqual(msg['type'], 'ping')
        self.assertEqual(msg['agent_id'], 'agent-123')
        self.assertEqual(msg['data']['status'], 'ok')
    
    def test_message_validation(self):
        """Test message validation"""
        # Valid message
        valid_msg = {
            'type': 'ping',
            'timestamp': '2025-01-01T00:00:00',
            'data': {}
        }
        self.assertTrue(AgentMessage.is_valid(valid_msg))
        
        # Invalid message (missing fields)
        invalid_msg = {
            'type': 'ping'
        }
        self.assertFalse(AgentMessage.is_valid(invalid_msg))


class TestLegalBanner(unittest.TestCase):
    """Test legal banner"""
    
    def test_legal_banner_exists(self):
        """Test that legal banner is generated"""
        banner = get_legal_banner()
        
        self.assertIsInstance(banner, str)
        self.assertIn("STARK SECURE AGENT", banner)
        self.assertIn("AUTHORIZED USE ONLY", banner)
        self.assertGreater(len(banner), 100)


if __name__ == '__main__':
    unittest.main()
