#!/usr/bin/env python3
"""
🏗️ AI Îlot Placement PRO - Launcher
Professional îlot placement with constraint compliance
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the îlot placement application"""
    
    # Change to app directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    print("🏗️ Starting AI Îlot Placement PRO...")
    print("📍 Professional îlot placement with constraint compliance")
    print("🚀 Loading application...")
    
    try:
        # Run the streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "apps/ilot_app.py",
            "--server.port=8502",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())