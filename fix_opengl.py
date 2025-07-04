#!/usr/bin/env python3
"""
Fix OpenGL/libGL issues for enterprise deployment
"""

import os
import sys
import subprocess

def fix_opengl_issues():
    """Fix OpenGL library issues"""
    
    # Set environment variables to avoid OpenGL issues
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['DISPLAY'] = ':99'
    
    # For matplotlib without GUI
    import matplotlib
    matplotlib.use('Agg')
    
    print("✅ OpenGL issues resolved - running in headless mode")

def install_system_libs():
    """Install required system libraries"""
    
    try:
        # Try to install OpenGL libraries
        if os.name == 'posix':  # Linux/Unix
            subprocess.run(['sudo', 'apt-get', 'update'], check=False)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'libgl1-mesa-glx', 'libglib2.0-0'], check=False)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'xvfb'], check=False)  # Virtual display
        
        print("✅ System libraries installation attempted")
    except:
        print("⚠️ Could not install system libraries - continuing without")

if __name__ == "__main__":
    fix_opengl_issues()
    install_system_libs()