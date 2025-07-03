"""
ÎLOT LAYOUT ENGINE - User-defined layout profiles with automatic placement and constraint optimization
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import itertools
from scipy.optimize import minimize
from dataclasses import dataclass
import json

@dataclass
class IlotProfile:
    """Îlot layout profile definition"""
    name: str
    width: float
    height: float
    area: float
    shape_type: str  # 'rectangular', 'L_shape', 'U_shape', 'custom'
    proportions: Dict[str, float]  # width_ratio, height_ratio, etc.
    constraints: Dict[str, Any]
    priority: int
    color: str

class IlotLayoutEngine:
    """Enterprise îlot layout engine with intelligent placement algorithms"""
    
    def __init__(self):
        self.predefined_profiles = self._create_predefined_profiles()
        self.placement_constraints = {
            'min_corridor_width': 120,  # Minimum corridor width in cm
            'min_wall_clearance': 50,   # Minimum clearance from walls
            'min_ilot_spacing': 80,     # Minimum spacing between îlots
            'max_corridor_length': 2000, # Maximum corridor length
            'accessibility_width': 150,  # Wheelchair accessibility width
            'fire_exit_clearance': 200  # Fire exit clearance
        }
        
    def _create_predefined_profiles(self) -> Dict[str, IlotProfile]:
        """Create predefined îlot profiles for different use cases"""
        profiles = {}
        
        # Standard Office Îlots
        profiles['standard_office'] = IlotProfile(
            name="Standard Office",
            width=400,
            height=300,
            area=120000,  # 12 m²
            shape_type='rectangular',
            proportions={'width_ratio': 1.33, 'height_ratio': 1.0},
            constraints={'min_perimeter_access': True, 'corner_preference': False},
            priority=1,
            color='#3498DB'
        )
        
        profiles['executive_office'] = IlotProfile(
            name="Executive Office",
            width=600,
            height=400,
            area=240000,  # 24 m²
            shape_type='rectangular',
            proportions={'width_ratio': 1.5, 'height_ratio': 1.0},
            constraints={'wall_adjacent': True, 'window_access': True},
            priority=2,
            color='#E74C3C'
        )
        
        profiles['meeting_room'] = IlotProfile(
            name="Meeting Room",
            width=500,
            height=350,
            area=175000,  # 17.5 m²
            shape_type='rectangular',
            proportions={'width_ratio': 1.43, 'height_ratio': 1.0},
            constraints={'central_access': True, 'sound_isolation': True},
            priority=3,
            color='#F39C12'
        )
        
        profiles['open_workspace'] = IlotProfile(
            name="Open Workspace",
            width=800,
            height=600,
            area=480000,  # 48 m²
            shape_type='rectangular',
            proportions={'width_ratio': 1.33, 'height_ratio': 1.0},
            constraints={'natural_light': True, 'flexible_layout': True},
            priority=1,
            color='#27AE60'
        )
        
        profiles['collaboration_zone'] = IlotProfile(
            name="Collaboration Zone",
            width=450,
            height=450,
            area=202500,  # 20.25 m²
            shape_type='L_shape',
            proportions={'width_ratio': 1.0, 'height_ratio': 1.0},
            constraints={'high_traffic_access': True, 'technology_ready': True},
            priority=2,
            color='#9B59B6'
        )
        
        profiles['storage_unit'] = IlotProfile(
            name="Storage Unit",
            width=250,
            height=200,
            area=50000,  # 5 m²
            shape_type='rectangular',
            proportions={'width_ratio': 1.25, 'height_ratio': 1.0},
            constraints={'wall_adjacent': True, 'service_access': True},
            priority=4,
            color='#95A5A6'
        )
        
        profiles['reception_area'] = IlotProfile(
            name="Reception Area",
            width=700,
            height=500,
            area=350000,  # 35 m²
            shape_type='U_shape',
            proportions={'width_ratio': 1.4, 'height_ratio': 1.0},
            constraints={'entrance_proximity': True, 'visibility': True},
            priority=1,
            color='#E67E22'
        )
        
        return profiles
    
    def create_custom_profile(self, name: str, specifications: Dict[str, Any]) -> IlotProfile:
        """Create custom îlot profile from user specifications"""
        return IlotProfile(
            name=name,
            width=specifications.get('width', 400),
            height=specifications.get('height', 300),
            area=specifications.get('area', 120000),
            shape_type=specifications.get('shape_type', 'rectangular'),
            proportions=specifications.get('proportions', {'width_ratio': 1.33, 'height_ratio': 1.0}),
            constraints=specifications.get('constraints', {}),
            priority=specifications.get('priority', 3),
            color=specifications.get('color', '#34495E')
        )
    
    def generate_layout_plan(self, 
                           room_geometry: List[Tuple[float, float]], 
                           walls: List[Dict], 
                           entrances: List[Dict],
                           restricted_areas: List[Dict],
                           ilot_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate complete îlot layout plan with automatic placement"""
        
        # Create room polygon
        room_polygon = Polygon(room_geometry)
        
        # Analyze room characteristics
        room_analysis = self._analyze_room_characteristics(room_polygon, walls, entrances)
        
        # Generate placement zones
        placement_zones = self._generate_placement_zones(room_polygon, walls, restricted_areas)
        
        # Create îlot instances from requirements
        ilots = self._create_ilot_instances(ilot_requirements)
        
        # Optimize îlot placement
        optimized_layout = self._optimize_ilot_placement(ilots, placement_zones, room_analysis)
        
        # Generate corridor system
        corridor_system = self._generate_corridor_system(optimized_layout, entrances, room_polygon)
        
        # Validate layout against constraints
        validation_results = self._validate_layout(optimized_layout, corridor_system, room_polygon)
        
        return {
            'ilots': optimized_layout,
            'corridors': corridor_system,
            'room_analysis': room_analysis,
            'placement_zones': placement_zones,
            'validation': validation_results,
            'layout_metrics': self._calculate_layout_metrics(optimized_layout, corridor_system, room_polygon)
        }
    
    def _analyze_room_characteristics(self, room_polygon: Polygon, walls: List[Dict], entrances: List[Dict]) -> Dict[str, Any]:
        """Analyze room characteristics for optimal îlot placement"""
        
        # Calculate room metrics
        area = room_polygon.area
        perimeter = room_polygon.length
        bounds = room_polygon.bounds
        centroid = room_polygon.centroid
        
        # Analyze shape complexity
        convex_hull = room_polygon.convex_hull
        shape_complexity = 1 - (room_polygon.area / convex_hull.area)
        
        # Identify natural light sources (assume walls with windows)
        natural_light_walls = self._identify_natural_light_walls(walls)
        
        # Analyze entrance positions
        entrance_analysis = self._analyze_entrance_positions(entrances, room_polygon)
        
        # Calculate aspect ratio
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        aspect_ratio = max(width, height) / min(width, height)
        
        return {
            'area': area,
            'perimeter': perimeter,
            'width': width,
            'height': height,
            'aspect_ratio': aspect_ratio,
            'shape_complexity': shape_complexity,
            'centroid': (centroid.x, centroid.y),
            'bounds': bounds,
            'natural_light_walls': natural_light_walls,
            'entrance_analysis': entrance_analysis,
            'usable_area_ratio': self._calculate_usable_area_ratio(room_polygon)
        }
    
    def _generate_placement_zones(self, room_polygon: Polygon, walls: List[Dict], restricted_areas: List[Dict]) -> List[Dict[str, Any]]:
        """Generate optimal placement zones within the room"""
        
        # Create buffer zones around walls and restricted areas
        wall_buffer_zones = []
        for wall in walls:
            if 'start_point' in wall and 'end_point' in wall:
                wall_line = Point(wall['start_point']).buffer(self.placement_constraints['min_wall_clearance'])
                wall_buffer_zones.append(wall_line)
        
        restricted_buffer_zones = []
        for restricted in restricted_areas:
            if 'geometry' in restricted:
                restricted_poly = Polygon(restricted['geometry'])
                buffer_zone = restricted_poly.buffer(self.placement_constraints['min_wall_clearance'])
                restricted_buffer_zones.append(buffer_zone)
        
        # Combine all buffer zones
        all_buffers = wall_buffer_zones + restricted_buffer_zones
        if all_buffers:
            combined_buffers = unary_union(all_buffers)
            available_area = room_polygon.difference(combined_buffers)
        else:
            available_area = room_polygon
        
        # Divide available area into placement zones
        placement_zones = self._subdivide_into_zones(available_area, room_polygon)
        
        return placement_zones
    
    def _subdivide_into_zones(self, available_area: Polygon, room_polygon: Polygon) -> List[Dict[str, Any]]:
        """Subdivide available area into placement zones"""
        zones = []
        
        if available_area.is_empty:
            return zones
        
        # Handle MultiPolygon case
        if hasattr(available_area, 'geoms'):
            polygons = list(available_area.geoms)
        else:
            polygons = [available_area]
        
        for i, poly in enumerate(polygons):
            if poly.area > 10000:  # Minimum zone area (1 m²)
                bounds = poly.bounds
                centroid = poly.centroid
                
                # Classify zone based on position
                zone_type = self._classify_zone_position(centroid, room_polygon)
                
                zone = {
                    'id': i,
                    'geometry': poly,
                    'area': poly.area,
                    'centroid': (centroid.x, centroid.y),
                    'bounds': bounds,
                    'zone_type': zone_type,
                    'accessibility_score': self._calculate_accessibility_score(poly, room_polygon),
                    'natural_light_score': self._calculate_natural_light_score(poly, room_polygon)
                }
                zones.append(zone)
        
        return zones
    
    def _create_ilot_instances(self, ilot_requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create îlot instances from requirements"""
        ilots = []
        
        for req in ilot_requirements:
            profile_name = req.get('profile', 'standard_office')
            quantity = req.get('quantity', 1)
            custom_specs = req.get('custom_specifications', {})
            
            # Get base profile
            if profile_name in self.predefined_profiles:
                base_profile = self.predefined_profiles[profile_name]
            else:
                base_profile = self.predefined_profiles['standard_office']
            
            # Create instances
            for i in range(quantity):
                ilot = {
                    'id': f"{profile_name}_{i+1}",
                    'profile': base_profile,
                    'width': custom_specs.get('width', base_profile.width),
                    'height': custom_specs.get('height', base_profile.height),
                    'area': custom_specs.get('area', base_profile.area),
                    'shape_type': custom_specs.get('shape_type', base_profile.shape_type),
                    'constraints': {**base_profile.constraints, **custom_specs.get('constraints', {})},
                    'priority': custom_specs.get('priority', base_profile.priority),
                    'color': custom_specs.get('color', base_profile.color),
                    'placed': False,
                    'position': None,
                    'rotation': 0
                }
                ilots.append(ilot)
        
        return ilots
    
    def _optimize_ilot_placement(self, ilots: List[Dict], placement_zones: List[Dict], room_analysis: Dict) -> List[Dict[str, Any]]:
        """Optimize îlot placement using advanced algorithms"""
        
        # Sort îlots by priority
        sorted_ilots = sorted(ilots, key=lambda x: x['priority'])
        
        # Initialize placement solution
        placed_ilots = []
        occupied_areas = []
        
        for ilot in sorted_ilots:
            best_placement = self._find_best_placement(ilot, placement_zones, occupied_areas, room_analysis)
            
            if best_placement:
                # Update îlot with placement information
                ilot.update({
                    'placed': True,
                    'position': best_placement['position'],
                    'rotation': best_placement['rotation'],
                    'zone_id': best_placement['zone_id'],
                    'placement_score': best_placement['score'],
                    'geometry': best_placement['geometry']
                })
                
                placed_ilots.append(ilot)
                occupied_areas.append(best_placement['geometry'])
            else:
                # Mark as unplaced
                ilot['placed'] = False
                ilot['placement_issue'] = 'No suitable placement found'
                placed_ilots.append(ilot)
        
        return placed_ilots
    
    def _find_best_placement(self, ilot: Dict, placement_zones: List[Dict], occupied_areas: List[Polygon], room_analysis: Dict) -> Optional[Dict[str, Any]]:
        """Find the best placement for a single îlot"""
        
        best_placement = None
        best_score = -1
        
        # Try each placement zone
        for zone in placement_zones:
            # Try different positions within the zone
            candidate_positions = self._generate_candidate_positions(ilot, zone)
            
            for position in candidate_positions:
                # Try different rotations
                for rotation in [0, 90, 180, 270]:
                    placement_geometry = self._create_ilot_geometry(ilot, position, rotation)
                    
                    if self._is_valid_placement(placement_geometry, zone['geometry'], occupied_areas):
                        score = self._calculate_placement_score(ilot, placement_geometry, zone, room_analysis)
                        
                        if score > best_score:
                            best_score = score
                            best_placement = {
                                'position': position,
                                'rotation': rotation,
                                'zone_id': zone['id'],
                                'geometry': placement_geometry,
                                'score': score
                            }
        
        return best_placement
    
    def _generate_candidate_positions(self, ilot: Dict, zone: Dict) -> List[Tuple[float, float]]:
        """Generate candidate positions within a zone"""
        positions = []
        
        zone_bounds = zone['bounds']
        zone_width = zone_bounds[2] - zone_bounds[0]
        zone_height = zone_bounds[3] - zone_bounds[1]
        
        # Grid-based position generation
        grid_size = 50  # 50cm grid
        
        for x in np.arange(zone_bounds[0], zone_bounds[2] - ilot['width'], grid_size):
            for y in np.arange(zone_bounds[1], zone_bounds[3] - ilot['height'], grid_size):
                positions.append((x + ilot['width']/2, y + ilot['height']/2))
        
        # Add zone centroid as high-priority position
        positions.insert(0, zone['centroid'])
        
        return positions
    
    def _create_ilot_geometry(self, ilot: Dict, position: Tuple[float, float], rotation: float) -> Polygon:
        """Create îlot geometry at specified position and rotation"""
        
        cx, cy = position
        width = ilot['width']
        height = ilot['height']
        
        if ilot['shape_type'] == 'rectangular':
            # Create rectangle centered at position
            half_width = width / 2
            half_height = height / 2
            
            corners = [
                (cx - half_width, cy - half_height),
                (cx + half_width, cy - half_height),
                (cx + half_width, cy + half_height),
                (cx - half_width, cy + half_height)
            ]
            
        elif ilot['shape_type'] == 'L_shape':
            # Create L-shaped îlot
            corners = self._create_l_shape_geometry(cx, cy, width, height)
            
        elif ilot['shape_type'] == 'U_shape':
            # Create U-shaped îlot
            corners = self._create_u_shape_geometry(cx, cy, width, height)
            
        else:
            # Default to rectangular
            half_width = width / 2
            half_height = height / 2
            corners = [
                (cx - half_width, cy - half_height),
                (cx + half_width, cy - half_height),
                (cx + half_width, cy + half_height),
                (cx - half_width, cy + half_height)
            ]
        
        # Apply rotation if needed
        if rotation != 0:
            corners = self._rotate_points(corners, cx, cy, np.radians(rotation))
        
        return Polygon(corners)
    
    def _create_l_shape_geometry(self, cx: float, cy: float, width: float, height: float) -> List[Tuple[float, float]]:
        """Create L-shaped geometry"""
        # L-shape with 60% width and height for the main sections
        main_width = width * 0.6
        main_height = height * 0.6
        
        corners = [
            (cx - width/2, cy - height/2),
            (cx - width/2 + main_width, cy - height/2),
            (cx - width/2 + main_width, cy - height/2 + main_height),
            (cx + width/2, cy - height/2 + main_height),
            (cx + width/2, cy + height/2),
            (cx - width/2, cy + height/2)
        ]
        
        return corners
    
    def _create_u_shape_geometry(self, cx: float, cy: float, width: float, height: float) -> List[Tuple[float, float]]:
        """Create U-shaped geometry"""
        # U-shape with opening at the top
        opening_width = width * 0.4
        wall_thickness = height * 0.2
        
        corners = [
            (cx - width/2, cy - height/2),
            (cx + width/2, cy - height/2),
            (cx + width/2, cy + height/2 - wall_thickness),
            (cx + opening_width/2, cy + height/2 - wall_thickness),
            (cx + opening_width/2, cy + height/2),
            (cx - opening_width/2, cy + height/2),
            (cx - opening_width/2, cy + height/2 - wall_thickness),
            (cx - width/2, cy + height/2 - wall_thickness)
        ]
        
        return corners
    
    def _rotate_points(self, points: List[Tuple[float, float]], cx: float, cy: float, angle: float) -> List[Tuple[float, float]]:
        """Rotate points around center"""
        rotated_points = []
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        
        for x, y in points:
            # Translate to origin
            x_translated = x - cx
            y_translated = y - cy
            
            # Rotate
            x_rotated = x_translated * cos_angle - y_translated * sin_angle
            y_rotated = x_translated * sin_angle + y_translated * cos_angle
            
            # Translate back
            rotated_points.append((x_rotated + cx, y_rotated + cy))
        
        return rotated_points
    
    def _is_valid_placement(self, ilot_geometry: Polygon, zone_geometry: Polygon, occupied_areas: List[Polygon]) -> bool:
        """Check if îlot placement is valid"""
        
        # Check if îlot is within zone
        if not zone_geometry.contains(ilot_geometry):
            return False
        
        # Check for overlaps with occupied areas
        for occupied in occupied_areas:
            if ilot_geometry.intersects(occupied):
                return False
        
        # Check minimum spacing
        for occupied in occupied_areas:
            if ilot_geometry.distance(occupied) < self.placement_constraints['min_ilot_spacing']:
                return False
        
        return True
    
    def _calculate_placement_score(self, ilot: Dict, geometry: Polygon, zone: Dict, room_analysis: Dict) -> float:
        """Calculate placement score for optimization"""
        
        score = 0.0
        
        # Base score from zone characteristics
        score += zone['accessibility_score'] * 0.3
        score += zone['natural_light_score'] * 0.2
        
        # Priority-based scoring
        priority_weight = (5 - ilot['priority']) * 0.2
        score += priority_weight
        
        # Constraint satisfaction scoring
        constraints = ilot['constraints']
        
        if constraints.get('wall_adjacent', False):
            # Check proximity to walls
            wall_proximity_score = self._calculate_wall_proximity_score(geometry, room_analysis)
            score += wall_proximity_score * 0.15
        
        if constraints.get('central_access', False):
            # Prefer central positions
            room_center = Point(room_analysis['centroid'])
            distance_to_center = geometry.centroid.distance(room_center)
            max_distance = max(room_analysis['width'], room_analysis['height']) / 2
            centrality_score = 1 - (distance_to_center / max_distance)
            score += centrality_score * 0.1
        
        if constraints.get('entrance_proximity', False):
            # Prefer positions near entrances
            entrance_score = self._calculate_entrance_proximity_score(geometry, room_analysis)
            score += entrance_score * 0.15
        
        # Shape efficiency score
        shape_efficiency = geometry.area / geometry.minimum_rotated_rectangle.area
        score += shape_efficiency * 0.1
        
        return score
    
    def _generate_corridor_system(self, placed_ilots: List[Dict], entrances: List[Dict], room_polygon: Polygon) -> Dict[str, Any]:
        """Generate corridor system connecting îlots and entrances"""
        
        # Extract îlot positions
        ilot_positions = []
        ilot_geometries = []
        
        for ilot in placed_ilots:
            if ilot['placed']:
                ilot_positions.append(ilot['position'])
                ilot_geometries.append(ilot['geometry'])
        
        # Create corridor network
        corridor_network = self._create_corridor_network(ilot_positions, entrances, room_polygon)
        
        # Optimize corridor widths
        optimized_corridors = self._optimize_corridor_widths(corridor_network, ilot_geometries)
        
        # Generate corridor geometry
        corridor_geometry = self._generate_corridor_geometry(optimized_corridors)
        
        return {
            'network': corridor_network,
            'corridors': optimized_corridors,
            'geometry': corridor_geometry,
            'total_length': sum(corridor['length'] for corridor in optimized_corridors),
            'total_area': sum(corridor['area'] for corridor in optimized_corridors)
        }
    
    def _create_corridor_network(self, ilot_positions: List[Tuple[float, float]], entrances: List[Dict], room_polygon: Polygon) -> Dict[str, Any]:
        """Create corridor network using graph algorithms"""
        
        # Create nodes for îlots and entrances
        nodes = []
        
        # Add îlot nodes
        for i, pos in enumerate(ilot_positions):
            nodes.append({
                'id': f'ilot_{i}',
                'type': 'ilot',
                'position': pos
            })
        
        # Add entrance nodes
        for i, entrance in enumerate(entrances):
            nodes.append({
                'id': f'entrance_{i}',
                'type': 'entrance',
                'position': entrance['location']
            })
        
        # Create minimum spanning tree for efficient corridor layout
        import networkx as nx
        
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node['id'], **node)
        
        # Add edges with distances as weights
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                distance = np.linalg.norm(np.array(node1['position']) - np.array(node2['position']))
                G.add_edge(node1['id'], node2['id'], weight=distance)
        
        # Find minimum spanning tree
        mst = nx.minimum_spanning_tree(G)
        
        return {
            'graph': G,
            'mst': mst,
            'nodes': nodes
        }
    
    def _optimize_corridor_widths(self, corridor_network: Dict, ilot_geometries: List[Polygon]) -> List[Dict[str, Any]]:
        """Optimize corridor widths based on traffic and accessibility requirements"""
        
        corridors = []
        mst = corridor_network['mst']
        nodes = {node['id']: node for node in corridor_network['nodes']}
        
        for edge in mst.edges(data=True):
            node1_id, node2_id, edge_data = edge
            node1 = nodes[node1_id]
            node2 = nodes[node2_id]
            
            # Calculate corridor properties
            start_pos = node1['position']
            end_pos = node2['position']
            length = edge_data['weight']
            
            # Determine corridor width based on traffic requirements
            width = self._calculate_corridor_width(node1, node2, length)
            
            corridor = {
                'id': f"{node1_id}_{node2_id}",
                'start_node': node1_id,
                'end_node': node2_id,
                'start_position': start_pos,
                'end_position': end_pos,
                'length': length,
                'width': width,
                'area': length * width,
                'type': self._classify_corridor_type(node1, node2)
            }
            
            corridors.append(corridor)
        
        return corridors
    
    def _calculate_corridor_width(self, node1: Dict, node2: Dict, length: float) -> float:
        """Calculate optimal corridor width"""
        
        base_width = self.placement_constraints['min_corridor_width']
        
        # Increase width for main circulation paths
        if node1['type'] == 'entrance' or node2['type'] == 'entrance':
            base_width = max(base_width, self.placement_constraints['accessibility_width'])
        
        # Increase width for long corridors
        if length > 1000:  # 10m
            base_width *= 1.2
        
        # Ensure fire safety compliance
        base_width = max(base_width, self.placement_constraints['fire_exit_clearance'])
        
        return base_width
    
    def _classify_corridor_type(self, node1: Dict, node2: Dict) -> str:
        """Classify corridor type based on connected nodes"""
        
        if node1['type'] == 'entrance' or node2['type'] == 'entrance':
            return 'main_circulation'
        else:
            return 'secondary_circulation'
    
    def _generate_corridor_geometry(self, corridors: List[Dict]) -> List[Dict[str, Any]]:
        """Generate corridor geometry polygons"""
        
        corridor_geometries = []
        
        for corridor in corridors:
            start_pos = corridor['start_position']
            end_pos = corridor['end_position']
            width = corridor['width']
            
            # Create corridor polygon
            corridor_polygon = self._create_corridor_polygon(start_pos, end_pos, width)
            
            corridor_geometries.append({
                'id': corridor['id'],
                'geometry': corridor_polygon,
                'type': corridor['type'],
                'width': width,
                'length': corridor['length']
            })
        
        return corridor_geometries
    
    def _create_corridor_polygon(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], width: float) -> Polygon:
        """Create corridor polygon between two points"""
        
        # Calculate perpendicular vector
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = np.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return Polygon()
        
        # Normalize and get perpendicular
        unit_x = dx / length
        unit_y = dy / length
        perp_x = -unit_y * width / 2
        perp_y = unit_x * width / 2
        
        # Create corridor corners
        corners = [
            (start_pos[0] + perp_x, start_pos[1] + perp_y),
            (end_pos[0] + perp_x, end_pos[1] + perp_y),
            (end_pos[0] - perp_x, end_pos[1] - perp_y),
            (start_pos[0] - perp_x, start_pos[1] - perp_y)
        ]
        
        return Polygon(corners)
    
    def _validate_layout(self, placed_ilots: List[Dict], corridor_system: Dict, room_polygon: Polygon) -> Dict[str, Any]:
        """Validate layout against all constraints and regulations"""
        
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'compliance_score': 0.0
        }
        
        # Check placement success rate
        total_ilots = len(placed_ilots)
        placed_count = sum(1 for ilot in placed_ilots if ilot['placed'])
        placement_rate = placed_count / total_ilots if total_ilots > 0 else 0
        
        if placement_rate < 0.8:
            validation_results['warnings'].append(f"Low placement rate: {placement_rate:.1%}")
        
        # Check corridor accessibility
        min_corridor_width = min(corridor['width'] for corridor in corridor_system['corridors']) if corridor_system['corridors'] else 0
        
        if min_corridor_width < self.placement_constraints['accessibility_width']:
            validation_results['errors'].append("Corridor width below accessibility requirements")
            validation_results['valid'] = False
        
        # Check fire safety compliance
        fire_exits = self._count_fire_exits(corridor_system)
        required_exits = max(2, total_ilots // 10)  # Minimum 2, plus 1 per 10 îlots
        
        if fire_exits < required_exits:
            validation_results['errors'].append(f"Insufficient fire exits: {fire_exits}/{required_exits}")
            validation_results['valid'] = False
        
        # Check space utilization
        total_ilot_area = sum(ilot.get('area', 0) for ilot in placed_ilots if ilot['placed'])
        total_corridor_area = corridor_system.get('total_area', 0)
        room_area = room_polygon.area
        
        utilization_rate = (total_ilot_area + total_corridor_area) / room_area
        
        if utilization_rate > 0.85:
            validation_results['warnings'].append(f"High space utilization: {utilization_rate:.1%}")
        elif utilization_rate < 0.6:
            validation_results['warnings'].append(f"Low space utilization: {utilization_rate:.1%}")
        
        # Calculate compliance score
        compliance_factors = [
            placement_rate,
            1.0 if min_corridor_width >= self.placement_constraints['accessibility_width'] else 0.5,
            min(1.0, fire_exits / required_exits),
            1.0 if 0.6 <= utilization_rate <= 0.85 else 0.7
        ]
        
        validation_results['compliance_score'] = np.mean(compliance_factors)
        
        return validation_results
    
    def _calculate_layout_metrics(self, placed_ilots: List[Dict], corridor_system: Dict, room_polygon: Polygon) -> Dict[str, Any]:
        """Calculate comprehensive layout metrics"""
        
        # Basic metrics
        total_ilots = len(placed_ilots)
        placed_ilots_count = sum(1 for ilot in placed_ilots if ilot['placed'])
        
        # Area calculations
        total_ilot_area = sum(ilot.get('area', 0) for ilot in placed_ilots if ilot['placed'])
        total_corridor_area = corridor_system.get('total_area', 0)
        room_area = room_polygon.area
        
        # Efficiency metrics
        space_utilization = (total_ilot_area + total_corridor_area) / room_area
        circulation_ratio = total_corridor_area / total_ilot_area if total_ilot_area > 0 else 0
        
        # Accessibility metrics
        avg_corridor_width = np.mean([corridor['width'] for corridor in corridor_system['corridors']]) if corridor_system['corridors'] else 0
        
        # Connectivity metrics
        connectivity_score = self._calculate_connectivity_score(corridor_system)
        
        return {
            'total_ilots': total_ilots,
            'placed_ilots': placed_ilots_count,
            'placement_rate': placed_ilots_count / total_ilots if total_ilots > 0 else 0,
            'room_area': room_area,
            'total_ilot_area': total_ilot_area,
            'total_corridor_area': total_corridor_area,
            'space_utilization': space_utilization,
            'circulation_ratio': circulation_ratio,
            'avg_corridor_width': avg_corridor_width,
            'total_corridor_length': corridor_system.get('total_length', 0),
            'connectivity_score': connectivity_score
        }
    
    def _identify_natural_light_walls(self, walls: List[Dict]) -> List[Dict]:
        """Identify walls that likely have natural light (windows)"""
        # Simplified assumption: exterior walls have natural light
        natural_light_walls = []
        
        for wall in walls:
            # Assume walls on the perimeter have natural light
            # This would need more sophisticated analysis in a real implementation
            if wall.get('layer', '').upper() in ['EXTERIOR', 'EXTERNAL', 'WINDOW']:
                natural_light_walls.append(wall)
        
        return natural_light_walls
    
    def _analyze_entrance_positions(self, entrances: List[Dict], room_polygon: Polygon) -> Dict[str, Any]:
        """Analyze entrance positions and accessibility"""
        if not entrances:
            return {'count': 0, 'distribution': 'none'}
        
        entrance_points = [Point(entrance['location']) for entrance in entrances]
        
        # Calculate entrance distribution
        centroid = room_polygon.centroid
        distances = [point.distance(centroid) for point in entrance_points]
        
        return {
            'count': len(entrances),
            'avg_distance_to_center': np.mean(distances),
            'distribution': 'distributed' if len(set(distances)) > 1 else 'clustered'
        }
    
    def _calculate_usable_area_ratio(self, room_polygon: Polygon) -> float:
        """Calculate ratio of usable area to total area"""
        # Simplified calculation - in reality would consider structural elements
        return 0.85  # Assume 85% of area is usable
    
    def _classify_zone_position(self, centroid: Point, room_polygon: Polygon) -> str:
        """Classify zone position within room"""
        room_centroid = room_polygon.centroid
        distance_to_center = centroid.distance(room_centroid)
        
        bounds = room_polygon.bounds
        max_distance = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) / 2
        
        if distance_to_center < max_distance * 0.3:
            return 'central'
        elif distance_to_center < max_distance * 0.7:
            return 'intermediate'
        else:
            return 'peripheral'
    
    def _calculate_accessibility_score(self, zone_geometry: Polygon, room_polygon: Polygon) -> float:
        """Calculate accessibility score for a zone"""
        # Simplified scoring based on zone position and shape
        zone_centroid = zone_geometry.centroid
        room_centroid = room_polygon.centroid
        
        # Distance factor
        distance = zone_centroid.distance(room_centroid)
        bounds = room_polygon.bounds
        max_distance = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) / 2
        distance_score = 1 - (distance / max_distance)
        
        # Shape factor (more regular shapes score higher)
        area = zone_geometry.area
        perimeter = zone_geometry.length
        compactness = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        
        return (distance_score * 0.7 + compactness * 0.3)
    
    def _calculate_natural_light_score(self, zone_geometry: Polygon, room_polygon: Polygon) -> float:
        """Calculate natural light score for a zone"""
        # Simplified scoring - zones closer to perimeter get higher scores
        zone_centroid = zone_geometry.centroid
        
        # Distance to room boundary
        boundary_distance = zone_centroid.distance(room_polygon.boundary)
        
        # Normalize score (closer to boundary = higher score)
        bounds = room_polygon.bounds
        max_distance = min(bounds[2] - bounds[0], bounds[3] - bounds[1]) / 2
        
        return max(0, 1 - (boundary_distance / max_distance))
    
    def _calculate_wall_proximity_score(self, geometry: Polygon, room_analysis: Dict) -> float:
        """Calculate wall proximity score"""
        # Simplified implementation
        return 0.7  # Default score
    
    def _calculate_entrance_proximity_score(self, geometry: Polygon, room_analysis: Dict) -> float:
        """Calculate entrance proximity score"""
        # Simplified implementation
        return 0.6  # Default score
    
    def _count_fire_exits(self, corridor_system: Dict) -> int:
        """Count fire exits in corridor system"""
        # Count entrances connected to corridor system
        entrance_connections = 0
        for corridor in corridor_system.get('corridors', []):
            if 'entrance' in corridor.get('start_node', '') or 'entrance' in corridor.get('end_node', ''):
                entrance_connections += 1
        
        return max(1, entrance_connections)  # At least 1 exit
    
    def _calculate_connectivity_score(self, corridor_system: Dict) -> float:
        """Calculate connectivity score of corridor system"""
        corridors = corridor_system.get('corridors', [])
        if not corridors:
            return 0.0
        
        # Simple connectivity metric based on corridor count and total length
        total_length = sum(corridor['length'] for corridor in corridors)
        avg_length = total_length / len(corridors)
        
        # Normalize score (shorter average length = better connectivity)
        return max(0, 1 - (avg_length / 2000))  # 2000 = max reasonable corridor length
    
    def export_layout_data(self, layout_result: Dict[str, Any]) -> Dict[str, Any]:
        """Export layout data in standardized format"""
        
        export_data = {
            'metadata': {
                'generated_at': np.datetime64('now').astype(str),
                'engine_version': '1.0.0',
                'layout_type': 'ilot_placement'
            },
            'ilots': [],
            'corridors': [],
            'metrics': layout_result.get('layout_metrics', {}),
            'validation': layout_result.get('validation', {})
        }
        
        # Export îlot data
        for ilot in layout_result.get('ilots', []):
            if ilot['placed']:
                ilot_data = {
                    'id': ilot['id'],
                    'profile_name': ilot['profile'].name,
                    'position': ilot['position'],
                    'rotation': ilot['rotation'],
                    'dimensions': {
                        'width': ilot['width'],
                        'height': ilot['height'],
                        'area': ilot['area']
                    },
                    'geometry': list(ilot['geometry'].exterior.coords),
                    'color': ilot['color']
                }
                export_data['ilots'].append(ilot_data)
        
        # Export corridor data
        for corridor in layout_result.get('corridors', {}).get('geometry', []):
            corridor_data = {
                'id': corridor['id'],
                'type': corridor['type'],
                'width': corridor['width'],
                'length': corridor['length'],
                'geometry': list(corridor['geometry'].exterior.coords)
            }
            export_data['corridors'].append(corridor_data)
        
        return export_data