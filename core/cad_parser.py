import ezdxf
import logging
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)

def parse_dxf(file_path):
    """Enhanced DXF parser that handles all entity types including POLYLINE, LWPOLYLINE, LINE, etc."""
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    walls, restricted, entrances = [], [], []
    
    # Process all entities in the drawing
    for entity in msp:
        try:
            geometry_data = extract_entity_geometry(entity)
            if geometry_data:
                # Classify entity based on various criteria
                entity_type = classify_entity_type(entity, geometry_data)
                
                if entity_type == 'wall':
                    walls.append(geometry_data['polygon'])
                elif entity_type == 'restricted':
                    restricted.append(geometry_data['polygon'])
                elif entity_type == 'entrance':
                    entrances.append(geometry_data['polygon'])
        except Exception as e:
            logger.warning(f"Error processing entity {entity.dxftype()}: {e}")
            continue
    
    logger.info(f"Parsed DXF: {len(walls)} walls, {len(restricted)} restricted, {len(entrances)} entrances")
    return walls, restricted, entrances

def extract_entity_geometry(entity) -> Optional[Dict[str, Any]]:
    """Extract geometry from any CAD entity type"""
    entity_type = entity.dxftype()
    
    try:
        if entity_type == 'POLYLINE':
            return extract_polyline_geometry(entity)
        elif entity_type == 'LWPOLYLINE':
            return extract_lwpolyline_geometry(entity)
        elif entity_type == 'LINE':
            return extract_line_geometry(entity)
        elif entity_type == 'ARC':
            return extract_arc_geometry(entity)
        elif entity_type == 'CIRCLE':
            return extract_circle_geometry(entity)
        elif entity_type == 'SPLINE':
            return extract_spline_geometry(entity)
        elif entity_type == 'ELLIPSE':
            return extract_ellipse_geometry(entity)
        elif entity_type in ['HATCH', 'SOLID']:
            return extract_hatch_geometry(entity)
        else:
            return None
    except Exception as e:
        logger.warning(f"Error extracting geometry from {entity_type}: {e}")
        return None

def extract_polyline_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from POLYLINE entity with vertex processing"""
    points = []
    
    # Handle POLYLINE with vertices
    if hasattr(entity, 'vertices'):
        for vertex in entity.vertices:
            if hasattr(vertex, 'dxf'):
                x = getattr(vertex.dxf, 'location', [0, 0, 0])[0]
                y = getattr(vertex.dxf, 'location', [0, 0, 0])[1]
                points.append((x, y))
    
    # Fallback: try to get points directly
    if not points and hasattr(entity, 'get_points'):
        try:
            points = [(p[0], p[1]) for p in entity.get_points()]
        except:
            pass
    
    # Another fallback: manual vertex extraction
    if not points:
        try:
            for vertex in entity:
                if hasattr(vertex, 'dxf') and hasattr(vertex.dxf, 'location'):
                    loc = vertex.dxf.location
                    points.append((loc[0], loc[1]))
        except:
            pass
    
    if len(points) < 3:
        return None
    
    # Create polygon from points
    try:
        polygon = Polygon(points)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)  # Fix invalid polygons
        
        return {
            'points': points,
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error creating polygon from POLYLINE: {e}")
        return None

def extract_lwpolyline_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from LWPOLYLINE entity"""
    try:
        points = [(p[0], p[1]) for p in entity.get_points()]
        if len(points) < 3:
            return None
        
        polygon = Polygon(points)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        
        return {
            'points': points,
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error processing LWPOLYLINE: {e}")
        return None

def extract_line_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from LINE entity"""
    try:
        start = entity.dxf.start
        end = entity.dxf.end
        
        # Create a small polygon around the line
        line = LineString([(start[0], start[1]), (end[0], end[1])])
        polygon = line.buffer(0.1)  # Small buffer to create polygon
        
        return {
            'points': [(start[0], start[1]), (end[0], end[1])],
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error processing LINE: {e}")
        return None

def extract_arc_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from ARC entity"""
    try:
        center = entity.dxf.center
        radius = entity.dxf.radius
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        
        # Convert arc to points
        points = []
        angle_step = (end_angle - start_angle) / 20
        for i in range(21):
            angle = start_angle + i * angle_step
            x = center[0] + radius * np.cos(np.radians(angle))
            y = center[1] + radius * np.sin(np.radians(angle))
            points.append((x, y))
        
        # Create polygon from arc points
        line = LineString(points)
        polygon = line.buffer(0.1)
        
        return {
            'points': points,
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error processing ARC: {e}")
        return None

def extract_circle_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from CIRCLE entity"""
    try:
        center = entity.dxf.center
        radius = entity.dxf.radius
        
        # Create circle polygon
        circle_point = Point(center[0], center[1])
        polygon = circle_point.buffer(radius)
        
        return {
            'points': [(center[0], center[1])],
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error processing CIRCLE: {e}")
        return None

def extract_spline_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from SPLINE entity"""
    try:
        if hasattr(entity, 'get_points'):
            points = [(p[0], p[1]) for p in entity.get_points()]
        else:
            # Fallback: use control points
            points = [(p[0], p[1]) for p in entity.control_points]
        
        if len(points) < 2:
            return None
        
        line = LineString(points)
        polygon = line.buffer(0.1)
        
        return {
            'points': points,
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error processing SPLINE: {e}")
        return None

def extract_ellipse_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from ELLIPSE entity"""
    try:
        center = entity.dxf.center
        major_axis = entity.dxf.major_axis
        ratio = entity.dxf.ratio
        
        # Create ellipse polygon approximation
        points = []
        for i in range(36):
            angle = i * 10 * np.pi / 180
            x = center[0] + major_axis[0] * np.cos(angle)
            y = center[1] + major_axis[1] * np.sin(angle) * ratio
            points.append((x, y))
        
        polygon = Polygon(points)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        
        return {
            'points': points,
            'polygon': polygon,
            'area': polygon.area,
            'centroid': polygon.centroid.coords[0],
            'layer': getattr(entity.dxf, 'layer', '0'),
            'color': getattr(entity.dxf, 'color', 7)
        }
    except Exception as e:
        logger.warning(f"Error processing ELLIPSE: {e}")
        return None

def extract_hatch_geometry(entity) -> Dict[str, Any]:
    """Extract geometry from HATCH/SOLID entity"""
    try:
        if hasattr(entity, 'paths'):
            # Process hatch boundary paths
            all_points = []
            for path in entity.paths:
                if hasattr(path, 'vertices'):
                    points = [(v[0], v[1]) for v in path.vertices]
                    all_points.extend(points)
            
            if len(all_points) >= 3:
                polygon = Polygon(all_points)
                if not polygon.is_valid:
                    polygon = polygon.buffer(0)
                
                return {
                    'points': all_points,
                    'polygon': polygon,
                    'area': polygon.area,
                    'centroid': polygon.centroid.coords[0],
                    'layer': getattr(entity.dxf, 'layer', '0'),
                    'color': getattr(entity.dxf, 'color', 7)
                }
        return None
    except Exception as e:
        logger.warning(f"Error processing HATCH: {e}")
        return None

def classify_entity_type(entity, geometry_data) -> str:
    """Classify entity type based on multiple criteria"""
    layer = geometry_data['layer'].upper()
    color = geometry_data['color']
    area = geometry_data['area']
    
    # Classification by layer name
    if any(wall_keyword in layer for wall_keyword in ['WALL', 'MUR', 'STRUCTURE', 'OUTLINE']):
        return 'wall'
    elif any(restricted_keyword in layer for restricted_keyword in ['RESTRICTED', 'STAIR', 'ELEVATOR', 'EQUIPMENT']):
        return 'restricted'
    elif any(entrance_keyword in layer for entrance_keyword in ['DOOR', 'ENTRANCE', 'OPENING', 'PORTE']):
        return 'entrance'
    
    # Classification by color
    if color in [0, 7]:  # Black/white typically walls
        return 'wall'
    elif color in [1, 2]:  # Red typically entrances
        return 'entrance'
    elif color in [5, 6]:  # Blue/cyan typically restricted
        return 'restricted'
    
    # Classification by area (larger areas likely rooms/walls)
    if area > 100:  # Large areas are likely walls or rooms
        return 'wall'
    elif area < 10:  # Small areas might be entrances
        return 'entrance'
    
    # Default classification
    return 'wall'
