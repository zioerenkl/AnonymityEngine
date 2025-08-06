#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure Installer for AnonymityEngine
Author: zioerenkl | Enhanced by Claude
GitHub: https://github.com/zioerenkl/AnonymityEngine
Description: Safe installation script with proper permissions and validation
"""

import os
import sys
import shutil
import subprocess
import stat
from pathlib import Path

class SecureInstaller:
    """Secure installer for AnonymityEngine"""
    
    def __init__(self):
        self.script_name = "anonymity_engine.py"
        self.command_name = "anonymity-engine"
        self.install_dir = Path("/opt/anonymity-engine")
        self.bin_path = Path("/usr/local/bin") / self.command_name
        
    def check_prerequisites(self) -> bool:
        """Check if system meets prerequisites"""
        print("🔍 Checking prerequisites...")
        
        # Check if running on Linux
        if sys.platform != 'linux':
            print("❌ This installer only works on Linux systems")
            return False
        
        # Check if running as root/sudo
        if os.geteuid() != 0:
            print("❌ This installer must be run with sudo privileges")
            print("   Usage: sudo python3 install.py")
            return False
        
        # Check if Python 3.6+ is available
        if sys.version_info < (3, 6):
            print("❌ Python 3.6 or higher is required")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def install_system_dependencies(self) -> bool:
        """Install required system packages"""
        print("📦 Installing system dependencies...")
        
        try:
            # Update package list
            print("   Updating package list...")
            subprocess.run(['apt-get', 'update'], 
                          check=True, 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.STDOUT)
            
            # Install Tor
            print("   Installing Tor...")
            result = subprocess.run(['apt-get', 'install', '-y', 'tor'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install Tor: {result.stderr}")
                return False
            
            # Install Python pip if not present
            print("   Ensuring pip is installed...")
            subprocess.run(['apt-get', 'install', '-y', 'python3-pip'], 
                          capture_output=True)
            
            print("✅ System dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install system dependencies: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        print("🐍 Installing Python dependencies...")
        
        try:
            # Try method 1: Regular pip install
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'requests[socks]', '--upgrade'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Python dependencies installed")
                return True
            
            # Check if it's externally-managed-environment error (Kali Linux, etc.)
            if "externally-managed-environment" in result.stderr.lower():
                print("⚠️  Detected externally-managed Python environment (Kali Linux)")
                print("   Trying alternative installation methods...")
                
                # Method 2: Try with --break-system-packages (risky but works)
                print("   Attempting installation with --break-system-packages...")
                result2 = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    'requests[socks]', '--upgrade', '--break-system-packages'
                ], capture_output=True, text=True)
                
                if result2.returncode == 0:
                    print("✅ Python dependencies installed (with --break-system-packages)")
                    return True
                
                # Method 3: Try system package manager
                print("   Trying system package manager (apt)...")
                try:
                    subprocess.run(['apt-get', 'install', '-y', 'python3-requests'], 
                                  check=True, capture_output=True)
                    subprocess.run(['apt-get', 'install', '-y', 'python3-socks'], 
                                  check=True, capture_output=True)
                    print("✅ Python dependencies installed via apt")
                    return True
                except subprocess.CalledProcessError:
                    pass
                
                # Method 4: Suggest pipx
                print("❌ Could not install Python dependencies")
                print("   Manual installation required:")
                print("   Option 1: sudo apt install python3-requests python3-socks")
                print("   Option 2: python3 -m pip install requests[socks] --break-system-packages")
                print("   Option 3: Use pipx (recommended for Kali):")
                print("           sudo apt install pipx")
                print("           pipx install requests[socks]")
                return False
            
            print(f"❌ Failed to install Python dependencies: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"❌ Error installing Python dependencies: {e}")
            return False
    
    def create_installation_directory(self) -> bool:
        """Create secure installation directory"""
        print(f"📁 Creating installation directory: {self.install_dir}")
        
        try:
            # Create directory with proper permissions
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            # Set secure permissions (755 - owner: rwx, group/other: rx)
            self.install_dir.chmod(0o755)
            
            print("✅ Installation directory created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create installation directory: {e}")
            return False
    
    def install_main_script(self) -> bool:
        """Install the main script"""
        print("📄 Installing main script...")
        
        try:
            # Check if source script exists
            source_script = Path(self.script_name)
            if not source_script.exists():
                print(f"❌ Source script '{self.script_name}' not found")
                return False
            
            # Copy script to installation directory
            dest_script = self.install_dir / self.script_name
            shutil.copy2(source_script, dest_script)
            
            # Set secure permissions (755 - executable by owner, readable by others)
            dest_script.chmod(0o755)
            
            # Verify the copy
            if not dest_script.exists():
                print("❌ Failed to copy script")
                return False
            
            print("✅ Main script installed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install main script: {e}")
            return False
    
    def create_command_wrapper(self) -> bool:
        """Create command wrapper in /usr/local/bin"""
        print(f"🔗 Creating command wrapper: {self.bin_path}")
        
        try:
            # Create wrapper script content
            wrapper_content = f'''#!/bin/bash
# AnonymityEngine Command Wrapper
# This script launches the main Python application

SCRIPT_DIR="{self.install_dir}"
PYTHON_SCRIPT="$SCRIPT_DIR/{self.script_name}"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: Main script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Execute the Python script with all passed arguments
exec python3 "$PYTHON_SCRIPT" "$@"
'''
            
            # Write wrapper script
            with open(self.bin_path, 'w') as f:
                f.write(wrapper_content)
            
            # Make executable (755)
            self.bin_path.chmod(0o755)
            
            # Verify the wrapper
            if not self.bin_path.exists():
                print("❌ Failed to create command wrapper")
                return False
            
            print("✅ Command wrapper created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create command wrapper: {e}")
            return False
    
    def configure_tor_service(self) -> bool:
        """Configure Tor service"""
        print("⚙️  Configuring Tor service...")
        
        try:
            # Enable and start Tor service
            subprocess.run(['systemctl', 'enable', 'tor'], 
                          capture_output=True, check=True)
            subprocess.run(['systemctl', 'start', 'tor'], 
                          capture_output=True, check=True)
            
            # Wait a moment for the service to start
            import time
            time.sleep(2)
            
            # Check if service is running
            result = subprocess.run(['systemctl', 'is-active', 'tor'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip() == 'active':
                print("✅ Tor service configured and running")
                return True
            else:
                print("⚠️  Tor service may not be running properly")
                return True  # Continue anyway
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not configure Tor service: {e}")
            return True  # Continue anyway, manual configuration might be needed
        except Exception as e:
            print(f"❌ Error configuring Tor service: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify the installation"""
        print("🔍 Verifying installation...")
        
        try:
            # Check if all files exist with correct permissions
            if not self.install_dir.exists():
                print("❌ Installation directory not found")
                return False
            
            main_script = self.install_dir / self.script_name
            if not main_script.exists():
                print("❌ Main script not found")
                return False
            
            if not self.bin_path.exists():
                print("❌ Command wrapper not found")
                return False
            
            # Check permissions
            script_stat = main_script.stat()
            if not (script_stat.st_mode & stat.S_IRUSR and 
                    script_stat.st_mode & stat.S_IXUSR):
                print("❌ Main script has incorrect permissions")
                return False
            
            wrapper_stat = self.bin_path.stat()
            if not (wrapper_stat.st_mode & stat.S_IRUSR and 
                    wrapper_stat.st_mode & stat.S_IXUSR):
                print("❌ Command wrapper has incorrect permissions")
                return False
            
            print("✅ Installation verification passed")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def install(self) -> bool:
        """Main installation process"""
        print("🚀 Starting AnonymityEngine installation...\n")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Install system dependencies
        if not self.install_system_dependencies():
            return False
        
        # Install Python dependencies
        if not self.install_python_dependencies():
            return False
        
        # Create installation directory
        if not self.create_installation_directory():
            return False
        
        # Install main script
        if not self.install_main_script():
            return False
        
        # Create command wrapper
        if not self.create_command_wrapper():
            return False
        
        # Configure Tor service
        if not self.configure_tor_service():
            return False
        
        # Verify installation
        if not self.verify_installation():
            return False
        
        return True
    
    def uninstall(self) -> bool:
        """Uninstall the application"""
        print("🗑️  Uninstalling AnonymityEngine...")
        
        try:
            # Remove command wrapper
            if self.bin_path.exists():
                self.bin_path.unlink()
                print(f"✅ Removed command wrapper: {self.bin_path}")
            
            # Remove installation directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                print(f"✅ Removed installation directory: {self.install_dir}")
            
            print("✅ Uninstallation completed")
            return True
            
        except Exception as e:
            print(f"❌ Error during uninstallation: {e}")
            return False

def main():
    """Main entry point"""
    installer = SecureInstaller()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
AnonymityEngine - Secure Installer

Usage:
  sudo python3 install.py [option]

Options:
  install     Install the application (default)
  uninstall   Remove the application
  -h, --help  Show this help message

Examples:
  sudo python3 install.py
  sudo python3 install.py install
  sudo python3 install.py uninstall
            """)
            return
        
        elif sys.argv[1] == 'uninstall':
            if installer.uninstall():
                print("\n👋 AnonymityEngine has been uninstalled successfully!")
            else:
                print("\n❌ Uninstallation failed!")
                sys.exit(1)
            return
    
    # Default action: install
    try:
        if installer.install():
            print(f"""
╔════════════════════════════════════════════════════════════════╗
║                  🎉 Installation Successful!                   ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Usage: {installer.command_name:<49} ║
║                                                                ║
║  The tool will guide you through the setup process.           ║
║  Configure your browser to use SOCKS5 proxy: 127.0.0.1:9050  ║
║                                                                ║
║  Files installed:                                             ║
║  • {str(installer.install_dir):<50} ║
║  • {str(installer.bin_path):<50} ║
║                                                                ║
║  To uninstall: sudo python3 install.py uninstall             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
            """)
        else:
            print("""
❌ Installation failed!

Common solutions:
• Make sure you're running with sudo privileges
• Check that you have internet connection
• Ensure Python 3.6+ is installed
• Try running: sudo apt-get update && sudo apt-get install tor python3-pip
            """)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
