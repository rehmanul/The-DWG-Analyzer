#!/usr/bin/env python3
"""
Streamlit App - Main Entry Point
Fixed for Streamlit Cloud deployment
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Import from apps directory
    from apps.streamlit_app import main
    
    if __name__ == "__main__":
        main()
        
except ImportError:
    # Fallback - run basic app
    st.title("🏗️ AI Architectural Space Analyzer PRO")
    st.error("Module import error - please check deployment")
    st.info("Repository structure changed - updating...")
    
    # Basic functionality
    st.subheader("📁 File Upload")
    uploaded_file = st.file_uploader("Upload DWG/DXF", type=['dwg', 'dxf'])
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info("Full functionality will be restored after deployment fix")