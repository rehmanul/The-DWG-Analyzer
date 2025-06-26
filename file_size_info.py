"""
File Size Information Display
"""
import streamlit as st

def display_file_size_info():
    """Display file size limitations and solutions"""
    st.info("""
    📁 **File Size Limits for Web Deployment:**
    
    • **Maximum file size**: 10 MB
    • **Recommended size**: Under 5 MB for best performance
    
    💡 **For larger files:**
    • Compress your DXF file using CAD software
    • Run the app locally (supports up to 190 MB)
    • Split large drawings into smaller sections
    """)

def check_file_size_before_upload():
    """Pre-upload file size check"""
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
    <h4>📏 File Size Guidelines</h4>
    <ul>
    <li><strong>Web version</strong>: Maximum 10 MB</li>
    <li><strong>Local version</strong>: Maximum 190 MB</li>
    <li><strong>Optimal size</strong>: 1-5 MB for fastest processing</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)