#!/usr/bin/env python3
"""
Project Cleanup - Remove unnecessary files
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Remove all unnecessary files and keep only essentials"""
    
    print("🧹 CLEANING PROJECT - REMOVING UNNECESSARY FILES")
    print("=" * 60)
    
    # Files to remove
    remove_files = [
        # Draft apps
        'complete_desktop_app.py',
        'desktop_app.py', 
        'enhanced_complete_app.py',
        'simple_launcher.py',
        'standalone_launcher.py',
        'desktop_launcher.py',
        'mobile_app.py',
        'mobile_wrapper.py',
        'snowflake_app.py',
        'streamlit_app_simple.py',
        'streamlit_app_snowflake.py',
        'temp_fix.py',
        'app.py',
        'build_desktop.py',
        'compress_dwg.py',
        'file_size_info.py',
        'display_construction_plans.py',
        
        # Build files
        'build_simple.bat',
        'package.json',
        'package-lock.json',
        'pyproject.toml',
        'stream-server.js',
        
        # Extra requirements
        'requirements_build.txt',
        'requirements_deploy.txt',
        'packages.txt',
        
        # Documentation drafts
        'APP_SPECIFICATIONS.md',
        'DEPLOYMENT_GUIDE.md',
        'FIXED_EXE_GUIDE.md',
        'INSTALLATION_GUIDE.md',
        
        # Database
        'dwg_analyzer.db',
        
        # Other
        'Construction plan Reference.jpg'
    ]
    
    # Directories to remove
    remove_dirs = [
        'node_modules/',
        'WP_FUQJSIAFPMCZO/',
        'dwg/',
        '.config/',
        'static/',
        'share streamlit logs/',
        '__pycache__/'
    ]
    
    # Remove files
    for file in remove_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Removed: {file}")
    
    # Remove directories
    for dir_path in remove_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"📁 Removed directory: {dir_path}")
    
    # Keep only best executable in dist/
    cleanup_dist()
    
    # Clean sample files
    cleanup_samples()
    
    print("\n✅ CLEANUP COMPLETE!")

def cleanup_dist():
    """Keep only the best executable"""
    
    if not os.path.exists('dist/'):
        return
    
    # Keep only WebFeatures version
    keep_exe = 'AI_Architectural_Analyzer_WebFeatures.exe'
    
    for file in os.listdir('dist/'):
        if file.endswith('.exe') and file != keep_exe:
            file_path = os.path.join('dist/', file)
            os.remove(file_path)
            print(f"🗑️ Removed old exe: {file}")
    
    print(f"✅ Kept best executable: {keep_exe}")

def cleanup_samples():
    """Clean up sample files - keep only essential ones"""
    
    if not os.path.exists('sample_files/'):
        return
    
    # Keep only a few essential samples
    keep_files = [
        'Sample 1.dwg',
        'Sample 1.dxf',
        'apartment_plans.dwg',
        'villa_2.dwg'
    ]
    
    for file in os.listdir('sample_files/'):
        if file not in keep_files and not file.endswith('.png') and not file.endswith('.pdf'):
            file_path = os.path.join('sample_files/', file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"🗑️ Removed sample: {file}")

def main():
    """Main cleanup"""
    
    os.chdir(r'C:\Users\HP\Desktop\DWG Analyzee')
    cleanup_project()
    
    print("\n📁 FINAL PROJECT STRUCTURE:")
    print("├── src/                    # Core modules")
    print("├── apps/                   # Main applications")
    print("├── installers/            # Installation files")
    print("├── dist/                  # Best executable only")
    print("├── docs/                  # Documentation")
    print("├── assets/                # Resources")
    print("├── sample_files/          # Essential samples")
    print("├── scripts/               # Utility scripts")
    print("├── streamlit_app.py       # Web app entry")
    print("├── requirements.txt       # Dependencies")
    print("└── .gitignore             # Git ignore")

if __name__ == "__main__":
    main()