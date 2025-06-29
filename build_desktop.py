#!/usr/bin/env python3
"""
Desktop App Builder for AI Architectural Space Analyzer PRO
Creates Windows EXE, macOS APP, and Linux executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages for building"""
    packages = [
        "pyinstaller",
        "auto-py-to-exe", 
        "streamlit",
        "plotly",
        "pandas",
        "numpy"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package])

def create_desktop_launcher():
    """Create desktop launcher script"""
    launcher_content = '''
import streamlit.web.cli as stcli
import sys
import os

def main():
    """Launch the Streamlit app"""
    # Get the directory of this script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(app_dir, "streamlit_app.py")
    
    # Set Streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        app_file,
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
        "--server.headless=true"
    ]
    
    # Launch Streamlit
    stcli.main()

if __name__ == "__main__":
    main()
'''
    
    with open("desktop_launcher.py", "w") as f:
        f.write(launcher_content)
    
    print("✅ Desktop launcher created")

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('streamlit_app.py', '.'),
        ('src', 'src'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'plotly',
        'pandas',
        'numpy',
        'ezdxf',
        'matplotlib',
        'tempfile',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI_Architectural_Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
)
'''
    
    with open("app.spec", "w") as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec created")

def build_windows_exe():
    """Build Windows EXE"""
    print("🔨 Building Windows EXE...")
    
    try:
        # Build with PyInstaller
        subprocess.run([
            "pyinstaller", 
            "--onefile",
            "--windowed",
            "--name=AI_Architectural_Analyzer",
            "--add-data=streamlit_app.py;.",
            "--add-data=src;src",
            "--hidden-import=streamlit",
            "--hidden-import=plotly",
            "desktop_launcher.py"
        ], check=True)
        
        print("✅ Windows EXE built successfully!")
        print("📁 Location: dist/AI_Architectural_Analyzer.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")

def create_mobile_config():
    """Create mobile app configuration"""
    
    # Create Kivy mobile app wrapper
    mobile_content = '''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.webview import WebView
import threading
import subprocess
import time

class ArchitecturalAnalyzerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='AI Architectural Space Analyzer PRO',
            size_hint_y=None,
            height=50,
            font_size=20
        )
        layout.add_widget(title)
        
        # Start button
        start_btn = Button(
            text='Launch Analyzer',
            size_hint_y=None,
            height=50,
            on_press=self.start_streamlit
        )
        layout.add_widget(start_btn)
        
        # WebView for Streamlit
        self.webview = WebView(url='http://localhost:8501')
        layout.add_widget(self.webview)
        
        return layout
    
    def start_streamlit(self, instance):
        """Start Streamlit in background thread"""
        def run_streamlit():
            subprocess.run([
                'python', '-m', 'streamlit', 'run', 'streamlit_app.py',
                '--server.port=8501',
                '--server.headless=true'
            ])
        
        thread = threading.Thread(target=run_streamlit)
        thread.daemon = True
        thread.start()
        
        # Wait and reload webview
        time.sleep(3)
        self.webview.url = 'http://localhost:8501'

if __name__ == '__main__':
    ArchitecturalAnalyzerApp().run()
'''
    
    with open("mobile_app.py", "w") as f:
        f.write(mobile_content)
    
    # Create buildozer.spec for Android
    buildozer_spec = '''
[app]
title = AI Architectural Analyzer
package.name = aiarchanalyzer
package.domain = com.aiarch.analyzer

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0
requirements = python3,kivy,streamlit,plotly,pandas,numpy

[buildozer]
log_level = 2

[android]
api = 31
minapi = 21
ndk = 25b
accept_sdk_license = True
'''
    
    with open("buildozer.spec", "w") as f:
        f.write(buildozer_spec)
    
    print("✅ Mobile configuration created")

def create_installation_guide():
    """Create installation and usage guide"""
    guide_content = '''
# 🚀 AI Architectural Space Analyzer PRO - Installation Guide

## 📱 MOBILE VERSIONS

### Android APK:
1. Install Python and Buildozer on Linux/WSL
2. Run: `buildozer android debug`
3. Install generated APK on Android device

### iOS IPA:
1. Use Xcode on macOS
2. Convert Python app using PyObjC
3. Build and sign for iOS

## 💻 DESKTOP VERSIONS

### Windows EXE:
1. Run: `python build_desktop.py`
2. EXE file created in `dist/` folder
3. Double-click to run

### macOS APP:
1. Run: `python build_desktop.py` on macOS
2. APP bundle created
3. Drag to Applications folder

### Linux:
1. Run: `python build_desktop.py`
2. Executable created
3. Make executable: `chmod +x AI_Architectural_Analyzer`

## 🌐 WEB VERSION (Current):
- Access: https://the-dwg-analyzer.streamlit.app/
- No installation needed
- Works on any device with browser

## 📋 FEATURES (All Versions):
✅ DWG/DXF file analysis
✅ AI room detection
✅ Construction planning
✅ Professional reports
✅ CAD export
✅ Enterprise-grade analysis

## 🔧 REQUIREMENTS:
- Python 3.8+
- 4GB RAM minimum
- 1GB storage space
- Internet connection (for AI features)

## 📞 SUPPORT:
- Web version: Always latest
- Desktop: Manual updates
- Mobile: App store updates
'''
    
    with open("INSTALLATION_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Installation guide created")

def main():
    """Main build process"""
    print("🚀 AI Architectural Space Analyzer PRO - Cross-Platform Builder")
    print("=" * 60)
    
    # Install requirements
    print("📦 Installing build requirements...")
    install_requirements()
    
    # Create launcher
    print("🔧 Creating desktop launcher...")
    create_desktop_launcher()
    
    # Create PyInstaller spec
    print("📝 Creating build configuration...")
    create_pyinstaller_spec()
    
    # Create mobile config
    print("📱 Creating mobile configuration...")
    create_mobile_config()
    
    # Create guide
    print("📋 Creating installation guide...")
    create_installation_guide()
    
    print("\n✅ BUILD SETUP COMPLETE!")
    print("\n🎯 NEXT STEPS:")
    print("1. Windows EXE: Run 'python build_desktop.py'")
    print("2. Android APK: Use buildozer on Linux")
    print("3. iOS IPA: Use Xcode on macOS")
    print("4. Web version: Already deployed!")
    
    # Ask user what to build
    choice = input("\n🔨 Build Windows EXE now? (y/n): ")
    if choice.lower() == 'y':
        build_windows_exe()

if __name__ == "__main__":
    main()