#!/usr/bin/env python3
"""
ErosionWatch Application Launcher
Simple script to start the ErosionWatch web application
"""

import os
import sys
import subprocess
import time

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask',
        'opencv-python',
        'numpy',
        'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                *missing_packages
            ])
            print("✅ All dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def create_directories():
    """Ensure required directories exist."""
    directories = [
        'static/uploads',
        'static/outputs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def main():
    """Main function to start the application."""
    print("🌱 ErosionWatch Application Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check and install dependencies
    if not check_dependencies():
        return 1
    
    # Create required directories
    create_directories()
    
    print("\n🚀 Starting ErosionWatch...")
    print("   The application will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("   Make sure you're in the ErosionWatch directory")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())