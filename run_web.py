#!/usr/bin/env python3
"""
Launch Enterprise Web Interface
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch Streamlit web interface"""
    
    print("🚀 Starting AI Architectural Analyzer PRO - Web Interface")
    print("=" * 60)
    
    # Set environment for headless operation
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    os.environ['MPLBACKEND'] = 'Agg'
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_enterprise.py",
            "--server.port=8501",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ])
    except KeyboardInterrupt:
        print("\n✅ Web interface stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try: pip install streamlit plotly")

if __name__ == "__main__":
    main()