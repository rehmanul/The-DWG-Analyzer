#!/usr/bin/env python3
"""
AI Architectural Space Analyzer PRO - Enterprise Edition
Direct launcher for full enterprise functionality
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Launch enterprise application directly"""
    
    print("🚀 AI Architectural Space Analyzer PRO - Enterprise Edition")
    print("=" * 60)
    
    try:
        # Import and run enterprise main application
        from enterprise_main import main as run_enterprise_app
        
        print("✅ Enterprise modules loaded successfully")
        print("🎯 Starting Professional CAD Analysis...")
        print("=" * 60)
        
        # Run the enterprise application
        return run_enterprise_app()
        
    except ImportError as e:
        print(f"❌ Failed to import enterprise modules: {e}")
        print("🔧 Please run the installer first:")
        print("   Windows: install_enterprise.bat")
        print("   Linux/macOS: ./install_enterprise.sh")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())