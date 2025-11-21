"""
Stark Secure Agent - Agent Component

This module implements the agent that runs on managed Windows systems.

LEGAL NOTICE: This is a legitimate remote administration tool for authorized use only.
Deploy only on systems you own or have explicit written permission to manage.
"""

import os
import sys
import platform
import socket
import subprocess
import psutil
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.utils import SecurityLogger, AgentMessage, get_legal_banner


class StarkAgent:
    """Main agent class for remote administration"""
    
    def __init__(self, server_host: str, server_port: int, auth_token: str):
        """
        Initialize the Stark Secure Agent
        
        Args:
            server_host: IP/hostname of the management server
            server_port: Port number of the management server
            auth_token: Authentication token for secure connection
        """
        self.server_host = server_host
        self.server_port = server_port
        self.auth_token = auth_token
        self.agent_id = self._generate_agent_id()
        self.logger = SecurityLogger("Agent")
        self.running = False
        
        print(get_legal_banner())
        print(f"[*] Agent initialized - ID: {self.agent_id}")
        print(f"[*] Server: {server_host}:{server_port}")
        print(f"[*] System: {platform.system()} {platform.release()}")
        
    def _generate_agent_id(self) -> str:
        """Generate unique agent identifier based on system info"""
        hostname = socket.gethostname()
        mac = ':'.join(['{:02x}'.format((int(time.time()) >> i) & 0xff) for i in range(0, 48, 8)])
        return f"{hostname}_{mac}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Collect system information for monitoring"""
        info = {
            'agent_id': self.agent_id,
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': {},
            'network_interfaces': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Disk information
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info['disk_usage'][partition.device] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except:
                pass
        
        # Network interfaces
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    info['network_interfaces'].append({
                        'interface': iface,
                        'ip': addr.address
                    })
        
        return info
    
    def execute_command(self, command: str, shell: str = "cmd") -> Dict[str, Any]:
        """
        Execute a command on the system
        
        Args:
            command: Command to execute
            shell: Shell type (cmd or powershell)
            
        Returns:
            Dictionary with execution results
        """
        self.logger.log_command("server", command, self.agent_id)
        
        try:
            if shell.lower() == "powershell":
                cmd = ["powershell", "-Command", command]
            else:
                cmd = ["cmd", "/c", command]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                shell=False
            )
            
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'timestamp': datetime.utcnow().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command execution timeout',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def start(self):
        """Start the agent (placeholder for connection logic)"""
        self.running = True
        print("[*] Agent started - Ready for administrative tasks")
        print("[*] Awaiting commands from authorized management server...")
        print("[!] Press Ctrl+C to stop")
        
        # Placeholder: In a real implementation, this would establish
        # encrypted connection to server and await commands
        self.logger.log_connection(self.agent_id, "connected", self.server_host)
        
    def stop(self):
        """Stop the agent"""
        self.running = False
        self.logger.log_connection(self.agent_id, "disconnected", self.server_host)
        print("[*] Agent stopped")


def main():
    """Main entry point for the agent"""
    print(get_legal_banner())
    
    # In production, these would come from config file or command line args
    server_host = os.getenv("STARK_SERVER_HOST", "127.0.0.1")
    server_port = int(os.getenv("STARK_SERVER_PORT", "8443"))
    auth_token = os.getenv("STARK_AUTH_TOKEN", "development_token")
    
    agent = StarkAgent(server_host, server_port, auth_token)
    
    try:
        agent.start()
        
        # Demo: Execute a simple system info command
        print("\n[*] Demo: Collecting system information...")
        sysinfo = agent.get_system_info()
        print(f"[+] System: {sysinfo['platform']} {sysinfo['platform_release']}")
        print(f"[+] CPU: {sysinfo['cpu_count']} cores, {sysinfo['cpu_percent']}% usage")
        print(f"[+] Memory: {sysinfo['memory_percent']}% used")
        
        # Keep running
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[!] Shutdown requested...")
    finally:
        agent.stop()


if __name__ == "__main__":
    main()
