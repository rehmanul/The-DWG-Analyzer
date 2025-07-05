"""
Enhanced Îlot Placement Application
Implements client requirements for proportional îlot placement with corridor generation
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import datetime
import json
import math

# Configure page
st.set_page_config(
    page_title="🏗️ AI Îlot Placement PRO",
    page_icon="🏗️",
    layout="wide"
)

# Import the enhanced engine
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.enhanced_ilot_engine import EnhancedIlotEngine
except ImportError:
    st.error("Enhanced Îlot Engine not found. Please check the installation.")
    st.stop()

# Initialize session state
if 'dxf_entities' not in st.session_state:
    st.session_state.dxf_entities = []
if 'detected_zones' not in st.session_state:
    st.session_state.detected_zones = {}
if 'placed_ilots' not in st.session_state:
    st.session_state.placed_ilots = []
if 'corridors' not in st.session_state:
    st.session_state.corridors = []
if 'metrics' not in st.session_state:
    st.session_state.metrics = {}

def parse_dxf_file(uploaded_file):
    """Parse DXF file and extract entities with color information"""
    try:
        import ezdxf
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Read DXF file
        doc = ezdxf.readfile(tmp_path)
        entities = []
        
        for entity in doc.modelspace():
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'LINE', 'CIRCLE', 'ARC']:
                entity_data = {
                    'type': entity.dxftype(),
                    'color': getattr(entity.dxf, 'color', 7),  # Default to white
                    'layer': getattr(entity.dxf, 'layer', '0'),
                    'geometry': []
                }
                
                # Extract geometry based on entity type
                if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    if hasattr(entity, 'get_points'):
                        points = list(entity.get_points())
                        entity_data['geometry'] = [(p[0], p[1]) for p in points]
                elif entity.dxftype() == 'LINE':
                    start = entity.dxf.start
                    end = entity.dxf.end
                    entity_data['geometry'] = [(start[0], start[1]), (end[0], end[1])]
                elif entity.dxftype() == 'CIRCLE':
                    center = entity.dxf.center
                    radius = entity.dxf.radius
                    # Create circle as polygon
                    points = []
                    for i in range(16):
                        angle = 2 * math.pi * i / 16
                        x = center[0] + radius * math.cos(angle)
                        y = center[1] + radius * math.sin(angle)
                        points.append((x, y))
                    entity_data['geometry'] = points
                
                if len(entity_data['geometry']) >= 2:
                    entities.append(entity_data)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return entities
        
    except Exception as e:
        st.error(f"Error parsing DXF file: {str(e)}")
        return []

def visualize_plan(detected_zones, placed_ilots, corridors):
    """Create interactive visualization of the îlot placement plan"""
    fig = go.Figure()
    
    # Add walls (black lines)
    for wall in detected_zones.get('walls', []):
        geometry = wall['geometry']
        if len(geometry) >= 2:
            x_coords = [p[0] for p in geometry] + [geometry[0][0]]
            y_coords = [p[1] for p in geometry] + [geometry[0][1]]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='black', width=3),
                name='Walls',
                showlegend=True
            ))
    
    # Add restricted areas (light blue)
    for restricted in detected_zones.get('restricted', []):
        geometry = restricted['geometry']
        if len(geometry) >= 3:
            x_coords = [p[0] for p in geometry]
            y_coords = [p[1] for p in geometry]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(173,216,230,0.6)',
                line=dict(color='lightblue', width=2),
                name='Restricted Areas',
                showlegend=True
            ))
    
    # Add entrances (red)
    for entrance in detected_zones.get('entrances', []):
        geometry = entrance['geometry']
        if len(geometry) >= 2:
            x_coords = [p[0] for p in geometry]
            y_coords = [p[1] for p in geometry]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(255,0,0,0.6)',
                line=dict(color='red', width=2),
                name='Entrances/Exits',
                showlegend=True
            ))
    
    # Add îlots with different colors by category
    category_colors = {
        '0-1m²': '#FF6B6B',
        '1-3m²': '#4ECDC4', 
        '3-5m²': '#45B7D1',
        '5-10m²': '#96CEB4'
    }
    
    for ilot in placed_ilots:
        if ilot.placed:
            bounds = ilot.geometry.bounds
            x_coords = [bounds[0], bounds[2], bounds[2], bounds[0], bounds[0]]
            y_coords = [bounds[1], bounds[1], bounds[3], bounds[3], bounds[1]]
            
            color = category_colors.get(ilot.category, '#34495E')
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor=color,
                line=dict(color=color, width=2),
                name=f'{ilot.category} - {ilot.area:.1f}m²',
                showlegend=True,
                text=f'{ilot.id}<br>{ilot.area:.1f}m²',
                hoverinfo='text'
            ))
    
    # Add corridors (yellow/orange)
    for corridor in corridors:
        geom = corridor['geometry']
        bounds = geom.bounds
        x_coords = [bounds[0], bounds[2], bounds[2], bounds[0], bounds[0]]
        y_coords = [bounds[1], bounds[1], bounds[3], bounds[3], bounds[1]]
        
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor='rgba(255,193,7,0.7)',
            line=dict(color='orange', width=2),
            name=f'Corridor {corridor["width"]:.0f}cm',
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title="Îlot Placement Plan with Corridors",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        showlegend=True,
        width=1000,
        height=700,
        xaxis=dict(scaleanchor="y", scaleratio=1),
        hovermode='closest'
    )
    
    return fig

def export_results_dxf(detected_zones, placed_ilots, corridors):
    """Export results to DXF format"""
    try:
        import ezdxf
        
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Add walls
        for wall in detected_zones.get('walls', []):
            geometry = wall['geometry']
            if len(geometry) >= 2:
                points = [(p[0], p[1], 0) for p in geometry]
                msp.add_lwpolyline(points, close=len(geometry) > 2, 
                                 dxfattribs={'color': 7, 'layer': 'WALLS'})
        
        # Add îlots
        for ilot in placed_ilots:
            if ilot.placed:
                bounds = ilot.geometry.bounds
                corners = [
                    (bounds[0], bounds[1], 0),
                    (bounds[2], bounds[1], 0),
                    (bounds[2], bounds[3], 0),
                    (bounds[0], bounds[3], 0)
                ]
                msp.add_lwpolyline(corners, close=True, 
                                 dxfattribs={'color': 3, 'layer': 'ILOTS'})
                
                # Add label
                center_x = (bounds[0] + bounds[2]) / 2
                center_y = (bounds[1] + bounds[3]) / 2
                msp.add_text(
                    f"{ilot.id}\n{ilot.area:.1f}m²",
                    dxfattribs={'color': 3, 'height': 0.5, 'layer': 'LABELS'}
                ).set_pos((center_x, center_y))
        
        # Add corridors
        for corridor in corridors:
            geom = corridor['geometry']
            bounds = geom.bounds
            corners = [
                (bounds[0], bounds[1], 0),
                (bounds[2], bounds[1], 0),
                (bounds[2], bounds[3], 0),
                (bounds[0], bounds[3], 0)
            ]
            msp.add_lwpolyline(corners, close=True, 
                             dxfattribs={'color': 2, 'layer': 'CORRIDORS'})
        
        # Save to bytes
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            doc.saveas(tmp.name)
            with open(tmp.name, 'rb') as f:
                dxf_data = f.read()
            os.unlink(tmp.name)
        
        return dxf_data
        
    except Exception as e:
        st.error(f"Export error: {str(e)}")
        return None

# Main UI
st.title("🏗️ AI Îlot Placement PRO")
st.markdown("**Professional îlot placement with constraint compliance and corridor generation**")

# Sidebar for configuration
with st.sidebar:
    st.header("📐 Îlot Configuration")
    
    # Profile configuration
    st.subheader("Size Distribution")
    size_0_1 = st.slider("0-1m² îlots (%)", 0, 50, 10) / 100
    size_1_3 = st.slider("1-3m² îlots (%)", 0, 50, 25) / 100
    size_3_5 = st.slider("3-5m² îlots (%)", 0, 50, 30) / 100
    size_5_10 = st.slider("5-10m² îlots (%)", 0, 50, 35) / 100
    
    # Validate percentages
    total_percent = size_0_1 + size_1_3 + size_3_5 + size_5_10
    if abs(total_percent - 1.0) > 0.01:
        st.warning(f"Total percentage: {total_percent:.1%} (should be 100%)")
    
    st.subheader("Parameters")
    total_ilots = st.number_input("Total Îlots", min_value=10, max_value=200, value=50)
    corridor_width = st.slider("Corridor Width (cm)", 80, 200, 120)

# File upload
uploaded_file = st.file_uploader("Upload DXF Plan", type=['dxf'])

if uploaded_file:
    with st.spinner("Parsing DXF file..."):
        entities = parse_dxf_file(uploaded_file)
        st.session_state.dxf_entities = entities
        st.success(f"✅ Loaded {len(entities)} entities from plan")

# Process îlot placement
if st.session_state.dxf_entities:
    
    # Configuration
    profile_config = {
        '0-1': size_0_1,
        '1-3': size_1_3,
        '3-5': size_3_5,
        '5-10': size_5_10
    }
    
    if st.button("🤖 Generate Îlot Layout", type="primary"):
        with st.spinner("Generating optimal îlot placement..."):
            
            # Initialize engine
            engine = EnhancedIlotEngine()
            
            # Process complete layout
            result = engine.process_complete_layout(
                st.session_state.dxf_entities,
                profile_config,
                total_ilots
            )
            
            if result['success']:
                st.session_state.detected_zones = result['detected_zones']
                st.session_state.placed_ilots = result['ilots']
                st.session_state.corridors = result['corridors']
                st.session_state.metrics = result['metrics']
                
                st.success(f"✅ Generated {len(result['ilots'])} îlots and {len(result['corridors'])} corridors")
            else:
                st.error("❌ Failed to generate îlot layout")

# Display results
if st.session_state.placed_ilots:
    
    # Metrics
    st.subheader("📊 Results")
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = st.session_state.metrics
    with col1:
        st.metric("Total Îlots", metrics.get('total_ilots', 0))
    with col2:
        st.metric("Placed Îlots", metrics.get('placed_ilots', 0))
    with col3:
        st.metric("Corridors", metrics.get('corridor_count', 0))
    with col4:
        placement_rate = metrics.get('placement_rate', 0)
        st.metric("Placement Rate", f"{placement_rate:.1%}")
    
    # Visualization
    st.subheader("🎨 Plan Visualization")
    fig = visualize_plan(
        st.session_state.detected_zones,
        st.session_state.placed_ilots,
        st.session_state.corridors
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.subheader("📋 Îlot Breakdown")
    
    # Create summary table
    summary_data = []
    category_counts = {}
    category_areas = {}
    
    for ilot in st.session_state.placed_ilots:
        if ilot.placed:
            category = ilot.category
            category_counts[category] = category_counts.get(category, 0) + 1
            category_areas[category] = category_areas.get(category, 0) + ilot.area
    
    for category in ['0-1m²', '1-3m²', '3-5m²', '5-10m²']:
        count = category_counts.get(category, 0)
        total_area = category_areas.get(category, 0)
        avg_area = total_area / count if count > 0 else 0
        
        summary_data.append({
            'Category': category,
            'Count': count,
            'Total Area (m²)': f"{total_area:.1f}",
            'Average Area (m²)': f"{avg_area:.1f}",
            'Percentage': f"{count / len([i for i in st.session_state.placed_ilots if i.placed]) * 100:.1f}%" if any(i.placed for i in st.session_state.placed_ilots) else "0%"
        })
    
    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True)
    
    # Export options
    st.subheader("📤 Export")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export DXF"):
            dxf_data = export_results_dxf(
                st.session_state.detected_zones,
                st.session_state.placed_ilots,
                st.session_state.corridors
            )
            if dxf_data:
                st.download_button(
                    "Download DXF File",
                    data=dxf_data,
                    file_name=f"ilot_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf",
                    mime="application/octet-stream"
                )
    
    with col2:
        if st.button("📊 Export Report"):
            # Create JSON report
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'configuration': profile_config,
                'metrics': st.session_state.metrics,
                'summary': summary_data
            }
            
            st.download_button(
                "Download JSON Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"ilot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

else:
    st.info("Upload a DXF file and configure îlot parameters to start placement")
    
    # Show example configuration
    st.subheader("💡 Example Configuration")
    st.markdown("""
    **Typical Hotel Layout:**
    - 10% small îlots (0-1m²) - Storage, utilities
    - 25% medium îlots (1-3m²) - Bathrooms, closets  
    - 30% large îlots (3-5m²) - Standard rooms
    - 35% extra large îlots (5-10m²) - Suites, common areas
    
    **Color Coding:**
    - **Black lines**: Walls (can be touched by îlots)
    - **Light blue areas**: Restricted zones (stairs, elevators)
    - **Red areas**: Entrances/exits (buffer zones)
    - **Colored rectangles**: Placed îlots by size category
    - **Orange areas**: Generated corridors
    """)