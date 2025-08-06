"""
AnonymityEngine - Advanced Tor IP Rotation Tool
Author: zioerenkl | Enhanced by Claude
License: MIT
GitHub: https://github.com/zioerenkl/AnonymityEngine
Description: Professional-grade automated IP rotation using Tor network for Linux
"""

import os
import sys
import time
import json
import signal
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Configuration class
@dataclass
class TorConfig:
    """Configuration settings for Tor IP changer"""
    socks_port: int = 9050
    control_port: int = 9051
    timeout: int = 30
    retry_attempts: int = 3
    log_level: str = "INFO"
    tor_service_name: str = "tor"
    min_interval: int = 10
    max_interval: int = 3600

class TorIPChanger:
    """Main class for managing Tor IP changes"""
    
    def __init__(self, config: TorConfig = None):
        self.config = config or TorConfig()
        self.setup_logging()
        self.ip_check_services = [
            'http://checkip.amazonaws.com',
            'http://ipinfo.io/ip', 
            'http://icanhazip.com',
            'http://httpbin.org/ip'
        ]
        self.current_ip = None
        self.requests = None
        self.session = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/tmp/anonymity_engine.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def ensure_dependencies(self) -> bool:
        """Ensure all required dependencies are installed"""
        try:
            # Try to import requests
            import requests
            self.requests = requests
            
            # Create a session for connection reuse
            self.session = requests.Session()
            
            # Verify socks support
            try:
                import socks
                self.logger.info("✓ All Python dependencies are available")
                return True
            except ImportError:
                self.logger.info("Installing requests[socks]...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'requests[socks]'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    import requests
                    self.requests = requests
                    self.session = requests.Session()
                    self.logger.info("✓ Dependencies installed successfully")
                    return True
                else:
                    self.logger.error(f"Failed to install dependencies: {result.stderr}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error ensuring dependencies: {e}")
            return False
    
    def check_system_requirements(self) -> bool:
        """Check if system requirements are met"""
        # Check if running on Linux
        if sys.platform != 'linux':
            self.logger.error("❌ This tool is designed for Linux systems only")
            return False
        
        # Check if Tor is installed
        try:
            result = subprocess.run(['which', 'tor'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error("❌ Tor is not installed")
                self.logger.info("Please install Tor: sudo apt-get install tor")
                return False
            
            self.logger.info("✓ Tor is installed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking Tor installation: {e}")
            return False
    
    def check_permissions(self) -> bool:
        """Check if we have necessary permissions"""
        # Check if we can control systemctl (might need sudo)
        try:
            result = subprocess.run(['systemctl', 'is-active', self.config.tor_service_name],
                                  capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            # Try with sudo
            try:
                result = subprocess.run(['sudo', '-n', 'systemctl', 'is-active', self.config.tor_service_name],
                                      capture_output=True, text=True)
                self.logger.info("✓ Sudo access available for systemctl")
                return True
            except subprocess.CalledProcessError:
                self.logger.warning("⚠️  Limited permissions - some features may not work")
                return True  # Continue anyway, might work without systemctl
    
    def ensure_tor_running(self) -> bool:
        """Ensure Tor service is running"""
        try:
            # Check if Tor is active
            result = subprocess.run(['systemctl', 'is-active', self.config.tor_service_name],
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip() == 'active':
                self.logger.info("✓ Tor service is running")
                return True
            
            # Try to start Tor service
            self.logger.info("Starting Tor service...")
            try:
                subprocess.run(['sudo', 'systemctl', 'start', self.config.tor_service_name],
                             check=True, timeout=30)
                time.sleep(3)  # Give it time to start
                self.logger.info("✓ Tor service started successfully")
                return True
            except subprocess.CalledProcessError:
                # Try without sudo
                subprocess.run(['systemctl', '--user', 'start', self.config.tor_service_name],
                             check=True, timeout=30)
                time.sleep(3)
                self.logger.info("✓ Tor service started in user mode")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start Tor service: {e}")
            # Try to start Tor manually
            return self._start_tor_manually()
    
    def _start_tor_manually(self) -> bool:
        """Start Tor daemon manually if systemctl fails"""
        try:
            self.logger.info("Attempting to start Tor manually...")
            subprocess.Popen(['tor'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
            return self._test_tor_connection()
        except Exception as e:
            self.logger.error(f"Failed to start Tor manually: {e}")
            return False
    
    def _test_tor_connection(self) -> bool:
        """Test if Tor SOCKS proxy is working"""
        try:
            proxies = {
                'http': f'socks5://127.0.0.1:{self.config.socks_port}',
                'https': f'socks5://127.0.0.1:{self.config.socks_port}'
            }
            
            response = self.session.get('http://checkip.amazonaws.com',
                                      proxies=proxies,
                                      timeout=self.config.timeout)
            if response.status_code == 200:
                self.logger.info("✓ Tor connection is working")
                return True
            return False
            
        except Exception as e:
            self.logger.debug(f"Tor connection test failed: {e}")
            return False
    
    def get_current_ip(self) -> Optional[str]:
        """Get current IP address through Tor"""
        proxies = {
            'http': f'socks5://127.0.0.1:{self.config.socks_port}',
            'https': f'socks5://127.0.0.1:{self.config.socks_port}'
        }
        
        for service in self.ip_check_services:
            for attempt in range(self.config.retry_attempts):
                try:
                    response = self.session.get(service, 
                                              proxies=proxies,
                                              timeout=self.config.timeout)
                    
                    if response.status_code == 200:
                        ip = response.text.strip()
                        # Basic IP validation
                        if self._is_valid_ip(ip):
                            return ip
                            
                except Exception as e:
                    self.logger.debug(f"Attempt {attempt + 1} failed for {service}: {e}")
                    if attempt < self.config.retry_attempts - 1:
                        time.sleep(2)
                    continue
        
        self.logger.error("❌ Failed to get IP from all services")
        return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Basic IP address validation"""
        try:
            # Handle JSON responses (like from httpbin.org/ip)
            if ip.startswith('{'):
                data = json.loads(ip)
                ip = data.get('origin', '').split(',')[0].strip()
            
            # Simple IPv4 validation
            parts = ip.split('.')
            if len(parts) == 4:
                return all(0 <= int(part) <= 255 for part in parts)
            return False
        except (ValueError, json.JSONDecodeError):
            return False
    
    def change_ip(self) -> bool:
        """Change IP by reloading Tor configuration"""
        try:
            # Method 1: Try systemctl reload
            try:
                result = subprocess.run(['sudo', 'systemctl', 'reload', self.config.tor_service_name],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.logger.info("✓ Tor configuration reloaded via systemctl")
                    time.sleep(2)  # Wait for new circuit
                    return True
            except subprocess.CalledProcessError:
                pass
            
            # Method 2: Try service command
            try:
                result = subprocess.run(['sudo', 'service', 'tor', 'reload'],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.logger.info("✓ Tor configuration reloaded via service")
                    time.sleep(2)
                    return True
            except subprocess.CalledProcessError:
                pass
            
            # Method 3: Try sending SIGHUP to tor process
            try:
                result = subprocess.run(['sudo', 'pkill', '-HUP', 'tor'],
                                      capture_output=True, text=True, timeout=10)
                self.logger.info("✓ Sent SIGHUP to Tor process")
                time.sleep(2)
                return True
            except subprocess.CalledProcessError:
                pass
            
            self.logger.warning("⚠️  Could not reload Tor configuration")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to change IP: {e}")
            return False
    
    def validate_input(self, value: str, min_val: int, max_val: int, name: str) -> int:
        """Validate user input"""
        try:
            val = int(value)
            if val < min_val or val > max_val:
                raise ValueError(f"{name} must be between {min_val} and {max_val}")
            return val
        except ValueError as e:
            raise ValueError(f"Invalid {name}: {e}")
    
    def display_banner(self):
        """Display application banner"""
        banner = """
╔════════════════════════════════════════════════════════════════╗
║              🔒 AnonymityEngine v2.0                           ║
║           Advanced Tor IP Rotation Tool                       ║
╠════════════════════════════════════════════════════════════════╣
║  • Professional-grade reliability                             ║
║  • Multiple IP verification services                          ║
║  • Graceful shutdown support                                  ║
║  • Comprehensive logging & monitoring                         ║
║  • Enterprise-level security                                  ║
╚════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def run_interactive(self):
        """Run the tool in interactive mode"""
        self.display_banner()
        
        # Initialize
        if not self.initialize():
            return False
        
        try:
            # Get configuration from user
            print(f"\n🔧 Configuration:")
            print(f"├─ SOCKS proxy: 127.0.0.1:{self.config.socks_port}")
            print(f"├─ Configure your browser/applications to use this proxy")
            print(f"└─ Press Ctrl+C to stop gracefully\n")
            
            # Get current IP
            initial_ip = self.get_current_ip()
            if initial_ip:
                print(f"🌐 Current IP: {initial_ip}")
                self.current_ip = initial_ip
            else:
                print("⚠️  Could not determine current IP")
            
            # Get interval
            while True:
                try:
                    interval_input = input(f"\n⏰ IP change interval in seconds [{self.config.min_interval}-{self.config.max_interval}]: ")
                    interval = self.validate_input(interval_input, self.config.min_interval, self.config.max_interval, "interval")
                    break
                except ValueError as e:
                    print(f"❌ {e}")
            
            # Get number of changes
            while True:
                try:
                    count_input = input("🔄 Number of IP changes (0 for infinite): ")
                    if count_input == "0":
                        count = 0
                        break
                    count = self.validate_input(count_input, 1, 9999, "count")
                    break
                except ValueError as e:
                    print(f"❌ {e}")
            
            # Start changing IPs
            self.running = True
            changes = 0
            
            print(f"\n🚀 Starting IP rotation (interval: {interval}s, count: {'∞' if count == 0 else count})")
            print("=" * 60)
            
            while self.running:
                if count > 0 and changes >= count:
                    break
                
                time.sleep(interval)
                
                if not self.running:
                    break
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔄 Changing IP...")
                
                if self.change_ip():
                    new_ip = self.get_current_ip()
                    if new_ip:
                        if new_ip != self.current_ip:
                            changes += 1
                            print(f"✅ IP changed successfully!")
                            print(f"   Old IP: {self.current_ip or 'Unknown'}")
                            print(f"   New IP: {new_ip}")
                            self.current_ip = new_ip
                        else:
                            print(f"⚠️  IP unchanged: {new_ip}")
                    else:
                        print("❌ Could not verify new IP")
                else:
                    print("❌ Failed to change IP")
                
                if count > 0:
                    remaining = count - changes
                    print(f"📊 Changes: {changes}/{count} (Remaining: {remaining})")
            
            print(f"\n🏁 IP rotation completed. Total changes: {changes}")
            return True
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Graceful shutdown initiated...")
            return True
        except Exception as e:
            self.logger.error(f"Error in interactive mode: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the tool"""
        print("🔍 Initializing...")
        
        # Check system requirements
        if not self.check_system_requirements():
            return False
        
        # Ensure dependencies
        if not self.ensure_dependencies():
            print("❌ Failed to install dependencies")
            return False
        
        # Check permissions
        self.check_permissions()
        
        # Ensure Tor is running
        if not self.ensure_tor_running():
            print("❌ Failed to start Tor service")
            return False
        
        # Test Tor connection
        if not self._test_tor_connection():
            print("❌ Tor connection test failed")
            return False
        
        print("✅ Initialization completed successfully!")
        return True

def main():
    """Main entry point"""
    try:
        # Create configuration
        config = TorConfig()
        
        # Parse command line arguments if needed
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
            print("""
Usage: python3 anonymity_engine.py [options]

Options:
  -h, --help    Show this help message
  
Interactive mode will start if no arguments provided.
Configure your browser/applications to use SOCKS5 proxy: 127.0.0.1:9050
            """)
            return
        
        # Create and run the changer
        changer = TorIPChanger(config)
        success = changer.run_interactive()
        
        if success:
            print("\n👋 Thank you for using Auto Tor IP Changer!")
        else:
            print("\n❌ Tool exited with errors. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
