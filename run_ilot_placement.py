"""
Launch script for the Enhanced Îlot Placement Application
"""

import subprocess
import sys
import os

def main():
    """Launch the îlot placement application"""
    
    # Get the path to the îlot placement app
    app_path = os.path.join(os.path.dirname(__file__), 'apps', 'ilot_placement_app.py')
    
    if not os.path.exists(app_path):
        print(f"Error: Application not found at {app_path}")
        return
    
    print("🏗️ Launching AI Îlot Placement PRO...")
    print(f"📁 App location: {app_path}")
    
    try:
        # Launch streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8502",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

if __name__ == "__main__":
    main()