import streamlit as st
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Polygon, box
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="🏗️ Îlot Placement FIXED", layout="wide")

# Initialize session state
if 'zones' not in st.session_state:
    st.session_state.zones = []
if 'ilots' not in st.session_state:
    st.session_state.ilots = []

def create_default_zones():
    """Create default placement zones for testing"""
    return [{
        'id': 0,
        'points': [(10, 10), (90, 10), (90, 90), (10, 90)],
        'type': 'placement_area',
        'color': 1
    }]

def simple_ilot_placement(zones, config):
    """Simple îlot placement without genetic algorithm"""
    ilots = []
    
    if not zones:
        zones = create_default_zones()
    
    # Get placement area
    zone = zones[0]
    points = zone['points']
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Calculate îlot counts
    total_area = (max_x - min_x) * (max_y - min_y)
    target_ilots = max(10, int(total_area * 0.01))  # 1% coverage
    
    counts = {
        '0-1m²': int(target_ilots * config['size_0_1']),
        '1-3m²': int(target_ilots * config['size_1_3']),
        '3-5m²': int(target_ilots * config['size_3_5']),
        '5-10m²': int(target_ilots * config['size_5_10'])
    }
    
    # Place îlots in grid
    x_pos = min_x + 5
    y_pos = min_y + 5
    spacing = 8
    
    for category, count in counts.items():
        if count == 0:
            continue
            
        # Determine size
        if category == '0-1m²':
            size = (1, 1)
        elif category == '1-3m²':
            size = (1.5, 1.5)
        elif category == '3-5m²':
            size = (2, 2)
        else:
            size = (3, 3)
        
        for i in range(count):
            if x_pos + size[0] > max_x - 5:
                x_pos = min_x + 5
                y_pos += spacing
                
            if y_pos + size[1] > max_y - 5:
                break
                
            # Create îlot
            poly = box(x_pos, y_pos, x_pos + size[0], y_pos + size[1])
            ilot = {
                'polygon': poly,
                'area': size[0] * size[1],
                'category': category,
                'position': (x_pos + size[0]/2, y_pos + size[1]/2),
                'width': size[0],
                'height': size[1]
            }
            ilots.append(ilot)
            
            x_pos += spacing
    
    return {'ilots': ilots, 'corridors': []}

def visualize_plan(zones, ilots):
    """Create visualization"""
    fig = go.Figure()
    
    # Add zones
    for zone in zones:
        points = zone['points'] + [zone['points'][0]]
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor='rgba(173,216,230,0.3)',
            line=dict(color='blue', width=2),
            name='Placement Area',
            showlegend=True
        ))
    
    # Add îlots
    colors = {'0-1m²': 'red', '1-3m²': 'green', '3-5m²': 'orange', '5-10m²': 'purple'}
    for i, ilot in enumerate(ilots):
        poly = ilot['polygon']
        x_coords, y_coords = poly.exterior.xy
        color = colors.get(ilot['category'], 'gray')
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor=f'rgba({{"red": "255,0,0", "green": "0,255,0", "orange": "255,165,0", "purple": "128,0,128"}}[color]},0.7)',
            line=dict(color=color, width=2),
            name=ilot['category'],
            showlegend=i < 4
        ))
    
    fig.update_layout(
        title="Îlot Placement Results",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        showlegend=True,
        width=800,
        height=600,
        xaxis=dict(scaleanchor="y", scaleratio=1)
    )
    
    return fig

# Main UI
st.title("🏗️ Îlot Placement FIXED")
st.markdown("**Working îlot placement with simplified algorithm**")

# Configuration
st.subheader("📐 Îlot Configuration")

col1, col2, col3, col4 = st.columns(4)
with col1:
    size_0_1 = st.slider("0-1m² îlots (%)", 0, 50, 10) / 100
with col2:
    size_1_3 = st.slider("1-3m² îlots (%)", 0, 50, 25) / 100
with col3:
    size_3_5 = st.slider("3-5m² îlots (%)", 0, 50, 30) / 100
with col4:
    size_5_10 = st.slider("5-10m² îlots (%)", 0, 50, 35) / 100

config = {
    'size_0_1': size_0_1,
    'size_1_3': size_1_3,
    'size_3_5': size_3_5,
    'size_5_10': size_5_10
}

# Generate îlots
if st.button("🤖 Generate Îlot Layout", type="primary"):
    with st.spinner("Generating îlot placement..."):
        # Use default zones if none loaded
        if not st.session_state.zones:
            st.session_state.zones = create_default_zones()
            st.info("Using default placement area (80x80m)")
        
        result = simple_ilot_placement(st.session_state.zones, config)
        st.session_state.ilots = result['ilots']
        
        st.success(f"✅ Generated {len(result['ilots'])} îlots successfully!")

# Visualization
if st.session_state.ilots or st.session_state.zones:
    st.subheader("🎨 Plan Visualization")
    
    zones = st.session_state.zones if st.session_state.zones else create_default_zones()
    fig = visualize_plan(zones, st.session_state.ilots)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    if st.session_state.ilots:
        st.subheader("📊 Results")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Îlots", len(st.session_state.ilots))
        with col2:
            total_area = sum(ilot['area'] for ilot in st.session_state.ilots)
            st.metric("Total Area", f"{total_area:.1f} m²")
        with col3:
            categories = set(ilot['category'] for ilot in st.session_state.ilots)
            st.metric("Categories", len(categories))
        with col4:
            avg_area = total_area / len(st.session_state.ilots)
            st.metric("Avg Size", f"{avg_area:.1f} m²")

else:
    st.info("Click 'Generate Îlot Layout' to start placement")