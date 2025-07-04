"""
ENTERPRISE DXF PARSER - Full Implementation
"""

import ezdxf
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
import cv2
from sklearn.cluster import DBSCAN
import networkx as nx

class EnterpriseDXFParser:
    """Enterprise-grade DXF parser with complete functionality"""
    
    def __init__(self):
        self.wall_colors = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.restricted_colors = [1, 5]
        self.entrance_colors = [3, 10]
        self.wall_layers = ['WALL', 'WALLS', 'MUR', 'MURS', 'ARCHITECTURE', 'A-WALL']
        self.door_layers = ['DOOR', 'DOORS', 'PORTE', 'PORTES', 'OPENING', 'OPENINGS']
        
    def parse_dxf_file(self, file_path: str) -> Dict[str, Any]:
        """Parse DXF file with enterprise-level precision"""
        try:
            doc = ezdxf.readfile(file_path)
            modelspace = doc.modelspace()
            
            walls = self._detect_walls(modelspace)
            restricted_areas = self._detect_restricted_areas(modelspace)
            entrances = self._detect_entrances_exits(modelspace)
            rooms = self._detect_rooms_from_walls(walls)
            spatial_analysis = self._analyze_spatial_relationships(walls, restricted_areas, entrances)
            
            return {
                'walls': walls,
                'restricted_areas': restricted_areas,
                'entrances_exits': entrances,
                'rooms': rooms,
                'spatial_analysis': spatial_analysis,
                'parsing_method': 'enterprise_precision'
            }
            
        except Exception as e:
            raise Exception(f"Enterprise DXF parsing failed: {str(e)}")
    
    def _detect_walls(self, modelspace) -> List[Dict[str, Any]]:
        """Detect walls with enterprise geometry analysis"""
        walls = []
        
        # Method 1: Layer-based detection
        for entity in modelspace:
            if self._is_wall_entity(entity):
                wall_data = self._extract_wall_geometry(entity)
                if wall_data:
                    walls.append(wall_data)
        
        # Method 2: Line clustering for wall detection
        all_lines = self._extract_all_lines(modelspace)
        clustered_walls = self._cluster_lines_into_walls(all_lines)
        walls.extend(clustered_walls)
        
        # Method 3: Polyline analysis
        polyline_walls = self._extract_walls_from_polylines(modelspace)
        walls.extend(polyline_walls)
        
        # Remove duplicates and validate
        walls = self._validate_and_merge_walls(walls)
        
        return walls
    
    def _detect_restricted_areas(self, modelspace) -> List[Dict[str, Any]]:
        """Detect restricted areas with enterprise analysis"""
        restricted_areas = []
        
        # Method 1: Hatch pattern analysis
        for entity in modelspace.query('HATCH'):
            if self._is_restricted_hatch(entity):
                area_data = self._extract_hatch_boundary(entity)
                if area_data:
                    area_data['restriction_type'] = self._classify_restriction_type(entity)
                    restricted_areas.append(area_data)
        
        # Method 2: Color-coded polygons
        for entity in modelspace:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                if self._is_restricted_by_color(entity):
                    area_data = self._extract_polygon_geometry(entity)
                    if area_data:
                        area_data['restriction_type'] = 'COLOR_CODED'
                        restricted_areas.append(area_data)
        
        return restricted_areas
    
    def _detect_entrances_exits(self, modelspace) -> List[Dict[str, Any]]:
        """Detect entrances and exits with enterprise precision"""
        entrances = []
        
        # Method 1: Door block references
        for entity in modelspace.query('INSERT'):
            if self._is_door_block(entity):
                entrance_data = self._extract_door_geometry(entity)
                if entrance_data:
                    entrances.append(entrance_data)
        
        # Method 2: Gap analysis in walls
        wall_gaps = self._detect_wall_gaps(modelspace)
        for gap in wall_gaps:
            if self._is_entrance_gap(gap):
                entrance_data = {
                    'type': 'ENTRANCE',
                    'geometry': gap['geometry'],
                    'width': gap['width'],
                    'location': gap['center'],
                    'detection_method': 'wall_gap_analysis'
                }
                entrances.append(entrance_data)
        
        return entrances
    
    def _detect_rooms_from_walls(self, walls: List[Dict]) -> List[Dict[str, Any]]:
        """Detect rooms by analyzing wall connectivity"""
        if not walls:
            return []
        
        # Create wall network graph
        wall_graph = self._create_wall_network(walls)
        
        # Find enclosed spaces
        enclosed_spaces = self._find_enclosed_spaces(wall_graph, walls)
        
        # Classify room types
        rooms = []
        for space in enclosed_spaces:
            room_data = {
                'geometry': space['polygon'],
                'area': space['area'],
                'perimeter': space['perimeter'],
                'centroid': space['centroid'],
                'room_type': self._classify_room_type(space),
                'wall_ids': space['wall_ids']
            }
            rooms.append(room_data)
        
        return rooms
    
    def _is_wall_entity(self, entity) -> bool:
        """Determine if entity represents a wall"""
        layer = getattr(entity.dxf, 'layer', '').upper()
        if any(wall_layer in layer for wall_layer in self.wall_layers):
            return True
        
        color = getattr(entity.dxf, 'color', 0)
        if color in self.wall_colors:
            return True
        
        lineweight = getattr(entity.dxf, 'lineweight', 0)
        if lineweight > 50:
            return True
        
        return False
    
    def _extract_wall_geometry(self, entity) -> Optional[Dict[str, Any]]:
        """Extract precise wall geometry"""
        try:
            if entity.dxftype() == 'LINE':
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)
                
                length = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                angle = np.arctan2(end[1] - start[1], end[0] - start[0])
                
                return {
                    'type': 'WALL_LINE',
                    'start_point': start,
                    'end_point': end,
                    'length': length,
                    'angle': angle,
                    'layer': entity.dxf.layer,
                    'color': getattr(entity.dxf, 'color', 0),
                    'thickness': getattr(entity.dxf, 'lineweight', 25) / 100.0
                }
            
            elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = self._extract_polyline_points(entity)
                if len(points) >= 2:
                    return {
                        'type': 'WALL_POLYLINE',
                        'points': points,
                        'layer': entity.dxf.layer,
                        'color': getattr(entity.dxf, 'color', 0),
                        'closed': getattr(entity.dxf, 'closed', False)
                    }
        
        except Exception:
            pass
        
        return None
    
    def _cluster_lines_into_walls(self, lines: List[Dict]) -> List[Dict[str, Any]]:
        """Use machine learning to cluster lines into wall segments"""
        if len(lines) < 2:
            return []
        
        # Extract features for clustering
        features = []
        for line in lines:
            mid_x = (line['start_point'][0] + line['end_point'][0]) / 2
            mid_y = (line['start_point'][1] + line['end_point'][1]) / 2
            features.append([mid_x, mid_y, line['angle'], line['length']])
        
        # Apply DBSCAN clustering
        features_array = np.array(features)
        clustering = DBSCAN(eps=50, min_samples=2).fit(features_array)
        
        # Group lines by clusters
        clustered_walls = []
        for cluster_id in set(clustering.labels_):
            if cluster_id == -1:
                continue
            
            cluster_lines = [lines[i] for i in range(len(lines)) if clustering.labels_[i] == cluster_id]
            merged_wall = self._merge_line_cluster(cluster_lines)
            if merged_wall:
                clustered_walls.append(merged_wall)
        
        return clustered_walls
    
    def _extract_walls_from_polylines(self, modelspace) -> List[Dict[str, Any]]:
        """Extract walls from polyline entities"""
        walls = []
        
        for entity in modelspace.query('LWPOLYLINE'):
            if self._is_wall_entity(entity):
                points = self._extract_polyline_points(entity)
                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        start = points[i]
                        end = points[i + 1]
                        length = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                        
                        if length > 10:
                            wall = {
                                'type': 'WALL_SEGMENT',
                                'start_point': start,
                                'end_point': end,
                                'length': length,
                                'angle': np.arctan2(end[1] - start[1], end[0] - start[0]),
                                'layer': entity.dxf.layer,
                                'source': 'polyline_segment'
                            }
                            walls.append(wall)
        
        return walls
    
    def _is_restricted_hatch(self, entity) -> bool:
        """Determine if hatch represents restricted area"""
        pattern_name = getattr(entity.dxf, 'pattern_name', '').upper()
        restricted_patterns = ['SOLID', 'ANSI31', 'ANSI32', 'CROSS', 'DOTS']
        
        if pattern_name in restricted_patterns:
            return True
        
        color = getattr(entity.dxf, 'color', 0)
        if color in self.restricted_colors:
            return True
        
        return False
    
    def _extract_hatch_boundary(self, entity) -> Optional[Dict[str, Any]]:
        """Extract boundary geometry from hatch entity"""
        try:
            boundaries = []
            
            for path in entity.paths:
                boundary_points = []
                
                if hasattr(path, 'edges'):
                    for edge in path.edges:
                        if hasattr(edge, 'start') and hasattr(edge, 'end'):
                            boundary_points.append((edge.start[0], edge.start[1]))
                            boundary_points.append((edge.end[0], edge.end[1]))
                
                if len(boundary_points) >= 3:
                    unique_points = []
                    for point in boundary_points:
                        if not unique_points or np.linalg.norm(np.array(point) - np.array(unique_points[-1])) > 1e-6:
                            unique_points.append(point)
                    
                    if len(unique_points) >= 3:
                        polygon = Polygon(unique_points)
                        if polygon.is_valid:
                            boundaries.append({
                                'geometry': unique_points,
                                'area': polygon.area,
                                'centroid': (polygon.centroid.x, polygon.centroid.y)
                            })
            
            if boundaries:
                largest = max(boundaries, key=lambda x: x['area'])
                return {
                    'type': 'RESTRICTED_AREA',
                    'geometry': largest['geometry'],
                    'area': largest['area'],
                    'centroid': largest['centroid'],
                    'detection_method': 'hatch_analysis'
                }
        
        except Exception:
            pass
        
        return None
    
    def _detect_wall_gaps(self, modelspace) -> List[Dict[str, Any]]:
        """Detect gaps in walls that could be entrances"""
        wall_lines = []
        for entity in modelspace:
            if entity.dxftype() == 'LINE' and self._is_wall_entity(entity):
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)
                wall_lines.append(LineString([start, end]))
        
        if len(wall_lines) < 2:
            return []
        
        gaps = []
        tolerance = 200
        
        for i, line1 in enumerate(wall_lines):
            for j, line2 in enumerate(wall_lines[i+1:], i+1):
                if self._are_lines_parallel(line1, line2):
                    gap_info = self._calculate_gap_between_lines(line1, line2)
                    if gap_info and gap_info['distance'] < tolerance:
                        gaps.append(gap_info)
        
        return gaps
    
    def _create_wall_network(self, walls: List[Dict]) -> nx.Graph:
        """Create network graph of wall connections"""
        G = nx.Graph()
        
        for i, wall in enumerate(walls):
            G.add_node(i, wall_data=wall)
        
        tolerance = 50
        
        for i, wall1 in enumerate(walls):
            for j, wall2 in enumerate(walls[i+1:], i+1):
                if self._walls_connected(wall1, wall2, tolerance):
                    G.add_edge(i, j)
        
        return G
    
    def _find_enclosed_spaces(self, wall_graph: nx.Graph, walls: List[Dict]) -> List[Dict[str, Any]]:
        """Find enclosed spaces formed by connected walls"""
        enclosed_spaces = []
        
        try:
            cycles = list(nx.simple_cycles(wall_graph))
            
            for cycle in cycles:
                if len(cycle) >= 3:
                    cycle_walls = [walls[i] for i in cycle]
                    polygon_points = self._extract_polygon_from_wall_cycle(cycle_walls)
                    
                    if polygon_points and len(polygon_points) >= 3:
                        try:
                            polygon = Polygon(polygon_points)
                            if polygon.is_valid and polygon.area > 100:
                                enclosed_spaces.append({
                                    'polygon': polygon_points,
                                    'area': polygon.area,
                                    'perimeter': polygon.length,
                                    'centroid': (polygon.centroid.x, polygon.centroid.y),
                                    'wall_ids': cycle
                                })
                        except Exception:
                            continue
        
        except Exception:
            # Fallback: use convex hull of wall endpoints
            all_points = []
            for wall in walls:
                if 'start_point' in wall:
                    all_points.extend([wall['start_point'], wall['end_point']])
                elif 'points' in wall:
                    all_points.extend(wall['points'])
            
            if len(all_points) >= 3:
                try:
                    from scipy.spatial import ConvexHull
                    hull = ConvexHull(all_points)
                    hull_points = [all_points[i] for i in hull.vertices]
                    
                    polygon = Polygon(hull_points)
                    if polygon.is_valid:
                        enclosed_spaces.append({
                            'polygon': hull_points,
                            'area': polygon.area,
                            'perimeter': polygon.length,
                            'centroid': (polygon.centroid.x, polygon.centroid.y),
                            'wall_ids': list(range(len(walls)))
                        })
                except Exception:
                    pass
        
        return enclosed_spaces
    
    def _analyze_spatial_relationships(self, walls, restricted_areas, entrances) -> Dict[str, Any]:
        """Analyze spatial relationships between architectural elements"""
        analysis = {
            'wall_connectivity': self._analyze_wall_connectivity(walls),
            'access_analysis': self._analyze_access_patterns(entrances, restricted_areas),
            'circulation_paths': self._identify_circulation_paths(walls, entrances),
            'security_zones': self._identify_security_zones(restricted_areas, entrances)
        }
        
        return analysis
    
    def _extract_polyline_points(self, entity) -> List[Tuple[float, float]]:
        """Extract points from polyline entity"""
        points = []
        try:
            if hasattr(entity, 'get_points'):
                for point in entity.get_points():
                    if len(point) >= 2:
                        points.append((point[0], point[1]))
            elif hasattr(entity, 'vertices'):
                for vertex in entity.vertices:
                    if hasattr(vertex.dxf, 'location'):
                        loc = vertex.dxf.location
                        points.append((loc[0], loc[1]))
        except Exception:
            pass
        
        return points
    
    def _validate_and_merge_walls(self, walls: List[Dict]) -> List[Dict[str, Any]]:
        """Validate and merge overlapping wall segments"""
        if not walls:
            return []
        
        unique_walls = []
        for wall in walls:
            is_duplicate = False
            for existing in unique_walls:
                if self._walls_similar(wall, existing):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_walls.append(wall)
        
        merged_walls = self._merge_collinear_walls(unique_walls)
        
        return merged_walls
    
    def _walls_similar(self, wall1: Dict, wall2: Dict, tolerance: float = 10.0) -> bool:
        """Check if two walls are similar"""
        if wall1.get('type') != wall2.get('type'):
            return False
        
        if 'start_point' in wall1 and 'start_point' in wall2:
            dist1 = np.linalg.norm(np.array(wall1['start_point']) - np.array(wall2['start_point']))
            dist2 = np.linalg.norm(np.array(wall1['end_point']) - np.array(wall2['end_point']))
            
            return dist1 < tolerance and dist2 < tolerance
        
        return False
    
    def _merge_collinear_walls(self, walls: List[Dict]) -> List[Dict[str, Any]]:
        """Merge collinear adjacent wall segments"""
        merged = []
        used = set()
        
        for i, wall in enumerate(walls):
            if i in used:
                continue
            
            current_wall = wall.copy()
            used.add(i)
            
            changed = True
            while changed:
                changed = False
                for j, other_wall in enumerate(walls):
                    if j in used:
                        continue
                    
                    if self._can_merge_walls(current_wall, other_wall):
                        current_wall = self._merge_two_walls(current_wall, other_wall)
                        used.add(j)
                        changed = True
                        break
            
            merged.append(current_wall)
        
        return merged
    
    def _can_merge_walls(self, wall1: Dict, wall2: Dict) -> bool:
        """Check if two walls can be merged"""
        if not ('start_point' in wall1 and 'start_point' in wall2):
            return False
        
        tolerance = 20.0
        
        dist1 = np.linalg.norm(np.array(wall1['end_point']) - np.array(wall2['start_point']))
        dist2 = np.linalg.norm(np.array(wall1['start_point']) - np.array(wall2['end_point']))
        
        if dist1 < tolerance or dist2 < tolerance:
            angle_diff = abs(wall1.get('angle', 0) - wall2.get('angle', 0))
            return angle_diff < 0.1 or abs(angle_diff - np.pi) < 0.1
        
        return False
    
    def _merge_two_walls(self, wall1: Dict, wall2: Dict) -> Dict[str, Any]:
        """Merge two adjacent collinear walls"""
        points = [wall1['start_point'], wall1['end_point'], wall2['start_point'], wall2['end_point']]
        
        max_dist = 0
        start_point = points[0]
        end_point = points[1]
        
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                dist = np.linalg.norm(np.array(points[i]) - np.array(points[j]))
                if dist > max_dist:
                    max_dist = dist
                    start_point = points[i]
                    end_point = points[j]
        
        merged_wall = wall1.copy()
        merged_wall.update({
            'start_point': start_point,
            'end_point': end_point,
            'length': max_dist,
            'angle': np.arctan2(end_point[1] - start_point[1], end_point[0] - start_point[0])
        })
        
        return merged_wall
    
    def _classify_room_type(self, space: Dict) -> str:
        """Classify room type based on geometry"""
        area = space['area']
        
        if area < 500:
            return 'Storage/Utility'
        elif area < 2000:
            return 'Office/Small Room'
        elif area < 5000:
            return 'Meeting Room'
        elif area < 10000:
            return 'Large Office'
        else:
            return 'Hall/Open Space'
    
    def _analyze_wall_connectivity(self, walls: List[Dict]) -> Dict[str, Any]:
        """Analyze how walls connect to each other"""
        if not walls:
            return {'connected_segments': 0, 'isolated_segments': 0}
        
        connections = 0
        tolerance = 50.0
        
        for i, wall1 in enumerate(walls):
            for j, wall2 in enumerate(walls[i+1:], i+1):
                if self._walls_connected(wall1, wall2, tolerance):
                    connections += 1
        
        return {
            'total_walls': len(walls),
            'connections': connections,
            'connectivity_ratio': connections / max(len(walls), 1)
        }
    
    def _walls_connected(self, wall1: Dict, wall2: Dict, tolerance: float) -> bool:
        """Check if two walls are connected"""
        if not ('start_point' in wall1 and 'start_point' in wall2):
            return False
        
        points1 = [wall1['start_point'], wall1['end_point']]
        points2 = [wall2['start_point'], wall2['end_point']]
        
        for p1 in points1:
            for p2 in points2:
                if np.linalg.norm(np.array(p1) - np.array(p2)) < tolerance:
                    return True
        
        return False
    
    def _analyze_access_patterns(self, entrances: List[Dict], restricted_areas: List[Dict]) -> Dict[str, Any]:
        """Analyze access patterns and security implications"""
        analysis = {
            'total_entrances': len(entrances),
            'restricted_access_points': 0,
            'security_risk_score': 0
        }
        
        for entrance in entrances:
            entrance_point = Point(entrance['location'])
            
            for restricted in restricted_areas:
                if 'geometry' in restricted:
                    restricted_poly = Polygon(restricted['geometry'])
                    if entrance_point.distance(restricted_poly) < 100:
                        analysis['restricted_access_points'] += 1
        
        if analysis['total_entrances'] > 0:
            analysis['security_risk_score'] = analysis['restricted_access_points'] / analysis['total_entrances']
        
        return analysis
    
    def _identify_circulation_paths(self, walls: List[Dict], entrances: List[Dict]) -> List[Dict[str, Any]]:
        """Identify main circulation paths"""
        paths = []
        
        if len(entrances) >= 2:
            for i, entrance1 in enumerate(entrances):
                for entrance2 in entrances[i+1:]:
                    path = {
                        'start': entrance1['location'],
                        'end': entrance2['location'],
                        'type': 'CIRCULATION_PATH',
                        'length': np.linalg.norm(
                            np.array(entrance1['location']) - np.array(entrance2['location'])
                        )
                    }
                    paths.append(path)
        
        return paths
    
    def _identify_security_zones(self, restricted_areas: List[Dict], entrances: List[Dict]) -> List[Dict[str, Any]]:
        """Identify security zones and access control requirements"""
        security_zones = []
        
        for restricted in restricted_areas:
            if 'geometry' in restricted:
                nearby_entrances = []
                restricted_poly = Polygon(restricted['geometry'])
                
                for entrance in entrances:
                    entrance_point = Point(entrance['location'])
                    if entrance_point.distance(restricted_poly) < 200:
                        nearby_entrances.append(entrance)
                
                security_zone = {
                    'area_geometry': restricted['geometry'],
                    'area_size': restricted.get('area', 0),
                    'access_points': len(nearby_entrances),
                    'security_level': self._calculate_security_level(restricted, nearby_entrances),
                    'access_control_required': len(nearby_entrances) > 0
                }
                security_zones.append(security_zone)
        
        return security_zones
    
    def _calculate_security_level(self, restricted_area: Dict, nearby_entrances: List[Dict]) -> str:
        """Calculate security level based on area and access points"""
        area_size = restricted_area.get('area', 0)
        num_entrances = len(nearby_entrances)
        
        if area_size > 10000 and num_entrances > 2:
            return 'HIGH'
        elif area_size > 5000 or num_entrances > 1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _are_lines_parallel(self, line1: LineString, line2: LineString, tolerance: float = 0.1) -> bool:
        """Check if two lines are roughly parallel"""
        try:
            coords1 = list(line1.coords)
            coords2 = list(line2.coords)
            
            if len(coords1) >= 2 and len(coords2) >= 2:
                angle1 = np.arctan2(coords1[1][1] - coords1[0][1], coords1[1][0] - coords1[0][0])
                angle2 = np.arctan2(coords2[1][1] - coords2[0][1], coords2[1][0] - coords2[0][0])
                
                angle_diff = abs(angle1 - angle2)
                return angle_diff < tolerance or abs(angle_diff - np.pi) < tolerance
        except Exception:
            pass
        
        return False
    
    def _calculate_gap_between_lines(self, line1: LineString, line2: LineString) -> Optional[Dict[str, Any]]:
        """Calculate gap between two parallel lines"""
        try:
            distance = line1.distance(line2)
            
            if 50 < distance < 300:
                from shapely.ops import nearest_points
                p1, p2 = nearest_points(line1, line2)
                
                return {
                    'geometry': [p1.coords[0], p2.coords[0]],
                    'distance': distance,
                    'width': distance,
                    'center': ((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                }
        except Exception:
            pass
        
        return None
    
    def _is_entrance_gap(self, gap: Dict) -> bool:
        """Determine if a gap represents an entrance"""
        width = gap.get('width', 0)
        return 80 <= width <= 250
    
    def _is_door_block(self, entity) -> bool:
        """Check if INSERT entity represents a door"""
        block_name = getattr(entity.dxf, 'name', '').upper()
        door_keywords = ['DOOR', 'PORTE', 'GATE', 'ENTRANCE', 'EXIT']
        
        return any(keyword in block_name for keyword in door_keywords)
    
    def _extract_door_geometry(self, entity) -> Optional[Dict[str, Any]]:
        """Extract door geometry from INSERT entity"""
        try:
            insert_point = (entity.dxf.insert.x, entity.dxf.insert.y)
            rotation = getattr(entity.dxf, 'rotation', 0)
            
            return {
                'type': 'DOOR',
                'location': insert_point,
                'rotation': rotation,
                'block_name': entity.dxf.name,
                'detection_method': 'block_reference'
            }
        except Exception:
            pass
        
        return None
    
    def _is_restricted_by_color(self, entity) -> bool:
        """Check if entity color indicates restricted area"""
        color = getattr(entity.dxf, 'color', 0)
        return color in self.restricted_colors
    
    def _extract_polygon_geometry(self, entity) -> Optional[Dict[str, Any]]:
        """Extract polygon geometry from polyline entity"""
        try:
            points = self._extract_polyline_points(entity)
            if len(points) >= 3:
                polygon = Polygon(points)
                if polygon.is_valid:
                    return {
                        'type': 'POLYGON_AREA',
                        'geometry': points,
                        'area': polygon.area,
                        'centroid': (polygon.centroid.x, polygon.centroid.y),
                        'detection_method': 'color_coding'
                    }
        except Exception:
            pass
        
        return None
    
    def _classify_restriction_type(self, entity) -> str:
        """Classify the type of restriction based on hatch pattern"""
        pattern_name = getattr(entity.dxf, 'pattern_name', '').upper()
        
        if pattern_name == 'SOLID':
            return 'NO_ACCESS'
        elif pattern_name in ['ANSI31', 'ANSI32']:
            return 'LIMITED_ACCESS'
        elif pattern_name == 'DOTS':
            return 'SECURITY_ZONE'
        else:
            return 'RESTRICTED'
    
    def _merge_line_cluster(self, cluster_lines: List[Dict]) -> Optional[Dict[str, Any]]:
        """Merge a cluster of lines into a single wall segment"""
        if not cluster_lines:
            return None
        
        all_points = []
        for line in cluster_lines:
            all_points.extend([line['start_point'], line['end_point']])
        
        if len(all_points) < 2:
            return None
        
        max_distance = 0
        start_point = all_points[0]
        end_point = all_points[1]
        
        for i in range(len(all_points)):
            for j in range(i + 1, len(all_points)):
                distance = np.linalg.norm(np.array(all_points[i]) - np.array(all_points[j]))
                if distance > max_distance:
                    max_distance = distance
                    start_point = all_points[i]
                    end_point = all_points[j]
        
        merged_wall = {
            'type': 'MERGED_WALL',
            'start_point': start_point,
            'end_point': end_point,
            'length': max_distance,
            'angle': np.arctan2(end_point[1] - start_point[1], end_point[0] - start_point[0]),
            'layer': cluster_lines[0].get('layer', '0'),
            'source_lines': len(cluster_lines)
        }
        
        return merged_wall
    
    def _extract_all_lines(self, modelspace) -> List[Dict[str, Any]]:
        """Extract all LINE entities from modelspace"""
        lines = []
        
        for entity in modelspace.query('LINE'):
            try:
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)
                
                length = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                angle = np.arctan2(end[1] - start[1], end[0] - start[0])
                
                if length > 10:
                    line_data = {
                        'start_point': start,
                        'end_point': end,
                        'length': length,
                        'angle': angle,
                        'layer': entity.dxf.layer,
                        'color': getattr(entity.dxf, 'color', 0)
                    }
                    lines.append(line_data)
            except Exception:
                continue
        
        return lines
    
    def _extract_polygon_from_wall_cycle(self, cycle_walls: List[Dict]) -> Optional[List[Tuple[float, float]]]:
        """Extract polygon points from a cycle of connected walls"""
        if not cycle_walls:
            return None
        
        points = []
        for wall in cycle_walls:
            if 'start_point' in wall:
                points.extend([wall['start_point'], wall['end_point']])
            elif 'points' in wall:
                points.extend(wall['points'])
        
        if len(points) < 3:
            return None
        
        unique_points = []
        tolerance = 10.0
        
        for point in points:
            is_duplicate = False
            for existing in unique_points:
                if np.linalg.norm(np.array(point) - np.array(existing)) < tolerance:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_points.append(point)
        
        return unique_points if len(unique_points) >= 3 else None