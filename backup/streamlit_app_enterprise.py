import streamlit as st
import tempfile
import os
from pathlib import Path

st.set_page_config(page_title="AI Architectural Analyzer ENTERPRISE", page_icon="🏗️", layout="wide")

# Initialize session state
if 'zones' not in st.session_state:
    st.session_state.zones = []

def process_file(uploaded_file):
    """Process uploaded file with enterprise precision"""
    if not uploaded_file:
        return None
    
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name
        
        if file_name.endswith('.dxf'):
            # DXF files
            from src.enterprise_dxf_parser import EnterpriseDXFParser
            parser = EnterpriseDXFParser()
            result = parser.parse_dxf_file(temp_file_path)
            zones = result.get('rooms', [])
            
        elif file_name.endswith('.dwg'):
            # DWG files
            from src.enhanced_dwg_parser import EnhancedDWGParser
            parser = EnhancedDWGParser()
            result = parser.parse_file(temp_file_path)
            zones = result.get('zones', [])
            
        else:
            raise Exception(f"Unsupported file type: {Path(file_name).suffix}")
        
        os.unlink(temp_file_path)
        
        if not zones:
            raise Exception("No architectural zones found in file")
        
        return zones
        
    except Exception as e:
        st.error(f"Enterprise processing failed: {str(e)}")
        return None

def main():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; margin-bottom: 30px; border-radius: 15px;'>
        <h1>🏗️ AI ARCHITECTURAL ANALYZER ENTERPRISE</h1>
        <h3>Real Enterprise-Grade Architectural Analysis</h3>
        <p>Only Real Zone Detection • No Fallbacks • Professional Results</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("🎛️ ENTERPRISE CONTROLS")
        
        uploaded_file = st.file_uploader(
            "📤 Upload Enterprise File",
            type=['dwg', 'dxf'],
            help="Upload DWG or DXF files for enterprise processing"
        )
        
        if uploaded_file:
            st.success(f"📁 {uploaded_file.name}")
            st.info(f"📊 Size: {len(uploaded_file.getvalue()) / 1024:.1f} KB")
            
            if st.button("🚀 ENTERPRISE PROCESSING", type="primary"):
                with st.spinner("Processing with enterprise precision..."):
                    zones = process_file(uploaded_file)
                    if zones:
                        st.session_state.zones = zones
                        st.success(f"✅ Enterprise processing complete! {len(zones)} zones detected")
                        st.rerun()
    
    if st.session_state.zones:
        st.subheader("📊 Enterprise Analysis Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Zones Detected", len(st.session_state.zones))
        with col2:
            total_area = sum(zone.get('area', 0) for zone in st.session_state.zones)
            st.metric("Total Area", f"{total_area:.1f} m²")
        with col3:
            st.metric("Processing Mode", "ENTERPRISE")
        
        # Display zones
        for i, zone in enumerate(st.session_state.zones):
            with st.expander(f"Zone {i+1}: {zone.get('zone_type', 'Room')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Area:** {zone.get('area', 0):.1f} m²")
                    st.write(f"**Layer:** {zone.get('layer', 'Unknown')}")
                with col2:
                    st.write(f"**Points:** {len(zone.get('points', []))}")
                    st.write(f"**Method:** {zone.get('parsing_method', 'Unknown')}")
    else:
        st.markdown("""
        ## 🌟 Welcome to Enterprise Mode
        
        ### 🎯 **Real Enterprise Features:**
        - ✅ **Real Zone Detection** - Only actual architectural data
        - ✅ **No Fallbacks** - Genuine parsing or failure
        - ✅ **DWG/DXF Support** - Proper file type routing
        - ✅ **Enterprise Validation** - Professional standards
        
        ### 📁 **Supported Formats:**
        - **DXF Files** - Enterprise DXF parser with precision detection
        - **DWG Files** - Enhanced DWG parser with multiple strategies
        
        ### 🚀 **Upload a file to begin enterprise analysis!**
        """)

if __name__ == "__main__":
    main()