import PyInstaller.__main__
import shutil
import os
from pathlib import Path
import time

def build_enterprise_exe():
    """Build enterprise executable safely"""
    print("🏗️ BUILDING ENTERPRISE DESKTOP APPLICATION")
    print("=" * 60)
    
    try:
        # Create new dist directory with timestamp
        timestamp = int(time.time())
        new_dist = f"dist_enterprise_{timestamp}"
        
        print(f"Building to: {new_dist}")
        
        # PyInstaller arguments
        args = [
            'apps/streamlit_app.py',
            '--name=AI_Architectural_Analyzer_ENTERPRISE',
            '--onefile',
            '--windowed',
            '--icon=assets/icon.ico',
            f'--distpath={new_dist}',
            '--add-data=src;src',
            '--add-data=assets;assets',
            '--add-data=config;config',
            '--hidden-import=streamlit',
            '--hidden-import=plotly',
            '--hidden-import=pandas',
            '--hidden-import=numpy',
            '--hidden-import=ezdxf',
            '--hidden-import=PIL',
            '--hidden-import=matplotlib',
            '--hidden-import=psycopg2',
            '--collect-all=streamlit',
            '--collect-all=plotly',
            '--noconfirm'
        ]
        
        print("Starting PyInstaller...")
        PyInstaller.__main__.run(args)
        
        # Copy to main dist directory
        if Path(new_dist).exists():
            exe_file = Path(new_dist) / "AI_Architectural_Analyzer_ENTERPRISE.exe"
            if exe_file.exists():
                # Create main dist if it doesn't exist
                Path("dist").mkdir(exist_ok=True)
                
                # Copy the new executable
                target = Path("dist") / "AI_Architectural_Analyzer_ENTERPRISE.exe"
                if target.exists():
                    try:
                        target.unlink()
                    except:
                        # If can't delete, create with timestamp
                        target = Path("dist") / f"AI_Architectural_Analyzer_ENTERPRISE_{timestamp}.exe"
                
                shutil.copy2(exe_file, target)
                print(f"✅ Enterprise executable built: {target}")
                
                # Cleanup temp directory
                try:
                    shutil.rmtree(new_dist)
                except:
                    print(f"Note: Temp directory {new_dist} not cleaned up")
                
                return True
        
        print("❌ Build failed - executable not found")
        return False
        
    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

if __name__ == "__main__":
    success = build_enterprise_exe()
    if success:
        print("\n🎉 ENTERPRISE BUILD COMPLETE!")
        print("Run: dist/AI_Architectural_Analyzer_ENTERPRISE.exe")
    else:
        print("\n❌ BUILD FAILED")