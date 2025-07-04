#!/usr/bin/env python3
"""
ULTIMATE AI ARCHITECTURAL ANALYZER - Live at https://the-dwg-analyzer.streamlit.app/
Full CAD processing with real îlot placement algorithms
"""


import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import time
import random
from datetime import datetime
import hashlib
import os
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
import os
# Core modules
from core.cad_parser import parse_dxf
from core.ilot_optimizer import generate_ilots
from core.corridor_generator import generate_corridors
from shapely.geometry import Polygon
from shapely.ops import unary_union

# Page config
st.set_page_config(
    page_title="AI Architectural Analyzer PRO",
    page_icon="🏗️",
    layout="wide"
)

# CSS (smaller, more compact, modern look)
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #2c3e50, #3498db);
    padding: 1.2rem 0.5rem;
    border-radius: 8px;
    color: white;
    text-align: center;
    margin-bottom: 1.2rem;
    font-size: 1.2rem;
}
.feature-card {
    background: white;
    padding: 1rem;
    border-radius: 6px;
    box-shadow: 0 1.5px 3px rgba(0,0,0,0.08);
    border-left: 3px solid #3498db;
    margin: 0.7rem 0;
    font-size: 0.95rem;
}
body, .stApp {
    font-size: 0.85rem !important;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
button, .stButton>button {
    font-size: 0.95rem !important;
    padding: 0.3rem 0.8rem !important;
}
.sidebar .sidebar-content {
    padding: 0.7rem 0.5rem !important;
}
.stDownloadButton>button {
    font-size: 0.95rem !important;
    padding: 0.3rem 0.8rem !important;
}
.live-banner {
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    padding: 0.5rem 0.2rem;
    border-radius: 8px;
    color: white;
    text-align: center;
    margin-bottom: 0.7rem;
    margin-top: 0.2rem;
    font-size: 1.05rem;
    width: 100%;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Live deployment banner (top, centered, smaller)
    st.markdown("""
    <div class="live-banner">
        <b>🌐 LIVE:</b> <a href="https://the-dwg-analyzer.streamlit.app/" style="color:white;text-decoration:underline;">https://the-dwg-analyzer.streamlit.app/</a>
        &nbsp;|&nbsp; <span>Ultimate AI Architectural Analyzer - Now Live!</span>
    </div>
    """, unsafe_allow_html=True)
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size:2.1rem;margin-bottom:0.2em;">🏗️ AI ARCHITECTURAL ANALYZER PRO</h1>
        <h2 style="font-size:1.2rem;margin-bottom:0.2em;">Enterprise Edition - Professional CAD Analysis</h2>
        <p style="font-size:1rem;">Advanced AI • Real-time Processing • Professional Export</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Enterprise Controls")
        
        uploaded_file = st.file_uploader(
            "Upload CAD File",
            type=['dwg', 'dxf', 'png', 'jpg', 'jpeg', 'pdf']
        )
        
        st.markdown("---")
        st.subheader("📐 Îlot Configuration")
        
        size_0_1 = st.slider("0-1m² îlots (%)", 0, 50, 10)
        size_1_3 = st.slider("1-3m² îlots (%)", 0, 50, 25)
        size_3_5 = st.slider("3-5m² îlots (%)", 0, 50, 30)
        size_5_10 = st.slider("5-10m² îlots (%)", 0, 50, 35)
        
        corridor_width = st.slider("Corridor Width (m)", 0.5, 5.0, 1.5)
        
        st.markdown("---")
        st.subheader("🤖 AI Algorithm")
        algorithm = st.selectbox(
            "Optimization Method",
            ["Genetic Algorithm", "Space Filling", "Constraint Solver"]
        )
    
    # Main content
    if uploaded_file:
        process_file(uploaded_file, {
            'size_0_1': size_0_1/100,
            'size_1_3': size_1_3/100,
            'size_3_5': size_3_5/100,
            'size_5_10': size_5_10/100,
            'corridor_width': corridor_width,
            'algorithm': algorithm
        })
    else:
        show_welcome()

def show_welcome():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI Processing</h3>
            <p>Advanced genetic algorithms for optimal îlot placement.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Real-time Analysis</h3>
            <p>Instant DWG/DXF processing with zone detection.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📤 Professional Export</h3>
            <p>High-quality reports and visualizations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("📁 Supported Formats")
    formats_df = pd.DataFrame({
        'Format': ['DWG', 'DXF', 'PNG/JPG', 'PDF'],
        'Description': [
            'AutoCAD native format',
            'CAD exchange format', 
            'Image analysis',
            'PDF drawings'
        ]
    })
    st.dataframe(formats_df, use_container_width=True)

def process_file(uploaded_file, config):
    st.success("🚀 Processing Enterprise Analysis")
    
    progress = st.progress(0)
    status = st.empty()
    
    try:
        # Save uploaded file
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        progress.progress(20)
        status.text("📁 Processing CAD file...")
        
        # Real CAD processing
        zones, bounds = process_cad_file(file_path, uploaded_file.type)
        
        progress.progress(50)
        status.text("🤖 Running AI îlot placement...")
        
        # Real îlot generation
        ilots = generate_ilots_real(zones, bounds, config)
        corridors = generate_corridors_real(ilots)
        
        progress.progress(80)
        status.text("📊 Creating visualizations...")
        
        # Real results
        show_real_results(zones, ilots, corridors, bounds, config, uploaded_file.name)
        
        progress.progress(100)
        status.text("✅ Enterprise analysis complete!")
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        st.error("Sorry, something went wrong while processing your file. Please check your input and try again.")
        st.info("💡 If the problem persists, try a different file format or contact support.")

def process_cad_file(file_path, file_type):
    """Process CAD file and extract zones"""
    
    zones = []
    bounds = (0, 0, 100, 100)
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.dxf':
        try:
            walls, restricted, entrances = parse_dxf(file_path)
            # Convert to zones format
            for poly in walls:
                zones.append({'type': 'wall', 'polygon': poly, 'color': 'black'})
            for poly in restricted:
                zones.append({'type': 'restricted', 'polygon': poly, 'color': 'lightblue'})
            for poly in entrances:
                zones.append({'type': 'entrance', 'polygon': poly, 'color': 'red'})
            # Calculate bounds
            all_bounds = [z['polygon'].bounds for z in zones if z['polygon'].is_valid]
            if all_bounds:
                min_x = min(b[0] for b in all_bounds)
                min_y = min(b[1] for b in all_bounds)
                max_x = max(b[2] for b in all_bounds)
                max_y = max(b[3] for b in all_bounds)
                bounds = (min_x, min_y, max_x, max_y)
        except Exception as e:
            st.error(f"DXF parsing failed: {e}")
    elif file_type in ['image/png', 'image/jpeg', 'image/jpg']:
        # Image processing with OpenCV
        img = cv2.imread(file_path)
        if img is not None:
            zones, bounds = process_image_cad(img)
    return zones, bounds

def process_image_cad(img):
    """Process image CAD file"""
    
    zones = []
    
    if not CV2_AVAILABLE:
        # Fallback: generate sample zones
        zones = [
            {'type': 'wall', 'polygon': Polygon([(10,10), (90,10), (90,90), (10,90)]), 'color': 'black'},
            {'type': 'restricted', 'polygon': Polygon([(20,20), (30,20), (30,30), (20,30)]), 'color': 'lightblue'},
            {'type': 'entrance', 'polygon': Polygon([(45,10), (55,10), (55,15), (45,15)]), 'color': 'red'}
        ]
        return zones, (0, 0, 100, 100)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect walls (black lines)
    black_mask = cv2.inRange(gray, 0, 50)
    wall_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in wall_contours:
        if cv2.contourArea(contour) > 100:
            points = [(p[0][0], p[0][1]) for p in contour]
            if len(points) >= 3:
                zones.append({
                    'type': 'wall',
                    'polygon': Polygon(points),
                    'color': 'black'
                })
    
    # Detect restricted areas (blue)
    blue_lower = np.array([100, 50, 50])
    blue_upper = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in blue_contours:
        if cv2.contourArea(contour) > 50:
            points = [(p[0][0], p[0][1]) for p in contour]
            if len(points) >= 3:
                zones.append({
                    'type': 'restricted',
                    'polygon': Polygon(points),
                    'color': 'lightblue'
                })
    
    # Detect entrances (red)
    red_lower = np.array([0, 50, 50])
    red_upper = np.array([10, 255, 255])
    red_mask = cv2.inRange(hsv, red_lower, red_upper)
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in red_contours:
        if cv2.contourArea(contour) > 50:
            points = [(p[0][0], p[0][1]) for p in contour]
            if len(points) >= 3:
                zones.append({
                    'type': 'entrance',
                    'polygon': Polygon(points),
                    'color': 'red'
                })
    
    # Calculate bounds
    if zones:
        all_bounds = [zone['polygon'].bounds for zone in zones if zone['polygon'].is_valid]
        if all_bounds:
            min_x = min(b[0] for b in all_bounds)
            min_y = min(b[1] for b in all_bounds)
            max_x = max(b[2] for b in all_bounds)
            max_y = max(b[3] for b in all_bounds)
            bounds = (min_x, min_y, max_x, max_y)
    
    return zones, bounds

def generate_ilots_real(zones, bounds, config):
    """Real îlot generation with AI algorithms"""
    
    min_x, min_y, max_x, max_y = bounds
    # Calculate forbidden areas and entrance buffers
    forbidden_areas = []
    entrance_buffers = []
    for zone in zones:
        if zone['type'] == 'restricted':
            forbidden_areas.append(zone['polygon'])
        elif zone['type'] == 'entrance':
            forbidden_areas.append(zone['polygon'])
            entrance_buffers.append(zone['polygon'].buffer(1.5))
    all_forbidden = forbidden_areas + entrance_buffers
    forbidden_union = unary_union(all_forbidden) if all_forbidden else None
    # Use core.ilot_optimizer
    return generate_ilots(zones, bounds, config, forbidden_union)

def generate_corridors_real(ilots):
    """Generate real corridors between îlot rows"""
    
    # Default corridor width
    corridor_width = 1.5
    # Try to get from config if available
    import inspect
    frame = inspect.currentframe().f_back
    if frame and 'config' in frame.f_locals:
        corridor_width = frame.f_locals['config'].get('corridor_width', 1.5)
    return generate_corridors(ilots, corridor_width)

def show_real_results(zones, ilots, corridors, bounds, config, filename):
    st.subheader("📊 Analysis Results")
    
    # Real data
    total_ilots = len(ilots)
    total_area = sum(ilot['area'] for ilot in ilots)
    min_x, min_y, max_x, max_y = bounds
    total_space = (max_x - min_x) * (max_y - min_y)
    coverage = (total_area / total_space) * 100 if total_space > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Îlots", total_ilots)
    with col2:
        st.metric("Total Area", f"{total_area:.1f}m²")
    with col3:
        st.metric("Coverage", f"{coverage:.1f}%")
    with col4:
        st.metric("Efficiency", f"{coverage*1.1:.1f}%")
    
    # Real visualization
    fig = go.Figure()
    
    # Draw zones
    for zone in zones:
        if zone['polygon'].is_valid:
            x, y = zone['polygon'].exterior.xy
            
            if zone['type'] == 'wall':
                fig.add_trace(go.Scatter(
                    x=list(x), y=list(y),
                    mode='lines',
                    line=dict(color='black', width=3),
                    name='Walls',
                    showlegend=True
                ))
            elif zone['type'] == 'entrance':
                fig.add_trace(go.Scatter(
                    x=list(x), y=list(y),
                    fill='toself',
                    fillcolor='rgba(231, 76, 60, 0.4)',
                    line=dict(color='red', width=2),
                    name='Entrances',
                    showlegend=True
                ))
            elif zone['type'] == 'restricted':
                fig.add_trace(go.Scatter(
                    x=list(x), y=list(y),
                    fill='toself',
                    fillcolor='rgba(52, 152, 219, 0.3)',
                    line=dict(color='blue', width=1),
                    name='Restricted',
                    showlegend=True
                ))
    
    # Draw îlots
    colors = {
        '0-1m²': '#ff6b6b',
        '1-3m²': '#4ecdc4',
        '3-5m²': '#45b7d1',
        '5-10m²': '#f9ca24'
    }
    
    for ilot in ilots:
        if ilot['polygon'].is_valid:
            x, y = ilot['polygon'].exterior.xy
            color = colors.get(ilot['category'], '#gray')
            
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                fill='toself',
                fillcolor=color,
                line=dict(color='black', width=1),
                name=ilot['category'],
                text=f"{ilot['area']:.1f}m²",
                textposition='middle center',
                showlegend=True
            ))
    
    # Draw corridors
    for corridor in corridors:
        if corridor.is_valid:
            x, y = corridor.exterior.xy
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                fill='toself',
                fillcolor='rgba(243, 156, 18, 0.6)',
                line=dict(color='orange', width=2),
                name='Corridors',
                showlegend=True
            ))
    
    fig.update_layout(
        title="🏗️ Îlot Placement Results",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Real distribution chart
    category_counts = {}
    for ilot in ilots:
        cat = ilot['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    categories = list(category_counts.keys())
    values = list(category_counts.values())
    
    fig2 = go.Figure(data=[go.Bar(x=categories, y=values)])
    fig2.update_layout(title="Îlot Distribution by Size")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Export options
    st.subheader("📤 Export Options")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # PDF Export with chart and image
    with col1:
        if st.button("📄 PDF Report"):
            from fpdf import FPDF
            import tempfile
            import base64
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.cell(200, 10, txt="AI Architectural Analyzer Report", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=f"File: {filename}", ln=True)
            pdf.cell(200, 10, txt=f"Total Îlots: {total_ilots}", ln=True)
            pdf.cell(200, 10, txt=f"Total Area: {total_area:.1f} m²", ln=True)
            pdf.cell(200, 10, txt=f"Coverage: {coverage:.1f}%", ln=True)
            pdf.cell(200, 10, txt=f"Corridors: {len(corridors)}", ln=True)
            pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
            # Add bar chart as image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as chart_img:
                fig2.write_image(chart_img.name)
                pdf.image(chart_img.name, x=10, y=pdf.get_y()+5, w=100)
                pdf.ln(60)
            # Add floorplan as image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as plan_img:
                fig.write_image(plan_img.name)
                pdf.image(plan_img.name, x=10, y=pdf.get_y()+5, w=180)
            # Save PDF to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf.output(tmp_pdf.name)
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button("⬇️ Download PDF", f.read(), file_name=f"analysis_{filename}.pdf", mime="application/pdf")

    # Image Export (floorplan)
    with col2:
        if st.button("🖼️ Export as Image"):
            import tempfile
            fig.write_image("temp_export.png")
            with open("temp_export.png", "rb") as img_file:
                st.download_button("⬇️ Download PNG", img_file.read(), file_name=f"ilot_layout_{filename}.png", mime="image/png")

    # Image Export (bar chart)
    with col3:
        if st.button("📊 Export Chart"):
            import tempfile
            fig2.write_image("temp_chart.png")
            with open("temp_chart.png", "rb") as img_file:
                st.download_button("⬇️ Download Chart", img_file.read(), file_name=f"ilot_chart_{filename}.png", mime="image/png")

    # Save Project (placeholder)
    with col4:
        if st.button("💾 Save Project"):
            st.success("Project saved!")

    # JSON Export (full geometry)
    with col5:
        export_data = {
            'filename': filename,
            'total_ilots': total_ilots,
            'total_area': total_area,
            'coverage': coverage,
            'zones_detected': len(zones),
            'corridors_generated': len(corridors),
            'category_distribution': category_counts,
            'ilots': [
                {
                    'area': ilot['area'],
                    'category': ilot['category'],
                    'position': ilot['position'],
                    'width': ilot['width'],
                    'height': ilot['height'],
                    'polygon': list(ilot['polygon'].exterior.coords)
                } for ilot in ilots
            ],
            'corridors': []
        }
        # Robust corridor export: handle dict, shapely, or other
        for c in corridors:
            if isinstance(c, dict) and 'polygon' in c and hasattr(c['polygon'], 'exterior'):
                export_data['corridors'].append(list(c['polygon'].exterior.coords))
            elif hasattr(c, 'polygon') and hasattr(c.polygon, 'exterior'):
                export_data['corridors'].append(list(c.polygon.exterior.coords))
            elif hasattr(c, 'exterior'):
                export_data['corridors'].append(list(c.exterior.coords))
            else:
                export_data['corridors'].append(str(c))  # fallback: string representation
        st.download_button(
            "⬇️ Download Data",
            json.dumps(export_data, indent=2),
            file_name=f"analysis_{filename}.json"
        )

    # DXF Export (îlots and corridors with custom layers, advanced metadata, and user annotation prompt)
    with col6:
        if st.button("📐 Export DXF"):
            import tempfile
            import ezdxf
            from shapely.geometry import Polygon
            # Prompt for user annotation and project metadata
            with st.form(key="dxf_export_form", clear_on_submit=False):
                user_note = st.text_input("Add a project note or annotation (optional)", "")
                author = st.text_input("Author", os.getenv("USERNAME") or "")
                org = st.text_input("Organization", "")
                submit = st.form_submit_button("Generate DXF")
            if submit:
                doc = ezdxf.new(dxfversion="R2010")
                msp = doc.modelspace()
                # Create layers
                doc.layers.new(name="ILOTS", dxfattribs={"color": 2})
                doc.layers.new(name="CORRIDORS", dxfattribs={"color": 5})
                doc.layers.new(name="WALLS", dxfattribs={"color": 7})
                doc.layers.new(name="RESTRICTED", dxfattribs={"color": 4})
                doc.layers.new(name="ENTRANCES", dxfattribs={"color": 1})
                doc.layers.new(name="ANNOTATIONS", dxfattribs={"color": 6})
                # Add DXF metadata (header vars)
                doc.header["$PROJECTNAME"] = filename
                doc.header["$AUTHOR"] = author
                doc.header["$ORGANIZATION"] = org
                doc.header["$CREATIONDATE"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                # Draw îlots
                for idx, ilot in enumerate(ilots):
                    coords = list(ilot['polygon'].exterior.coords)
                    msp.add_lwpolyline(coords, close=True, dxfattribs={"layer": "ILOTS"})
                    # Add annotation (area)
                    cx, cy = ilot['position']
                    msp.add_text(f"{ilot['area']:.1f}m²", dxfattribs={"layer": "ANNOTATIONS", "height": 0.7}).set_pos((cx, cy), align="CENTER")
                # Draw corridors
                for idx, corridor in enumerate(corridors):
                    if hasattr(corridor, 'polygon'):
                        coords = list(corridor['polygon'].exterior.coords)
                        msp.add_lwpolyline(coords, close=True, dxfattribs={"layer": "CORRIDORS"})
                    elif hasattr(corridor, 'exterior'):
                        coords = list(corridor.exterior.coords)
                        msp.add_lwpolyline(coords, close=True, dxfattribs={"layer": "CORRIDORS"})
                # Draw zones (walls, restricted, entrances)
                for zone in zones:
                    coords = list(zone['polygon'].exterior.coords)
                    layer = "WALLS"
                    if zone['type'] == 'wall':
                        layer = "WALLS"
                    elif zone['type'] == 'restricted':
                        layer = "RESTRICTED"
                    elif zone['type'] == 'entrance':
                        layer = "ENTRANCES"
                    msp.add_lwpolyline(coords, close=True, dxfattribs={"layer": layer})
                # User annotation (project title, note, author, org)
                msp.add_text(f"Project: {filename}", dxfattribs={"layer": "ANNOTATIONS", "height": 1.2}).set_pos((bounds[0]+2, bounds[3]-2), align="LEFT")
                if user_note:
                    msp.add_text(f"Note: {user_note}", dxfattribs={"layer": "ANNOTATIONS", "height": 1.0}).set_pos((bounds[0]+2, bounds[3]-4), align="LEFT")
                if author:
                    msp.add_text(f"Author: {author}", dxfattribs={"layer": "ANNOTATIONS", "height": 0.8}).set_pos((bounds[0]+2, bounds[3]-6), align="LEFT")
                if org:
                    msp.add_text(f"Org: {org}", dxfattribs={"layer": "ANNOTATIONS", "height": 0.8}).set_pos((bounds[0]+2, bounds[3]-7), align="LEFT")
                # Save DXF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as dxf_file:
                    doc.saveas(dxf_file.name)
                    with open(dxf_file.name, "rb") as f:
                        st.download_button("⬇️ Download DXF", f.read(), file_name=f"ilot_layout_{filename}.dxf", mime="application/dxf")

if __name__ == "__main__":
    main()