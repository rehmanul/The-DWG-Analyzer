"""
Mobile-Responsive Interface Components
"""
import streamlit as st

def inject_mobile_css():
    """Inject mobile-responsive CSS"""
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem !important;
            max-width: 100% !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.3rem 0.5rem !important;
            font-size: 0.8rem !important;
        }
        
        .stMetric {
            background: white;
            padding: 0.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 0.5rem;
        }
        
        .stSelectbox, .stNumberInput {
            margin-bottom: 0.5rem;
        }
        
        .plotly-graph-div {
            height: 300px !important;
        }
    }
    
    @media (max-width: 480px) {
        .stColumns {
            flex-direction: column !important;
        }
        
        .stColumns > div {
            width: 100% !important;
            margin-bottom: 0.5rem;
        }
        
        .plotly-graph-div {
            height: 250px !important;
        }
    }
    
    /* Touch-friendly buttons */
    .stButton > button {
        min-height: 44px;
        font-size: 1rem;
        border-radius: 8px;
    }
    
    /* Improved file uploader for mobile */
    .stFileUploader {
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def mobile_file_upload():
    """Mobile-optimized file upload"""
    st.markdown("### 📱 Upload DWG File")
    
    uploaded_file = st.file_uploader(
        "Tap to select DWG/DXF file",
        type=['dwg', 'dxf'],
        help="Maximum 50MB",
        key="mobile_upload"
    )
    
    if uploaded_file:
        file_size = uploaded_file.size / (1024 * 1024)
        st.success(f"✅ {uploaded_file.name} ({file_size:.1f} MB)")
        
        if st.button("📤 Process File", use_container_width=True):
            return uploaded_file
    
    return None

def mobile_metrics_grid(zones, analysis_results):
    """Mobile-optimized metrics display"""
    if not zones:
        return
        
    total_area = sum(zone.get('area', 0) for zone in zones)
    total_rooms = len(zones)
    
    # Single column layout for mobile
    st.metric("🏠 Total Rooms", total_rooms)
    st.metric("📐 Total Area", f"{total_area:.1f} m²")
    
    if analysis_results:
        total_furniture = analysis_results.get('total_boxes', 0)
        efficiency = analysis_results.get('optimization', {}).get('total_efficiency', 0.85) * 100
        
        st.metric("🪑 Furniture Items", total_furniture)
        st.metric("⚡ Efficiency", f"{efficiency:.1f}%")

def mobile_visualization_controls():
    """Mobile-optimized visualization controls"""
    st.markdown("### 🎨 View Options")
    
    view_type = st.radio(
        "Select View",
        ["2D Plan", "3D Model", "Construction"],
        horizontal=True,
        key="mobile_view"
    )
    
    show_furniture = st.checkbox("Show Furniture", value=True, key="mobile_furniture")
    show_labels = st.checkbox("Show Labels", value=True, key="mobile_labels")
    
    return {
        'view_type': view_type,
        'show_furniture': show_furniture,
        'show_labels': show_labels
    }

def is_mobile():
    """Detect if user is on mobile device"""
    # Simple detection based on screen width
    return st.session_state.get('is_mobile', False)

def mobile_layout_wrapper(content_func):
    """Wrapper for mobile-responsive layout"""
    inject_mobile_css()
    
    # Add mobile detection
    st.markdown("""
    <script>
    if (window.innerWidth <= 768) {
        window.parent.postMessage({type: 'mobile_detected'}, '*');
    }
    </script>
    """, unsafe_allow_html=True)
    
    return content_func()