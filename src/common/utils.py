"""
Stark Secure Agent - Common Utilities

This module contains common utilities used by both server and agent components.

LEGAL NOTICE: This is a legitimate remote administration tool for authorized use only.
"""

import logging
import hashlib
import secrets
from typing import Dict, Any
from datetime import datetime


class SecurityLogger:
    """Secure logging for audit trails"""
    
    def __init__(self, component: str):
        self.component = component
        self.logger = logging.getLogger(f"StarkSecure.{component}")
        
    def log_auth_attempt(self, user: str, success: bool, ip: str):
        """Log authentication attempts"""
        self.logger.info(
            f"AUTH: user={user}, success={success}, ip={ip}, time={datetime.utcnow().isoformat()}"
        )
        
    def log_command(self, user: str, command: str, target: str):
        """Log command execution"""
        self.logger.info(
            f"CMD: user={user}, target={target}, cmd={command[:100]}, time={datetime.utcnow().isoformat()}"
        )
        
    def log_file_transfer(self, user: str, action: str, filename: str, target: str):
        """Log file transfers"""
        self.logger.info(
            f"FILE: user={user}, action={action}, file={filename}, target={target}, time={datetime.utcnow().isoformat()}"
        )
        
    def log_connection(self, agent_id: str, status: str, ip: str):
        """Log agent connections"""
        self.logger.info(
            f"CONN: agent={agent_id}, status={status}, ip={ip}, time={datetime.utcnow().isoformat()}"
        )


def generate_auth_token(length: int = 32) -> str:
    """Generate a secure random authentication token"""
    return secrets.token_hex(length)


def hash_password(password: str, salt: str = None) -> tuple:
    """Hash a password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return pwd_hash.hex(), salt


def verify_password(password: str, pwd_hash: str, salt: str) -> bool:
    """Verify a password against its hash"""
    test_hash, _ = hash_password(password, salt)
    return test_hash == pwd_hash


class AgentMessage:
    """Standard message format for agent-server communication"""
    
    MSG_TYPES = {
        'PING': 'ping',
        'PONG': 'pong',
        'AUTH': 'auth',
        'CMD': 'command',
        'RESULT': 'result',
        'FILE_UP': 'file_upload',
        'FILE_DOWN': 'file_download',
        'SYSINFO': 'sysinfo',
        'ERROR': 'error'
    }
    
    @staticmethod
    def create(msg_type: str, data: Dict[str, Any], agent_id: str = None) -> Dict[str, Any]:
        """Create a standardized message"""
        return {
            'type': msg_type,
            'agent_id': agent_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
    
    @staticmethod
    def is_valid(message: Dict[str, Any]) -> bool:
        """Validate message format"""
        required_fields = ['type', 'timestamp', 'data']
        return all(field in message for field in required_fields)


def get_legal_banner() -> str:
    """Return the legal authorization banner"""
    return """
╔════════════════════════════════════════════════════════════════════════════╗
║                        STARK SECURE AGENT                                   ║
║              Professional Remote Administration Tool                        ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ⚠️  AUTHORIZED USE ONLY - Legal Notice:                                    ║
║                                                                              ║
║  This system is for authorized administrators only. By proceeding, you      ║
║  certify that you have explicit authorization to access and manage the      ║
║  target systems. Unauthorized access is strictly prohibited and may be      ║
║  subject to legal prosecution.                                              ║
║                                                                              ║
║  All activities are logged and monitored for security and compliance.       ║
║                                                                              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
