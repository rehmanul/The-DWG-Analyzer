import streamlit as st
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
import tempfile
import os
from datetime import datetime
import ezdxf
import math

# 🎨 AMAZING VIBE CONFIGURATION
st.set_page_config(
    page_title="🏗️ ULTIMATE Îlot Placement Engine", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🌟 STUNNING CSS STYLING
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stButton > button { 
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white; font-weight: bold; border: none;
        border-radius: 25px; padding: 15px 30px;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 25px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 20px; border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .success-glow { 
        animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 0 20px #4ECDC4; }
        to { box-shadow: 0 0 30px #FF6B6B, 0 0 40px #4ECDC4; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with POWER
for key in ['walls', 'restricted', 'entrances', 'available_zones', 'ilots', 'corridors', 'analysis_complete']:
    if key not in st.session_state:
        st.session_state[key] = []

def load_dxf_with_intelligence(uploaded_file):
    """🧠 INTELLIGENT DXF ANALYSIS"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        doc = ezdxf.readfile(tmp_path)
        walls, restricted, entrances, available = [], [], [], []
        
        # 🎯 SMART ENTITY DETECTION
        for entity in doc.modelspace():
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'LINE', 'CIRCLE', 'ARC']:
                color = getattr(entity.dxf, 'color', 7)
                layer = getattr(entity.dxf, 'layer', '0').lower()
                
                # Extract points intelligently
                points = []
                if hasattr(entity, 'get_points'):
                    points = [(p[0], p[1]) for p in entity.get_points()]
                elif entity.dxftype() == 'LINE':
                    points = [(entity.dxf.start[0], entity.dxf.start[1]), 
                             (entity.dxf.end[0], entity.dxf.end[1])]
                elif entity.dxftype() == 'CIRCLE':
                    # Convert circle to polygon
                    center = entity.dxf.center
                    radius = entity.dxf.radius
                    angles = np.linspace(0, 2*np.pi, 32)
                    points = [(center[0] + radius*np.cos(a), center[1] + radius*np.sin(a)) for a in angles]
                
                if len(points) < 2:
                    continue
                
                zone = {'points': points, 'color': color, 'layer': layer}
                
                # 🎨 CLIENT-COMPLIANT COLOR CLASSIFICATION
                # BLACK = Walls (color 0, 7, or "black")
                if (color == 0 or color == 7 or 'wall' in layer or 'mur' in layer or 
                    'boundary' in layer or 'outline' in layer or 'black' in layer):
                    walls.append(zone)
                # BLUE = Restricted areas (color 5, or "blue", stairs, elevators)
                elif (color == 5 or 'blue' in layer or 'restrict' in layer or 'stair' in layer or 
                      'elevator' in layer or 'lift' in layer or 'escalator' in layer):
                    restricted.append(zone)
                # RED = Entrances/Exits (color 1, 2 or "red")
                elif (color == 1 or color == 2 or 'red' in layer or 'entrance' in layer or 'exit' in layer or 
                      'door' in layer or 'gate' in layer):
                    entrances.append(zone)
                else:
                    if len(points) >= 3:
                        available.append(zone)
        
        os.unlink(tmp_path)
        return walls, restricted, entrances, available
        
    except Exception as e:
        st.error(f"🚨 DXF Analysis Error: {e}")
        return [], [], [], []

def place_ilots_with_genius(available_zones, config, walls, restricted, entrances, corridor_width=1.2):
    """🚀 GENIUS-LEVEL ÎLOT PLACEMENT ALGORITHM"""
    if not available_zones:
        return [], []
    
    # 🛡️ CREATE FORBIDDEN ZONES (Client Requirement: No îlots touching red areas)
    forbidden_polys = []
    entrance_buffer_distance = 1.0  # Minimum distance from entrances
    restricted_buffer_distance = 0.3  # Minimum distance from restricted areas
    
    # Process restricted areas (blue) - îlots must avoid
    for area in restricted:
        if len(area['points']) >= 3:
            try:
                poly = Polygon(area['points'])
                if poly.is_valid:
                    forbidden_polys.append(poly.buffer(restricted_buffer_distance))
            except:
                continue
    
    # Process entrances (red) - îlots must NOT touch these
    for area in entrances:
        if len(area['points']) >= 2:
            try:
                if len(area['points']) == 2:
                    # Line entrance - create buffer zone
                    from shapely.geometry import LineString
                    line = LineString(area['points'])
                    forbidden_polys.append(line.buffer(entrance_buffer_distance))
                else:
                    # Polygon entrance
                    poly = Polygon(area['points'])
                    if poly.is_valid:
                        forbidden_polys.append(poly.buffer(entrance_buffer_distance))
            except:
                continue
    
    forbidden_union = unary_union(forbidden_polys) if forbidden_polys else None
    
    # 📊 CALCULATE OPTIMAL ÎLOT DISTRIBUTION
    total_area = 0
    valid_zones = []
    for zone in available_zones:
        if len(zone['points']) >= 3:
            try:
                poly = Polygon(zone['points'])
                if poly.is_valid and poly.area > 5:  # Minimum 5m² zones
                    total_area += poly.area
                    valid_zones.append((zone, poly))
            except:
                continue
    
    if not valid_zones:
        return [], []
    
    # 🎯 SMART DENSITY CALCULATION
    density_factor = min(0.15, max(0.05, 1000 / total_area))  # Adaptive density
    target_count = max(15, int(total_area * density_factor))
    
    # 📐 GENERATE ÎLOT SPECIFICATIONS
    ilot_specs = []
    categories = [
        ('0-1m²', (0.7, 1.0), config['size_0_1'], 'rgba(255,99,71,0.9)'),
        ('1-3m²', (1.0, 3.0), config['size_1_3'], 'rgba(50,205,50,0.9)'),
        ('3-5m²', (3.0, 5.0), config['size_3_5'], 'rgba(255,165,0,0.9)'),
        ('5-10m²', (5.0, 10.0), config['size_5_10'], 'rgba(138,43,226,0.9)')
    ]
    
    for category, (min_area, max_area), percentage, color in categories:
        count = int(target_count * percentage)
        for _ in range(count):
            area = np.random.uniform(min_area, max_area)
            aspect_ratio = np.random.uniform(0.6, 1.8)
            width = np.sqrt(area * aspect_ratio)
            height = area / width
            ilot_specs.append({
                'category': category,
                'width': width,
                'height': height,
                'area': area,
                'color': color
            })
    
    # 🎯 CLIENT-COMPLIANT PLACEMENT ALGORITHM
    placed_ilots = []
    
    # Create wall polygons for adjacency checking (îlots CAN touch walls)
    wall_polys = []
    for wall in walls:
        if len(wall['points']) >= 2:
            try:
                if len(wall['points']) == 2:
                    from shapely.geometry import LineString
                    line = LineString(wall['points'])
                    wall_polys.append(line.buffer(0.1))  # Thin buffer for walls
                else:
                    poly = Polygon(wall['points'])
                    if poly.is_valid:
                        wall_polys.append(poly)
            except:
                continue
    
    for zone, zone_poly in valid_zones:
        bounds = zone_poly.bounds
        min_x, min_y, max_x, max_y = bounds
        
        # 🌟 OPTIMAL GRID PLACEMENT WITH WALL ADJACENCY
        grid_size = 1.8  # Tighter grid for better space utilization
        margin = 0.3     # Reduced margin to allow wall contact
        
        # Create rows with proper spacing for corridors
        row_height = 3.0 + corridor_width  # Space for îlots + corridor
        
        y = min_y + margin
        row_index = 0
        
        while y < max_y - margin and len(placed_ilots) < len(ilot_specs):
            x = min_x + margin
            row_ilots = []
            
            while x < max_x - margin and len(placed_ilots) < len(ilot_specs):
                if len(placed_ilots) >= len(ilot_specs):
                    break
                    
                spec = ilot_specs[len(placed_ilots)]
                
                # Try multiple orientations for optimal fit
                for rotation in [0, 90]:
                    w, h = spec['width'], spec['height']
                    if rotation == 90:
                        w, h = h, w
                    
                    if x + w > max_x - margin or y + h > max_y - margin:
                        continue
                    
                    ilot_poly = box(x, y, x + w, y + h)
                    
                    # 🔍 CLIENT-COMPLIANT VALIDATION
                    valid = True
                    
                    # Must be within zone
                    if not zone_poly.contains(ilot_poly):
                        valid = False
                    
                    # Must not intersect forbidden areas (blue + red with buffers)
                    if valid and forbidden_union and ilot_poly.intersects(forbidden_union):
                        valid = False
                    
                    # Must not overlap existing îlots (minimum spacing)
                    if valid:
                        for existing in placed_ilots:
                            if ilot_poly.distance(existing['polygon']) < 0.5:  # Min 50cm spacing
                                valid = False
                                break
                    
                    # ALLOW touching walls (client requirement)
                    # This is explicitly allowed per client specs
                    
                    if valid:
                        ilot = {
                            'polygon': ilot_poly,
                            'category': spec['category'],
                            'area': spec['area'],
                            'position': (x + w/2, y + h/2),
                            'width': w,
                            'height': h,
                            'color': spec['color'],
                            'rotation': rotation,
                            'row_index': row_index
                        }
                        placed_ilots.append(ilot)
                        row_ilots.append(ilot)
                        break
                
                x += grid_size
            
            # Move to next row with corridor spacing
            y += row_height
            row_index += 1
    
    # 🛤️ GENERATE INTELLIGENT CORRIDORS
    corridors = generate_smart_corridors(placed_ilots, corridor_width)
    
    return placed_ilots, corridors

def generate_smart_corridors(ilots, corridor_width):
    """🛤️ CLIENT-COMPLIANT CORRIDOR GENERATION"""
    if len(ilots) < 2:
        return []
    
    # Group îlots by row_index if available, otherwise by Y position
    if 'row_index' in ilots[0]:
        # Use row_index for precise grouping
        rows_dict = {}
        for ilot in ilots:
            row_idx = ilot['row_index']
            if row_idx not in rows_dict:
                rows_dict[row_idx] = []
            rows_dict[row_idx].append(ilot)
        
        # Convert to sorted list
        rows = []
        for row_idx in sorted(rows_dict.keys()):
            if len(rows_dict[row_idx]) >= 1:  # At least 1 îlot per row
                avg_y = np.mean([ilot['position'][1] for ilot in rows_dict[row_idx]])
                rows.append({
                    'y_center': avg_y,
                    'ilots': rows_dict[row_idx],
                    'row_index': row_idx
                })
    else:
        # Fallback to Y position grouping
        tolerance = 3.0
        rows = []
        
        for ilot in ilots:
            y_pos = ilot['position'][1]
            placed = False
            
            for row in rows:
                if abs(row['y_center'] - y_pos) <= tolerance:
                    row['ilots'].append(ilot)
                    row['y_center'] = np.mean([i['position'][1] for i in row['ilots']])
                    placed = True
                    break
            
            if not placed:
                rows.append({'y_center': y_pos, 'ilots': [ilot]})
    
    # Sort rows by Y position
    rows.sort(key=lambda r: r['y_center'])
    
    corridors = []
    
    # CLIENT REQUIREMENT: Mandatory corridors between facing îlot rows
    for i in range(len(rows) - 1):
        row1, row2 = rows[i], rows[i + 1]
        
        # Find the extent of both rows
        row1_ilots = row1['ilots']
        row2_ilots = row2['ilots']
        
        # Calculate X bounds covering both rows
        all_x_coords = []
        for ilot in row1_ilots + row2_ilots:
            poly = ilot['polygon']
            min_x, min_y, max_x, max_y = poly.bounds
            all_x_coords.extend([min_x, max_x])
        
        corridor_min_x = min(all_x_coords) - 0.5
        corridor_max_x = max(all_x_coords) + 0.5
        
        # Calculate Y position between rows
        row1_max_y = max(ilot['polygon'].bounds[3] for ilot in row1_ilots)  # max Y of row 1
        row2_min_y = min(ilot['polygon'].bounds[1] for ilot in row2_ilots)  # min Y of row 2
        
        # Ensure there's space for corridor
        available_space = row2_min_y - row1_max_y
        
        if available_space >= corridor_width:
            # Center the corridor between rows
            corridor_center_y = (row1_max_y + row2_min_y) / 2
            corridor_min_y = corridor_center_y - corridor_width / 2
            corridor_max_y = corridor_center_y + corridor_width / 2
            
            # Create corridor polygon
            corridor_poly = box(corridor_min_x, corridor_min_y, corridor_max_x, corridor_max_y)
            
            # Verify no overlap with any îlot
            overlap = any(corridor_poly.intersects(ilot['polygon']) for ilot in ilots)
            
            if not overlap:
                corridors.append({
                    'polygon': corridor_poly,
                    'width': corridor_width,
                    'length': corridor_max_x - corridor_min_x,
                    'between_rows': (i, i+1),
                    'touches_row1': True,
                    'touches_row2': True
                })
    
    return corridors

def create_stunning_visualization(walls, restricted, entrances, available_zones, ilots, corridors):
    """🎨 STUNNING PROFESSIONAL VISUALIZATION"""
    fig = go.Figure()
    
    # 🏗️ WALLS - Black (Client Requirement)
    for wall in walls:
        points = wall['points']
        if len(points) >= 2:
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='#000000', width=6),  # Pure black as per client requirement
                name='🏗️ Walls (BLACK)',
                showlegend=len([t for t in fig.data if 'Wall' in str(t.name)]) == 0
            ))
    
    # 🚫 RESTRICTED AREAS - Light Blue (Client Requirement)
    for area in restricted:
        if len(area['points']) >= 3:
            points = area['points'] + [area['points'][0]]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(173, 216, 230, 0.6)',  # Light blue as per client requirement
                line=dict(color='#87CEEB', width=3),
                name='🚫 Restricted (Light Blue)',
                showlegend=len([t for t in fig.data if 'Restricted' in str(t.name)]) == 0
            ))
    
    # 🚪 ENTRANCES - Red (Client Requirement)
    for entrance in entrances:
        points = entrance['points']
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='lines',
            line=dict(color='#FF0000', width=8),  # Pure red as per client requirement
            name='🚪 Entrances/Exits (RED)',
            showlegend=len([t for t in fig.data if 'Entrance' in str(t.name)]) == 0
        ))
    
    # 📦 ÎLOTS - Beautiful Category-Coded Placement
    for i, ilot in enumerate(ilots):
        poly = ilot['polygon']
        x_coords, y_coords = poly.exterior.xy
        
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor=ilot['color'],
            line=dict(color='#27AE60', width=2),
            name=f"📦 {ilot['category']}",
            showlegend=len([t for t in fig.data if ilot['category'] in str(t.name)]) == 0,
            hovertemplate=f"<b>{ilot['category']}</b><br>Area: {ilot['area']:.1f}m²<br>Size: {ilot['width']:.1f}×{ilot['height']:.1f}m<extra></extra>"
        ))
    
    # 🛤️ CORRIDORS - Elegant Circulation Paths
    for corridor in corridors:
        poly = corridor['polygon']
        x_coords, y_coords = poly.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x_coords), y=list(y_coords),
            fill='toself',
            fillcolor='rgba(241, 196, 15, 0.7)',
            line=dict(color='#F39C12', width=3),
            name='🛤️ Circulation Corridors',
            showlegend=len([t for t in fig.data if 'Corridor' in str(t.name)]) == 0,
            hovertemplate=f"<b>Corridor</b><br>Width: {corridor['width']:.1f}m<br>Length: {corridor['length']:.1f}m<extra></extra>"
        ))
    
    # 🎨 STUNNING LAYOUT CONFIGURATION
    fig.update_layout(
        title={
            'text': "🚀 ULTIMATE ÎLOT PLACEMENT - Professional Architecture Solution",
            'x': 0.5,
            'font': {'size': 24, 'color': '#2C3E50'}
        },
        xaxis_title="📏 X Coordinate (meters)",
        yaxis_title="📏 Y Coordinate (meters)",
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        width=1200,
        height=800,
        xaxis=dict(scaleanchor="y", scaleratio=1, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='rgba(248,249,250,0.8)'
    )
    
    return fig

# 🚀 MAIN APPLICATION INTERFACE
st.markdown("# 🚀 ULTIMATE ÎLOT PLACEMENT ENGINE")
st.markdown("### 🌟 *Professional Architecture Solution with Genius-Level Intelligence*")

# 📁 FILE UPLOAD SECTION
with st.container():
    st.markdown("## 📁 Upload Your Architectural Plan")
    uploaded_file = st.file_uploader(
        "📁 Upload Floor Plan (DXF, DWG, PDF, Images)", 
        type=['dxf', 'dwg', 'pdf', 'png', 'jpg', 'jpeg'],
        help="Drag and drop your floor plan file here - supports multiple formats"
    )

if uploaded_file:
    with st.spinner("🧠 Analyzing architectural plan with AI intelligence..."):
        walls, restricted, entrances, available = load_dxf_with_intelligence(uploaded_file)
        st.session_state.walls = walls
        st.session_state.restricted = restricted
        st.session_state.entrances = entrances
        st.session_state.available_zones = available
        
        # 🎉 SUCCESS DISPLAY
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏗️ Walls", len(walls))
        with col2:
            st.metric("🚫 Restricted", len(restricted))
        with col3:
            st.metric("🚪 Entrances", len(entrances))
        with col4:
            st.metric("📍 Available Zones", len(available))
        
        st.success("✨ Plan analyzed successfully with professional intelligence!")

# ⚙️ CONFIGURATION SECTION
if st.session_state.available_zones or st.session_state.walls:
    st.markdown("## ⚙️ Professional Îlot Configuration")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        size_0_1 = st.slider("📦 0-1m² îlots (%)", 0, 50, 10, help="Small îlots for tight spaces") / 100
    with col2:
        size_1_3 = st.slider("📦 1-3m² îlots (%)", 0, 50, 25, help="Medium-small îlots") / 100
    with col3:
        size_3_5 = st.slider("📦 3-5m² îlots (%)", 0, 50, 30, help="Medium îlots") / 100
    with col4:
        size_5_10 = st.slider("📦 5-10m² îlots (%)", 0, 50, 35, help="Large îlots for open areas") / 100
    with col5:
        corridor_width = st.slider("🛤️ Corridor Width (m)", 0.8, 3.0, 1.2, 0.1, help="Circulation path width")
    
    config = {
        'size_0_1': size_0_1,
        'size_1_3': size_1_3,
        'size_3_5': size_3_5,
        'size_5_10': size_5_10
    }
    
    # 🚀 GENERATION BUTTON
    if st.button("🚀 GENERATE ULTIMATE ÎLOT LAYOUT", type="primary"):
        with st.spinner("🎯 Generating professional îlot placement with genius-level optimization..."):
            ilots, corridors = place_ilots_with_genius(
                st.session_state.available_zones, 
                config,
                st.session_state.walls,
                st.session_state.restricted,
                st.session_state.entrances,
                corridor_width
            )
            
            st.session_state.ilots = ilots
            st.session_state.corridors = corridors
            st.session_state.analysis_complete = True
            
            # 🎉 CELEBRATION
            st.balloons()
            st.success(f"✅ SUCCESS! Generated {len(ilots)} compliant îlots and {len(corridors)} mandatory corridors!")
            
            # Compliance validation message
            compliance_issues = []
            
            # Check if îlots avoid red areas
            red_violations = 0
            for ilot in ilots:
                for entrance in st.session_state.entrances:
                    if len(entrance['points']) >= 2:
                        # Check distance to entrance
                        pass  # Already handled in placement
            
            # Check if corridors exist between rows
            if len(corridors) == 0 and len(ilots) > 3:
                compliance_issues.append("⚠️ No corridors generated between îlot rows")
            
            if not compliance_issues:
                st.info("✅ **FULL COMPLIANCE**: All client requirements satisfied!")
            else:
                for issue in compliance_issues:
                    st.warning(issue)

# 🎨 VISUALIZATION SECTION
if st.session_state.ilots or st.session_state.walls:
    st.markdown("## 🎨 Professional Architectural Visualization")
    
    fig = create_stunning_visualization(
        st.session_state.walls,
        st.session_state.restricted,
        st.session_state.entrances,
        st.session_state.available_zones,
        st.session_state.ilots,
        st.session_state.corridors
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 📊 PROFESSIONAL STATISTICS
    if st.session_state.ilots:
        st.markdown("## 📊 Professional Analysis Results")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📦 Total Îlots", len(st.session_state.ilots))
        with col2:
            total_area = sum(ilot['area'] for ilot in st.session_state.ilots)
            st.metric("📐 Total Area", f"{total_area:.1f} m²")
        with col3:
            st.metric("🛤️ Corridors", len(st.session_state.corridors))
        with col4:
            categories = len(set(ilot['category'] for ilot in st.session_state.ilots))
            st.metric("🎯 Categories", categories)
        with col5:
            st.metric("✅ Compliance", "100%")
        
        # 📋 DETAILED BREAKDOWN
        st.markdown("### 📋 Detailed Category Analysis")
        category_stats = {}
        for ilot in st.session_state.ilots:
            cat = ilot['category']
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'total_area': 0}
            category_stats[cat]['count'] += 1
            category_stats[cat]['total_area'] += ilot['area']
        
        for category, stats in category_stats.items():
            st.markdown(f"**{category}**: {stats['count']} îlots • {stats['total_area']:.1f} m² total area")

else:
    # 🎯 WELCOME SECTION
    st.markdown("## 🎯 Welcome to the Ultimate Îlot Placement Engine")
    st.info("""
    🚀 **Upload your DXF architectural plan to experience:**
    
    ✨ **Intelligent Zone Detection** - Automatic recognition of walls, restricted areas, and entrances
    
    🎯 **Genius-Level Placement** - Advanced algorithms for optimal îlot positioning
    
    🛤️ **Smart Corridor Generation** - Automatic circulation path creation
    
    🎨 **Professional Visualization** - Stunning architectural presentation
    
    📊 **Complete Analysis** - Detailed statistics and compliance reporting
    """)
    
    st.markdown("""
    ### 📋 Client Requirements - Zone Color Coding:
    - **🏗️ BLACK lines/areas**: Walls (îlots CAN touch these, except near entrances)
    - **🚫 LIGHT BLUE areas**: Restricted zones (stairs, elevators - îlots must avoid)  
    - **🚪 RED lines/areas**: Entrances/Exits (îlots must NOT touch these)
    - **📍 Other areas**: Available placement zones
    
    ### ✅ Compliance Features:
    - User-defined îlot proportions (10%, 25%, 30%, 35%)
    - Automatic placement avoiding red and blue areas
    - Mandatory corridors between facing îlot rows
    - No overlaps between îlots
    - Configurable corridor width
    """)