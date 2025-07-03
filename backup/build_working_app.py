#!/usr/bin/env python3
"""
BUILD WORKING DESKTOP APP
"""

import PyInstaller.__main__
import os
import shutil

def build_working_app():
    print("🏗️ BUILDING WORKING DESKTOP APP")
    print("=" * 50)
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Cleaned {dir_name}")
            except:
                pass
    
    # Build working app
    args = [
        'working_desktop_app.py',
        '--name=AI_Architectural_Analyzer_WORKING',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--hidden-import=tkinter',
        '--hidden-import=matplotlib',
        '--hidden-import=numpy',
        '--collect-all=matplotlib'
    ]
    
    print("Building working desktop app...")
    PyInstaller.__main__.run(args)
    
    # Check result
    exe_path = "dist/AI_Architectural_Analyzer_WORKING.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ SUCCESS: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ BUILD FAILED")
        return False

if __name__ == "__main__":
    success = build_working_app()
    if success:
        print("\n🎉 WORKING APP READY!")
        print("📍 Location: dist/AI_Architectural_Analyzer_WORKING.exe")
    else:
        print("\n❌ BUILD FAILED")