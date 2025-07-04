#!/usr/bin/env python3
"""
Smart Enterprise Launcher - Detects environment and launches appropriate interface
"""

import sys
import os
import subprocess
from pathlib import Path

def detect_environment():
    """Detect if GUI or headless environment"""
    
    # Check for display
    if os.environ.get('DISPLAY') or os.name == 'nt':
        # Try importing GUI libraries
        try:
            from PyQt5.QtWidgets import QApplication
            return 'gui'
        except ImportError:
            return 'web'
    else:
        return 'web'

def main():
    """Smart launcher for enterprise application"""
    
    print("🏗️ AI ARCHITECTURAL ANALYZER PRO - ENTERPRISE EDITION")
    print("=" * 60)
    
    env_type = detect_environment()
    
    if env_type == 'gui':
        print("🖥️  Launching Desktop Interface...")
        try:
            from enterprise_main import main as run_gui
            return run_gui()
        except Exception as e:
            print(f"❌ Desktop launch failed: {e}")
            print("🌐 Falling back to web interface...")
            env_type = 'web'
    
    if env_type == 'web':
        print("🌐 Launching Web Interface...")
        print("📱 Access at: http://localhost:8501")
        print("=" * 60)
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "streamlit_enterprise.py",
                "--server.port=8501",
                "--server.enableCORS=false"
            ])
        except KeyboardInterrupt:
            print("\n✅ Application stopped")
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            print("💡 Install: pip install streamlit plotly")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())