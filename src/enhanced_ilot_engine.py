"""
Enhanced Îlot Placement Engine - Client Requirements Implementation
Handles zone detection, proportional placement, and corridor generation
"""

import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from typing import List, Dict, Any, Tuple, Optional
import random
import math
from dataclasses import dataclass

@dataclass
class IlotSpec:
    """Îlot specification with size and placement data"""
    id: str
    area: float
    width: float
    height: float
    category: str
    position: Tuple[float, float]
    geometry: Polygon
    placed: bool = False

class EnhancedIlotEngine:
    """Enhanced îlot placement engine matching client requirements"""
    
    def __init__(self):
        self.corridor_width = 120  # 1.2m default
        self.min_clearance = 30    # 30cm minimum
        self.entrance_buffer = 100 # 1m buffer from entrances
        
    def detect_zones_by_color(self, dxf_entities: List[Dict]) -> Dict[str, List[Dict]]:
        """Detect zones by color coding as per client requirements"""
        zones = {
            'walls': [],        # Black lines (color 7 or 0)
            'restricted': [],   # Light blue areas (color 5)
            'entrances': [],    # Red areas (color 1)
            'available': []     # Other areas
        }
        
        for entity in dxf_entities:
            color = entity.get('color', 7)
            geometry = entity.get('geometry', [])
            
            if not geometry or len(geometry) < 3:
                continue
                
            zone_data = {
                'geometry': geometry,
                'color': color,
                'type': entity.get('type', 'unknown')
            }
            
            # Classify by color
            if color in [0, 7]:  # Black/white - walls
                zones['walls'].append(zone_data)
            elif color == 5:     # Blue - restricted (stairs, elevators)
                zones['restricted'].append(zone_data)
            elif color == 1:     # Red - entrances/exits
                zones['entrances'].append(zone_data)
            else:
                zones['available'].append(zone_data)
        
        return zones
    
    def create_placement_zones(self, detected_zones: Dict[str, List[Dict]]) -> List[Polygon]:
        """Create valid placement zones avoiding restricted areas and entrances"""
        available_zones = []
        
        # Start with available areas
        for zone in detected_zones['available']:
            try:
                poly = Polygon(zone['geometry'])
                if poly.is_valid and poly.area > 1.0:  # Minimum 1m²
                    available_zones.append(poly)
            except:
                continue
        
        # If no available zones, create from overall bounds minus restrictions
        if not available_zones:
            all_geoms = []
            for zone_list in detected_zones.values():
                for zone in zone_list:
                    all_geoms.extend(zone['geometry'])
            
            if all_geoms:
                min_x = min(p[0] for p in all_geoms)
                max_x = max(p[0] for p in all_geoms)
                min_y = min(p[1] for p in all_geoms)
                max_y = max(p[1] for p in all_geoms)
                
                # Create overall boundary
                boundary = box(min_x, min_y, max_x, max_y)
                available_zones = [boundary]
        
        # Remove restricted areas and entrance buffers
        final_zones = []
        for zone in available_zones:
            current_zone = zone
            
            # Remove restricted areas
            for restricted in detected_zones['restricted']:
                try:
                    restricted_poly = Polygon(restricted['geometry']).buffer(self.min_clearance)
                    current_zone = current_zone.difference(restricted_poly)
                except:
                    continue
            
            # Remove entrance buffers
            for entrance in detected_zones['entrances']:
                try:
                    entrance_poly = Polygon(entrance['geometry']).buffer(self.entrance_buffer)
                    current_zone = current_zone.difference(entrance_poly)
                except:
                    continue
            
            # Handle MultiPolygon results
            if hasattr(current_zone, 'geoms'):
                for geom in current_zone.geoms:
                    if geom.area > 1.0:
                        final_zones.append(geom)
            elif current_zone.area > 1.0:
                final_zones.append(current_zone)
        
        return final_zones
    
    def generate_ilot_specs(self, profile_config: Dict[str, float], total_count: int = 50) -> List[IlotSpec]:
        """Generate îlot specifications based on user profile"""
        specs = []
        
        # Define size categories
        categories = [
            ('0-1m²', 0.5, 1.0, profile_config.get('0-1', 0.10)),
            ('1-3m²', 1.0, 3.0, profile_config.get('1-3', 0.25)),
            ('3-5m²', 3.0, 5.0, profile_config.get('3-5', 0.30)),
            ('5-10m²', 5.0, 10.0, profile_config.get('5-10', 0.35))
        ]
        
        # Calculate counts per category
        for category, min_area, max_area, percentage in categories:
            count = int(total_count * percentage)
            
            for i in range(count):
                area = random.uniform(min_area, max_area)
                
                # Calculate dimensions (prefer rectangular shapes)
                aspect_ratio = random.uniform(1.0, 1.8)
                width = math.sqrt(area * aspect_ratio)
                height = area / width
                
                spec = IlotSpec(
                    id=f"{category}_{i+1}",
                    area=area,
                    width=width,
                    height=height,
                    category=category,
                    position=(0, 0),  # Will be set during placement
                    geometry=box(0, 0, width, height)  # Temporary
                )
                specs.append(spec)
        
        return specs
    
    def place_ilots_optimized(self, ilot_specs: List[IlotSpec], 
                             placement_zones: List[Polygon],
                             walls: List[Dict]) -> List[IlotSpec]:
        """Place îlots optimally within zones"""
        placed_ilots = []
        occupied_areas = []
        
        # Sort by area (place larger îlots first)
        sorted_specs = sorted(ilot_specs, key=lambda x: x.area, reverse=True)
        
        for spec in sorted_specs:
            best_placement = None
            best_score = -1
            
            # Try each placement zone
            for zone in placement_zones:
                # Generate candidate positions
                candidates = self._generate_positions_in_zone(zone, spec.width, spec.height)
                
                for position in candidates:
                    # Create îlot geometry at position
                    x, y = position
                    ilot_geom = box(x, y, x + spec.width, y + spec.height)
                    
                    # Check validity
                    if self._is_valid_placement(ilot_geom, zone, occupied_areas, walls):
                        score = self._calculate_placement_score(ilot_geom, zone, occupied_areas)
                        
                        if score > best_score:
                            best_score = score
                            best_placement = {
                                'position': (x + spec.width/2, y + spec.height/2),
                                'geometry': ilot_geom
                            }
            
            # Place îlot if valid position found
            if best_placement:
                spec.position = best_placement['position']
                spec.geometry = best_placement['geometry']
                spec.placed = True
                placed_ilots.append(spec)
                occupied_areas.append(best_placement['geometry'])
        
        return placed_ilots
    
    def _generate_positions_in_zone(self, zone: Polygon, width: float, height: float) -> List[Tuple[float, float]]:
        """Generate candidate positions within zone"""
        positions = []
        bounds = zone.bounds
        
        # Grid-based generation
        step = min(width, height) / 2
        
        x = bounds[0]
        while x + width <= bounds[2]:
            y = bounds[1]
            while y + height <= bounds[3]:
                test_box = box(x, y, x + width, y + height)
                if zone.contains(test_box):
                    positions.append((x, y))
                y += step
            x += step
        
        # Add some random positions for diversity
        for _ in range(10):
            x = random.uniform(bounds[0], bounds[2] - width)
            y = random.uniform(bounds[1], bounds[3] - height)
            test_box = box(x, y, x + width, y + height)
            if zone.contains(test_box):
                positions.append((x, y))
        
        return positions
    
    def _is_valid_placement(self, ilot_geom: Polygon, zone: Polygon, 
                           occupied_areas: List[Polygon], walls: List[Dict]) -> bool:
        """Check if îlot placement is valid"""
        
        # Must be within zone
        if not zone.contains(ilot_geom):
            return False
        
        # Check overlap with existing îlots
        for occupied in occupied_areas:
            if ilot_geom.intersects(occupied.buffer(self.min_clearance)):
                return False
        
        # Îlots CAN touch walls (this is allowed per requirements)
        return True
    
    def _calculate_placement_score(self, ilot_geom: Polygon, zone: Polygon, 
                                  occupied_areas: List[Polygon]) -> float:
        """Calculate placement quality score"""
        score = 1.0
        
        # Prefer positions closer to zone center
        zone_center = zone.centroid
        ilot_center = ilot_geom.centroid
        distance_to_center = zone_center.distance(ilot_center)
        zone_radius = math.sqrt(zone.area / math.pi)
        center_score = max(0, 1 - distance_to_center / zone_radius)
        
        # Prefer positions with good spacing from other îlots
        min_distance = float('inf')
        for occupied in occupied_areas:
            distance = ilot_geom.distance(occupied)
            min_distance = min(min_distance, distance)
        
        spacing_score = min(1.0, min_distance / 50) if min_distance != float('inf') else 1.0
        
        return center_score * 0.6 + spacing_score * 0.4
    
    def generate_corridors(self, placed_ilots: List[IlotSpec]) -> List[Dict[str, Any]]:
        """Generate corridors between îlot rows"""
        if len(placed_ilots) < 2:
            return []
        
        # Group îlots into rows
        rows = self._group_into_rows(placed_ilots)
        
        corridors = []
        
        # Generate corridors between adjacent rows
        for i in range(len(rows) - 1):
            row1 = rows[i]
            row2 = rows[i + 1]
            
            corridor = self._create_corridor_between_rows(row1, row2)
            if corridor:
                corridors.append({
                    'id': f'corridor_{i}_{i+1}',
                    'geometry': corridor,
                    'width': self.corridor_width,
                    'type': 'inter_row',
                    'connects': [f'row_{i}', f'row_{i+1}']
                })
        
        return corridors
    
    def _group_into_rows(self, placed_ilots: List[IlotSpec]) -> List[List[IlotSpec]]:
        """Group îlots into rows based on Y position"""
        if not placed_ilots:
            return []
        
        # Sort by Y coordinate
        sorted_ilots = sorted(placed_ilots, key=lambda x: x.position[1])
        
        rows = []
        current_row = [sorted_ilots[0]]
        row_tolerance = 100  # 1m tolerance for same row
        
        for ilot in sorted_ilots[1:]:
            if abs(ilot.position[1] - current_row[-1].position[1]) <= row_tolerance:
                current_row.append(ilot)
            else:
                if len(current_row) >= 2:  # Only keep rows with multiple îlots
                    rows.append(current_row)
                current_row = [ilot]
        
        if len(current_row) >= 2:
            rows.append(current_row)
        
        return rows
    
    def _create_corridor_between_rows(self, row1: List[IlotSpec], row2: List[IlotSpec]) -> Optional[Polygon]:
        """Create corridor geometry between two rows"""
        
        # Calculate row bounds
        row1_bounds = self._get_row_bounds(row1)
        row2_bounds = self._get_row_bounds(row2)
        
        # Check if rows are reasonably close
        distance = abs(row1_bounds['center_y'] - row2_bounds['center_y'])
        if distance > 300:  # Max 3m between rows
            return None
        
        # Find overlapping X range
        min_x = max(row1_bounds['min_x'], row2_bounds['min_x'])
        max_x = min(row1_bounds['max_x'], row2_bounds['max_x'])
        
        if max_x <= min_x:
            return None
        
        # Position corridor between rows
        y1 = row1_bounds['center_y']
        y2 = row2_bounds['center_y']
        
        if y1 < y2:  # row1 is above row2
            corridor_y_start = row1_bounds['max_y'] + 10
            corridor_y_end = row2_bounds['min_y'] - 10
        else:  # row1 is below row2
            corridor_y_start = row2_bounds['max_y'] + 10
            corridor_y_end = row1_bounds['min_y'] - 10
        
        if corridor_y_end <= corridor_y_start:
            # Use fixed width corridor
            corridor_center = (y1 + y2) / 2
            corridor_y_start = corridor_center - self.corridor_width / 2
            corridor_y_end = corridor_center + self.corridor_width / 2
        
        corridor_geom = box(min_x, corridor_y_start, max_x, corridor_y_end)
        
        return corridor_geom if corridor_geom.area > 0.5 else None
    
    def _get_row_bounds(self, row: List[IlotSpec]) -> Dict[str, float]:
        """Get bounding information for a row of îlots"""
        geometries = [ilot.geometry for ilot in row]
        positions = [ilot.position for ilot in row]
        
        all_bounds = [geom.bounds for geom in geometries]
        
        return {
            'min_x': min(bounds[0] for bounds in all_bounds),
            'min_y': min(bounds[1] for bounds in all_bounds),
            'max_x': max(bounds[2] for bounds in all_bounds),
            'max_y': max(bounds[3] for bounds in all_bounds),
            'center_y': sum(pos[1] for pos in positions) / len(positions)
        }
    
    def calculate_metrics(self, placed_ilots: List[IlotSpec], corridors: List[Dict], 
                         total_area: float) -> Dict[str, Any]:
        """Calculate placement metrics"""
        
        total_ilot_area = sum(ilot.area for ilot in placed_ilots if ilot.placed)
        total_corridor_area = sum(corridor['geometry'].area for corridor in corridors)
        
        placed_count = sum(1 for ilot in placed_ilots if ilot.placed)
        total_count = len(placed_ilots)
        
        return {
            'total_ilots': total_count,
            'placed_ilots': placed_count,
            'placement_rate': placed_count / total_count if total_count > 0 else 0,
            'total_ilot_area': total_ilot_area,
            'total_corridor_area': total_corridor_area,
            'space_utilization': (total_ilot_area + total_corridor_area) / total_area if total_area > 0 else 0,
            'corridor_count': len(corridors),
            'avg_ilot_size': total_ilot_area / placed_count if placed_count > 0 else 0
        }
    
    def process_complete_layout(self, dxf_entities: List[Dict], 
                               profile_config: Dict[str, float],
                               total_ilots: int = 50) -> Dict[str, Any]:
        """Complete îlot layout processing pipeline"""
        
        # Step 1: Detect zones by color
        detected_zones = self.detect_zones_by_color(dxf_entities)
        
        # Step 2: Create placement zones
        placement_zones = self.create_placement_zones(detected_zones)
        
        # Step 3: Generate îlot specifications
        ilot_specs = self.generate_ilot_specs(profile_config, total_ilots)
        
        # Step 4: Place îlots
        placed_ilots = self.place_ilots_optimized(ilot_specs, placement_zones, detected_zones['walls'])
        
        # Step 5: Generate corridors
        corridors = self.generate_corridors(placed_ilots)
        
        # Step 6: Calculate metrics
        total_area = sum(zone.area for zone in placement_zones)
        metrics = self.calculate_metrics(placed_ilots, corridors, total_area)
        
        return {
            'detected_zones': detected_zones,
            'placement_zones': placement_zones,
            'ilots': placed_ilots,
            'corridors': corridors,
            'metrics': metrics,
            'success': True
        }