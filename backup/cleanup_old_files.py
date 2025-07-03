#!/usr/bin/env python3
"""
CLEANUP OLD BROKEN FILES
Remove old broken EXE files to avoid confusion
"""

import os
import shutil
from pathlib import Path

def cleanup_old_exe_files():
    """Clean up old broken EXE files"""
    print("🧹 CLEANING UP OLD BROKEN FILES")
    print("=" * 50)
    
    # List of old broken EXE files to remove
    old_files = [
        "AI_Architectural_Analyzer_Enterprise.exe",
        "dist_enterprise/AI_Architectural_Analyzer_Enterprise.exe",
        "dist_enterprise_1751573542/AI_Architectural_Analyzer_ENTERPRISE.exe", 
        "dist_enterprise_1751576102/AI_Architectural_Analyzer_ENTERPRISE.exe"
    ]
    
    removed_count = 0
    
    for file_path in old_files:
        if os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path) / 1024  # KB
                os.remove(file_path)
                print(f"✅ Removed: {file_path} ({file_size:.1f} KB)")
                removed_count += 1
            except Exception as e:
                print(f"❌ Could not remove {file_path}: {e}")
        else:
            print(f"ℹ️ Not found: {file_path}")
    
    # Clean up old directories
    old_dirs = [
        "dist_enterprise",
        "dist_enterprise_1751573542", 
        "dist_enterprise_1751576102",
        "build_enterprise"
    ]
    
    for dir_path in old_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed directory: {dir_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Could not remove directory {dir_path}: {e}")
    
    print(f"\n📊 Cleanup complete: {removed_count} items removed")
    
    # Show current working files
    print("\n✅ CURRENT WORKING FILES:")
    working_exe = "dist/AI_Architectural_Analyzer_ENTERPRISE_LATEST.exe"
    if os.path.exists(working_exe):
        size_mb = os.path.getsize(working_exe) / (1024 * 1024)
        print(f"🎯 Working EXE: {working_exe} ({size_mb:.1f} MB)")
    
    print("🌐 Web Version: streamlit_app.py")
    print("📋 Documentation: FIXES_COMPLETED.md")

if __name__ == "__main__":
    cleanup_old_exe_files()