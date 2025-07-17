"""
Intelligent Corridor System - Phase 3 Implementation
Advanced corridor generation with pathfinding and optimization
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union, linemerge
import networkx as nx
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial.distance import cdist
import math
import logging

logger = logging.getLogger(__name__)

@dataclass
class CorridorConfig:
    """Configuration for corridor generation"""
    width: float = 1.8
    min_width: float = 1.2
    max_width: float = 3.0
    junction_buffer: float = 0.5
    optimization_iterations: int = 100
    pathfinding_algorithm: str = "A*"  # A*, Dijkstra, or RRT
    
    # Corridor styles
    style: str = "straight"  # straight, curved, organic
    junction_style: str = "rounded"  # 90_corners, rounded, beveled
    
    # Connection preferences
    connect_to_entrances: bool = True
    connect_to_walls: bool = False
    avoid_restricted: bool = True
    
    # Optimization parameters
    minimize_total_length: bool = True
    maximize_accessibility: bool = True
    ensure_connectivity: bool = True

@dataclass
class CorridorSegment:
    """Represents a corridor segment"""
    id: int
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    width: float
    length: float
    polygon: Polygon
    connects_to: List[int]
    segment_type: str = "main"  # main, junction, entrance_connection
    
    def __post_init__(self):
        if self.length == 0:
            self.length = math.sqrt(
                (self.end_point[0] - self.start_point[0])**2 + 
                (self.end_point[1] - self.start_point[1])**2
            )

@dataclass
class CorridorNetwork:
    """Complete corridor network"""
    segments: List[CorridorSegment]
    junctions: List[Dict]
    total_length: float
    connectivity_score: float
    accessibility_score: float
    
    def get_network_polygon(self) -> Polygon:
        """Get unified polygon of entire corridor network"""
        if not self.segments:
            return Polygon()
        
        polygons = [segment.polygon for segment in self.segments]
        return unary_union(polygons)

class IntelligentCorridorSystem:
    """
    Advanced corridor generation system with intelligent pathfinding
    Creates optimal circulation networks connecting all îlots
    """
    
    def __init__(self, config: CorridorConfig):
        self.config = config
        self.ilots = []
        self.walls = []
        self.restricted_areas = []
        self.entrances = []
        self.available_space = []
        
        # Network analysis
        self.graph = nx.Graph()
        self.corridor_network = None
        
        # Pathfinding grid
        self.grid_resolution = 0.1
        self.pathfinding_grid = None
        self.grid_bounds = None

    def generate_corridor_network(self, ilots: List[Dict], walls: List[Dict], 
                                 restricted_areas: List[Dict], entrances: List[Dict], 
                                 available_space: List[Dict]) -> CorridorNetwork:
        """
        Generate complete corridor network connecting all îlots
        """
        logger.info("Starting intelligent corridor generation")
        
        # Initialize spatial context
        self.ilots = self._process_ilots(ilots)
        self.walls = self._process_walls(walls)
        self.restricted_areas = self._process_restricted_areas(restricted_areas)
        self.entrances = self._process_entrances(entrances)
        self.available_space = self._process_available_space(available_space)
        
        # Phase 1: Create pathfinding grid
        self._create_pathfinding_grid()
        
        # Phase 2: Generate initial corridor network
        initial_network = self._generate_initial_network()
        
        # Phase 3: Optimize corridor paths
        optimized_network = self._optimize_corridor_paths(initial_network)
        
        # Phase 4: Add junction improvements
        final_network = self._enhance_junctions(optimized_network)
        
        # Phase 5: Validate and finalize
        self.corridor_network = self._validate_and_finalize(final_network)
        
        logger.info(f"Generated corridor network with {len(self.corridor_network.segments)} segments")
        return self.corridor_network

    def _process_ilots(self, ilots: List[Dict]) -> List[Dict]:
        """Process îlots for corridor generation"""
        processed_ilots = []
        for ilot in ilots:
            if 'polygon' in ilot:
                processed_ilots.append({
                    'id': ilot.get('id', len(processed_ilots)),
                    'polygon': ilot['polygon'],
                    'centroid': ilot['polygon'].centroid,
                    'area': ilot.get('area', ilot['polygon'].area),
                    'category': ilot.get('category', 'Standard')
                })
            elif 'x' in ilot and 'y' in ilot:
                polygon = box(ilot['x'], ilot['y'], 
                            ilot['x'] + ilot['width'], ilot['y'] + ilot['height'])
                processed_ilots.append({
                    'id': ilot.get('id', len(processed_ilots)),
                    'polygon': polygon,
                    'centroid': polygon.centroid,
                    'area': ilot.get('area', polygon.area),
                    'category': ilot.get('category', 'Standard')
                })
        return processed_ilots

    def _process_walls(self, walls: List[Dict]) -> List[Polygon]:
        """Process walls that corridors should avoid"""
        processed_walls = []
        for wall in walls:
            if 'points' in wall and len(wall['points']) >= 2:
                try:
                    if len(wall['points']) == 2:
                        line = LineString(wall['points'])
                        wall_polygon = line.buffer(0.1)
                        processed_walls.append(wall_polygon)
                    elif len(wall['points']) >= 3:
                        wall_polygon = Polygon(wall['points'])
                        if wall_polygon.is_valid:
                            processed_walls.append(wall_polygon)
                except Exception as e:
                    logger.warning(f"Invalid wall geometry: {e}")
        return processed_walls

    def _process_restricted_areas(self, restricted: List[Dict]) -> List[Polygon]:
        """Process restricted areas that corridors must avoid"""
        processed_restricted = []
        for area in restricted:
            if 'points' in area and len(area['points']) >= 3:
                try:
                    polygon = Polygon(area['points'])
                    if polygon.is_valid:
                        # Buffer restricted areas
                        buffered = polygon.buffer(self.config.width / 2)
                        processed_restricted.append(buffered)
                except Exception as e:
                    logger.warning(f"Invalid restricted area: {e}")
        return processed_restricted

    def _process_entrances(self, entrances: List[Dict]) -> List[Dict]:
        """Process entrances that corridors should connect to"""
        processed_entrances = []
        for entrance in entrances:
            if 'points' in entrance and len(entrance['points']) >= 2:
                try:
                    if len(entrance['points']) == 2:
                        # Line entrance
                        line = LineString(entrance['points'])
                        midpoint = line.interpolate(0.5, normalized=True)
                        processed_entrances.append({
                            'geometry': line,
                            'connection_point': (midpoint.x, midpoint.y),
                            'type': 'line'
                        })
                    elif len(entrance['points']) >= 3:
                        # Area entrance
                        polygon = Polygon(entrance['points'])
                        if polygon.is_valid:
                            centroid = polygon.centroid
                            processed_entrances.append({
                                'geometry': polygon,
                                'connection_point': (centroid.x, centroid.y),
                                'type': 'area'
                            })
                except Exception as e:
                    logger.warning(f"Invalid entrance geometry: {e}")
        return processed_entrances

    def _process_available_space(self, available: List[Dict]) -> List[Polygon]:
        """Process available space for corridor routing"""
        processed_space = []
        for space in available:
            if 'points' in space and len(space['points']) >= 3:
                try:
                    polygon = Polygon(space['points'])
                    if polygon.is_valid and polygon.area > 0.1:
                        processed_space.append(polygon)
                except Exception as e:
                    logger.warning(f"Invalid available space: {e}")
        return processed_space

    def _create_pathfinding_grid(self):
        """Create grid for pathfinding algorithms"""
        logger.info("Creating pathfinding grid")
        
        # Determine grid bounds
        all_geometries = []
        for ilot in self.ilots:
            all_geometries.append(ilot['polygon'])
        all_geometries.extend(self.walls)
        all_geometries.extend(self.restricted_areas)
        all_geometries.extend(self.available_space)
        
        if not all_geometries:
            logger.warning("No geometries found for grid creation")
            return
        
        # Calculate bounds
        union_geom = unary_union(all_geometries)
        bounds = union_geom.bounds
        
        # Expand bounds slightly
        margin = 2.0
        self.grid_bounds = (
            bounds[0] - margin, bounds[1] - margin,
            bounds[2] + margin, bounds[3] + margin
        )
        
        # Create grid
        width = self.grid_bounds[2] - self.grid_bounds[0]
        height = self.grid_bounds[3] - self.grid_bounds[1]
        
        cols = int(width / self.grid_resolution)
        rows = int(height / self.grid_resolution)
        
        self.pathfinding_grid = np.zeros((rows, cols), dtype=np.int8)
        
        # Mark obstacles in grid
        for row in range(rows):
            for col in range(cols):
                x = self.grid_bounds[0] + col * self.grid_resolution
                y = self.grid_bounds[1] + row * self.grid_resolution
                point = Point(x, y)
                
                # Check if point is in obstacle
                is_obstacle = False
                
                # Check walls
                for wall in self.walls:
                    if wall.contains(point) or wall.distance(point) < self.config.width / 2:
                        is_obstacle = True
                        break
                
                # Check restricted areas
                if not is_obstacle:
                    for restricted in self.restricted_areas:
                        if restricted.contains(point):
                            is_obstacle = True
                            break
                
                # Check if outside available space
                if not is_obstacle and self.available_space:
                    in_available = False
                    for space in self.available_space:
                        if space.contains(point):
                            in_available = True
                            break
                    if not in_available:
                        is_obstacle = True
                
                self.pathfinding_grid[row, col] = 1 if is_obstacle else 0

    def _generate_initial_network(self) -> List[CorridorSegment]:
        """Generate initial corridor network using graph algorithms"""
        logger.info("Generating initial corridor network")
        
        if not self.ilots:
            return []
        
        # Create graph with îlots as nodes
        self.graph = nx.Graph()
        
        # Add îlot nodes
        for ilot in self.ilots:
            self.graph.add_node(ilot['id'], 
                              pos=ilot['centroid'],
                              area=ilot['area'],
                              category=ilot['category'])
        
        # Calculate connections using different strategies
        if self.config.pathfinding_algorithm == "MST":
            connections = self._generate_mst_connections()
        elif self.config.pathfinding_algorithm == "Delaunay":
            connections = self._generate_delaunay_connections()
        else:
            connections = self._generate_proximity_connections()
        
        # Create corridor segments
        segments = []
        for i, connection in enumerate(connections):
            start_id, end_id = connection
            start_ilot = next(ilot for ilot in self.ilots if ilot['id'] == start_id)
            end_ilot = next(ilot for ilot in self.ilots if ilot['id'] == end_id)
            
            # Find optimal path between îlots
            path = self._find_optimal_path(start_ilot, end_ilot)
            
            if path and len(path) >= 2:
                # Create corridor segment
                segment = self._create_corridor_segment(i, path)
                segments.append(segment)
        
        # Add entrance connections if configured
        if self.config.connect_to_entrances:
            entrance_segments = self._create_entrance_connections(segments)
            segments.extend(entrance_segments)
        
        return segments

    def _generate_mst_connections(self) -> List[Tuple[int, int]]:
        """Generate connections using Minimum Spanning Tree"""
        if len(self.ilots) < 2:
            return []
        
        # Calculate distances between all îlots
        positions = np.array([(ilot['centroid'].x, ilot['centroid'].y) for ilot in self.ilots])
        distances = cdist(positions, positions)
        
        # Add edges to graph
        for i in range(len(self.ilots)):
            for j in range(i + 1, len(self.ilots)):
                weight = distances[i, j]
                self.graph.add_edge(self.ilots[i]['id'], self.ilots[j]['id'], weight=weight)
        
        # Find MST
        mst = nx.minimum_spanning_tree(self.graph)
        return list(mst.edges())

    def _generate_delaunay_connections(self) -> List[Tuple[int, int]]:
        """Generate connections using Delaunay triangulation"""
        if len(self.ilots) < 3:
            return self._generate_mst_connections()
        
        from scipy.spatial import Delaunay
        
        # Get îlot positions
        positions = np.array([(ilot['centroid'].x, ilot['centroid'].y) for ilot in self.ilots])
        
        # Create Delaunay triangulation
        tri = Delaunay(positions)
        
        # Extract edges
        connections = set()
        for simplex in tri.simplices:
            for i in range(3):
                for j in range(i + 1, 3):
                    id1 = self.ilots[simplex[i]]['id']
                    id2 = self.ilots[simplex[j]]['id']
                    connections.add((min(id1, id2), max(id1, id2)))
        
        return list(connections)

    def _generate_proximity_connections(self) -> List[Tuple[int, int]]:
        """Generate connections based on proximity and accessibility"""
        connections = []
        
        # Sort îlots by area (connect larger îlots first)
        sorted_ilots = sorted(self.ilots, key=lambda x: x['area'], reverse=True)
        
        for i, ilot in enumerate(sorted_ilots):
            # Find nearest neighbors
            distances = []
            for j, other_ilot in enumerate(sorted_ilots):
                if i != j:
                    dist = ilot['centroid'].distance(other_ilot['centroid'])
                    distances.append((dist, other_ilot['id']))
            
            # Connect to 2-3 nearest neighbors
            distances.sort()
            max_connections = min(3, len(distances))
            
            for k in range(max_connections):
                _, neighbor_id = distances[k]
                connection = (min(ilot['id'], neighbor_id), max(ilot['id'], neighbor_id))
                if connection not in connections:
                    connections.append(connection)
        
        return connections

    def _find_optimal_path(self, start_ilot: Dict, end_ilot: Dict) -> List[Tuple[float, float]]:
        """Find optimal path between two îlots using A* algorithm"""
        if not self.pathfinding_grid is None:
            return self._a_star_pathfinding(start_ilot, end_ilot)
        else:
            # Fallback to straight line
            start_pos = (start_ilot['centroid'].x, start_ilot['centroid'].y)
            end_pos = (end_ilot['centroid'].x, end_ilot['centroid'].y)
            return [start_pos, end_pos]

    def _a_star_pathfinding(self, start_ilot: Dict, end_ilot: Dict) -> List[Tuple[float, float]]:
        """A* pathfinding algorithm implementation"""
        # Convert world coordinates to grid coordinates
        start_pos = (start_ilot['centroid'].x, start_ilot['centroid'].y)
        end_pos = (end_ilot['centroid'].x, end_ilot['centroid'].y)
        
        start_grid = self._world_to_grid(start_pos)
        end_grid = self._world_to_grid(end_pos)
        
        if start_grid is None or end_grid is None:
            return [start_pos, end_pos]
        
        # A* algorithm
        open_set = [(0, start_grid, [])]
        closed_set = set()
        
        while open_set:
            current_cost, current_pos, path = open_set.pop(0)
            
            if current_pos == end_grid:
                # Convert path back to world coordinates
                world_path = [self._grid_to_world(pos) for pos in path + [current_pos]]
                return world_path
            
            if current_pos in closed_set:
                continue
            
            closed_set.add(current_pos)
            
            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)
                
                if (new_pos[0] < 0 or new_pos[0] >= self.pathfinding_grid.shape[1] or
                    new_pos[1] < 0 or new_pos[1] >= self.pathfinding_grid.shape[0]):
                    continue
                
                if self.pathfinding_grid[new_pos[1], new_pos[0]] == 1:  # Obstacle
                    continue
                
                if new_pos in closed_set:
                    continue
                
                # Calculate costs
                move_cost = math.sqrt(dx*dx + dy*dy)
                new_cost = current_cost + move_cost
                heuristic = math.sqrt((new_pos[0] - end_grid[0])**2 + (new_pos[1] - end_grid[1])**2)
                total_cost = new_cost + heuristic
                
                # Add to open set
                open_set.append((total_cost, new_pos, path + [current_pos]))
                open_set.sort()
        
        # No path found, return straight line
        return [start_pos, end_pos]

    def _world_to_grid(self, world_pos: Tuple[float, float]) -> Optional[Tuple[int, int]]:
        """Convert world coordinates to grid coordinates"""
        if self.grid_bounds is None:
            return None
        
        x, y = world_pos
        col = int((x - self.grid_bounds[0]) / self.grid_resolution)
        row = int((y - self.grid_bounds[1]) / self.grid_resolution)
        
        if (0 <= col < self.pathfinding_grid.shape[1] and 
            0 <= row < self.pathfinding_grid.shape[0]):
            return (col, row)
        return None

    def _grid_to_world(self, grid_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates"""
        col, row = grid_pos
        x = self.grid_bounds[0] + col * self.grid_resolution
        y = self.grid_bounds[1] + row * self.grid_resolution
        return (x, y)

    def _create_corridor_segment(self, segment_id: int, path: List[Tuple[float, float]]) -> CorridorSegment:
        """Create corridor segment from path"""
        if len(path) < 2:
            return None
        
        # Create corridor polygon
        corridor_polygons = []
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            
            # Create line segment
            line = LineString([start, end])
            # Buffer to create corridor width
            segment_poly = line.buffer(self.config.width / 2, cap_style=2)
            corridor_polygons.append(segment_poly)
        
        # Union all segments
        corridor_polygon = unary_union(corridor_polygons)
        
        # Calculate total length
        total_length = sum(
            math.sqrt((path[i+1][0] - path[i][0])**2 + (path[i+1][1] - path[i][1])**2)
            for i in range(len(path) - 1)
        )
        
        return CorridorSegment(
            id=segment_id,
            start_point=path[0],
            end_point=path[-1],
            width=self.config.width,
            length=total_length,
            polygon=corridor_polygon,
            connects_to=[]
        )

    def _create_entrance_connections(self, existing_segments: List[CorridorSegment]) -> List[CorridorSegment]:
        """Create connections to entrances"""
        entrance_segments = []
        
        for i, entrance in enumerate(self.entrances):
            # Find nearest corridor segment
            entrance_point = Point(entrance['connection_point'])
            min_distance = float('inf')
            nearest_segment = None
            
            for segment in existing_segments:
                distance = segment.polygon.distance(entrance_point)
                if distance < min_distance:
                    min_distance = distance
                    nearest_segment = segment
            
            if nearest_segment and min_distance < 5.0:  # Within 5 meters
                # Create connection
                connection_path = [
                    entrance['connection_point'],
                    nearest_segment.polygon.boundary.project(entrance_point)
                ]
                
                connection_segment = self._create_corridor_segment(
                    len(existing_segments) + len(entrance_segments),
                    connection_path
                )
                
                if connection_segment:
                    connection_segment.segment_type = "entrance_connection"
                    entrance_segments.append(connection_segment)
        
        return entrance_segments

    def _optimize_corridor_paths(self, segments: List[CorridorSegment]) -> List[CorridorSegment]:
        """Optimize corridor paths for efficiency and aesthetics"""
        logger.info("Optimizing corridor paths")
        
        # Implementation depends on configuration
        if self.config.style == "curved":
            return self._apply_curved_optimization(segments)
        elif self.config.style == "organic":
            return self._apply_organic_optimization(segments)
        else:
            return self._apply_straight_optimization(segments)

    def _apply_straight_optimization(self, segments: List[CorridorSegment]) -> List[CorridorSegment]:
        """Apply straight line optimization"""
        optimized_segments = []
        
        for segment in segments:
            # Straighten path by removing unnecessary waypoints
            optimized_segment = segment  # For now, keep as is
            optimized_segments.append(optimized_segment)
        
        return optimized_segments

    def _apply_curved_optimization(self, segments: List[CorridorSegment]) -> List[CorridorSegment]:
        """Apply curved path optimization"""
        # Implement curved corridor generation
        return self._apply_straight_optimization(segments)

    def _apply_organic_optimization(self, segments: List[CorridorSegment]) -> List[CorridorSegment]:
        """Apply organic path optimization"""
        # Implement organic corridor generation
        return self._apply_straight_optimization(segments)

    def _enhance_junctions(self, segments: List[CorridorSegment]) -> List[CorridorSegment]:
        """Enhance junction areas between corridors"""
        logger.info("Enhancing corridor junctions")
        
        # Find intersection points
        junctions = []
        for i, segment1 in enumerate(segments):
            for j, segment2 in enumerate(segments):
                if i != j and segment1.polygon.intersects(segment2.polygon):
                    intersection = segment1.polygon.intersection(segment2.polygon)
                    if intersection.area > 0.1:  # Significant intersection
                        junctions.append({
                            'segments': [i, j],
                            'geometry': intersection,
                            'style': self.config.junction_style
                        })
        
        # Apply junction enhancements
        enhanced_segments = segments.copy()
        
        for junction in junctions:
            if self.config.junction_style == "rounded":
                # Apply rounded junction
                enhanced_segments = self._apply_rounded_junction(enhanced_segments, junction)
            elif self.config.junction_style == "beveled":
                # Apply beveled junction
                enhanced_segments = self._apply_beveled_junction(enhanced_segments, junction)
        
        return enhanced_segments

    def _apply_rounded_junction(self, segments: List[CorridorSegment], junction: Dict) -> List[CorridorSegment]:
        """Apply rounded junction enhancement"""
        # Implementation for rounded junctions
        return segments

    def _apply_beveled_junction(self, segments: List[CorridorSegment], junction: Dict) -> List[CorridorSegment]:
        """Apply beveled junction enhancement"""
        # Implementation for beveled junctions
        return segments

    def _validate_and_finalize(self, segments: List[CorridorSegment]) -> CorridorNetwork:
        """Validate and finalize corridor network"""
        logger.info("Validating and finalizing corridor network")
        
        # Remove invalid segments
        valid_segments = [seg for seg in segments if seg and seg.polygon.is_valid and seg.length > 0.1]
        
        # Calculate network statistics
        total_length = sum(seg.length for seg in valid_segments)
        connectivity_score = self._calculate_connectivity_score(valid_segments)
        accessibility_score = self._calculate_accessibility_score(valid_segments)
        
        # Create network
        network = CorridorNetwork(
            segments=valid_segments,
            junctions=[],  # Will be populated by junction analysis
            total_length=total_length,
            connectivity_score=connectivity_score,
            accessibility_score=accessibility_score
        )
        
        return network

    def _calculate_connectivity_score(self, segments: List[CorridorSegment]) -> float:
        """Calculate connectivity score for network"""
        if not segments:
            return 0.0
        
        # Simple connectivity measure based on network coverage
        network_polygon = unary_union([seg.polygon for seg in segments])
        total_available_area = sum(space.area for space in self.available_space)
        
        if total_available_area == 0:
            return 0.0
        
        # Calculate coverage ratio
        coverage_ratio = network_polygon.area / total_available_area
        return min(coverage_ratio * 100, 100.0)

    def _calculate_accessibility_score(self, segments: List[CorridorSegment]) -> float:
        """Calculate accessibility score for network"""
        if not segments or not self.ilots:
            return 0.0
        
        # Check how many îlots are accessible via corridors
        accessible_ilots = 0
        network_polygon = unary_union([seg.polygon for seg in segments])
        
        for ilot in self.ilots:
            # Check if îlot is connected to corridor network
            if network_polygon.distance(ilot['polygon']) < self.config.width:
                accessible_ilots += 1
        
        return (accessible_ilots / len(self.ilots)) * 100.0

    def get_network_statistics(self) -> Dict:
        """Get comprehensive network statistics"""
        if not self.corridor_network:
            return {}
        
        return {
            'total_segments': len(self.corridor_network.segments),
            'total_length': self.corridor_network.total_length,
            'average_width': self.config.width,
            'connectivity_score': self.corridor_network.connectivity_score,
            'accessibility_score': self.corridor_network.accessibility_score,
            'network_area': self.corridor_network.get_network_polygon().area,
            'style': self.config.style,
            'junction_style': self.config.junction_style
        }

    def export_to_legacy_format(self) -> List[Dict]:
        """Export corridor network to legacy format for compatibility"""
        if not self.corridor_network:
            return []
        
        legacy_corridors = []
        
        for segment in self.corridor_network.segments:
            # Convert polygon to points
            if hasattr(segment.polygon, 'exterior'):
                points = list(segment.polygon.exterior.coords)[:-1]  # Remove duplicate last point
            else:
                # Fallback for non-polygon geometries
                points = [segment.start_point, segment.end_point]
            
            legacy_corridors.append({
                'points': points,
                'polygon': segment.polygon,
                'width': segment.width,
                'length': segment.length,
                'type': segment.segment_type
            })
        
        return legacy_corridors