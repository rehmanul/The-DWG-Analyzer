#!/usr/bin/env python3
"""
Simple launcher that works with PyInstaller
"""

import os
import sys
import subprocess
import time
import webbrowser

def main():
    print("🚀 AI Architectural Space Analyzer PRO")
    print("=" * 50)
    
    try:
        # Get the correct Python executable
        if getattr(sys, 'frozen', False):
            # We're running as an executable
            python_exe = sys.executable
            # Get the temp directory where files are extracted
            if hasattr(sys, '_MEIPASS'):
                app_dir = sys._MEIPASS
            else:
                app_dir = os.path.dirname(sys.executable)
        else:
            # We're running as a script
            python_exe = sys.executable
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        app_file = os.path.join(app_dir, "streamlit_app.py")
        
        print(f"📁 App directory: {app_dir}")
        print(f"📄 App file: {app_file}")
        
        if not os.path.exists(app_file):
            print(f"❌ streamlit_app.py not found at {app_file}")
            print("📂 Files in directory:")
            try:
                files = os.listdir(app_dir)
                for f in files[:10]:  # Show first 10 files
                    print(f"   - {f}")
            except:
                print("   Could not list files")
            input("Press Enter to exit...")
            return
        
        print("🌐 Starting web server...")
        
        # Start Streamlit with proper working directory
        cmd = [
            python_exe, "-m", "streamlit", "run", app_file,
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ]
        
        # Start the process with proper working directory
        process = subprocess.Popen(
            cmd,
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for server to start...")
        time.sleep(5)  # Give more time for startup
        
        # Open browser
        url = "http://localhost:8501"
        print(f"🌍 Opening {url}")
        webbrowser.open(url)
        
        print("✅ Application started!")
        print("🔗 URL: http://localhost:8501")
        print("❌ Close this window to stop")
        print("-" * 50)
        
        # Keep running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()