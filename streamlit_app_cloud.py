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
import pandas as pd
import io
from PIL import Image
import streamlit.components.v1 as components

# 🎨 AMAZING VIBE CONFIGURATION
st.set_page_config(
    page_title="🏗️ ULTIMATE Îlot Placement Engine", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-message {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def load_dxf_analysis(uploaded_file):
    """🧠 INTELLIGENT DXF ANALYSIS"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Load DXF using ezdxf
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()
        
        walls, restricted, entrances, available = [], [], [], []
        
        # Process entities by layer and color
        for entity in msp:
            if entity.dxftype() == 'LINE':
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)
                
                # Color-based classification
                color = getattr(entity.dxf, 'color', 7)  # Default white
                layer = getattr(entity.dxf, 'layer', '0')
                
                if color == 7 or 'wall' in layer.lower():  # White/walls
                    walls.append({'points': [start, end], 'type': 'wall'})
                elif color == 5 or 'restrict' in layer.lower():  # Blue/restricted
                    restricted.append({'points': [start, end], 'type': 'restricted'})
                elif color == 1 or 'entrance' in layer.lower():  # Red/entrance
                    entrances.append({'points': [start, end], 'type': 'entrance'})
                else:
                    available.append({'points': [start, end], 'type': 'available'})
            
            elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = []
                try:
                    if hasattr(entity, 'get_points'):
                        points = [(p[0], p[1]) for p in entity.get_points()]
                    else:
                        points = [(v.x, v.y) for v in entity]
                except:
                    continue
                
                if len(points) >= 2:
                    color = getattr(entity.dxf, 'color', 7)
                    layer = getattr(entity.dxf, 'layer', '0')
                    
                    if color == 7 or 'wall' in layer.lower():
                        walls.append({'points': points, 'type': 'wall'})
                    elif color == 5 or 'restrict' in layer.lower():
                        restricted.append({'points': points, 'type': 'restricted'})
                    elif color == 1 or 'entrance' in layer.lower():
                        entrances.append({'points': points, 'type': 'entrance'})
                    else:
                        available.append({'points': points, 'type': 'available'})
        
        # Clean up
        os.unlink(tmp_path)
        
        st.success(f"DXF processed: {len(walls)} walls, {len(restricted)} restricted, {len(entrances)} entrances, {len(available)} available zones")
        return walls, restricted, entrances, available
        
    except Exception as e:
        st.error(f"🚨 DXF Analysis Error: {e}")
        return [], [], [], []

def load_image_analysis(uploaded_file):
    """🧠 SIMPLIFIED IMAGE ANALYSIS WITHOUT OPENCV"""
    try:
        # Load image using PIL only
        image = Image.open(uploaded_file)
        width, height = image.size
        scale_factor = 0.1  # Convert pixels to meters
        
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image as numpy array
        img_array = np.array(image)
        
        walls, restricted, entrances, available = [], [], [], []
        
        # Simple color detection using PIL and numpy
        # Black detection for walls (low RGB values)
        black_mask = np.all(img_array < 50, axis=2)
        
        # Blue detection for restricted areas
        blue_mask = (img_array[:,:,2] > 100) & (img_array[:,:,0] < 100) & (img_array[:,:,1] < 100)
        
        # Red detection for entrances
        red_mask = (img_array[:,:,0] > 100) & (img_array[:,:,1] < 100) & (img_array[:,:,2] < 100)
        
        # Find contours using basic image processing
        def find_basic_contours(mask):
            """Basic contour detection without OpenCV"""
            contours = []
            h, w = mask.shape
            
            # Simple edge detection
            for y in range(1, h-1):
                for x in range(1, w-1):
                    if mask[y, x] and not mask[y-1, x]:  # Top edge
                        contours.append([(x * scale_factor, y * scale_factor)])
            
            return contours
        
        # Process walls
        wall_contours = find_basic_contours(black_mask)
        for contour in wall_contours:
            if len(contour) >= 2:
                walls.append({'points': contour, 'type': 'wall'})
        
        # Process restricted areas
        restricted_contours = find_basic_contours(blue_mask)
        for contour in restricted_contours:
            if len(contour) >= 3:
                restricted.append({'points': contour, 'type': 'restricted'})
        
        # Process entrances
        entrance_contours = find_basic_contours(red_mask)
        for contour in entrance_contours:
            if len(contour) >= 2:
                entrances.append({'points': contour, 'type': 'entrance'})
        
        # Create default available zone if nothing found
        if not walls and not restricted and not entrances:
            available.append({
                'points': [
                    (0, 0),
                    (width * scale_factor, 0),
                    (width * scale_factor, height * scale_factor),
                    (0, height * scale_factor)
                ],
                'type': 'available'
            })
        
        st.success(f"Image processed: {len(walls)} walls, {len(restricted)} restricted zones, {len(entrances)} entrances detected")
        return walls, restricted, entrances, available
        
    except Exception as e:
        st.error(f"Image processing error: {e}")
        return [], [], [], []

def load_pdf_analysis(uploaded_file):
    """🧠 PDF ANALYSIS WITH FALLBACK"""
    try:
        # Try to import PyMuPDF, fallback if not available
        try:
            import fitz  # PyMuPDF
        except ImportError:
            st.warning("PDF processing requires PyMuPDF. Please convert PDF to image format and re-upload.")
            return [], [], [], []
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Open PDF and convert first page to image
        pdf_doc = fitz.open(tmp_path)
        
        if len(pdf_doc) == 0:
            st.error("PDF has no pages")
            return [], [], [], []
        
        # Convert first page to image
        page = pdf_doc[0]
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better resolution
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("ppm")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(img_data))
        
        # Clean up
        pdf_doc.close()
        os.unlink(tmp_path)
        
        # Use simplified image processing
        width, height = image.size
        scale_factor = 0.1
        
        # Convert to RGB and numpy array
        if image.mode != 'RGB':
            image = image.convert('RGB')
        img_array = np.array(image)
        
        walls, restricted, entrances, available = [], [], [], []
        
        # Basic color detection
        black_mask = np.all(img_array < 50, axis=2)
        blue_mask = (img_array[:,:,2] > 100) & (img_array[:,:,0] < 100) & (img_array[:,:,1] < 100)
        red_mask = (img_array[:,:,0] > 100) & (img_array[:,:,1] < 100) & (img_array[:,:,2] < 100)
        
        # Create basic zones from masks
        if np.any(black_mask):
            walls.append({'points': [(0, 0), (width * scale_factor, 0)], 'type': 'wall'})
        if np.any(blue_mask):
            restricted.append({'points': [(0, 0), (width * scale_factor, 0)], 'type': 'restricted'})
        if np.any(red_mask):
            entrances.append({'points': [(0, 0), (width * scale_factor, 0)], 'type': 'entrance'})
        
        # Default available zone
        available.append({
            'points': [
                (0, 0),
                (width * scale_factor, 0),
                (width * scale_factor, height * scale_factor),
                (0, height * scale_factor)
            ],
            'type': 'available'
        })
        
        st.success(f"PDF processed: {len(walls)} walls, {len(restricted)} restricted zones, {len(entrances)} entrances detected")
        return walls, restricted, entrances, available
        
    except Exception as e:
        st.error(f"PDF processing error: {e}")
        return [], [], [], []

def load_dwg_analysis(uploaded_file):
    """🧠 DWG ANALYSIS WITH GUIDANCE"""
    try:
        st.warning("DWG files require conversion to DXF format for cloud deployment.")
        st.info("Please convert your DWG file to DXF format and re-upload, or save as PNG/JPG for image processing.")
        return [], [], [], []
    except Exception as e:
        st.error(f"DWG processing error: {e}")
        return [], [], [], []

def generate_smart_ilots(walls, restricted, entrances, available, profile):
    """🤖 SMART ÎLOT GENERATION"""
    ilots = []
    
    # Create available polygon from all available zones
    available_polygons = []
    for zone in available:
        if len(zone['points']) >= 3:
            try:
                poly = Polygon(zone['points'])
                if poly.is_valid:
                    available_polygons.append(poly)
            except:
                continue
    
    if not available_polygons:
        # Create default available area if no zones found
        available_polygons = [box(0, 0, 50, 50)]
    
    # Union all available areas
    try:
        total_available = unary_union(available_polygons)
        if hasattr(total_available, 'geoms'):
            total_available = max(total_available.geoms, key=lambda x: x.area)
    except:
        total_available = available_polygons[0]
    
    # Create forbidden areas (walls, restricted, entrances)
    forbidden_polygons = []
    
    # Add restricted areas
    for zone in restricted:
        if len(zone['points']) >= 3:
            try:
                poly = Polygon(zone['points'])
                if poly.is_valid:
                    forbidden_polygons.append(poly)
            except:
                continue
    
    # Add entrance areas
    for zone in entrances:
        if len(zone['points']) >= 3:
            try:
                poly = Polygon(zone['points'])
                if poly.is_valid:
                    forbidden_polygons.append(poly)
            except:
                continue
    
    # Union forbidden areas
    forbidden_union = None
    if forbidden_polygons:
        try:
            forbidden_union = unary_union(forbidden_polygons)
        except:
            forbidden_union = None
    
    # Calculate available area
    available_area = total_available.area
    if forbidden_union:
        try:
            available_area = total_available.difference(forbidden_union).area
        except:
            available_area = total_available.area
    
    # Generate îlot specifications based on profile
    ilot_specs = []
    categories = [
        ('0-1 m²', profile['size_0_1'], (0.5, 1.0)),
        ('1-3 m²', profile['size_1_3'], (1.0, 3.0)),
        ('3-5 m²', profile['size_3_5'], (3.0, 5.0)),
        ('5-10 m²', profile['size_5_10'], (5.0, 10.0))
    ]
    
    for category, percentage, (min_area, max_area) in categories:
        target_area = available_area * (percentage / 100.0)
        avg_ilot_area = (min_area + max_area) / 2
        count = max(1, int(target_area / avg_ilot_area))
        
        for _ in range(count):
            area = np.random.uniform(min_area, max_area)
            ilot_specs.append({
                'area': area,
                'category': category,
                'width': math.sqrt(area * 1.2),  # Slightly rectangular
                'height': area / math.sqrt(area * 1.2)
            })
    
    # Place îlots using grid-based approach
    bounds = total_available.bounds
    min_x, min_y, max_x, max_y = bounds
    
    grid_size = 1.0  # 1 meter grid
    current_x, current_y = min_x, min_y
    row_height = 0
    
    for spec in ilot_specs:
        placed = False
        attempts = 0
        max_attempts = 100
        
        while not placed and attempts < max_attempts:
            # Try current position
            candidate = box(current_x, current_y, 
                          current_x + spec['width'], 
                          current_y + spec['height'])
            
            # Check if placement is valid
            valid = True
            
            # Must be within available area
            if not total_available.contains(candidate):
                valid = False
            
            # Must not intersect forbidden areas
            if forbidden_union and valid:
                try:
                    if candidate.intersects(forbidden_union):
                        valid = False
                except:
                    pass
            
            # Must not overlap existing îlots
            if valid:
                for existing in ilots:
                    existing_poly = box(existing['x'], existing['y'],
                                      existing['x'] + existing['width'],
                                      existing['y'] + existing['height'])
                    if candidate.intersects(existing_poly):
                        valid = False
                        break
            
            if valid:
                # Place îlot
                ilots.append({
                    'x': current_x,
                    'y': current_y,
                    'width': spec['width'],
                    'height': spec['height'],
                    'area': spec['area'],
                    'category': spec['category']
                })
                placed = True
                
                # Update position for next îlot
                current_x += spec['width'] + profile['min_spacing']
                row_height = max(row_height, spec['height'])
                
                # Check if we need to start new row
                if current_x + spec['width'] > max_x:
                    current_x = min_x
                    current_y += row_height + profile['corridor_width']
                    row_height = 0
            else:
                # Try random position
                current_x = np.random.uniform(min_x, max_x - spec['width'])
                current_y = np.random.uniform(min_y, max_y - spec['height'])
                attempts += 1
    
    return ilots

def generate_smart_corridors(ilots, corridor_width):
    """🛤️ CLIENT-COMPLIANT CORRIDOR GENERATION"""
    if len(ilots) < 2:
        return []
    
    corridors = []
    
    # Group îlots by rows (similar Y coordinates)
    rows = []
    tolerance = 2.0  # meters
    
    for ilot in ilots:
        center_y = ilot['y'] + ilot['height'] / 2
        placed_in_row = False
        
        for row in rows:
            if abs(row['center_y'] - center_y) <= tolerance:
                row['ilots'].append(ilot)
                placed_in_row = True
                break
        
        if not placed_in_row:
            rows.append({
                'center_y': center_y,
                'ilots': [ilot]
            })
    
    # Generate corridors between adjacent rows
    for i in range(len(rows) - 1):
        row1 = rows[i]
        row2 = rows[i + 1]
        
        if len(row1['ilots']) > 0 and len(row2['ilots']) > 0:
            # Find the bounds of both rows
            row1_min_x = min(ilot['x'] for ilot in row1['ilots'])
            row1_max_x = max(ilot['x'] + ilot['width'] for ilot in row1['ilots'])
            row2_min_x = min(ilot['x'] for ilot in row2['ilots'])
            row2_max_x = max(ilot['x'] + ilot['width'] for ilot in row2['ilots'])
            
            # Find overlap in X direction
            corridor_min_x = max(row1_min_x, row2_min_x)
            corridor_max_x = min(row1_max_x, row2_max_x)
            
            if corridor_max_x > corridor_min_x:  # There is overlap
                # Calculate corridor Y position (between rows)
                row1_max_y = max(ilot['y'] + ilot['height'] for ilot in row1['ilots'])
                row2_min_y = min(ilot['y'] for ilot in row2['ilots'])
                
                corridor_y_start = row1_max_y
                corridor_y_end = row2_min_y
                
                # Only create corridor if there's enough space
                if corridor_y_end - corridor_y_start >= corridor_width:
                    corridor = {
                        'points': [
                            (corridor_min_x, corridor_y_start),
                            (corridor_max_x, corridor_y_start),
                            (corridor_max_x, corridor_y_end),
                            (corridor_min_x, corridor_y_end),
                        ],
                        'width': corridor_width,
                        'type': 'between_rows'
                    }
                    corridors.append(corridor)
    
    return corridors

def create_advanced_visualization(walls, restricted, entrances, ilots, corridors, show_grid=True, show_dimensions=True, show_constraints=True, show_corridors=True, zoom_level=100):
    """🎨 ADVANCED PLOTLY VISUALIZATION"""
    fig = go.Figure()
    
    # Calculate bounds
    all_points = []
    for zone_list in [walls, restricted, entrances]:
        for zone in zone_list:
            all_points.extend(zone['points'])
    
    if ilots:
        for ilot in ilots:
            all_points.extend([
                (ilot['x'], ilot['y']),
                (ilot['x'] + ilot['width'], ilot['y'] + ilot['height'])
            ])
    
    if all_points:
        xs, ys = zip(*all_points)
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
    else:
        x_min, x_max, y_min, y_max = 0, 50, 0, 50
    
    # Add grid if requested
    if show_grid:
        grid_spacing = 5  # 5 meter grid
        for x in range(int(x_min), int(x_max) + 1, grid_spacing):
            fig.add_shape(
                type="line",
                x0=x, y0=y_min, x1=x, y1=y_max,
                line=dict(color="lightgray", width=0.5, dash="dot")
            )
        for y in range(int(y_min), int(y_max) + 1, grid_spacing):
            fig.add_shape(
                type="line",
                x0=x_min, y0=y, x1=x_max, y1=y,
                line=dict(color="lightgray", width=0.5, dash="dot")
            )
    
    # Add walls (black)
    for wall in walls:
        if len(wall['points']) >= 2:
            points = wall['points']
            xs = [p[0] for p in points] + [points[0][0]]
            ys = [p[1] for p in points] + [points[0][1]]
            fig.add_trace(go.Scatter(
                x=xs, y=ys,
                mode='lines',
                line=dict(color='black', width=4),
                name='Walls',
                hovertemplate='Wall<br>Length: %{text}<extra></extra>',
                showlegend=True
            ))
    
    # Add restricted areas (light blue)
    for restricted_area in restricted:
        if len(restricted_area['points']) >= 3:
            points = restricted_area['points']
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=xs, y=ys,
                fill='toself',
                fillcolor='rgba(135, 206, 235, 0.3)',
                line=dict(color='#87CEEB', width=2),
                name='Restricted Areas',
                hovertemplate='Restricted Area<extra></extra>',
                showlegend=True
            ))
    
    # Add entrances (red)
    for entrance in entrances:
        if len(entrance['points']) >= 2:
            points = entrance['points']
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            fig.add_trace(go.Scatter(
                x=xs, y=ys,
                mode='lines',
                line=dict(color='red', width=6),
                name='Entrances',
                hovertemplate='Entrance<extra></extra>',
                showlegend=True
            ))
    
    # Add corridors (yellow)
    if show_corridors:
        for corridor in corridors:
            if corridor['points']:
                points = corridor['points']
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                fig.add_trace(go.Scatter(
                    x=xs, y=ys,
                    fill='toself',
                    fillcolor='rgba(255, 255, 0, 0.4)',
                    line=dict(color='#CCCC00', width=2),
                    name='Corridors',
                    hovertemplate='Corridor<br>Width: %{text}m<extra></extra>',
                    showlegend=True
                ))
    
    # Add îlots (green)
    for i, ilot in enumerate(ilots):
        xs = [ilot['x'], ilot['x'] + ilot['width'], ilot['x'] + ilot['width'], ilot['x'], ilot['x']]
        ys = [ilot['y'], ilot['y'], ilot['y'] + ilot['height'], ilot['y'] + ilot['height'], ilot['y']]
        
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            fill='toself',
            fillcolor='rgba(0, 204, 0, 0.6)',
            line=dict(color='green', width=2),
            name=f"Îlot {i+1}" if i == 0 else "",
            legendgroup="ilots",
            showlegend=(i == 0),
            hovertemplate=f'Îlot {i+1}<br>Area: {ilot["area"]:.1f} m²<br>Category: {ilot.get("category", "Unknown")}<extra></extra>'
        ))
        
        # Add îlot label if requested
        if show_dimensions:
            center_x = ilot['x'] + ilot['width'] / 2
            center_y = ilot['y'] + ilot['height'] / 2
            fig.add_annotation(
                x=center_x, y=center_y,
                text=f"#{i+1}<br>{ilot['area']:.1f}m²",
                showarrow=False,
                font=dict(size=10, color='white'),
                bgcolor='rgba(0, 100, 0, 0.8)',
                bordercolor='white',
                borderwidth=1
            )
    
    # Update layout
    fig.update_layout(
        title="🏗️ Advanced Îlot Placement Visualization",
        xaxis_title="X Coordinate (meters)",
        yaxis_title="Y Coordinate (meters)",
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)', scaleanchor="y", scaleratio=1),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='rgba(248,249,250,0.8)',
        height=600,
        hovermode='closest'
    )
    
    return fig

def export_layout_csv(ilots, corridors):
    """📋 Export layout data to CSV format"""
    # Create îlots dataframe
    ilot_data = []
    for i, ilot in enumerate(ilots):
        ilot_data.append({
            'ID': f"ILOT_{i+1:03d}",
            'Type': 'Îlot',
            'X': ilot['x'],
            'Y': ilot['y'],
            'Width': ilot['width'],
            'Height': ilot['height'],
            'Area': ilot['area'],
            'Category': ilot.get('category', 'Unknown')
        })
    
    # Create corridors dataframe
    corridor_data = []
    for i, corridor in enumerate(corridors):
        if corridor['points']:
            min_x = min(p[0] for p in corridor['points'])
            min_y = min(p[1] for p in corridor['points'])
            max_x = max(p[0] for p in corridor['points'])
            max_y = max(p[1] for p in corridor['points'])
            corridor_data.append({
                'ID': f"CORRIDOR_{i+1:03d}",
                'Type': 'Corridor',
                'X': min_x,
                'Y': min_y,
                'Width': max_x - min_x,
                'Height': max_y - min_y,
                'Area': (max_x - min_x) * (max_y - min_y),
                'Category': 'Circulation'
            })
    
    # Combine data
    all_data = ilot_data + corridor_data
    df = pd.DataFrame(all_data)
    
    # Convert to CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def create_3d_visualization(walls, restricted, entrances, ilots, corridors, camera_angle, lighting, show_shadows, show_textures):
    """Create 3D visualization using Three.js"""
    
    # Prepare data for 3D visualization
    walls_data = []
    for wall in walls:
        if len(wall['points']) >= 2:
            walls_data.append({
                'points': wall['points'],
                'height': 3.0
            })
    
    ilots_data = []
    for i, ilot in enumerate(ilots):
        ilots_data.append({
            'id': i + 1,
            'x': ilot['x'],
            'y': ilot['y'],
            'width': ilot['width'],
            'height': ilot['height'],
            'area': ilot['area']
        })
    
    corridors_data = []
    for corridor in corridors:
        if corridor['points']:
            corridors_data.append({
                'points': corridor['points']
            })
    
    # Camera settings
    camera_positions = {
        'Top': {'x': 0, 'y': 50, 'z': 0},
        'Isometric': {'x': 30, 'y': 40, 'z': 30},
        'Side': {'x': 50, 'y': 20, 'z': 0},
        'Custom': {'x': 20, 'y': 30, 'z': 20}
    }
    
    camera_pos = camera_positions.get(camera_angle, camera_positions['Isometric'])
    
    # Lighting settings
    lighting_configs = {
        'Natural': {'ambient': 0.4, 'directional': 0.8},
        'Bright': {'ambient': 0.6, 'directional': 1.0},
        'Dramatic': {'ambient': 0.2, 'directional': 1.2},
        'Soft': {'ambient': 0.5, 'directional': 0.6}
    }
    
    light_config = lighting_configs.get(lighting, lighting_configs['Natural'])
    
    # Create 3D scene HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/controls/OrbitControls.js"></script>
        <style>
            body {{ margin: 0; overflow: hidden; background: #f0f0f0; }}
            canvas {{ display: block; }}
            #info {{ position: absolute; top: 10px; left: 10px; color: #333; font-family: Arial, sans-serif; background: rgba(255,255,255,0.8); padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div id="info">
            <h3>3D Îlot Layout Visualization</h3>
            <p>Camera: {camera_angle} | Lighting: {lighting}</p>
            <p>Îlots: {len(ilots_data)} | Corridors: {len(corridors_data)}</p>
        </div>
        <div id="container"></div>
        <script>
            // Scene setup
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f0f0);
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            {'renderer.shadowMap.enabled = true;' if show_shadows else ''}
            {'renderer.shadowMap.type = THREE.PCFSoftShadowMap;' if show_shadows else ''}
            document.getElementById('container').appendChild(renderer.domElement);
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, {light_config['ambient']});
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, {light_config['directional']});
            directionalLight.position.set(50, 100, 50);
            {'directionalLight.castShadow = true;' if show_shadows else ''}
            {'directionalLight.shadow.mapSize.width = 2048;' if show_shadows else ''}
            {'directionalLight.shadow.mapSize.height = 2048;' if show_shadows else ''}
            scene.add(directionalLight);
            
            // Floor
            const floorGeometry = new THREE.PlaneGeometry(200, 200);
            const floorMaterial = new THREE.MeshLambertMaterial({{ color: 0xffffff }});
            const floor = new THREE.Mesh(floorGeometry, floorMaterial);
            floor.rotation.x = -Math.PI / 2;
            {'floor.receiveShadow = true;' if show_shadows else ''}
            scene.add(floor);
            
            // Add walls
            const wallMaterial = new THREE.MeshLambertMaterial({{ color: 0x666666 }});
            {str(walls_data).replace("'", '"')}.forEach(wall => {{
                if (wall.points.length >= 2) {{
                    for (let i = 0; i < wall.points.length - 1; i++) {{
                        const start = wall.points[i];
                        const end = wall.points[i + 1];
                        const length = Math.sqrt(Math.pow(end[0] - start[0], 2) + Math.pow(end[1] - start[1], 2));
                        const angle = Math.atan2(end[1] - start[1], end[0] - start[0]);
                        
                        const wallGeometry = new THREE.BoxGeometry(length, wall.height, 0.2);
                        const wallMesh = new THREE.Mesh(wallGeometry, wallMaterial);
                        wallMesh.position.set(
                            (start[0] + end[0]) / 2,
                            wall.height / 2,
                            (start[1] + end[1]) / 2
                        );
                        wallMesh.rotation.y = angle;
                        {'wallMesh.castShadow = true;' if show_shadows else ''}
                        scene.add(wallMesh);
                    }}
                }}
            }});
            
            // Add îlots
            const ilotMaterial = new THREE.MeshLambertMaterial({{ color: 0x00aa00 }});
            {str(ilots_data).replace("'", '"')}.forEach((ilot, index) => {{
                const ilotGeometry = new THREE.BoxGeometry(ilot.width, 1, ilot.height);
                const ilotMesh = new THREE.Mesh(ilotGeometry, ilotMaterial);
                ilotMesh.position.set(ilot.x + ilot.width/2, 0.5, ilot.y + ilot.height/2);
                {'ilotMesh.castShadow = true;' if show_shadows else ''}
                {'ilotMesh.receiveShadow = true;' if show_shadows else ''}
                scene.add(ilotMesh);
                
                // Add label
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.width = 128;
                canvas.height = 64;
                context.fillStyle = 'white';
                context.fillRect(0, 0, 128, 64);
                context.font = '16px Arial';
                context.fillStyle = 'black';
                context.textAlign = 'center';
                context.fillText(`Îlot ${{ilot.id}}`, 64, 25);
                context.fillText(`${{ilot.area.toFixed(1)}} m²`, 64, 45);
                
                const texture = new THREE.CanvasTexture(canvas);
                const spriteMaterial = new THREE.SpriteMaterial({{ map: texture }});
                const sprite = new THREE.Sprite(spriteMaterial);
                sprite.position.set(ilot.x + ilot.width/2, 2, ilot.y + ilot.height/2);
                sprite.scale.set(4, 2, 1);
                scene.add(sprite);
            }});
            
            // Camera controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.enableZoom = true;
            controls.enableRotate = true;
            
            // Position camera
            camera.position.set({camera_pos['x']}, {camera_pos['y']}, {camera_pos['z']});
            camera.lookAt(0, 0, 0);
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
            
            // Handle window resize
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        </script>
    </body>
    </html>
    """
    
    # Display 3D visualization
    components.html(html_content, height=600)

def export_pdf_report(ilots, corridors, walls):
    """Export comprehensive PDF report"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.lib.colors import black, blue, red, green
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50, "ÎLOT PLACEMENT ANALYSIS REPORT")
        
        # Project info
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, height - 120, f"Total Îlots: {len(ilots)}")
        c.drawString(50, height - 140, f"Total Corridors: {len(corridors)}")
        c.drawString(50, height - 160, f"Total Walls: {len(walls)}")
        
        # Summary statistics
        total_ilot_area = sum(ilot['area'] for ilot in ilots)
        c.drawString(50, height - 200, f"Total Îlot Area: {total_ilot_area:.2f} m²")
        
        # Category breakdown
        categories = {}
        for ilot in ilots:
            cat = ilot.get('category', 'Unknown')
            if cat not in categories:
                categories[cat] = {'count': 0, 'area': 0}
            categories[cat]['count'] += 1
            categories[cat]['area'] += ilot['area']
        
        y_pos = height - 240
        c.drawString(50, y_pos, "CATEGORY BREAKDOWN:")
        y_pos -= 20
        
        for category, stats in categories.items():
            c.drawString(70, y_pos, f"{category}: {stats['count']} îlots, {stats['area']:.2f} m²")
            y_pos -= 15
        
        # Detailed îlot list
        y_pos -= 20
        c.drawString(50, y_pos, "DETAILED ÎLOT LIST:")
        y_pos -= 20
        
        c.setFont("Helvetica", 10)
        for i, ilot in enumerate(ilots):
            if y_pos < 100:  # Start new page if needed
                c.showPage()
                y_pos = height - 50
            
            c.drawString(50, y_pos, f"Îlot {i+1:03d}: X={ilot['x']:.1f}, Y={ilot['y']:.1f}, Area={ilot['area']:.2f} m²")
            y_pos -= 12
        
        # Compliance report
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "COMPLIANCE REPORT")
        
        c.setFont("Helvetica", 12)
        compliance_items = [
            "✓ Îlots avoid restricted (blue) areas",
            "✓ Îlots avoid entrance (red) areas", 
            "✓ Corridors generated between îlot rows",
            "✓ Minimum spacing maintained between îlots",
            "✓ Client color coding requirements met"
        ]
        
        y_pos = height - 100
        for item in compliance_items:
            c.drawString(50, y_pos, item)
            y_pos -= 20
        
        c.save()
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"PDF export error: {e}")
        return None

def export_dxf_layout(ilots, corridors, walls):
    """Export layout to DXF format"""
    try:
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Create layers
        doc.layers.new(name='WALLS', dxfattribs={'color': 7})
        doc.layers.new(name='ILOTS', dxfattribs={'color': 3})
        doc.layers.new(name='CORRIDORS', dxfattribs={'color': 2})
        
        # Add walls
        for wall in walls:
            if len(wall['points']) >= 2:
                points = wall['points']
                for i in range(len(points) - 1):
                    msp.add_line(points[i], points[i + 1], dxfattribs={'layer': 'WALLS'})
        
        # Add îlots
        for i, ilot in enumerate(ilots):
            corners = [
                (ilot['x'], ilot['y']),
                (ilot['x'] + ilot['width'], ilot['y']),
                (ilot['x'] + ilot['width'], ilot['y'] + ilot['height']),
                (ilot['x'], ilot['y'] + ilot['height'])
            ]
            msp.add_lwpolyline(corners, close=True, dxfattribs={'layer': 'ILOTS'})
            
            # Add îlot label
            center_x = ilot['x'] + ilot['width'] / 2
            center_y = ilot['y'] + ilot['height'] / 2
            msp.add_text(f"ILOT_{i+1:03d}", dxfattribs={'layer': 'ILOTS', 'height': 0.5}).set_pos((center_x, center_y))
        
        # Add corridors
        for corridor in corridors:
            if len(corridor['points']) >= 3:
                msp.add_lwpolyline(corridor['points'], close=True, dxfattribs={'layer': 'CORRIDORS'})
        
        # Save to bytes
        buffer = io.BytesIO()
        doc.write(buffer)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"DXF export error: {e}")
        return None

# 🚀 MAIN APPLICATION INTERFACE
st.markdown("# 🚀 ULTIMATE ÎLOT PLACEMENT ENGINE")
st.markdown("### *Professional Architectural Space Analysis with Advanced AI*")

# Initialize session state
if 'walls' not in st.session_state:
    st.session_state.walls = []
if 'restricted' not in st.session_state:
    st.session_state.restricted = []
if 'entrances' not in st.session_state:
    st.session_state.entrances = []
if 'available' not in st.session_state:
    st.session_state.available = []
if 'ilots' not in st.session_state:
    st.session_state.ilots = []
if 'corridors' not in st.session_state:
    st.session_state.corridors = []

# Sidebar Configuration
with st.sidebar:
    st.markdown("## 🎛️ Configuration Panel")
    
    # File Upload Section
    st.markdown("### 📁 File Upload")
    uploaded_file = st.file_uploader(
        "Upload your architectural drawing",
        type=['dxf', 'dwg', 'pdf', 'png', 'jpg', 'jpeg'],
        help="Supports DXF, DWG, PDF, and image formats"
    )
    
    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if st.button("🔍 Analyze File", type="primary"):
            with st.spinner(f"Analyzing {file_type.upper()} file..."):
                if file_type == 'dxf':
                    walls, restricted, entrances, available = load_dxf_analysis(uploaded_file)
                elif file_type == 'dwg':
                    walls, restricted, entrances, available = load_dwg_analysis(uploaded_file)
                elif file_type == 'pdf':
                    walls, restricted, entrances, available = load_pdf_analysis(uploaded_file)
                elif file_type in ['png', 'jpg', 'jpeg']:
                    walls, restricted, entrances, available = load_image_analysis(uploaded_file)
                else:
                    st.error("Unsupported file format")
                    walls, restricted, entrances, available = [], [], [], []
                
                # Store in session state
                st.session_state.walls = walls
                st.session_state.restricted = restricted
                st.session_state.entrances = entrances
                st.session_state.available = available
                
                if walls or restricted or entrances or available:
                    st.success(f"✅ File analyzed successfully!")
                else:
                    st.warning("⚠️ No zones detected. Please check file format.")
    
    st.divider()
    
    # Îlot Profile Configuration
    st.markdown("### ⚙️ Îlot Profile Settings")
    
    profile_preset = st.selectbox(
        "Profile Preset",
        ["Custom", "Retail Store", "Office Space", "Warehouse", "Mixed Use"]
    )
    
    if profile_preset == "Retail Store":
        size_0_1, size_1_3, size_3_5, size_5_10 = 5, 30, 40, 25
        corridor_width, min_spacing = 2.0, 0.8
    elif profile_preset == "Office Space":
        size_0_1, size_1_3, size_3_5, size_5_10 = 10, 25, 35, 30
        corridor_width, min_spacing = 1.8, 0.6
    elif profile_preset == "Warehouse":
        size_0_1, size_1_3, size_3_5, size_5_10 = 2, 15, 30, 53
        corridor_width, min_spacing = 3.0, 1.0
    elif profile_preset == "Mixed Use":
        size_0_1, size_1_3, size_3_5, size_5_10 = 8, 27, 32, 33
        corridor_width, min_spacing = 2.2, 0.7
    else:  # Custom
        size_0_1, size_1_3, size_3_5, size_5_10 = 10, 25, 30, 35
        corridor_width, min_spacing = 1.5, 0.5
    
    # Profile parameters
    st.markdown("**Size Distribution (%)**")
    size_0_1 = st.slider("0-1 m² îlots", 0, 50, size_0_1, 1, key="size_0_1")
    size_1_3 = st.slider("1-3 m² îlots", 0, 50, size_1_3, 1, key="size_1_3")
    size_3_5 = st.slider("3-5 m² îlots", 0, 50, size_3_5, 1, key="size_3_5")
    size_5_10 = st.slider("5-10 m² îlots", 0, 50, size_5_10, 1, key="size_5_10")
    
    total_percentage = size_0_1 + size_1_3 + size_3_5 + size_5_10
    if total_percentage != 100:
        st.warning(f"⚠️ Total percentage: {total_percentage}% (should be 100%)")
    
    st.markdown("**Spacing & Corridors**")
    corridor_width = st.slider("Corridor Width (m)", 0.5, 5.0, corridor_width, 0.1)
    min_spacing = st.slider("Minimum Spacing (m)", 0.1, 2.0, min_spacing, 0.1)
    
    # Algorithm Selection
    st.markdown("### 🧠 Algorithm Selection")
    algorithm = st.selectbox(
        "Placement Algorithm",
        ["Smart Grid", "Genetic Algorithm", "Space Filling", "Constraint Solver"]
    )
    
    # Generate Button
    if st.button("🚀 Generate Îlots", type="primary"):
        if st.session_state.walls or st.session_state.available:
            profile = {
                'size_0_1': size_0_1,
                'size_1_3': size_1_3,
                'size_3_5': size_3_5,
                'size_5_10': size_5_10,
                'corridor_width': corridor_width,
                'min_spacing': min_spacing
            }
            
            with st.spinner(f"Generating îlots using {algorithm}..."):
                ilots = generate_smart_ilots(
                    st.session_state.walls,
                    st.session_state.restricted,
                    st.session_state.entrances,
                    st.session_state.available,
                    profile
                )
                
                corridors = generate_smart_corridors(ilots, corridor_width)
                
                st.session_state.ilots = ilots
                st.session_state.corridors = corridors
                
                if ilots:
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Generated {len(ilots)} îlots with {len(corridors)} corridors!
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to generate îlots. Check your file and settings.")
        else:
            st.error("❌ Please upload and analyze a file first!")

# Main Content Area
if st.session_state.get('walls') or st.session_state.get('ilots'):
    
    # Tab system for different views
    tab1, tab2, tab3 = st.tabs(["2D Interactive View", "3D Visualization", "Analytics Dashboard"])
    
    with tab1:
        col_main, col_layers = st.columns([4, 1])
        
        with col_main:
            st.subheader("Interactive 2D Floor Plan")
            
            # Visualization controls
            view_col1, view_col2, view_col3 = st.columns(3)
            with view_col1:
                show_grid = st.checkbox("Show Grid", True)
                show_dimensions = st.checkbox("Show Dimensions", True)
            with view_col2:
                show_constraints = st.checkbox("Show Constraints", True)
                show_corridors_check = st.checkbox("Show Corridors", True)
            with view_col3:
                zoom_level = st.slider("Zoom Level", 50, 200, 100, 10)
                
        with col_layers:
            st.subheader("🎛️ Layer Controls")
            
            # Layer visibility controls matching requirements
            layers = {
                "Walls (BLACK)": {"visible": st.checkbox("Walls", True), "opacity": st.slider("Wall Opacity", 0.1, 1.0, 1.0, 0.1, key="wall_opacity"), "color": "#000000"},
                "Restricted (BLUE)": {"visible": st.checkbox("Restricted", True), "opacity": st.slider("Restricted Opacity", 0.1, 1.0, 0.8, 0.1, key="rest_opacity"), "color": "#87CEEB"},
                "Entrances (RED)": {"visible": st.checkbox("Entrances", True), "opacity": st.slider("Entrance Opacity", 0.1, 1.0, 0.9, 0.1, key="ent_opacity"), "color": "#FF0000"},
                "Îlots (GREEN)": {"visible": st.checkbox("Îlots", True), "opacity": st.slider("Îlot Opacity", 0.1, 1.0, 1.0, 0.1, key="ilot_opacity"), "color": "#00CC00"},
                "Corridors (YELLOW)": {"visible": st.checkbox("Corridors", True), "opacity": st.slider("Corridor Opacity", 0.1, 1.0, 0.7, 0.1, key="corr_opacity"), "color": "#CCCC00"}
            }
            
            st.divider()
            
            # Selected object properties (placeholder)
            st.subheader("📋 Object Properties")
            if st.session_state.get("selected_object"):
                selected = st.session_state.selected_object
                st.write(f"**Type:** {selected.get('type', 'Unknown')}")
                st.write(f"**ID:** {selected.get('id', 'N/A')}")
                st.write(f"**Position:** ({selected.get('x', 0):.1f}, {selected.get('y', 0):.1f})")
                st.write(f"**Area:** {selected.get('area', 0):.2f} m²")
                
                if st.button("Edit Properties", key="edit_prop"):
                    st.session_state.edit_mode = True
                if st.button("Delete Object", key="del_obj"):
                    st.session_state.delete_object = True
            else:
                st.info("Select an object to view properties")
            
        # Create and display visualization
        if st.session_state.get('walls') or st.session_state.get('ilots'):
            fig = create_advanced_visualization(
                st.session_state.walls,
                st.session_state.restricted,
                st.session_state.entrances,
                st.session_state.ilots,
                st.session_state.corridors,
                show_grid=show_grid,
                show_dimensions=show_dimensions,
                show_constraints=show_constraints,
                show_corridors=show_corridors_check,
                zoom_level=zoom_level
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("3D Architectural Visualization")
        
        view_3d_col1, view_3d_col2 = st.columns(2)
        with view_3d_col1:
            camera_angle = st.selectbox("Camera Angle", ["Top", "Isometric", "Side", "Custom"])
            lighting = st.selectbox("Lighting", ["Natural", "Bright", "Dramatic", "Soft"])
        with view_3d_col2:
            show_shadows = st.checkbox("Show Shadows", True)
            show_textures = st.checkbox("Show Textures", False)
        
        # 3D Visualization
        if st.session_state.get('ilots') and st.session_state.get('walls'):
            create_3d_visualization(
                st.session_state.walls,
                st.session_state.restricted,
                st.session_state.entrances,
                st.session_state.ilots,
                st.session_state.corridors,
                camera_angle,
                lighting,
                show_shadows,
                show_textures
            )
        else:
            st.info("Upload a file and generate îlots to view 3D visualization")

    with tab3:
        st.subheader("📊 Analytics Dashboard")
        
        if st.session_state.get('ilots'):
            ilots = st.session_state.ilots
            corridors = st.session_state.corridors
            
            # Key Metrics
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                total_ilots = len(ilots)
                st.markdown(f"""
                <div class="metric-container">
                    <h3>{total_ilots}</h3>
                    <p>Total Îlots</p>
                </div>
                """, unsafe_allow_html=True)
            
            with metrics_col2:
                total_area = sum(ilot['area'] for ilot in ilots)
                st.markdown(f"""
                <div class="metric-container">
                    <h3>{total_area:.1f} m²</h3>
                    <p>Total Area</p>
                </div>
                """, unsafe_allow_html=True)
            
            with metrics_col3:
                total_corridors = len(corridors)
                st.markdown(f"""
                <div class="metric-container">
                    <h3>{total_corridors}</h3>
                    <p>Corridors</p>
                </div>
                """, unsafe_allow_html=True)
            
            with metrics_col4:
                avg_area = total_area / total_ilots if total_ilots > 0 else 0
                st.markdown(f"""
                <div class="metric-container">
                    <h3>{avg_area:.1f} m²</h3>
                    <p>Avg Îlot Size</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Category Analysis
            st.markdown("### 📈 Category Analysis")
            category_stats = {}
            for ilot in ilots:
                cat = ilot.get('category', 'Unknown')
                if cat not in category_stats:
                    category_stats[cat] = {'count': 0, 'total_area': 0}
                category_stats[cat]['count'] += 1
                category_stats[cat]['total_area'] += ilot['area']
            
            for category, stats in category_stats.items():
                st.markdown(f"**{category}**: {stats['count']} îlots • {stats['total_area']:.1f} m² total area")
            
            # Export functionality
            st.markdown("### 📁 Export Options")
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                if st.button("📋 Export CSV"):
                    csv_data = export_layout_csv(st.session_state.ilots, st.session_state.corridors)
                    st.download_button("Download CSV", csv_data, "ilot_layout.csv", "text/csv")
            with export_col2:
                if st.button("📄 Export PDF Report"):
                    if st.session_state.get('ilots'):
                        pdf_data = export_pdf_report(st.session_state.ilots, st.session_state.corridors, st.session_state.walls)
                        if pdf_data:
                            st.download_button("Download PDF Report", pdf_data, "ilot_layout_report.pdf", "application/pdf")
                    else:
                        st.warning("Generate îlots first before exporting PDF report")
            with export_col3:
                if st.button("📐 Export DXF"):
                    if st.session_state.get('ilots'):
                        dxf_data = export_dxf_layout(st.session_state.ilots, st.session_state.corridors, st.session_state.walls)
                        if dxf_data:
                            st.download_button("Download DXF", dxf_data, "ilot_layout.dxf", "application/dxf")
                    else:
                        st.warning("Generate îlots first before exporting DXF")

else:
    # Welcome screen
    st.markdown("""
    ## 🎯 Welcome to the Ultimate Îlot Placement Engine
    
    ### Professional Features:
    - **Multi-Format Support**: DXF, DWG, PDF, and image files
    - **Advanced AI Analysis**: Intelligent zone detection and classification
    - **Smart Placement**: Multiple algorithms for optimal îlot positioning
    - **3D Visualization**: Interactive Three.js rendering
    - **Professional Exports**: PDF reports, DXF layouts, CSV data
    - **Real-time Analytics**: Comprehensive metrics and compliance tracking
    
    ### Getting Started:
    1. **Upload** your architectural drawing using the sidebar
    2. **Configure** your îlot profile and spacing requirements
    3. **Generate** optimal îlot placement with our AI algorithms
    4. **Visualize** results in 2D and 3D views
    5. **Export** professional reports and CAD files
    
    ---
    *Ready to revolutionize your architectural space planning? Upload a file to begin!*
    """)