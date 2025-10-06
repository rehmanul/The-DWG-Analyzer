"""
Production CAD Parser - Robust DXF/DWG Processing
Handles all CAD entity types with precise color-based classification
NO SIMULATIONS - Only real CAD data processing
"""

import ezdxf
import logging
import numpy as np
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ZoneType(Enum):
    """Zone classification based on color coding"""
    WALL = "wall"  # Black lines - boundaries
    RESTRICTED = "restricted"  # Blue zones - NO ENTREE (stairs, elevators)
    ENTRANCE = "entrance"  # Red zones - ENTREE/SORTIE
    OPEN_SPACE = "open_space"  # Available for îlot placement


@dataclass
class CADZone:
    """Represents a zone extracted from CAD"""
    zone_type: ZoneType
    polygon: Polygon
    area: float
    layer: str
    color: int
    true_color: Optional[int]
    
    @property
    def centroid(self) -> Tuple[float, float]:
        c = self.polygon.centroid
        return (c.x, c.y)


class ProductionCADParser:
    """
    Production-grade CAD parser with robust entity processing
    Strictly follows color coding rules for zone classification
    """
    
    # AutoCAD Color Index (ACI) to zone type mapping
    COLOR_MAP = {
        1: ZoneType.ENTRANCE,      # Red = ENTREE/SORTIE
        5: ZoneType.RESTRICTED,    # Blue = NO ENTREE
        7: ZoneType.WALL,          # White/Black = MUR
        8: ZoneType.WALL,          # Dark gray = MUR
        0: ZoneType.WALL,          # BYBLOCK (default to wall)
        256: ZoneType.WALL,        # BYLAYER (default to wall)
    }
    
    def __init__(self):
        self.wall_buffer = 0.15  # 15cm wall thickness
        self.min_area_threshold = 0.1  # Minimum 0.1m² area
        self.entrance_buffer = 0.2  # 20cm clearance around entrances
        
    def parse_dxf(self, file_path: str) -> Tuple[List[Polygon], List[Polygon], List[Polygon], List[Polygon]]:
        """
        Parse DXF file and extract zones by type
        Returns: (walls, restricted_areas, entrances, open_spaces)
        """
        try:
            doc = ezdxf.readfile(file_path)
        except Exception as e:
            logger.error(f"Failed to read DXF file: {e}")
            raise ValueError(f"Invalid DXF file: {e}")
        
        msp = doc.modelspace()
        
        # Extract all entities
        raw_zones = []
        for entity in msp:
            zones = self._extract_entity_zones(entity)
            raw_zones.extend(zones)
        
        logger.info(f"Extracted {len(raw_zones)} raw zones from {file_path}")
        
        # Classify and organize zones
        walls = []
        restricted_areas = []
        entrances = []
        potential_spaces = []
        
        for zone in raw_zones:
            if zone.zone_type == ZoneType.WALL:
                walls.append(zone.polygon)
            elif zone.zone_type == ZoneType.RESTRICTED:
                restricted_areas.append(zone.polygon)
            elif zone.zone_type == ZoneType.ENTRANCE:
                entrances.append(zone.polygon)
            else:
                potential_spaces.append(zone.polygon)
        
        # Calculate open spaces (areas NOT occupied by walls/restricted/entrances)
        open_spaces = self._calculate_open_spaces(walls, restricted_areas, entrances, potential_spaces)
        
        logger.info(f"Classified zones - Walls: {len(walls)}, Restricted: {len(restricted_areas)}, "
                   f"Entrances: {len(entrances)}, Open spaces: {len(open_spaces)}")
        
        return walls, restricted_areas, entrances, open_spaces
    
    def _extract_entity_zones(self, entity) -> List[CADZone]:
        """Extract zones from any CAD entity type"""
        entity_type = entity.dxftype()
        
        # Get entity properties
        layer = getattr(entity.dxf, 'layer', '0')
        color = getattr(entity.dxf, 'color', 7)
        true_color = getattr(entity.dxf, 'true_color', None) if hasattr(entity.dxf, 'true_color') else None
        
        # Extract geometry based on entity type
        polygons = []
        
        if entity_type == 'LWPOLYLINE':
            polygons = self._extract_lwpolyline(entity)
        elif entity_type == 'POLYLINE':
            polygons = self._extract_polyline(entity)
        elif entity_type == 'LINE':
            polygons = self._extract_line(entity)
        elif entity_type == 'ARC':
            polygons = self._extract_arc(entity)
        elif entity_type == 'CIRCLE':
            polygons = self._extract_circle(entity)
        elif entity_type == 'SPLINE':
            polygons = self._extract_spline(entity)
        elif entity_type == 'ELLIPSE':
            polygons = self._extract_ellipse(entity)
        elif entity_type in ['HATCH', 'SOLID', '3DFACE']:
            polygons = self._extract_filled_entity(entity)
        
        # Create CADZone objects with classification
        zones = []
        for poly in polygons:
            if poly and poly.is_valid and poly.area >= self.min_area_threshold:
                zone_type = self._classify_zone(color, true_color, layer, poly.area)
                zones.append(CADZone(
                    zone_type=zone_type,
                    polygon=poly,
                    area=poly.area,
                    layer=layer,
                    color=color,
                    true_color=true_color
                ))
        
        return zones
    
    def _extract_lwpolyline(self, entity) -> List[Polygon]:
        """Extract polygon from LWPOLYLINE"""
        try:
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) < 3:
                # Convert line to thin polygon
                if len(points) == 2:
                    line = LineString(points)
                    return [line.buffer(self.wall_buffer)]
                return []
            
            poly = Polygon(points)
            if not poly.is_valid:
                poly = poly.buffer(0)
            return [poly] if poly.is_valid else []
        except Exception as e:
            logger.warning(f"Failed to extract LWPOLYLINE: {e}")
            return []
    
    def _extract_polyline(self, entity) -> List[Polygon]:
        """Extract polygon from POLYLINE"""
        try:
            points = []
            if hasattr(entity, 'vertices'):
                for vertex in entity.vertices:
                    loc = vertex.dxf.location
                    points.append((loc[0], loc[1]))
            
            if len(points) < 3:
                if len(points) == 2:
                    line = LineString(points)
                    return [line.buffer(self.wall_buffer)]
                return []
            
            poly = Polygon(points)
            if not poly.is_valid:
                poly = poly.buffer(0)
            return [poly] if poly.is_valid else []
        except Exception as e:
            logger.warning(f"Failed to extract POLYLINE: {e}")
            return []
    
    def _extract_line(self, entity) -> List[Polygon]:
        """Extract polygon from LINE (create buffered corridor)"""
        try:
            start = entity.dxf.start
            end = entity.dxf.end
            line = LineString([(start[0], start[1]), (end[0], end[1])])
            return [line.buffer(self.wall_buffer)]
        except Exception as e:
            logger.warning(f"Failed to extract LINE: {e}")
            return []
    
    def _extract_arc(self, entity) -> List[Polygon]:
        """Extract polygon from ARC"""
        try:
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = np.radians(entity.dxf.start_angle)
            end_angle = np.radians(entity.dxf.end_angle)
            
            # Sample points along arc
            num_points = max(10, int(abs(end_angle - start_angle) * 20))
            angles = np.linspace(start_angle, end_angle, num_points)
            points = [(center[0] + radius * np.cos(a), 
                      center[1] + radius * np.sin(a)) for a in angles]
            
            line = LineString(points)
            return [line.buffer(self.wall_buffer)]
        except Exception as e:
            logger.warning(f"Failed to extract ARC: {e}")
            return []
    
    def _extract_circle(self, entity) -> List[Polygon]:
        """Extract polygon from CIRCLE"""
        try:
            center = entity.dxf.center
            radius = entity.dxf.radius
            point = Point(center[0], center[1])
            return [point.buffer(radius)]
        except Exception as e:
            logger.warning(f"Failed to extract CIRCLE: {e}")
            return []
    
    def _extract_spline(self, entity) -> List[Polygon]:
        """Extract polygon from SPLINE"""
        try:
            if hasattr(entity, 'flattening'):
                points = [(p[0], p[1]) for p in entity.flattening(0.01)]
            else:
                points = [(p[0], p[1]) for p in entity.control_points]
            
            if len(points) < 2:
                return []
            
            line = LineString(points)
            return [line.buffer(self.wall_buffer)]
        except Exception as e:
            logger.warning(f"Failed to extract SPLINE: {e}")
            return []
    
    def _extract_ellipse(self, entity) -> List[Polygon]:
        """Extract polygon from ELLIPSE"""
        try:
            center = entity.dxf.center
            major_axis = entity.dxf.major_axis
            ratio = entity.dxf.ratio
            
            # Create ellipse points
            points = []
            for i in range(36):
                angle = i * 10 * np.pi / 180
                x = center[0] + major_axis[0] * np.cos(angle)
                y = center[1] + major_axis[1] * np.sin(angle) * ratio
                points.append((x, y))
            
            poly = Polygon(points)
            if not poly.is_valid:
                poly = poly.buffer(0)
            return [poly] if poly.is_valid else []
        except Exception as e:
            logger.warning(f"Failed to extract ELLIPSE: {e}")
            return []
    
    def _extract_filled_entity(self, entity) -> List[Polygon]:
        """Extract polygon from HATCH/SOLID entities"""
        try:
            if hasattr(entity, 'paths'):
                polygons = []
                for path in entity.paths:
                    if hasattr(path, 'vertices'):
                        points = [(v[0], v[1]) for v in path.vertices]
                        if len(points) >= 3:
                            poly = Polygon(points)
                            if not poly.is_valid:
                                poly = poly.buffer(0)
                            if poly.is_valid:
                                polygons.append(poly)
                return polygons
            return []
        except Exception as e:
            logger.warning(f"Failed to extract HATCH: {e}")
            return []
    
    def _classify_zone(self, color: int, true_color: Optional[int], layer: str, area: float) -> ZoneType:
        """
        Classify zone based on color coding rules
        Priority: true_color > ACI color > layer name > area-based heuristics
        """
        
        # Priority 1: True color RGB classification
        if true_color is not None:
            r = (true_color >> 16) & 0xFF
            g = (true_color >> 8) & 0xFF
            b = true_color & 0xFF
            
            # Red dominant (R > 180, G < 100, B < 100)
            if r > 180 and g < 100 and b < 100:
                return ZoneType.ENTRANCE
            
            # Blue dominant (B > 180, R < 100, G < 150)
            if b > 180 and r < 100 and g < 150:
                return ZoneType.RESTRICTED
            
            # Black/Gray (all components < 100 or all > 200)
            if (r < 100 and g < 100 and b < 100) or (r > 200 and g > 200 and b > 200):
                return ZoneType.WALL
        
        # Priority 2: AutoCAD Color Index (ACI)
        if color in self.COLOR_MAP:
            return self.COLOR_MAP[color]
        
        # Priority 3: Layer name analysis
        layer_upper = layer.upper()
        
        if any(kw in layer_upper for kw in ['WALL', 'MUR', 'STRUCTURE', 'OUTLINE']):
            return ZoneType.WALL
        
        if any(kw in layer_upper for kw in ['STAIR', 'ELEVATOR', 'LIFT', 'RESTRICTED', 'EQUIPMENT']):
            return ZoneType.RESTRICTED
        
        if any(kw in layer_upper for kw in ['DOOR', 'ENTRANCE', 'OPENING', 'PORTE', 'EXIT']):
            return ZoneType.ENTRANCE
        
        # Priority 4: Area-based heuristics
        if area < 2:  # Small areas likely entrances
            return ZoneType.ENTRANCE
        elif area > 100:  # Large areas likely structural
            return ZoneType.WALL
        
        # Default: treat as wall (conservative approach)
        return ZoneType.WALL
    
    def _calculate_open_spaces(self, walls: List[Polygon], restricted: List[Polygon], 
                              entrances: List[Polygon], potential_spaces: List[Polygon]) -> List[Polygon]:
        """
        Calculate open spaces available for îlot placement
        These are areas NOT covered by walls, restricted zones, or entrances
        """
        
        # Get overall bounding box
        all_geoms = walls + restricted + entrances
        if potential_spaces:
            all_geoms.extend(potential_spaces)
        
        if not all_geoms:
            logger.warning("No geometries found to calculate open spaces")
            return []
        
        # Calculate bounds
        all_bounds = [g.bounds for g in all_geoms]
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        # Create overall floor area
        floor_area = Polygon([
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y)
        ])
        
        # Remove all obstacles
        obstacles = []
        
        # Add walls
        if walls:
            obstacles.extend(walls)
        
        # Add restricted areas (with buffer)
        if restricted:
            obstacles.extend([r.buffer(0.1) for r in restricted])
        
        # Add entrance buffers (îlots cannot touch entrances)
        if entrances:
            obstacles.extend([e.buffer(self.entrance_buffer) for e in entrances])
        
        # Union all obstacles
        if obstacles:
            try:
                obstacle_union = unary_union(obstacles)
                remaining_space = floor_area.difference(obstacle_union)
            except Exception as e:
                logger.error(f"Failed to calculate open spaces: {e}")
                return []
        else:
            remaining_space = floor_area
        
        # Extract individual spaces
        open_spaces = []
        if remaining_space.geom_type == 'Polygon':
            if remaining_space.area >= self.min_area_threshold:
                open_spaces.append(remaining_space)
        elif remaining_space.geom_type == 'MultiPolygon':
            for poly in remaining_space.geoms:
                if poly.area >= self.min_area_threshold:
                    open_spaces.append(poly)
        
        logger.info(f"Calculated {len(open_spaces)} open spaces for îlot placement")
        return open_spaces
