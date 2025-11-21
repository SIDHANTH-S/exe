"""
Stark Secure Agent - Server Component

This module implements the central management server for the remote administration tool.

LEGAL NOTICE: This is a legitimate remote administration tool for authorized use only.
Only use to manage systems you own or have explicit written permission to administer.
"""

import os
import sys
import json
import socket
import threading
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.utils import SecurityLogger, AgentMessage, generate_auth_token, get_legal_banner


class StarkServer:
    """Main server class for remote administration management"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8443):
        """
        Initialize the Stark Secure Server
        
        Args:
            host: IP address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.logger = SecurityLogger("Server")
        self.agents: Dict[str, Dict] = {}
        self.running = False
        self.auth_tokens = {}
        
        print(get_legal_banner())
        print(f"[*] Server initialized")
        print(f"[*] Listening on: {host}:{port}")
        
    def generate_agent_token(self, agent_name: str) -> str:
        """Generate authentication token for a new agent"""
        token = generate_auth_token()
        self.auth_tokens[token] = {
            'agent_name': agent_name,
            'created': datetime.utcnow().isoformat(),
            'active': True
        }
        self.logger.logger.info(f"Generated token for agent: {agent_name}")
        return token
    
    def register_agent(self, agent_id: str, agent_info: Dict):
        """Register a new agent connection"""
        self.agents[agent_id] = {
            'info': agent_info,
            'connected': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat(),
            'status': 'connected'
        }
        self.logger.log_connection(
            agent_id, 
            "registered", 
            agent_info.get('ip', 'unknown')
        )
        print(f"[+] Agent registered: {agent_id}")
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return [
            {
                'agent_id': agent_id,
                'hostname': data['info'].get('hostname', 'unknown'),
                'platform': data['info'].get('platform', 'unknown'),
                'status': data['status'],
                'connected': data['connected'],
                'last_seen': data['last_seen']
            }
            for agent_id, data in self.agents.items()
        ]
    
    def send_command(self, agent_id: str, command: str, shell: str = "cmd") -> bool:
        """
        Send a command to an agent
        
        Args:
            agent_id: Target agent identifier
            command: Command to execute
            shell: Shell type (cmd or powershell)
            
        Returns:
            True if command was sent successfully
        """
        if agent_id not in self.agents:
            print(f"[-] Agent {agent_id} not found")
            return False
        
        self.logger.log_command("admin", command, agent_id)
        
        # Placeholder: In real implementation, this would send command via secure channel
        print(f"[*] Command sent to {agent_id}: {command}")
        return True
    
    def start(self):
        """Start the server"""
        self.running = True
        print("[*] Server started - Ready to accept agent connections")
        print("[*] Authorized administrators may connect to manage remote systems")
        print("[!] All activities are logged for security and compliance")
        print("[!] Press Ctrl+C to stop")
        
        # Placeholder: In real implementation, this would start listening socket
        self.logger.logger.info("Server started")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        self.logger.logger.info("Server stopped")
        print("[*] Server stopped")


class AdminConsole:
    """Interactive console for server administration"""
    
    def __init__(self, server: StarkServer):
        self.server = server
        self.running = False
    
    def print_help(self):
        """Print available commands"""
        print("\nStark Secure Agent - Admin Console")
        print("=" * 60)
        print("Available Commands:")
        print("  list agents          - List all connected agents")
        print("  exec <id> <cmd>      - Execute command on agent")
        print("  sysinfo <id>         - Get system information from agent")
        print("  generate-token <name> - Generate auth token for new agent")
        print("  help                 - Show this help message")
        print("  exit                 - Exit the console")
        print("=" * 60)
    
    def start(self):
        """Start the interactive console"""
        self.running = True
        print(get_legal_banner())
        print("\n[*] Admin Console - Type 'help' for commands")
        
        while self.running:
            try:
                command = input("\nstark> ").strip()
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                
                if cmd == "exit" or cmd == "quit":
                    self.running = False
                    print("[*] Exiting console...")
                    
                elif cmd == "help":
                    self.print_help()
                    
                elif cmd == "list" and len(parts) > 1 and parts[1] == "agents":
                    agents = self.server.list_agents()
                    if agents:
                        print(f"\n{'Agent ID':<30} {'Hostname':<20} {'Platform':<15} {'Status':<10}")
                        print("-" * 80)
                        for agent in agents:
                            print(f"{agent['agent_id']:<30} {agent['hostname']:<20} "
                                  f"{agent['platform']:<15} {agent['status']:<10}")
                    else:
                        print("No agents connected")
                        
                elif cmd == "generate-token" and len(parts) > 1:
                    agent_name = parts[1]
                    token = self.server.generate_agent_token(agent_name)
                    print(f"[+] Token generated for {agent_name}:")
                    print(f"    {token}")
                    print(f"[!] Save this token securely - it won't be shown again")
                    
                elif cmd == "exec":
                    if len(parts) < 2:
                        print("Usage: exec <agent-id> <command>")
                    else:
                        args = parts[1].split(maxsplit=1)
                        if len(args) < 2:
                            print("Usage: exec <agent-id> <command>")
                        else:
                            agent_id, command = args
                            self.server.send_command(agent_id, command)
                            
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n[!] Use 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point for the server"""
    print(get_legal_banner())
    
    # In production, these would come from config file or command line args
    host = os.getenv("STARK_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("STARK_SERVER_PORT", "8443"))
    
    server = StarkServer(host, port)
    
    try:
        server.start()
        
        # Start admin console
        console = AdminConsole(server)
        console.start()
        
    except KeyboardInterrupt:
        print("\n[!] Shutdown requested...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
