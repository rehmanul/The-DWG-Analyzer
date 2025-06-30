#!/usr/bin/env python3
"""
Standalone launcher that doesn't rely on Streamlit metadata
Works around PyInstaller packaging issues
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

class StandaloneApp:
    def __init__(self):
        self.process = None
        self.port = 8501
        
    def find_python(self):
        """Find Python executable"""
        if sys.executable:
            return sys.executable
        
        # Fallback options
        for python_cmd in ['python', 'python3', 'py']:
            try:
                subprocess.run([python_cmd, '--version'], 
                             capture_output=True, check=True)
                return python_cmd
            except:
                continue
        
        return None
    
    def find_app_file(self):
        """Find the main app file"""
        # Multiple search locations
        search_paths = []
        
        if getattr(sys, 'frozen', False):
            # Running as executable - check multiple locations
            exe_dir = os.path.dirname(sys.executable)
            search_paths.extend([
                exe_dir,
                os.path.join(exe_dir, "."),
                os.path.join(exe_dir, "_internal"),
                sys._MEIPASS if hasattr(sys, '_MEIPASS') else exe_dir
            ])
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            search_paths.append(script_dir)
        
        # Add current directory
        search_paths.append(os.getcwd())
        
        # Search for streamlit_app.py
        for path in search_paths:
            app_file = os.path.join(path, "streamlit_app.py")
            if os.path.exists(app_file):
                print(f"📁 Found app file: {app_file}")
                return app_file
        
        # Debug: show what we're looking for
        print("❌ streamlit_app.py not found in:")
        for path in search_paths:
            print(f"   - {path}")
            if os.path.exists(path):
                files = [f for f in os.listdir(path) if f.endswith('.py')]
                print(f"     Python files: {files[:5]}")
        
        return None
    
    def start_server(self):
        """Start the Streamlit server"""
        python_exe = self.find_python()
        app_file = self.find_app_file()
        
        if not python_exe:
            raise Exception("Python executable not found")
        
        if not app_file:
            raise Exception("streamlit_app.py not found")
        
        print(f"🐍 Using Python: {python_exe}")
        print(f"📁 Using app file: {app_file}")
        
        # Start Streamlit
        cmd = [
            python_exe, "-m", "streamlit", "run", app_file,
            f"--server.port={self.port}",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
            "--server.headless=true"
        ]
        
        print("🚀 Starting Streamlit server...")
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(app_file) if os.path.dirname(app_file) else None
        )
        
        return True
    
    def wait_for_server(self, timeout=30):
        """Wait for server to be ready"""
        import urllib.request
        import urllib.error
        
        url = f"http://localhost:{self.port}"
        
        for i in range(timeout):
            try:
                urllib.request.urlopen(url, timeout=1)
                return True
            except:
                time.sleep(1)
                print(f"⏳ Waiting for server... ({i+1}/{timeout})")
        
        return False
    
    def open_browser(self):
        """Open the app in browser"""
        url = f"http://localhost:{self.port}"
        print(f"🌐 Opening {url}")
        webbrowser.open(url)
    
    def run(self):
        """Main run method"""
        try:
            print("🏗️ AI Architectural Space Analyzer PRO")
            print("=" * 50)
            
            # Start server
            if not self.start_server():
                raise Exception("Failed to start server")
            
            # Wait for server
            if not self.wait_for_server():
                raise Exception("Server failed to start within timeout")
            
            print("✅ Server started successfully!")
            
            # Open browser
            self.open_browser()
            
            print("\n🎯 Application is running!")
            print(f"🔗 URL: http://localhost:{self.port}")
            print("❌ Close this window to stop the application")
            print("-" * 50)
            
            # Keep running
            try:
                self.process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping application...")
                self.stop()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n🔍 Debug Info:")
            print(f"   Executable: {sys.executable}")
            print(f"   Frozen: {getattr(sys, 'frozen', False)}")
            print(f"   Current dir: {os.getcwd()}")
            if hasattr(sys, '_MEIPASS'):
                print(f"   PyInstaller temp: {sys._MEIPASS}")
            
            try:
                input("\nPress Enter to exit...")
            except:
                time.sleep(5)  # Auto-close after 5 seconds if no input
    
    def stop(self):
        """Stop the server"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("✅ Application stopped")

def main():
    app = StandaloneApp()
    app.run()

if __name__ == "__main__":
    main()