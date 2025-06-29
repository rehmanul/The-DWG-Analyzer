"""
Mobile App Wrapper for AI Architectural Space Analyzer PRO
Creates installable mobile apps for Android and iOS
"""

import streamlit as st
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

class MobileAppLauncher:
    def __init__(self):
        self.streamlit_process = None
        self.port = 8501
    
    def start_streamlit_server(self):
        """Start Streamlit server in background"""
        try:
            cmd = [
                'python', '-m', 'streamlit', 'run', 'streamlit_app.py',
                f'--server.port={self.port}',
                '--server.headless=true',
                '--browser.gatherUsageStats=false'
            ]
            
            self.streamlit_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"Error starting Streamlit: {e}")
            return False
    
    def open_app(self):
        """Open the app in default browser"""
        url = f"http://localhost:{self.port}"
        webbrowser.open(url)
    
    def stop_server(self):
        """Stop Streamlit server"""
        if self.streamlit_process:
            self.streamlit_process.terminate()

def create_android_manifest():
    """Create Android manifest for APK"""
    manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.aiarch.analyzer">
    
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="AI Architectural Analyzer"
        android:theme="@style/AppTheme">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
    
    Path("android").mkdir(exist_ok=True)
    with open("android/AndroidManifest.xml", "w") as f:
        f.write(manifest)

def create_ios_info_plist():
    """Create iOS Info.plist"""
    plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>AI Architectural Analyzer</string>
    <key>CFBundleIdentifier</key>
    <string>com.aiarch.analyzer</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>armv7</string>
    </array>
</dict>
</plist>'''
    
    Path("ios").mkdir(exist_ok=True)
    with open("ios/Info.plist", "w") as f:
        f.write(plist)

if __name__ == "__main__":
    # Create mobile configurations
    create_android_manifest()
    create_ios_info_plist()
    
    # Launch mobile app
    launcher = MobileAppLauncher()
    
    print("🚀 Starting AI Architectural Space Analyzer PRO...")
    
    if launcher.start_streamlit_server():
        print("✅ Server started successfully!")
        print(f"🌐 Opening app at http://localhost:{launcher.port}")
        launcher.open_app()
        
        try:
            # Keep running
            input("Press Enter to stop the app...")
        except KeyboardInterrupt:
            pass
        finally:
            launcher.stop_server()
            print("🛑 App stopped")
    else:
        print("❌ Failed to start server")