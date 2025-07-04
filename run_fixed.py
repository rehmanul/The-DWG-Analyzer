#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    print("🏗️ Starting FIXED Îlot Placement App...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "apps/fixed_ilot_app.py",
            "--server.port=8503",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()