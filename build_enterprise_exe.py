#!/usr/bin/env python3
"""
Build Enterprise-Grade Desktop EXE
Real functional application
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_enterprise_exe():
    """Build real enterprise desktop application"""
    
    print("🏗️ BUILDING ENTERPRISE DESKTOP APPLICATION")
    print("=" * 60)
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Enterprise PyInstaller arguments
    args = [
        'apps/desktop_app_web_features.py',  # Main application
        '--name=AI_Architectural_Analyzer_Enterprise',
        '--onefile',
        '--windowed',
        '--icon=assets/app_icon.ico',
        '--add-data=src;src',
        '--add-data=assets;assets',
        '--add-data=sample_files;sample_files',
        '--hidden-import=streamlit',
        '--hidden-import=plotly',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=matplotlib',
        '--hidden-import=ezdxf',
        '--hidden-import=psycopg2',
        '--hidden-import=sqlalchemy',
        '--hidden-import=google.generativeai',
        '--hidden-import=reportlab',
        '--hidden-import=PIL',
        '--collect-all=streamlit',
        '--collect-all=plotly',
        '--noconfirm'
    ]
    
    print("🔨 Running PyInstaller...")
    PyInstaller.__main__.run(args)
    
    # Verify build
    exe_path = Path('dist/AI_Architectural_Analyzer_Enterprise.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ SUCCESS: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ BUILD FAILED")
        return False

if __name__ == "__main__":
    success = build_enterprise_exe()
    if success:
        print("\n🎉 ENTERPRISE EXE READY!")
        print("📍 Location: dist/AI_Architectural_Analyzer_Enterprise.exe")
    else:
        print("\n❌ BUILD FAILED - Check logs above")