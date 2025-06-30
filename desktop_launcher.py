
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    """Launch the Streamlit app without metadata issues"""
    try:
        # Get the directory of this script
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        app_file = os.path.join(app_dir, "streamlit_app.py")
        
        # Check if streamlit_app.py exists
        if not os.path.exists(app_file):
            print(f"Error: streamlit_app.py not found at {app_file}")
            input("Press Enter to exit...")
            return
        
        print("🚀 Starting AI Architectural Space Analyzer PRO...")
        print("📁 Loading application files...")
        
        # Launch Streamlit using subprocess to avoid metadata issues
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.port=8501",
            "--server.address=localhost", 
            "--browser.gatherUsageStats=false",
            "--server.headless=false"
        ]
        
        print("🌐 Starting web server...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        print("🌍 Opening in browser...")
        webbrowser.open("http://localhost:8501")
        
        print("✅ Application started successfully!")
        print("🔗 Access at: http://localhost:8501")
        print("❌ Close this window to stop the application")
        
        # Keep running until user closes
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            print("\n🛑 Application stopped")
            
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
