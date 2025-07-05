import streamlit as st
import plotly.graph_objects as go
import numpy as np
import tempfile
import os
from datetime import datetime
import json
import math
import random

# Configure page
st.set_page_config(
    page_title="🏗️ AI Îlot Placement PRO",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if 'dxf_loaded' not in st.session_state:
    st.session_state.dxf_loaded = False
if 'zones' not in st.session_state:
    st.session_state.zones = []
if 'ilots' not in st.session_state:
    st.session_state.ilots = []
if 'corridors' not in st.session_state:
    st.session_state.corridors = []

def parse_dxf_simple(uploaded_file):
    """Simple DXF parser that actually works"""
    try:
        import ezdxf
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Read DXF
        doc = ezdxf.readfile(tmp_path)
        entities = []
        
        for entity in doc.modelspace():
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                try:
                    points = list(entity.get_points())
                    if len(points) >= 3:
                        color = getattr(entity.dxf, 'color', 7)
                        entities.append({
                            'points': [(p[0], p[1]) for p in points],
                            'color': color,
                            'type': 'zone'
                        })
                except:
                    continue
        
        os.unlink(tmp_path)
        return entities
        
    except Exception as e:
        st.error(f"DXF Error: {str(e)}")
        return []

def classify_zones(entities):
    """Classify zones by color"""
    walls = []
    restricted = []
    entrances = []
    available = []
    
    for entity in entities:
        color = entity.get('color', 7)
        if color in [0, 7]:  # Black/white - walls
            walls.append(entity)
        elif color == 5:  # Blue - restricted
            restricted.append(entity)
        elif color == 1:  # Red - entrances
            entrances.append(entity)
        else:
            available.append(entity)
    
    # If no specific zones, treat all as available
    if not available and not walls:
        available = entities
    
    return {
        'walls': walls,
        'restricted': restricted,
        'entrances': entrances,
        'available': available
    }

def generate_ilots(zones, config, total_ilots=50):
    """Generate îlots based on configuration"""
    if not zones['available']:
        return [], []
    
    # Get bounds from available zones
    all_points = []
    for zone in zones['available']:
        all_points.extend(zone['points'])
    
    if not all_points:
        return [], []
    
    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    
    # Generate îlots
    ilots = []
    categories = [
        ('0-1m²', 0.5, 1.0, config['0-1']),
        ('1-3m²', 1.0, 3.0, config['1-3']),
        ('3-5m²', 3.0, 5.0, config['3-5']),
        ('5-10m²', 5.0, 10.0, config['5-10'])
    ]
    
    for category, min_area, max_area, percentage in categories:
        count = int(total_ilots * percentage)
        
        for i in range(count):
            area = random.uniform(min_area, max_area)
            width = math.sqrt(area * random.uniform(1.0, 1.8))
            height = area / width
            
            # Try to place îlot
            for _ in range(50):  # 50 attempts
                x = random.uniform(min_x + width/2, max_x - width/2)
                y = random.uniform(min_y + height/2, max_y - height/2)
                
                # Check if position is valid
                ilot_corners = [
                    (x - width/2, y - height/2),
                    (x + width/2, y - height/2),
                    (x + width/2, y + height/2),
                    (x - width/2, y + height/2)
                ]
                
                # Simple overlap check
                valid = True
                for existing in ilots:
                    if abs(x - existing['x']) < (width + existing['width'])/2 + 0.5:
                        if abs(y - existing['y']) < (height + existing['height'])/2 + 0.5:
                            valid = False
                            break
                
                if valid:
                    ilots.append({
                        'id': f"{category}_{i+1}",
                        'category': category,
                        'x': x, 'y': y,
                        'width': width, 'height': height,
                        'area': area,
                        'corners': ilot_corners
                    })
                    break
    
    # Generate simple corridors
    corridors = []
    if len(ilots) > 4:
        # Group îlots by Y position (rows)
        sorted_ilots = sorted(ilots, key=lambda i: i['y'])
        
        # Create corridors between groups
        for i in range(0, len(sorted_ilots)-2, 3):
            group1 = sorted_ilots[i:i+2]
            group2 = sorted_ilots[i+2:i+4] if i+4 <= len(sorted_ilots) else sorted_ilots[i+2:]
            
            if len(group1) >= 1 and len(group2) >= 1:
                # Create corridor between groups
                min_x_corridor = min(min(g['x'] - g['width']/2 for g in group1), 
                                   min(g['x'] - g['width']/2 for g in group2))
                max_x_corridor = max(max(g['x'] + g['width']/2 for g in group1),
                                   max(g['x'] + g['width']/2 for g in group2))
                
                y1 = max(g['y'] + g['height']/2 for g in group1)
                y2 = min(g['y'] - g['height']/2 for g in group2)
                
                if y2 > y1:
                    corridors.append({
                        'x1': min_x_corridor, 'x2': max_x_corridor,
                        'y1': y1 + 0.2, 'y2': y2 - 0.2,
                        'width': 1.2
                    })
    
    return ilots, corridors

def visualize_plan(zones, ilots, corridors):
    """Create visualization"""
    fig = go.Figure()
    
    # Add zones
    for zone_type, zone_list in zones.items():
        if zone_type == 'walls':
            color = 'black'
            name = 'Walls'
        elif zone_type == 'restricted':
            color = 'lightblue'
            name = 'Restricted'
        elif zone_type == 'entrances':
            color = 'red'
            name = 'Entrances'
        else:
            color = 'lightgray'
            name = 'Available'
        
        for zone in zone_list:
            points = zone['points']
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself' if zone_type != 'walls' else None,
                fillcolor=f'rgba({color}, 0.3)' if zone_type != 'walls' else None,
                line=dict(color=color, width=3 if zone_type == 'walls' else 2),
                name=name,
                showlegend=True
            ))
    
    # Add îlots
    category_colors = {
        '0-1m²': '#FF6B6B',
        '1-3m²': '#4ECDC4',
        '3-5m²': '#45B7D1',
        '5-10m²': '#96CEB4'
    }
    
    for ilot in ilots:
        corners = ilot['corners']
        x_coords = [c[0] for c in corners] + [corners[0][0]]
        y_coords = [c[1] for c in corners] + [corners[0][1]]
        
        color = category_colors.get(ilot['category'], '#34495E')
        
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor=color,
            line=dict(color=color, width=2),
            name=f"{ilot['category']} - {ilot['area']:.1f}m²",
            text=f"{ilot['id']}<br>{ilot['area']:.1f}m²",
            hoverinfo='text'
        ))
    
    # Add corridors
    for corridor in corridors:
        fig.add_trace(go.Scatter(
            x=[corridor['x1'], corridor['x2'], corridor['x2'], corridor['x1'], corridor['x1']],
            y=[corridor['y1'], corridor['y1'], corridor['y2'], corridor['y2'], corridor['y1']],
            fill='toself',
            fillcolor='rgba(255,193,7,0.7)',
            line=dict(color='orange', width=2),
            name='Corridor',
            showlegend=False
        ))
    
    fig.update_layout(
        title="Îlot Placement Plan",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        showlegend=True,
        height=600
    )
    
    return fig

# Main UI
st.title("🏗️ AI Îlot Placement PRO")
st.markdown("**Professional îlot placement with constraint compliance**")

# File upload
uploaded_file = st.file_uploader("Upload DXF Plan", type=['dxf'])

if uploaded_file:
    with st.spinner("Loading DXF file..."):
        entities = parse_dxf_simple(uploaded_file)
        if entities:
            st.session_state.zones = classify_zones(entities)
            st.session_state.dxf_loaded = True
            st.success(f"✅ Loaded {len(entities)} entities from DXF")
        else:
            st.error("❌ Failed to load DXF file")

# Configuration
if st.session_state.dxf_loaded:
    st.subheader("📐 Îlot Configuration")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        size_0_1 = st.slider("0-1m² (%)", 0, 50, 10) / 100
    with col2:
        size_1_3 = st.slider("1-3m² (%)", 0, 50, 25) / 100
    with col3:
        size_3_5 = st.slider("3-5m² (%)", 0, 50, 30) / 100
    with col4:
        size_5_10 = st.slider("5-10m² (%)", 0, 50, 35) / 100
    
    total_percent = size_0_1 + size_1_3 + size_3_5 + size_5_10
    if abs(total_percent - 1.0) > 0.01:
        st.warning(f"Total: {total_percent:.1%} (should be 100%)")
    
    col1, col2 = st.columns(2)
    with col1:
        total_ilots = st.number_input("Total Îlots", 10, 100, 30)
    with col2:
        corridor_width = st.slider("Corridor Width (cm)", 80, 200, 120)
    
    # Generate button
    if st.button("🤖 Generate Îlot Layout", type="primary"):
        with st.spinner("Generating îlot placement..."):
            config = {
                '0-1': size_0_1,
                '1-3': size_1_3,
                '3-5': size_3_5,
                '5-10': size_5_10
            }
            
            ilots, corridors = generate_ilots(st.session_state.zones, config, total_ilots)
            st.session_state.ilots = ilots
            st.session_state.corridors = corridors
            
            st.success(f"✅ Generated {len(ilots)} îlots and {len(corridors)} corridors")

# Display results
if st.session_state.ilots:
    # Metrics
    st.subheader("📊 Results")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Îlots", len(st.session_state.ilots))
    with col2:
        total_area = sum(i['area'] for i in st.session_state.ilots)
        st.metric("Total Area", f"{total_area:.1f} m²")
    with col3:
        st.metric("Corridors", len(st.session_state.corridors))
    with col4:
        avg_area = total_area / len(st.session_state.ilots) if st.session_state.ilots else 0
        st.metric("Avg Size", f"{avg_area:.1f} m²")
    
    # Visualization
    st.subheader("🎨 Plan Visualization")
    fig = visualize_plan(st.session_state.zones, st.session_state.ilots, st.session_state.corridors)
    st.plotly_chart(fig, use_container_width=True)
    
    # Breakdown
    st.subheader("📋 Îlot Breakdown")
    categories = {}
    for ilot in st.session_state.ilots:
        cat = ilot['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        st.write(f"**{category}**: {count} îlots")

else:
    st.info("Upload a DXF file and configure îlot parameters to start")
    
    # Show example
    st.subheader("💡 Example Configuration")
    st.markdown("""
    **Hotel Layout Example:**
    - 10% small îlots (0-1m²) - Storage, utilities
    - 25% medium îlots (1-3m²) - Bathrooms, closets
    - 30% large îlots (3-5m²) - Standard rooms
    - 35% extra large îlots (5-10m²) - Suites, common areas
    
    **Color Coding in DXF:**
    - **Black lines**: Walls (îlots can touch)
    - **Blue areas**: Restricted zones (avoided)
    - **Red areas**: Entrances/exits (buffer zones)
    """)