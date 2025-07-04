import streamlit as st
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import tempfile
import os
from pathlib import Path
from datetime import datetime
import json

# Configure page
st.set_page_config(
    page_title="🏗️ AI Îlot Placement PRO",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if 'zones' not in st.session_state:
    st.session_state.zones = []
if 'ilots' not in st.session_state:
    st.session_state.ilots = []
if 'corridors' not in st.session_state:
    st.session_state.corridors = []

def create_placement_zones_from_dxf(file_path):
    """Create placement zones from DXF entities"""
    try:
        import ezdxf
        doc = ezdxf.readfile(file_path)
        zones = []
        
        # Extract boundaries from polylines/rectangles
        for entity in doc.modelspace():
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'LINE']:
                try:
                    if hasattr(entity, 'get_points'):
                        points = list(entity.get_points())
                        if len(points) >= 3:
                            zone = {
                                'id': len(zones),
                                'points': [(p[0], p[1]) for p in points],
                                'type': 'placement_area',
                                'color': getattr(entity.dxf, 'color', 1)
                            }
                            zones.append(zone)
                except:
                    continue
        
        # If no polylines, create default placement area
        if not zones:
            zones = [{
                'id': 0,
                'points': [(0, 0), (50, 0), (50, 30), (0, 30)],
                'type': 'placement_area',
                'color': 1
            }]
        
        return zones
    except Exception as e:
        st.error(f"DXF parsing error: {e}")
        return []

def detect_zone_types(zones):
    """Detect walls, restricted areas, and entrances by color"""
    walls = []
    restricted = []
    entrances = []
    available = []
    
    for zone in zones:
        color = zone.get('color', 1)
        if color == 1 or color == 7:  # Black/white - walls
            walls.append(zone)
        elif color == 5:  # Blue - restricted
            restricted.append(zone)
        elif color == 1:  # Red - entrances
            entrances.append(zone)
        else:
            available.append(zone)
    
    return {
        'walls': walls,
        'restricted': restricted, 
        'entrances': entrances,
        'available': available if available else zones
    }

def generate_ilots_genetic(available_zones, config, forbidden_areas=None):
    """Generate îlots using genetic algorithm"""
    from core.ilot_optimizer import generate_ilots
    
    if not available_zones:
        return {'ilots': [], 'corridors': []}
    
    # Calculate bounds from available zones
    all_points = []
    for zone in available_zones:
        all_points.extend(zone['points'])
    
    if not all_points:
        return {'ilots': [], 'corridors': []}
    
    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    bounds = (min_x, min_y, max_x, max_y)
    
    # Create forbidden union
    forbidden_union = None
    if forbidden_areas:
        forbidden_polys = []
        for area in forbidden_areas:
            try:
                poly = Polygon(area['points'])
                forbidden_polys.append(poly)
            except:
                continue
        if forbidden_polys:
            forbidden_union = unary_union(forbidden_polys)
    
    # Generate îlots
    result = generate_ilots(available_zones, bounds, config, forbidden_union)
    return result

def visualize_plan(zones, ilots, corridors, zone_types):
    """Create interactive visualization"""
    fig = go.Figure()
    
    # Add walls (black)
    for wall in zone_types['walls']:
        points = wall['points'] + [wall['points'][0]]  # Close polygon
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor='rgba(0,0,0,0.8)',
            line=dict(color='black', width=3),
            name='Walls',
            showlegend=True
        ))
    
    # Add restricted areas (light blue)
    for restricted in zone_types['restricted']:
        points = restricted['points'] + [restricted['points'][0]]
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor='rgba(173,216,230,0.6)',
            line=dict(color='lightblue', width=2),
            name='Restricted Areas',
            showlegend=True
        ))
    
    # Add entrances (red)
    for entrance in zone_types['entrances']:
        points = entrance['points'] + [entrance['points'][0]]
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor='rgba(255,0,0,0.6)',
            line=dict(color='red', width=2),
            name='Entrances/Exits',
            showlegend=True
        ))
    
    # Add îlots (green)
    for i, ilot in enumerate(ilots):
        poly = ilot['polygon']
        x_coords, y_coords = poly.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor='rgba(34,139,34,0.7)',
            line=dict(color='green', width=2),
            name=f'Îlot {i+1} ({ilot["category"]})',
            showlegend=i < 5  # Only show first 5 in legend
        ))
    
    # Add corridors (yellow)
    for i, corridor in enumerate(corridors):
        if hasattr(corridor, 'polygon'):
            poly = corridor['polygon']
        else:
            poly = corridor
        x_coords, y_coords = poly.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor='rgba(255,255,0,0.5)',
            line=dict(color='orange', width=2),
            name=f'Corridor {i+1}',
            showlegend=i < 3
        ))
    
    fig.update_layout(
        title="Îlot Placement Plan",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        showlegend=True,
        width=1000,
        height=700,
        xaxis=dict(scaleanchor="y", scaleratio=1)
    )
    
    return fig

def export_results(zones, ilots, corridors, config):
    """Export results to DXF format"""
    try:
        import ezdxf
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Add îlots
        for i, ilot in enumerate(ilots):
            poly = ilot['polygon']
            points = list(poly.exterior.coords)
            msp.add_lwpolyline(points, close=True, dxfattribs={'color': 3})  # Green
            
            # Add label
            center = poly.centroid
            msp.add_text(
                f"Îlot {i+1}\n{ilot['category']}\n{ilot['area']:.1f}m²",
                dxfattribs={'color': 3, 'height': 0.5}
            ).set_pos((center.x, center.y))
        
        # Add corridors
        for i, corridor in enumerate(corridors):
            if hasattr(corridor, 'polygon'):
                poly = corridor['polygon']
            else:
                poly = corridor
            points = list(poly.exterior.coords)
            msp.add_lwpolyline(points, close=True, dxfattribs={'color': 2})  # Yellow
        
        # Save to bytes
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            doc.saveas(tmp.name)
            with open(tmp.name, 'rb') as f:
                dxf_data = f.read()
            os.unlink(tmp.name)
        
        return dxf_data
    except Exception as e:
        st.error(f"Export error: {e}")
        return None

# Main UI
st.title("🏗️ AI Îlot Placement PRO")
st.markdown("**Professional îlot placement with constraint compliance and corridor generation**")

# File upload
uploaded_file = st.file_uploader("Upload DXF Plan", type=['dxf'])

if uploaded_file:
    with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    zones = create_placement_zones_from_dxf(tmp_path)
    os.unlink(tmp_path)
    
    if zones:
        st.session_state.zones = zones
        st.success(f"✅ Loaded {len(zones)} zones from plan")

# Configuration
if st.session_state.zones:
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
    
    corridor_width = st.slider("Corridor Width (m)", 0.5, 5.0, 1.2)
    
    config = {
        'size_0_1': size_0_1,
        'size_1_3': size_1_3,
        'size_3_5': size_3_5,
        'size_5_10': size_5_10
    }
    
    # Generate îlots
    if st.button("🤖 Generate Îlot Layout", type="primary"):
        with st.spinner("Generating optimal îlot placement..."):
            zone_types = detect_zone_types(st.session_state.zones)
            
            # Combine restricted areas and entrances as forbidden
            forbidden_areas = zone_types['restricted'] + zone_types['entrances']
            
            result = generate_ilots_genetic(
                zone_types['available'], 
                config, 
                forbidden_areas
            )
            
            st.session_state.ilots = result['ilots']
            st.session_state.corridors = result['corridors']
            
            st.success(f"✅ Generated {len(result['ilots'])} îlots and {len(result['corridors'])} corridors")

# Visualization
if st.session_state.ilots:
    st.subheader("🎨 Plan Visualization")
    
    zone_types = detect_zone_types(st.session_state.zones)
    fig = visualize_plan(
        st.session_state.zones, 
        st.session_state.ilots, 
        st.session_state.corridors,
        zone_types
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    st.subheader("📊 Results")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Îlots", len(st.session_state.ilots))
    with col2:
        total_area = sum(ilot['area'] for ilot in st.session_state.ilots)
        st.metric("Total Area", f"{total_area:.1f} m²")
    with col3:
        st.metric("Corridors", len(st.session_state.corridors))
    with col4:
        avg_area = total_area / len(st.session_state.ilots) if st.session_state.ilots else 0
        st.metric("Avg Îlot Size", f"{avg_area:.1f} m²")
    
    # Export
    st.subheader("📤 Export")
    if st.button("📥 Export DXF"):
        dxf_data = export_results(
            st.session_state.zones,
            st.session_state.ilots,
            st.session_state.corridors,
            config
        )
        if dxf_data:
            st.download_button(
                "Download DXF File",
                data=dxf_data,
                file_name=f"ilot_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf",
                mime="application/octet-stream"
            )

else:
    st.info("Upload a DXF file to start îlot placement")