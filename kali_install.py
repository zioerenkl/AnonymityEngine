"""
AnonymityEngine - Kali Linux Installer
Author: zioerenkl
GitHub: https://github.com/zioerenkl/AnonymityEngine
Description: Specialized installer for Kali Linux and other Debian-based systems
"""

import os
import sys
import subprocess
from pathlib import Path

class KaliInstaller:
    """Kali Linux specialized installer for AnonymityEngine"""
    
    def __init__(self):
        self.script_name = "anonymity_engine.py"
        self.command_name = "anonymity-engine"
        self.install_dir = Path("/opt/anonymity-engine")
        self.bin_path = Path("/usr/local/bin") / self.command_name
        
    def print_banner(self):
        """Display Kali-specific banner"""
        banner = """
╔════════════════════════════════════════════════════════════════╗
║               🐲 AnonymityEngine - Kali Installer              ║
║              Specialized for Kali Linux & Debian              ║
╠════════════════════════════════════════════════════════════════╣
║  • Uses system package manager (apt)                          ║
║  • Handles externally-managed Python environments             ║
║  • Optimized for penetration testing distributions            ║
╚════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_kali_environment(self):
        """Check if running on Kali or compatible system"""
        print("🔍 Detecting system environment...")
        
        # Check for Kali Linux
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'kali' in content:
                    print("✅ Kali Linux detected")
                    return True
                elif 'debian' in content or 'ubuntu' in content:
                    print("✅ Debian-based system detected")
                    return True
        except FileNotFoundError:
            pass
        
        # Check for apt package manager
        try:
            subprocess.run(['apt', '--version'], capture_output=True, check=True)
            print("✅ APT package manager available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ This installer requires APT package manager")
            return False
    
    def install_system_packages(self):
        """Install packages using apt"""
        print("📦 Installing system packages...")
        
        packages = [
            'tor',                    # Tor daemon
            'python3',                # Python 3
            'python3-pip',            # pip for Python 3
            'python3-requests',       # requests library
            'python3-socks',          # SOCKS support
            'python3-urllib3',        # urllib3
            'python3-certifi',        # SSL certificates
        ]
        
        try:
            # Update package list
            print("   Updating package list...")
            subprocess.run(['apt', 'update'], check=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            
            # Install packages
            print("   Installing packages...")
            cmd = ['apt', 'install', '-y'] + packages
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install packages: {result.stderr}")
                return False
            
            print("✅ System packages installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install system packages: {e}")
            return False
    
    def verify_python_dependencies(self):
        """Verify Python dependencies are available"""
        print("🐍 Verifying Python dependencies...")
        
        try:
            # Test import of required modules
            subprocess.run([
                sys.executable, '-c', 
                'import requests, socks, urllib3, certifi; print("All modules available")'
            ], check=True, capture_output=True)
            
            print("✅ Python dependencies verified")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Python dependencies not available")
            print("   Try: sudo apt install python3-requests python3-socks")
            return False
    
    def create_installation_directory(self):
        """Create installation directory"""
        print(f"📁 Creating installation directory...")
        
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.install_dir.chmod(0o755)
            print("✅ Installation directory created")
            return True
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False
    
    def install_main_script(self):
        """Install the main script"""
        print("📄 Installing main script...")
        
        try:
            source_script = Path(self.script_name)
            if not source_script.exists():
                print(f"❌ Source script '{self.script_name}' not found")
                print("   Make sure you're in the AnonymityEngine directory")
                return False
            
            dest_script = self.install_dir / self.script_name
            import shutil
            shutil.copy2(source_script, dest_script)
            dest_script.chmod(0o755)
            
            print("✅ Main script installed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install script: {e}")
            return False
    
    def create_kali_wrapper(self):
        """Create Kali-optimized wrapper script"""
        print(f"🔗 Creating command wrapper...")
        
        try:
            wrapper_content = f'''#!/bin/bash
# AnonymityEngine - Kali Linux Wrapper
# Optimized for Kali Linux and penetration testing distributions

SCRIPT_DIR="{self.install_dir}"
PYTHON_SCRIPT="$SCRIPT_DIR/{self.script_name}"

# Check if script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: AnonymityEngine script not found"
    echo "   Expected location: $PYTHON_SCRIPT"
    echo "   Try reinstalling with: sudo python3 kali_install.py"
    exit 1
fi

# Check if running as root (common in Kali)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root - this is common in Kali Linux"
    echo "   AnonymityEngine will work with elevated privileges"
fi

# Execute with system Python (avoids venv issues)
exec /usr/bin/python3 "$PYTHON_SCRIPT" "$@"
'''
            
            with open(self.bin_path, 'w') as f:
                f.write(wrapper_content)
            
            self.bin_path.chmod(0o755)
            print("✅ Command wrapper created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create wrapper: {e}")
            return False
    
    def configure_tor_for_kali(self):
        """Configure Tor service for Kali Linux"""
        print("⚙️  Configuring Tor for Kali Linux...")
        
        try:
            # Enable and start Tor
            subprocess.run(['systemctl', 'enable', 'tor'], capture_output=True)
            subprocess.run(['systemctl', 'start', 'tor'], capture_output=True)
            
            # Check status
            result = subprocess.run(['systemctl', 'is-active', 'tor'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip() == 'active':
                print("✅ Tor service configured and running")
            else:
                print("⚠️  Tor service status unclear - may need manual start")
                print("   Try: sudo systemctl start tor")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not configure Tor: {e}")
            print("   You may need to start Tor manually: sudo systemctl start tor")
            return True  # Continue anyway
    
    def test_installation(self):
        """Test the installation"""
        print("🧪 Testing installation...")
        
        try:
            # Test command availability
            result = subprocess.run([str(self.bin_path), '--help'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Installation test passed")
                return True
            else:
                print("⚠️  Installation test had issues")
                print(f"   Output: {result.stderr}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"⚠️  Could not test installation: {e}")
            return True  # Continue anyway
    
    def display_kali_completion(self):
        """Display Kali-specific completion message"""
        print("\n" + "="*60)
        print("🐲 AnonymityEngine installed successfully on Kali Linux!")
        print("="*60)
        
        print(f"\n🚀 Quick Start:")
        print(f"   {self.command_name}")
        
        print(f"\n🔧 Kali-Specific Notes:")
        print(f"   • Uses system Python packages (no venv conflicts)")
        print(f"   • Optimized for root user environment")
        print(f"   • Compatible with Kali's security policies")
        
        print(f"\n🌐 Browser Setup:")
        print(f"   • Firefox: Preferences → Network → Manual Proxy")
        print(f"   • SOCKS Host: 127.0.0.1  Port: 9050")
        print(f"   • Or use: firefox --proxy-server='socks5://127.0.0.1:9050'")
        
        print(f"\n🛠️  Troubleshooting:")
        print(f"   • Start Tor: sudo systemctl start tor")
        print(f"   • Check Tor: sudo systemctl status tor")
        print(f"   • Test proxy: curl --socks5 127.0.0.1:9050 http://checkip.amazonaws.com")
        
        print(f"\n📁 Installation Paths:")
        print(f"   • Main script: {self.install_dir}")
        print(f"   • Command: {self.bin_path}")
        
        print(f"\n🗑️  To uninstall:")
        print(f"   sudo rm -rf {self.install_dir}")
        print(f"   sudo rm {self.bin_path}")
        
        print("\n🎯 Happy penetration testing!")
    
    def install(self):
        """Main installation process for Kali"""
        self.print_banner()
        
        # Check environment
        if not self.check_kali_environment():
            return False
        
        # Install system packages
        if not self.install_system_packages():
            return False
        
        # Verify dependencies
        if not self.verify_python_dependencies():
            return False
        
        # Create installation directory
        if not self.create_installation_directory():
            return False
        
        # Install main script
        if not self.install_main_script():
            return False
        
        # Create wrapper
        if not self.create_kali_wrapper():
            return False
        
        # Configure Tor
        self.configure_tor_for_kali()
        
        # Test installation
        self.test_installation()
        
        # Display completion message
        self.display_kali_completion()
        
        return True
    
    def uninstall(self):
        """Uninstall AnonymityEngine"""
        print("🗑️  Uninstalling AnonymityEngine...")
        
        try:
            import shutil
            
            if self.bin_path.exists():
                self.bin_path.unlink()
                print(f"✅ Removed: {self.bin_path}")
            
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                print(f"✅ Removed: {self.install_dir}")
            
            print("✅ AnonymityEngine uninstalled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during uninstallation: {e}")
            return False

def main():
    """Main entry point"""
    installer = KaliInstaller()
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
AnonymityEngine - Kali Linux Installer

Usage:
  sudo python3 kali_install.py [option]

Options:
  install     Install AnonymityEngine (default)
  uninstall   Remove AnonymityEngine
  -h, --help  Show this help message

This installer is optimized for:
  • Kali Linux
  • Debian-based distributions
  • Systems with externally-managed Python environments

Features:
  • Uses APT package manager
  • Avoids pip conflicts
  • Root-user optimized
  • Penetration testing ready
            """)
            return
        
        elif sys.argv[1] == 'uninstall':
            if installer.uninstall():
                print("\n👋 AnonymityEngine removed successfully!")
            else:
                print("\n❌ Uninstallation failed!")
                sys.exit(1)
            return
    
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This installer must be run with sudo privileges")
        print("   Usage: sudo python3 kali_install.py")
        sys.exit(1)
    
    # Default action: install
    try:
        if installer.install():
            print("\n🎉 Installation completed successfully!")
        else:
            print("\n❌ Installation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Installation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
