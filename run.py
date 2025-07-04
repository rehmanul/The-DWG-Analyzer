#!/usr/bin/env python3
"""
AI Architectural Space Analyzer PRO - Enterprise Edition Launcher
Handles all system dependencies and enterprise module loading
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def install_requirements():
    """Install all enterprise requirements"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("🔧 Installing enterprise dependencies...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "--upgrade"
            ])
            print("✅ All enterprise dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    return True

def check_system_libraries():
    """Check and install system libraries for enterprise features"""
    print("🔍 Checking system libraries...")
    
    # Check for OpenGL libraries (for advanced visualization)
    try:
        import OpenGL.GL
        print("✅ OpenGL libraries available")
    except ImportError:
        print("⚠️  Installing OpenGL libraries...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyOpenGL", "PyOpenGL_accelerate"])
        except:
            print("ℹ️  OpenGL installation optional - continuing without hardware acceleration")
    
    # Check for GDAL (for advanced geospatial processing)
    try:
        import gdal
        print("✅ GDAL libraries available")
    except ImportError:
        print("ℹ️  GDAL not available - using alternative processing methods")
    
    return True

def setup_environment():
    """Setup enterprise environment variables"""
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    
    # Set matplotlib backend for enterprise deployment
    os.environ['MPLBACKEND'] = 'Qt5Agg'
    
    # Configure enterprise logging
    os.environ['PYTHONUNBUFFERED'] = '1'

def main():
    """Main launcher with enterprise initialization"""
    print("🚀 AI Architectural Space Analyzer PRO - Enterprise Edition")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Install requirements if needed
    if not install_requirements():
        print("❌ Failed to setup enterprise environment")
        return 1
    
    # Check system libraries
    check_system_libraries()
    
    # Import and run main application
    try:
        print("🏗️  Loading enterprise modules...")
        
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Import main application
        from main import main as run_main_app
        
        print("✅ Enterprise modules loaded successfully")
        print("🎯 Starting AI Architectural Space Analyzer PRO...")
        print("=" * 60)
        
        # Run the main application
        return run_main_app()
        
    except ImportError as e:
        print(f"❌ Failed to import enterprise modules: {e}")
        print("🔧 Attempting to resolve dependencies...")
        
        # Try to install missing modules
        missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
        
        module_mappings = {
            'cv2': 'opencv-python',
            'PyQt5': 'PyQt5',
            'ezdxf': 'ezdxf',
            'shapely': 'shapely',
            'matplotlib': 'matplotlib',
            'scipy': 'scipy',
            'sklearn': 'scikit-learn',
            'psycopg2': 'psycopg2-binary',
            'reportlab': 'reportlab'
        }
        
        package_name = module_mappings.get(missing_module, missing_module)
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ Installed {package_name}")
            
            # Retry import
            from main import main as run_main_app
            return run_main_app()
            
        except Exception as install_error:
            print(f"❌ Failed to install {package_name}: {install_error}")
            return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())