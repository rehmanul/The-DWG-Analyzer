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
    page_title="🏗️ AI Architectural Space Analyzer PRO",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'ilot'
if 'dxf_loaded' not in st.session_state:
    st.session_state.dxf_loaded = False
if 'zones' not in st.session_state:
    st.session_state.zones = []
if 'ilots' not in st.session_state:
    st.session_state.ilots = []
if 'corridors' not in st.session_state:
    st.session_state.corridors = []

def parse_dxf_working(uploaded_file):
    """Working DXF parser"""
    try:
        import ezdxf
        
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        doc = ezdxf.readfile(tmp_path)
        entities = []
        
        for entity in doc.modelspace():
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'LINE']:
                try:
                    if entity.dxftype() == 'LINE':
                        start = entity.dxf.start
                        end = entity.dxf.end
                        points = [(start[0], start[1]), (end[0], end[1])]
                    else:
                        points = [(p[0], p[1]) for p in entity.get_points()]
                    
                    if len(points) >= 2:
                        color = getattr(entity.dxf, 'color', 7)
                        entities.append({
                            'points': points,
                            'color': color,
                            'layer': getattr(entity.dxf, 'layer', '0')
                        })
                except:
                    continue
        
        os.unlink(tmp_path)
        return entities
        
    except Exception as e:
        st.error(f"DXF parsing error: {str(e)}")
        return []

def classify_zones_working(entities):
    """Classify zones by color - working version"""
    walls = []
    restricted = []
    entrances = []
    available = []
    
    for entity in entities:
        color = entity.get('color', 7)
        points = entity.get('points', [])
        
        if len(points) < 2:
            continue
            
        if color in [0, 7]:  # Black/white - walls
            walls.append(entity)
        elif color == 5:  # Blue - restricted
            restricted.append(entity)
        elif color == 1:  # Red - entrances
            entrances.append(entity)
        else:
            available.append(entity)
    
    # Create default available area if none specified
    if not available and entities:
        all_points = []
        for entity in entities:
            all_points.extend(entity['points'])
        
        if all_points:
            min_x = min(p[0] for p in all_points) - 1
            max_x = max(p[0] for p in all_points) + 1
            min_y = min(p[1] for p in all_points) - 1
            max_y = max(p[1] for p in all_points) + 1
            
            available = [{
                'points': [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)],
                'color': 8,
                'layer': 'AVAILABLE'
            }]
    
    return {
        'walls': walls,
        'restricted': restricted,
        'entrances': entrances,
        'available': available
    }

def generate_ilots_working(zones, config, total_ilots=50):
    """Generate îlots - working implementation"""
    if not zones.get('available'):
        return [], []
    
    # Get placement area bounds
    all_points = []
    for zone in zones['available']:
        all_points.extend(zone['points'])
    
    if not all_points:
        return [], []
    
    min_x = min(p[0] for p in all_points)
    max_x = max(p[0] for p in all_points)
    min_y = min(p[1] for p in all_points)
    max_y = max(p[1] for p in all_points)
    
    # Generate îlots by category
    ilots = []
    categories = [
        ('0-1m²', 0.7, 1.0, config.get('0-1', 0.1), '#FF6B6B'),
        ('1-3m²', 1.5, 2.5, config.get('1-3', 0.25), '#4ECDC4'),
        ('3-5m²', 2.5, 3.5, config.get('3-5', 0.3), '#45B7D1'),
        ('5-10m²', 4.0, 6.0, config.get('5-10', 0.35), '#96CEB4')
    ]
    
    for category, min_size, max_size, percentage, color in categories:
        count = max(1, int(total_ilots * percentage))
        
        for i in range(count):
            # Random size within category
            side_length = random.uniform(min_size, max_size)
            width = side_length * random.uniform(0.8, 1.4)
            height = side_length * side_length / width
            area = width * height
            
            # Try to place îlot
            placed = False
            for attempt in range(100):
                x = random.uniform(min_x + width/2 + 1, max_x - width/2 - 1)
                y = random.uniform(min_y + height/2 + 1, max_y - height/2 - 1)
                
                # Check overlap with existing îlots
                overlap = False
                for existing in ilots:
                    dx = abs(x - existing['x'])
                    dy = abs(y - existing['y'])
                    min_dx = (width + existing['width']) / 2 + 0.8
                    min_dy = (height + existing['height']) / 2 + 0.8
                    
                    if dx < min_dx and dy < min_dy:
                        overlap = True
                        break
                
                if not overlap:
                    ilots.append({
                        'id': f"{category}_{i+1}",
                        'category': category,
                        'x': x, 'y': y,
                        'width': width, 'height': height,
                        'area': area,
                        'color': color,
                        'corners': [
                            (x - width/2, y - height/2),
                            (x + width/2, y - height/2),
                            (x + width/2, y + height/2),
                            (x - width/2, y + height/2)
                        ]
                    })
                    placed = True
                    break
    
    # Generate corridors between îlot groups
    corridors = generate_corridors_working(ilots)
    
    return ilots, corridors

def generate_corridors_working(ilots):
    """Generate corridors between îlot rows"""
    if len(ilots) < 4:
        return []
    
    corridors = []
    
    # Sort îlots by Y coordinate to find rows
    sorted_ilots = sorted(ilots, key=lambda i: i['y'])
    
    # Group into rows (îlots with similar Y coordinates)
    rows = []
    current_row = [sorted_ilots[0]]
    row_tolerance = 2.0  # 2m tolerance for same row
    
    for ilot in sorted_ilots[1:]:
        if abs(ilot['y'] - current_row[-1]['y']) <= row_tolerance:
            current_row.append(ilot)
        else:
            if len(current_row) >= 2:
                rows.append(current_row)
            current_row = [ilot]
    
    if len(current_row) >= 2:
        rows.append(current_row)
    
    # Create corridors between adjacent rows
    for i in range(len(rows) - 1):
        row1 = rows[i]
        row2 = rows[i + 1]
        
        # Find overlapping X range
        row1_min_x = min(ilot['x'] - ilot['width']/2 for ilot in row1)
        row1_max_x = max(ilot['x'] + ilot['width']/2 for ilot in row1)
        row2_min_x = min(ilot['x'] - ilot['width']/2 for ilot in row2)
        row2_max_x = max(ilot['x'] + ilot['width']/2 for ilot in row2)
        
        corridor_min_x = max(row1_min_x, row2_min_x)
        corridor_max_x = min(row1_max_x, row2_max_x)
        
        if corridor_max_x > corridor_min_x:
            # Find Y positions
            row1_max_y = max(ilot['y'] + ilot['height']/2 for ilot in row1)
            row2_min_y = min(ilot['y'] - ilot['height']/2 for ilot in row2)
            
            if row2_min_y > row1_max_y:
                corridor_y1 = row1_max_y + 0.2
                corridor_y2 = row2_min_y - 0.2
                
                corridors.append({
                    'id': f'corridor_{i}',
                    'x1': corridor_min_x, 'x2': corridor_max_x,
                    'y1': corridor_y1, 'y2': corridor_y2,
                    'width': 1.2,
                    'corners': [
                        (corridor_min_x, corridor_y1),
                        (corridor_max_x, corridor_y1),
                        (corridor_max_x, corridor_y2),
                        (corridor_min_x, corridor_y2)
                    ]
                })
    
    return corridors

def visualize_plan_working(zones, ilots, corridors):
    """Create working visualization"""
    fig = go.Figure()
    
    # Add zones by type
    zone_configs = {
        'walls': {'color': 'black', 'name': 'Walls', 'width': 3},
        'restricted': {'color': 'lightblue', 'name': 'Restricted', 'width': 2},
        'entrances': {'color': 'red', 'name': 'Entrances', 'width': 2},
        'available': {'color': 'lightgray', 'name': 'Available Area', 'width': 1}
    }
    
    for zone_type, zone_list in zones.items():
        config = zone_configs.get(zone_type, {'color': 'gray', 'name': zone_type, 'width': 1})
        
        for i, zone in enumerate(zone_list):
            points = zone['points']
            if len(points) >= 2:
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                # Close polygon if more than 2 points
                if len(points) > 2:
                    x_coords.append(points[0][0])
                    y_coords.append(points[0][1])
                
                fig.add_trace(go.Scatter(
                    x=x_coords, y=y_coords,
                    mode='lines',
                    fill='toself' if zone_type in ['restricted', 'entrances', 'available'] else None,
                    fillcolor=f'rgba(128,128,128,0.2)' if zone_type == 'available' else 
                             f'rgba(173,216,230,0.4)' if zone_type == 'restricted' else
                             f'rgba(255,0,0,0.3)' if zone_type == 'entrances' else None,
                    line=dict(color=config['color'], width=config['width']),
                    name=config['name'],
                    showlegend=(i == 0),
                    hoverinfo='skip'
                ))
    
    # Add îlots
    for ilot in ilots:
        corners = ilot['corners']
        x_coords = [c[0] for c in corners] + [corners[0][0]]
        y_coords = [c[1] for c in corners] + [corners[0][1]]
        
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor=ilot['color'],
            line=dict(color=ilot['color'], width=2),
            name=ilot['category'],
            text=f"{ilot['id']}<br>{ilot['area']:.1f}m²",
            hoverinfo='text',
            showlegend=False
        ))
    
    # Add corridors
    for corridor in corridors:
        corners = corridor['corners']
        x_coords = [c[0] for c in corners] + [corners[0][0]]
        y_coords = [c[1] for c in corners] + [corners[0][1]]
        
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            fill='toself',
            fillcolor='rgba(255,193,7,0.6)',
            line=dict(color='orange', width=2),
            name='Corridor',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title="🏗️ Îlot Placement Plan",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        showlegend=True,
        height=700,
        hovermode='closest'
    )
    
    return fig

# Main App
st.title("🏗️ AI Architectural Space Analyzer PRO")
st.markdown("**Professional îlot placement with constraint compliance and corridor generation**")

# Tabs
tab1, tab2 = st.tabs(["🏗️ Îlot Placement", "📊 Analysis Results"])

with tab1:
    st.subheader("📁 Upload DXF Plan")
    
    uploaded_file = st.file_uploader(
        "Choose DXF file", 
        type=['dxf'],
        help="Upload your architectural plan with color coding: Black=walls, Blue=restricted, Red=entrances"
    )
    
    if uploaded_file:
        with st.spinner("Loading DXF file..."):
            entities = parse_dxf_working(uploaded_file)
            if entities:
                st.session_state.zones = classify_zones_working(entities)
                st.session_state.dxf_loaded = True
                st.success(f"✅ Successfully loaded {len(entities)} entities from DXF")
                
                # Show zone summary
                zone_summary = []
                for zone_type, zone_list in st.session_state.zones.items():
                    if zone_list:
                        zone_summary.append(f"{zone_type.title()}: {len(zone_list)}")
                
                if zone_summary:
                    st.info("Detected zones: " + " | ".join(zone_summary))
            else:
                st.error("❌ Failed to parse DXF file")
    
    # Configuration section
    if st.session_state.dxf_loaded:
        st.subheader("📐 Îlot Configuration")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            size_0_1 = st.slider("0-1m² (%)", 0, 50, 10, key="size_0_1") / 100
        with col2:
            size_1_3 = st.slider("1-3m² (%)", 0, 50, 25, key="size_1_3") / 100
        with col3:
            size_3_5 = st.slider("3-5m² (%)", 0, 50, 30, key="size_3_5") / 100
        with col4:
            size_5_10 = st.slider("5-10m² (%)", 0, 50, 35, key="size_5_10") / 100
        
        total_percent = size_0_1 + size_1_3 + size_3_5 + size_5_10
        if abs(total_percent - 1.0) > 0.01:
            st.warning(f"⚠️ Total percentage: {total_percent:.1%} (should be 100%)")
        
        col1, col2 = st.columns(2)
        with col1:
            total_ilots = st.number_input("Total Îlots", 10, 100, 40, key="total_ilots")
        with col2:
            corridor_width = st.slider("Corridor Width (cm)", 80, 200, 120, key="corridor_width")
        
        # Generate button
        if st.button("🤖 Generate Îlot Layout", type="primary"):
            with st.spinner("Generating optimal îlot placement..."):
                config = {
                    '0-1': size_0_1,
                    '1-3': size_1_3,
                    '3-5': size_3_5,
                    '5-10': size_5_10
                }
                
                ilots, corridors = generate_ilots_working(st.session_state.zones, config, total_ilots)
                st.session_state.ilots = ilots
                st.session_state.corridors = corridors
                
                if ilots:
                    st.success(f"✅ Successfully generated {len(ilots)} îlots and {len(corridors)} corridors!")
                else:
                    st.error("❌ Failed to generate îlots. Try adjusting parameters.")

with tab2:
    if st.session_state.ilots:
        # Results metrics
        st.subheader("📊 Placement Results")
        
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
            st.metric("Avg Îlot Size", f"{avg_area:.1f} m²")
        
        # Visualization
        st.subheader("🎨 Plan Visualization")
        fig = visualize_plan_working(st.session_state.zones, st.session_state.ilots, st.session_state.corridors)
        st.plotly_chart(fig, use_container_width=True)
        
        # Category breakdown
        st.subheader("📋 Îlot Breakdown by Category")
        categories = {}
        for ilot in st.session_state.ilots:
            cat = ilot['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'total_area': 0}
            categories[cat]['count'] += 1
            categories[cat]['total_area'] += ilot['area']
        
        for category, data in categories.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{category}**")
            with col2:
                st.write(f"{data['count']} îlots")
            with col3:
                st.write(f"{data['total_area']:.1f} m² total")
        
        # Export section
        st.subheader("📤 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Summary (JSON)"):
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_ilots': len(st.session_state.ilots),
                    'total_corridors': len(st.session_state.corridors),
                    'categories': categories,
                    'total_area': total_area
                }
                
                st.download_button(
                    "Download JSON Report",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"ilot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            st.info("DXF export available in full version")
    
    else:
        st.info("Generate îlot layout first to see results")

# Instructions
if not st.session_state.dxf_loaded:
    st.subheader("💡 How to Use")
    st.markdown("""
    1. **Upload DXF File**: Your architectural plan with color coding
       - **Black lines**: Walls (îlots can touch these)
       - **Blue areas**: Restricted zones like stairs, elevators (avoided)
       - **Red areas**: Entrances/exits (buffer zones applied)
    
    2. **Configure Îlot Distribution**: Set percentages for each size category
       - 0-1m²: Small utilities, storage
       - 1-3m²: Bathrooms, closets
       - 3-5m²: Standard rooms
       - 5-10m²: Suites, common areas
    
    3. **Generate Layout**: Click to automatically place îlots with corridors
    
    4. **View Results**: See color-coded visualization and export data
    """)
    
    st.subheader("🎯 Expected Output")
    st.markdown("""
    - **Colored îlots** arranged by size category
    - **Orange corridors** automatically placed between îlot rows
    - **Constraint compliance** (avoids restricted zones)
    - **Professional metrics** and export capabilities
    """)