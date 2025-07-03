#!/usr/bin/env python3
"""
FIXED ENTERPRISE EXE BUILDER
This will create a working EXE file
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path
import sys

def build_working_exe():
    """Build a working enterprise EXE"""
    
    print("🏗️ BUILDING WORKING ENTERPRISE EXE")
    print("=" * 60)
    
    # Clean previous builds
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Cleaned {dir_name}")
            except:
                pass
    
    # Ensure we have the main app file
    main_app = "apps/desktop_app_web_features.py"
    if not os.path.exists(main_app):
        print(f"❌ Main app file not found: {main_app}")
        return False
    
    # Build arguments for a WORKING EXE
    args = [
        main_app,
        '--name=AI_Architectural_Analyzer_ENTERPRISE_LATEST',
        '--onefile',
        '--windowed',
        '--noconfirm',
        
        # Essential data files
        '--add-data=src;src',
        '--add-data=assets;assets',
        
        # Core imports that MUST be included
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=matplotlib',
        '--hidden-import=matplotlib.pyplot',
        '--hidden-import=matplotlib.backends.backend_tkagg',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        
        # Optional imports (won't break if missing)
        '--hidden-import=ezdxf',
        '--hidden-import=plotly',
        '--hidden-import=streamlit',
        
        # Collect all matplotlib
        '--collect-all=matplotlib',
        
        # Icon if available
        '--icon=assets/app_icon.ico' if os.path.exists('assets/app_icon.ico') else '',
    ]
    
    # Remove empty arguments
    args = [arg for arg in args if arg]
    
    print("🔨 Running PyInstaller with working configuration...")
    print(f"Main file: {main_app}")
    print(f"Output name: AI_Architectural_Analyzer_ENTERPRISE_LATEST.exe")
    
    try:
        PyInstaller.__main__.run(args)
        
        # Check if build succeeded
        exe_path = Path('dist/AI_Architectural_Analyzer_ENTERPRISE_LATEST.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ SUCCESS: {exe_path} ({size_mb:.1f} MB)")
            
            if size_mb < 10:
                print("⚠️ WARNING: EXE size is suspiciously small - may be missing dependencies")
                return False
            else:
                print("✅ EXE size looks good - likely contains all dependencies")
                return True
        else:
            print("❌ BUILD FAILED: EXE file not created")
            return False
            
    except Exception as e:
        print(f"❌ PyInstaller error: {str(e)}")
        return False

if __name__ == "__main__":
    success = build_working_exe()
    if success:
        print("\n🎉 WORKING EXE CREATED!")
        print("📍 Location: dist/AI_Architectural_Analyzer_ENTERPRISE_LATEST.exe")
        print("\n🚀 Test the EXE by running it directly")
    else:
        print("\n❌ BUILD FAILED")
        print("Check the error messages above")
