# Stark Secure Agent - Installation Guide

## Prerequisites

Before installing Stark Secure Agent, ensure you have:

1. **Authorization**: Written permission to deploy on target systems
2. **Operating System**: Windows 10/11 or Windows Server 2016+
3. **Python**: Version 3.8 or higher
4. **Privileges**: Administrator/root access for installation
5. **Network**: Connectivity between server and agents

## Server Installation

### Step 1: Download and Setup

```bash
# Clone the repository
git clone https://github.com/SIDHANTH-S/exe.git
cd exe

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Server

Edit the server configuration file:

```bash
# Edit config/server_config.json
notepad config/server_config.json  # Windows
nano config/server_config.json     # Linux/Mac
```

Key configuration items:
- `server.host`: IP address to bind (0.0.0.0 for all interfaces)
- `server.port`: Port number (default 8443)
- `security.require_authentication`: Enable/disable auth (always keep enabled)
- `logging.level`: Log verbosity (INFO recommended)

### Step 3: Generate TLS Certificates (Optional but Recommended)

```bash
# Generate self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -keyout config/server_key.pem -out config/server_cert.pem -days 365 -nodes

# For production, use certificates from a trusted CA
```

### Step 4: Start Server

```bash
# Start the server
python src/server/server.py

# Or with environment variables
export STARK_SERVER_HOST=0.0.0.0
export STARK_SERVER_PORT=8443
python src/server/server.py
```

### Step 5: Generate Agent Tokens

From the admin console:

```
stark> generate-token workstation-01
[+] Token generated for workstation-01:
    a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...
[!] Save this token securely - it won't be shown again
```

## Agent Installation

### Step 1: Prepare Target System

On each Windows system to be managed:

```bash
# Copy agent files to target system
# Transfer: src/agent/agent.py, src/common/utils.py, config/agent_config.json

# Or clone repository
git clone https://github.com/SIDHANTH-S/exe.git
cd exe

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Agent

Edit the agent configuration:

```bash
notepad config/agent_config.json
```

Update the following:
- `agent.server_host`: IP/hostname of management server
- `agent.server_port`: Server port (must match server config)
- `security.auth_token`: Token generated from server

Or use environment variables:

```bash
set STARK_SERVER_HOST=192.168.1.100
set STARK_SERVER_PORT=8443
set STARK_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...
```

### Step 3: Test Agent

```bash
# Test run the agent
python src/agent/agent.py

# You should see:
# [*] Agent initialized - ID: HOSTNAME_...
# [*] Server: 192.168.1.100:8443
# [*] Agent started - Ready for administrative tasks
```

### Step 4: Install as Windows Service (Optional)

For production deployments, install as a Windows service:

```bash
# Using NSSM (Non-Sucking Service Manager)
nssm install StarkSecureAgent "C:\path\to\venv\Scripts\python.exe" "C:\path\to\exe\src\agent\agent.py"
nssm set StarkSecureAgent AppDirectory "C:\path\to\exe"
nssm start StarkSecureAgent
```

Or use Task Scheduler for automatic startup:

```bash
# Create scheduled task that runs at startup
schtasks /create /tn "Stark Secure Agent" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\exe\src\agent\agent.py" /sc onstart /ru SYSTEM
```

## Network Configuration

### Firewall Rules

**On Server:**
```bash
# Windows Firewall
netsh advfirewall firewall add rule name="Stark Secure Server" dir=in action=allow protocol=TCP localport=8443

# Linux iptables
sudo iptables -A INPUT -p tcp --dport 8443 -j ACCEPT
```

**On Agents:**
```bash
# Ensure outbound connections to server are allowed
netsh advfirewall firewall add rule name="Stark Secure Agent" dir=out action=allow protocol=TCP remoteport=8443
```

### DNS Configuration

For easier management, configure DNS entries:
- `stark-server.yourdomain.com` → Server IP
- Update agent configs to use hostname instead of IP

## Verification

### Verify Server

1. Server starts without errors
2. Admin console is accessible
3. Can generate agent tokens
4. Logs are being written to `logs/server.log`

### Verify Agent

1. Agent starts without errors
2. Connects to server successfully
3. Appears in server's agent list
4. Can receive and execute commands
5. Logs are being written to `logs/agent.log`

### Test Communication

From server console:

```
stark> list agents
Agent ID                        Hostname             Platform        Status    
--------------------------------------------------------------------------------
WORKSTATION-01_...              WORKSTATION-01       Windows         connected

stark> exec WORKSTATION-01_... "echo Hello from server"
[*] Command sent to WORKSTATION-01_...: echo Hello from server
```

## Troubleshooting

### Common Issues

**Agent can't connect to server:**
- Check network connectivity: `ping server-ip`
- Verify firewall rules
- Ensure server is running
- Check server IP/port in agent config
- Verify authentication token is correct

**Authentication failed:**
- Verify token is correct
- Check token hasn't expired
- Generate new token on server
- Update agent config with new token

**Command execution fails:**
- Verify agent has necessary permissions
- Check command syntax
- Review agent logs for errors
- Ensure command timeout is sufficient

**High resource usage:**
- Adjust monitoring intervals
- Reduce number of concurrent commands
- Check for runaway processes
- Review agent configuration

## Security Checklist

Before deployment, verify:

- [ ] Written authorization obtained
- [ ] Server protected by firewall
- [ ] Strong authentication tokens generated
- [ ] TLS/SSL enabled for production
- [ ] Audit logging enabled
- [ ] Access controls configured
- [ ] IP whitelisting configured (if applicable)
- [ ] Regular backup schedule established
- [ ] Incident response plan documented
- [ ] Administrators trained on proper use

## Next Steps

After installation:

1. Review [Security Best Practices](SECURITY_BEST_PRACTICES.md)
2. Configure logging and monitoring
3. Set up regular maintenance schedule
4. Document deployed agents
5. Train administrators
6. Conduct security assessment
7. Establish backup procedures

## Support

For issues or questions:
- Check documentation in `docs/` folder
- Review logs in `logs/` directory
- Create issue on GitHub repository
- Contact your security team

---

**Remember: Always ensure you have proper authorization before deploying agents on any system.**
