# 🔒 AnonymityEngine - Advanced Tor IP Rotation Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux](https://img.shields.io/badge/platform-linux-green.svg)](https://www.linux.org/)

An advanced, secure, and professional-grade tool for automated IP rotation using the Tor network on Linux systems. Built for penetration testing, privacy research, and educational purposes with enterprise-level reliability.

## 🌟 Key Features

### ✅ **Professional-Grade Improvements:**
- **Robust Error Handling** with automatic retry mechanisms
- **Complete Input Validation** preventing user errors
- **Structured Logging** with multiple detail levels
- **Graceful Shutdown** with signal handling (Ctrl+C)
- **Multiple IP Services** with automatic fallback
- **Secure Installation** with proper file permissions
- **Extended Compatibility** across Linux distributions
- **Enhanced User Interface** with real-time progress tracking

### 🔧 **Technical Features:**
- Secure installation with prerequisite checking
- Automatic Python dependency management
- Custom Tor configuration support
- Automatic connectivity testing
- Multiple fallback methods for Tor service control
- IP validation with JSON response support

## 📋 System Requirements

- **Operating System**: Linux (Ubuntu, Debian, Kali, Arch, etc.)
- **Python**: 3.6 or higher
- **Privileges**: sudo access for installation
- **Network**: Active internet connection

## 🚀 Quick Installation

### 1. **Download Files**
```bash
# Clone the repository
git clone https://github.com/zioerenkl/AnonymityEngine.git
cd AnonymityEngine
```

### 2. **Secure Installation**
```bash
# Run the secure installer with administrator privileges
sudo python3 install.py
```

The installer will:
- ✅ Automatically install Tor if not present
- ✅ Configure necessary Python dependencies
- ✅ Set up proper security permissions
- ✅ Configure Tor service
- ✅ Create global `anonymity-engine` command

### 3. **Verify Installation**
```bash
# Test that the command is available
anonymity-engine --help
```

## 💻 Usage

### **Interactive Mode (Recommended)**
```bash
# Launch the tool in guided mode
anonymity-engine
```

The tool will guide you through:
1. **Proxy Configuration**: Set browser to `127.0.0.1:9050`
2. **Change Interval**: From 10 seconds to 1 hour
3. **Number of Changes**: Defined count or infinite
4. **Real-time Monitoring**: View each IP change live

### **Example Session**
```
🔒 AnonymityEngine v2.0 - Advanced Tor IP Rotation
🔍 Initializing...
✅ Initialization completed successfully!

🔧 Configuration:
├─ SOCKS proxy: 127.0.0.1:9050
├─ Configure your browser/applications to use this proxy
└─ Press Ctrl+C to stop gracefully

🌐 Current IP: 185.220.101.45

⏰ IP change interval in seconds [10-3600]: 30
🔄 Number of IP changes (0 for infinite): 5

🚀 Starting IP rotation (interval: 30s, count: 5)
============================================================

[14:23:15] 🔄 Changing IP...
✅ IP changed successfully!
   Old IP: 185.220.101.45
   New IP: 199.87.154.255
📊 Changes: 1/5 (Remaining: 4)
```

## ⚙️ Browser Configuration

### **Firefox**
1. Go to `Preferences → Network Settings`
2. Select `Manual proxy configuration`
3. SOCKS Host: `127.0.0.1` Port: `9050`
4. Select `SOCKS v5`

### **Chrome/Chromium**
```bash
# Launch Chrome with Tor proxy
google-chrome --proxy-server="socks5://127.0.0.1:9050"
```

### **Command Line Tools**
```bash
# Test with curl
curl --socks5 127.0.0.1:9050 http://checkip.amazonaws.com

# Test with wget
wget --proxy=on --socks5-hostname=127.0.0.1:9050 -qO- http://checkip.amazonaws.com
```

## 🔧 Advanced Configuration

### **Configuration File** (Optional)
Create `/opt/anonymity-engine/config.json` for advanced customizations:

```json
{
  "tor_config": {
    "socks_port": 9050,
    "control_port": 9051,
    "timeout": 30,
    "retry_attempts": 3,
    "min_interval": 10,
    "max_interval": 3600
  },
  "ip_check_services": [
    "http://checkip.amazonaws.com",
    "http://ipinfo.io/ip",
    "http://icanhazip.com",
    "http://httpbin.org/ip"
  ],
  "logging": {
    "level": "INFO",
    "file": "/tmp/anonymity_engine.log",
    "max_size_mb": 10
  },
  "security": {
    "validate_ssl": true,
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
  }
}
```

### **Customizable Parameters**
- **SOCKS Port**: Change proxy port (default: 9050)
- **Timeout**: HTTP request timeout (default: 30s)
- **IP Services**: Customizable list of IP check services
- **Logging**: Levels: DEBUG, INFO, WARNING, ERROR

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### ❌ "Tor service is not running"
```bash
# Manually restart Tor service
sudo systemctl restart tor
sudo systemctl status tor
```

#### ❌ "Connection refused on port 9050"
```bash
# Check if port is in use
netstat -tlnp | grep 9050

# If occupied, change port in config
sudo nano /etc/tor/torrc
# Add: SocksPort 9051
```

#### ❌ "Permission denied"
```bash
# Reinstall with correct permissions
sudo python3 install.py uninstall
sudo python3 install.py install
```

#### ❌ "Could not determine current IP"
```bash
# Manual Tor connectivity test
curl --socks5 127.0.0.1:9050 http://checkip.amazonaws.com

# If it fails, restart Tor
sudo systemctl restart tor
```

### **System Status Verification**
```bash
# Check Tor service
systemctl status tor

# Check listening ports
ss -tlnp | grep 9050

# Test connectivity
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip
```

## 📊 Logging & Monitoring

### **Log Files**
- **Location**: `/tmp/anonymity_engine.log`
- **Format**: Timestamp - Level - Message
- **Rotation**: Automatic when file exceeds 10MB

### **Example Log Output**
```
2024-01-15 14:23:12 - INFO - ✓ Tor service is running
2024-01-15 14:23:15 - INFO - ✓ IP changed: 185.220.101.45 → 199.87.154.255
2024-01-15 14:23:45 - WARNING - ⚠️ Retry attempt 1/3 for IP check
2024-01-15 14:24:00 - ERROR - ❌ Failed to change IP after 3 attempts
```

## 🛡️ Security & Privacy

### **Security Considerations**
- ✅ **Minimal Privileges**: Tool requires only necessary permissions
- ✅ **Input Sanitization**: Complete user input validation
- ✅ **Secure Logging**: No sensitive information in logs
- ✅ **Clean Installation**: Complete removal with uninstall

### **Privacy Limitations**
- ⚠️ **DNS Leaks**: Configure DNS to 127.0.0.1:53 to prevent leaks
- ⚠️ **WebRTC**: Disable WebRTC in browser to avoid IP leaks
- ⚠️ **Browser Storage**: Regularly clear cookies and storage

### **Best Practices**
1. **Always use HTTPS** when possible
2. **Disable JavaScript** for maximum anonymity
3. **Avoid personal logins** while using Tor
4. **Change browser User-Agent** to reduce fingerprinting

## 📁 File Structure

```
/opt/anonymity-engine/
├── anonymity_engine.py      # Main script
├── config.json              # Configuration (optional)
└── README.md                # Documentation

/usr/local/bin/
└── anonymity-engine         # Global command wrapper

/tmp/
└── anonymity_engine.log     # Log file
```

## 🗑️ Uninstallation

### **Complete Removal**
```bash
# Remove the tool completely
sudo python3 install.py uninstall
```

Uninstallation removes:
- ✅ Executable files and scripts
- ✅ Installation directory
- ✅ Global command wrapper
- ✅ Configuration files
- ❗ **Does NOT remove**: Tor (may be used by other software)

## ⚖️ Legal Considerations

### **Legal Use**
- ✅ **Tor is legal** in most countries
- ✅ **Privacy protection** is a fundamental right
- ✅ **Research and testing** in controlled environments

### **Responsibility**
- ❗ **User is responsible** for how they use this tool
- ❗ **Comply with local laws** in your jurisdiction
- ❗ **Do not use for illegal activities**

### **Disclaimer**
This tool is provided for educational and research purposes. The authors are not responsible for misuse of the software.

## 🤝 Contributing

### **Contributions Welcome**
- 🐛 **Bug Reports**: Submit issues via GitHub Issues
- 💡 **Feature Requests**: Suggest new functionality
- 🔧 **Pull Requests**: Contribute improved code

### **Development Setup**
```bash
# Clone repository for development
git clone https://github.com/zioerenkl/AnonymityEngine.git
cd AnonymityEngine

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Support

If you encounter issues:

1. **Check logs**: `/tmp/anonymity_engine.log`
2. **Verify prerequisites**: Python 3.6+, Tor installed
3. **Test connectivity**: `curl --socks5 127.0.0.1:9050 http://checkip.amazonaws.com`
4. **Create issue**: Submit GitHub issue with detailed logs

## 🚀 Roadmap

### **Planned Features**
- [ ] GUI interface with web dashboard
- [ ] Docker containerization support
- [ ] Windows/macOS compatibility layer
- [ ] Advanced circuit control via Tor Controller
- [ ] Integration with VPN services
- [ ] Scheduled IP rotation profiles

## 📈 Stats

- **⭐ Stars**: Help us reach 1000 stars!
- **🍴 Forks**: Join the development community
- **🐛 Issues**: Help us improve by reporting bugs
- **📝 Commits**: Active development and maintenance

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for complete details.

---

## 🏆 Acknowledgments

- **Original inspiration**: FDX100's Auto_Tor_IP_changer
- **Tor Project**: For providing the anonymity network
- **Python Community**: For excellent libraries and tools
- **Security Researchers**: For privacy and anonymity advocacy

---

**🎉 Thank you for choosing AnonymityEngine!**

*Built with focus on security, reliability, and professional-grade performance.*

---

### 📌 Quick Links

- **🏠 Homepage**: https://github.com/zioerenkl/AnonymityEngine
- **📚 Documentation**: [Wiki](https://github.com/zioerenkl/AnonymityEngine/wiki)
- **🐛 Issues**: [Bug Reports](https://github.com/zioerenkl/AnonymityEngine/issues)
- **💬 Discussions**: [Community](https://github.com/zioerenkl/AnonymityEngine/discussions)
- **🔒 Security**: [Security Policy](https://github.com/zioerenkl/AnonymityEngine/security)

**Star ⭐ this repository if you find it useful!**
