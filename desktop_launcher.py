
import streamlit.web.cli as stcli
import sys
import os

def main():
    """Launch the Streamlit app"""
    # Get the directory of this script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(app_dir, "streamlit_app.py")
    
    # Set Streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        app_file,
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
        "--server.headless=true"
    ]
    
    # Launch Streamlit
    stcli.main()

if __name__ == "__main__":
    main()
