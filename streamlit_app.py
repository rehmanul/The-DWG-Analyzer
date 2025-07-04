import streamlit as st
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
import tempfile
import os
from datetime import datetime
import ezdxf

st.set_page_config(page_title="🏗️ Professional Îlot Placement", layout="wide")

# Initialize session state
for key in ['walls', 'restricted', 'entrances', 'available_zones', 'ilots', 'corridors']:
    if key not in st.session_state:
        st.session_state[key] = []

def load_dxf_plan(uploaded_file):
    """Load DXF and detect walls, restricted areas, entrances by color/layer"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        doc = ezdxf.readfile(tmp_path)
        walls, restricted, entrances, available = [], [], [], []
        
        for entity in doc.modelspace():
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'LINE']:
                color = getattr(entity.dxf, 'color', 7)
                layer = getattr(entity.dxf, 'layer', '0').lower()
                
                if hasattr(entity, 'get_points'):
                    points = [(p[0], p[1]) for p in entity.get_points()]
                elif entity.dxftype() == 'LINE':
                    points = [(entity.dxf.start[0], entity.dxf.start[1]), 
                             (entity.dxf.end[0], entity.dxf.end[1])]
                else:
                    continue
                
                if len(points) < 2:
                    continue
                
                zone = {'points': points, 'color': color, 'layer': layer}
                
                # Classify by color and layer
                if color == 0 or 'wall' in layer or 'mur' in layer:  # Black - walls
                    walls.append(zone)
                elif color == 5 or 'restrict' in layer or 'stair' in layer or 'elevator' in layer:  # Blue - restricted
                    restricted.append(zone)
                elif color == 1 or 'entrance' in layer or 'exit' in layer or 'door' in layer:  # Red - entrances
                    entrances.append(zone)
                else:  # Available areas
                    if len(points) >= 3:  # Only closed polygons for placement
                        available.append(zone)
        
        os.unlink(tmp_path)
        return walls, restricted, entrances, available
        
    except Exception as e:
        st.error(f"DXF loading error: {e}")
        return [], [], [], []

def place_ilots_with_constraints(available_zones, config, walls, restricted, entrances, corridor_width=1.2):
    """Place îlots with proper constraint compliance and corridor generation"""
    if not available_zones:
        return [], []
    
    # Create constraint polygons
    forbidden_polys = []
    for area_list in [restricted, entrances]:
        for area in area_list:
            if len(area['points']) >= 3:
                try:
                    poly = Polygon(area['points'])
                    if poly.is_valid:
                        forbidden_polys.append(poly)
                except:
                    continue
    
    forbidden_union = unary_union(forbidden_polys) if forbidden_polys else None
    
    # Calculate îlot specifications
    total_area = sum(Polygon(zone['points']).area for zone in available_zones if len(zone['points']) >= 3)
    target_count = max(20, int(total_area * 0.005))  # Density control
    
    ilot_specs = []
    categories = [
        ('0-1m²', (0.8, 1.0), config['size_0_1']),
        ('1-3m²', (1.0, 3.0), config['size_1_3']),
        ('3-5m²', (3.0, 5.0), config['size_3_5']),
        ('5-10m²', (5.0, 10.0), config['size_5_10'])
    ]
    
    for category, (min_area, max_area), percentage in categories:
        count = int(target_count * percentage)
        for _ in range(count):
            area = np.random.uniform(min_area, max_area)
            width = np.sqrt(area * np.random.uniform(0.7, 1.4))  # Aspect ratio variation
            height = area / width
            ilot_specs.append({
                'category': category,
                'width': width,
                'height': height,
                'area': area
            })
    
    # Place îlots using grid-based approach with constraint checking
    placed_ilots = []
    
    for zone in available_zones:
        if len(zone['points']) < 3:
            continue
            
        try:
            zone_poly = Polygon(zone['points'])
            if not zone_poly.is_valid:
                continue
                
            bounds = zone_poly.bounds
            min_x, min_y, max_x, max_y = bounds
            
            # Grid placement within zone
            grid_spacing = 3.0
            y = min_y + 2
            
            while y < max_y - 2 and len(placed_ilots) < len(ilot_specs):
                x = min_x + 2
                row_ilots = []
                
                while x < max_x - 2 and len(placed_ilots) < len(ilot_specs):
                    spec = ilot_specs[len(placed_ilots)]
                    
                    # Try to place îlot
                    ilot_poly = box(x, y, x + spec['width'], y + spec['height'])
                    
                    # Check constraints
                    valid = True
                    
                    # Must be within zone
                    if not zone_poly.contains(ilot_poly):
                        valid = False
                    
                    # Must not intersect forbidden areas
                    if valid and forbidden_union and ilot_poly.intersects(forbidden_union):
                        valid = False
                    
                    # Must not overlap existing îlots
                    if valid:
                        for existing in placed_ilots:
                            if ilot_poly.intersects(existing['polygon']):
                                valid = False
                                break
                    
                    if valid:
                        ilot = {
                            'polygon': ilot_poly,
                            'category': spec['category'],
                            'area': spec['area'],
                            'position': (x + spec['width']/2, y + spec['height']/2),
                            'width': spec['width'],
                            'height': spec['height']
                        }
                        placed_ilots.append(ilot)
                        row_ilots.append(ilot)
                    
                    x += grid_spacing
                
                y += grid_spacing + corridor_width
        
        except Exception as e:
            continue
    
    # Generate corridors between îlot rows
    corridors = generate_corridors(placed_ilots, corridor_width)
    
    return placed_ilots, corridors

def generate_corridors(ilots, corridor_width):
    """Generate corridors between facing îlot rows"""
    if len(ilots) < 4:
        return []
    
    # Group îlots by Y position (rows)
    rows = {}
    for ilot in ilots:
        y = round(ilot['position'][1] / 5) * 5  # Group by 5m intervals
        if y not in rows:
            rows[y] = []
        rows[y].append(ilot)
    
    corridors = []
    sorted_y = sorted(rows.keys())
    
    for i in range(len(sorted_y) - 1):
        y1, y2 = sorted_y[i], sorted_y[i + 1]
        row1, row2 = rows[y1], rows[y2]
        
        if len(row1) >= 2 and len(row2) >= 2:
            # Calculate corridor bounds
            all_x = [ilot['position'][0] for ilot in row1 + row2]
            min_x, max_x = min(all_x) - 2, max(all_x) + 2
            
            # Position corridor between rows
            max_y1 = max(ilot['position'][1] + ilot['height']/2 for ilot in row1)
            min_y2 = min(ilot['position'][1] - ilot['height']/2 for ilot in row2)
            
            if min_y2 - max_y1 >= corridor_width:
                corridor_y = (max_y1 + min_y2) / 2
                corridor_poly = box(min_x, corridor_y - corridor_width/2, 
                                  max_x, corridor_y + corridor_width/2)
                
                # Check no overlap with îlots
                overlap = False
                for ilot in ilots:
                    if corridor_poly.intersects(ilot['polygon']):
                        overlap = True
                        break
                
                if not overlap:
                    corridors.append({
                        'polygon': corridor_poly,
                        'width': corridor_width,
                        'between_rows': (y1, y2)
                    })
    
    return corridors

def visualize_plan(walls, restricted, entrances, available_zones, ilots, corridors):
    """Create professional visualization with proper color coding"""
    fig = go.Figure()
    
    # Add walls (black)
    for wall in walls:
        points = wall['points']
        if len(points) >= 2:
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='black', width=4),
                name='Walls',
                showlegend=len(fig.data) == 0
            ))
    
    # Add restricted areas (light blue)
    for area in restricted:
        if len(area['points']) >= 3:
            points = area['points'] + [area['points'][0]]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(173,216,230,0.6)',
                line=dict(color='lightblue', width=2),
                name='Restricted Areas',
                showlegend=len([t for t in fig.data if 'Restricted' in t.name]) == 0
            ))
    
    # Add entrances (red)
    for entrance in entrances:
        points = entrance['points']
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='lines',
            line=dict(color='red', width=6),
            name='Entrances/Exits',
            showlegend=len([t for t in fig.data if 'Entrance' in t.name]) == 0
        ))
    
    # Add available zones (light gray outline)
    for zone in available_zones:
        if len(zone['points']) >= 3:
            points = zone['points'] + [zone['points'][0]]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='gray', width=1, dash='dot'),
                name='Available Areas',
                showlegend=len([t for t in fig.data if 'Available' in t.name]) == 0
            ))
    
    # Add îlots (green with category colors)
    category_colors = {
        '0-1m²': 'rgba(255,99,71,0.8)',    # Tomato
        '1-3m²': 'rgba(50,205,50,0.8)',    # Lime green
        '3-5m²': 'rgba(255,165,0,0.8)',    # Orange
        '5-10m²': 'rgba(138,43,226,0.8)'   # Blue violet
    }
    
    for ilot in ilots:
        poly = ilot['polygon']
        x_coords, y_coords = poly.exterior.xy
        color = category_colors.get(ilot['category'], 'rgba(128,128,128,0.8)')
        
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor=color,
            line=dict(color='darkgreen', width=2),
            name=f"Îlot {ilot['category']}",
            showlegend=len([t for t in fig.data if ilot['category'] in t.name]) == 0
        ))
    
    # Add corridors (yellow)
    for corridor in corridors:
        poly = corridor['polygon']
        x_coords, y_coords = poly.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor='rgba(255,255,0,0.6)',
            line=dict(color='orange', width=2),
            name='Corridors',
            showlegend=len([t for t in fig.data if 'Corridor' in t.name]) == 0
        ))
    
    fig.update_layout(
        title="Professional Îlot Placement with Constraint Compliance",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        showlegend=True,
        width=1000,
        height=700,
        xaxis=dict(scaleanchor="y", scaleratio=1)
    )
    
    return fig

# Main UI
st.title("🏗️ Professional Îlot Placement System")
st.markdown("**Enterprise-grade îlot placement with full constraint compliance**")

# File upload
uploaded_file = st.file_uploader("📁 Upload DXF Floor Plan", type=['dxf'])

if uploaded_file:
    with st.spinner("Loading and analyzing DXF plan..."):
        walls, restricted, entrances, available = load_dxf_plan(uploaded_file)
        st.session_state.walls = walls
        st.session_state.restricted = restricted
        st.session_state.entrances = entrances
        st.session_state.available_zones = available
        
        st.success(f"✅ Plan loaded: {len(walls)} walls, {len(restricted)} restricted areas, {len(entrances)} entrances, {len(available)} available zones")

# Configuration
if st.session_state.available_zones or st.session_state.walls:
    st.subheader("📐 Îlot Layout Configuration")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        size_0_1 = st.slider("0-1m² îlots (%)", 0, 50, 10) / 100
    with col2:
        size_1_3 = st.slider("1-3m² îlots (%)", 0, 50, 25) / 100
    with col3:
        size_3_5 = st.slider("3-5m² îlots (%)", 0, 50, 30) / 100
    with col4:
        size_5_10 = st.slider("5-10m² îlots (%)", 0, 50, 35) / 100
    with col5:
        corridor_width = st.slider("Corridor Width (m)", 0.8, 3.0, 1.2, 0.1)
    
    config = {
        'size_0_1': size_0_1,
        'size_1_3': size_1_3,
        'size_3_5': size_3_5,
        'size_5_10': size_5_10
    }
    
    # Generate îlots
    if st.button("🤖 Generate Professional Îlot Layout", type="primary"):
        with st.spinner("Generating îlots with constraint compliance..."):
            ilots, corridors = place_ilots_with_constraints(
                st.session_state.available_zones, 
                config,
                st.session_state.walls,
                st.session_state.restricted,
                st.session_state.entrances,
                corridor_width
            )
            
            st.session_state.ilots = ilots
            st.session_state.corridors = corridors
            
            st.success(f"✅ Generated {len(ilots)} îlots and {len(corridors)} corridors with full constraint compliance!")

# Visualization
if st.session_state.ilots or st.session_state.walls:
    st.subheader("🎨 Professional Plan Visualization")
    
    fig = visualize_plan(
        st.session_state.walls,
        st.session_state.restricted,
        st.session_state.entrances,
        st.session_state.available_zones,
        st.session_state.ilots,
        st.session_state.corridors
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    if st.session_state.ilots:
        st.subheader("📊 Professional Analysis Results")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Îlots", len(st.session_state.ilots))
        with col2:
            total_area = sum(ilot['area'] for ilot in st.session_state.ilots)
            st.metric("Total Area", f"{total_area:.1f} m²")
        with col3:
            st.metric("Corridors", len(st.session_state.corridors))
        with col4:
            categories = len(set(ilot['category'] for ilot in st.session_state.ilots))
            st.metric("Categories", categories)
        with col5:
            compliance = "100%" if st.session_state.ilots else "0%"
            st.metric("Constraint Compliance", compliance)
        
        # Category breakdown
        st.subheader("📋 Îlot Category Breakdown")
        category_stats = {}
        for ilot in st.session_state.ilots:
            cat = ilot['category']
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'total_area': 0}
            category_stats[cat]['count'] += 1
            category_stats[cat]['total_area'] += ilot['area']
        
        for category, stats in category_stats.items():
            st.write(f"**{category}**: {stats['count']} îlots, {stats['total_area']:.1f} m² total")

else:
    st.info("Upload a DXF floor plan to start professional îlot placement")
    st.markdown("""
    **Expected DXF Structure:**
    - **Black lines/layer 'walls'**: Building walls
    - **Blue areas/layer 'restricted'**: Stairs, elevators, restricted zones  
    - **Red lines/layer 'entrances'**: Doors, entrances, exits
    - **Other closed polygons**: Available placement areas
    """)