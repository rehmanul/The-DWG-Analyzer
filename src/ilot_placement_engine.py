"""
Îlot Placement Engine - Core Implementation
Automatically places îlots based on layout profiles with constraint compliance
"""

import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from typing import List, Dict, Any, Tuple, Optional
import random
from dataclasses import dataclass
import math

@dataclass
class IlotProfile:
    """Îlot size profile definition"""
    name: str
    min_area: float
    max_area: float
    percentage: float
    color: str

@dataclass
class PlacedIlot:
    """Placed îlot with geometry and metadata"""
    id: str
    geometry: Polygon
    profile: IlotProfile
    position: Tuple[float, float]
    rotation: float
    area: float
    placement_score: float
    placed: bool = True

class IlotPlacementEngine:
    """Advanced îlot placement engine with constraint compliance"""
    
    def __init__(self):
        self.corridor_width = 150  # 1.5m default corridor width
        self.min_clearance = 50    # 50cm minimum clearance
        self.entrance_buffer = 200 # 2m buffer around entrances
        
    def create_layout_profile(self, profile_config: Dict[str, float]) -> List[IlotProfile]:
        """Create îlot profiles from configuration"""
        profiles = []
        colors = ['#3498DB', '#E74C3C', '#F39C12', '#27AE60', '#9B59B6', '#E67E22']
        
        for i, (size_range, percentage) in enumerate(profile_config.items()):
            if '-' in size_range:
                min_area, max_area = map(float, size_range.split('-'))
            else:
                min_area = max_area = float(size_range)
            
            profile = IlotProfile(
                name=f"Îlot_{size_range}m²",
                min_area=min_area,
                max_area=max_area,
                percentage=percentage,
                color=colors[i % len(colors)]
            )
            profiles.append(profile)
        
        return profiles
    
    def place_ilots_automatically(self, 
                                 zones: List[Dict],
                                 walls: List[Dict],
                                 restricted_areas: List[Dict],
                                 entrances: List[Dict],
                                 profile_config: Dict[str, float],
                                 total_ilots: int = 50) -> Dict[str, Any]:
        """Main îlot placement function"""
        
        # Create profiles
        profiles = self.create_layout_profile(profile_config)
        
        # Calculate îlot counts per profile
        ilot_counts = self._calculate_ilot_counts(profiles, total_ilots)
        
        # Create placement zones (avoid restricted areas and entrances)
        placement_zones = self._create_placement_zones(zones, restricted_areas, entrances)
        
        # Place îlots
        placed_ilots = []
        for profile, count in zip(profiles, ilot_counts):
            for _ in range(count):
                ilot = self._place_single_ilot(profile, placement_zones, placed_ilots, walls)
                if ilot:
                    placed_ilots.append(ilot)
        
        # Generate corridors between îlot rows
        corridors = self._generate_corridors(placed_ilots, placement_zones)
        
        # Calculate metrics
        metrics = self._calculate_placement_metrics(placed_ilots, zones, corridors)
        
        return {
            'ilots': placed_ilots,
            'corridors': corridors,
            'layout_metrics': metrics,
            'profiles': profiles,
            'placement_zones': placement_zones
        }
    
    def _calculate_ilot_counts(self, profiles: List[IlotProfile], total_ilots: int) -> List[int]:
        """Calculate number of îlots per profile"""
        counts = []
        remaining = total_ilots
        
        for i, profile in enumerate(profiles):
            if i == len(profiles) - 1:  # Last profile gets remaining
                counts.append(remaining)
            else:
                count = int(total_ilots * profile.percentage / 100)
                counts.append(count)
                remaining -= count
        
        return counts
    
    def _create_placement_zones(self, zones: List[Dict], restricted_areas: List[Dict], 
                               entrances: List[Dict]) -> List[Polygon]:
        """Create valid placement zones avoiding restrictions"""
        placement_zones = []
        
        for zone in zones:
            if not zone.get('points') or len(zone['points']) < 3:
                continue
            
            try:
                zone_poly = Polygon(zone['points'])
                if not zone_poly.is_valid:
                    zone_poly = zone_poly.buffer(0)
                
                # Remove restricted areas
                for restricted in restricted_areas:
                    if 'geometry' in restricted and len(restricted['geometry']) >= 3:
                        restricted_poly = Polygon(restricted['geometry']).buffer(self.min_clearance)
                        zone_poly = zone_poly.difference(restricted_poly)
                
                # Remove entrance buffers
                for entrance in entrances:
                    entrance_point = Point(entrance.get('location', (0, 0)))
                    entrance_buffer = entrance_point.buffer(self.entrance_buffer)
                    zone_poly = zone_poly.difference(entrance_buffer)
                
                if zone_poly.area > 10:  # Minimum viable area
                    if hasattr(zone_poly, 'geoms'):
                        placement_zones.extend([geom for geom in zone_poly.geoms if geom.area > 10])
                    else:
                        placement_zones.append(zone_poly)
                        
            except Exception:
                continue
        
        return placement_zones
    
    def _place_single_ilot(self, profile: IlotProfile, placement_zones: List[Polygon],
                          existing_ilots: List[PlacedIlot], walls: List[Dict]) -> Optional[PlacedIlot]:
        """Place a single îlot optimally"""
        
        # Generate îlot size within profile range
        area = random.uniform(profile.min_area, profile.max_area)
        
        # Try different aspect ratios
        aspect_ratios = [1.0, 1.2, 1.5, 0.8, 0.67]
        
        for zone in placement_zones:
            for aspect_ratio in aspect_ratios:
                # Calculate dimensions
                width = math.sqrt(area * aspect_ratio)
                height = area / width
                
                # Try multiple positions in zone
                for _ in range(20):  # Max 20 attempts per zone/ratio
                    position = self._get_random_position_in_zone(zone, width, height)
                    if not position:
                        continue
                    
                    # Create îlot geometry
                    ilot_geom = box(
                        position[0] - width/2, position[1] - height/2,
                        position[0] + width/2, position[1] + height/2
                    )
                    
                    # Check constraints
                    if self._is_valid_placement(ilot_geom, zone, existing_ilots, walls):
                        return PlacedIlot(
                            id=f"ilot_{len(existing_ilots)+1}",
                            geometry=ilot_geom,
                            profile=profile,
                            position=position,
                            rotation=0,
                            area=area,
                            placement_score=self._calculate_placement_score(ilot_geom, zone, existing_ilots),
                            color=profile.color
                        )
        
        return None
    
    def _get_random_position_in_zone(self, zone: Polygon, width: float, height: float) -> Optional[Tuple[float, float]]:
        """Get random valid position within zone"""
        bounds = zone.bounds
        margin = max(width, height) / 2 + self.min_clearance
        
        if bounds[2] - bounds[0] < width + 2*margin or bounds[3] - bounds[1] < height + 2*margin:
            return None
        
        for _ in range(10):  # Max 10 attempts
            x = random.uniform(bounds[0] + margin, bounds[2] - margin)
            y = random.uniform(bounds[1] + margin, bounds[3] - margin)
            
            test_point = Point(x, y)
            if zone.contains(test_point):
                return (x, y)
        
        return None
    
    def _is_valid_placement(self, ilot_geom: Polygon, zone: Polygon, 
                           existing_ilots: List[PlacedIlot], walls: List[Dict]) -> bool:
        """Check if îlot placement is valid"""
        
        # Must be within zone
        if not zone.contains(ilot_geom):
            return False
        
        # Check overlap with existing îlots
        for existing in existing_ilots:
            if ilot_geom.intersects(existing.geometry.buffer(self.min_clearance)):
                return False
        
        # Can touch walls (this is allowed)
        return True
    
    def _calculate_placement_score(self, ilot_geom: Polygon, zone: Polygon, 
                                  existing_ilots: List[PlacedIlot]) -> float:
        """Calculate placement quality score"""
        score = 1.0
        
        # Distance from zone center
        zone_center = zone.centroid
        ilot_center = ilot_geom.centroid
        distance_to_center = zone_center.distance(ilot_center)
        zone_radius = math.sqrt(zone.area / math.pi)
        center_score = max(0, 1 - distance_to_center / zone_radius)
        
        # Spacing from other îlots
        min_distance = float('inf')
        for existing in existing_ilots:
            distance = ilot_geom.distance(existing.geometry)
            min_distance = min(min_distance, distance)
        
        spacing_score = min(1.0, min_distance / 100) if min_distance != float('inf') else 1.0
        
        return (center_score * 0.6 + spacing_score * 0.4)
    
    def _generate_corridors(self, placed_ilots: List[PlacedIlot], 
                           placement_zones: List[Polygon]) -> Dict[str, Any]:
        """Generate corridors between îlot rows"""
        corridors = {
            'geometry': [],
            'total_length': 0,
            'corridors': []
        }
        
        if len(placed_ilots) < 2:
            return corridors
        
        # Group îlots by approximate rows
        ilot_rows = self._group_ilots_into_rows(placed_ilots)
        
        # Generate corridors between facing rows
        for i, row1 in enumerate(ilot_rows):
            for j, row2 in enumerate(ilot_rows[i+1:], i+1):
                corridor_geom = self._create_corridor_between_rows(row1, row2, placement_zones)
                if corridor_geom:
                    corridor_data = {
                        'id': f"corridor_{i}_{j}",
                        'geometry': corridor_geom,
                        'type': 'secondary_circulation',
                        'width': self.corridor_width,
                        'length': self._calculate_corridor_length(corridor_geom)
                    }
                    corridors['geometry'].append(corridor_data)
                    corridors['corridors'].append(corridor_data)
                    corridors['total_length'] += corridor_data['length']
        
        return corridors
    
    def _group_ilots_into_rows(self, placed_ilots: List[PlacedIlot]) -> List[List[PlacedIlot]]:
        """Group îlots into approximate rows"""
        if not placed_ilots:
            return []
        
        # Sort by Y coordinate
        sorted_ilots = sorted(placed_ilots, key=lambda i: i.position[1])
        
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
    
    def _create_corridor_between_rows(self, row1: List[PlacedIlot], row2: List[PlacedIlot],
                                     placement_zones: List[Polygon]) -> Optional[Polygon]:
        """Create corridor geometry between two rows"""
        
        # Calculate row bounds
        row1_bounds = self._get_row_bounds(row1)
        row2_bounds = self._get_row_bounds(row2)
        
        # Check if rows are facing each other (reasonable distance)
        distance = abs(row1_bounds['center_y'] - row2_bounds['center_y'])
        if distance > 500:  # Max 5m between rows
            return None
        
        # Create corridor rectangle
        min_x = max(row1_bounds['min_x'], row2_bounds['min_x'])
        max_x = min(row1_bounds['max_x'], row2_bounds['max_x'])
        
        if max_x <= min_x:
            return None
        
        # Position corridor between rows
        y1 = row1_bounds['center_y']
        y2 = row2_bounds['center_y']
        corridor_y = (y1 + y2) / 2
        
        corridor_geom = box(
            min_x, corridor_y - self.corridor_width/2,
            max_x, corridor_y + self.corridor_width/2
        )
        
        # Ensure corridor is within placement zones
        for zone in placement_zones:
            if zone.intersects(corridor_geom):
                corridor_geom = corridor_geom.intersection(zone)
                break
        
        return corridor_geom if corridor_geom.area > 10 else None
    
    def _get_row_bounds(self, row: List[PlacedIlot]) -> Dict[str, float]:
        """Get bounding information for a row of îlots"""
        positions = [ilot.position for ilot in row]
        geometries = [ilot.geometry for ilot in row]
        
        all_bounds = [geom.bounds for geom in geometries]
        
        return {
            'min_x': min(bounds[0] for bounds in all_bounds),
            'min_y': min(bounds[1] for bounds in all_bounds),
            'max_x': max(bounds[2] for bounds in all_bounds),
            'max_y': max(bounds[3] for bounds in all_bounds),
            'center_y': sum(pos[1] for pos in positions) / len(positions)
        }
    
    def _calculate_corridor_length(self, corridor_geom: Polygon) -> float:
        """Calculate corridor length"""
        bounds = corridor_geom.bounds
        return max(bounds[2] - bounds[0], bounds[3] - bounds[1])
    
    def _calculate_placement_metrics(self, placed_ilots: List[PlacedIlot], 
                                   zones: List[Dict], corridors: Dict) -> Dict[str, Any]:
        """Calculate placement quality metrics"""
        
        total_zone_area = sum(
            Polygon(zone['points']).area 
            for zone in zones 
            if zone.get('points') and len(zone['points']) >= 3
        )
        
        total_ilot_area = sum(ilot.area for ilot in placed_ilots)
        corridor_area = sum(
            corridor['geometry'].area 
            for corridor in corridors.get('geometry', [])
            if hasattr(corridor.get('geometry'), 'area')
        )
        
        return {
            'total_ilots': len(placed_ilots),
            'placed_ilots': len([i for i in placed_ilots if i.placed]),
            'placement_rate': len(placed_ilots) / max(1, len(placed_ilots)),
            'space_utilization': (total_ilot_area + corridor_area) / max(1, total_zone_area),
            'average_placement_score': sum(i.placement_score for i in placed_ilots) / max(1, len(placed_ilots)),
            'total_corridor_length': corridors.get('total_length', 0),
            'corridor_count': len(corridors.get('corridors', []))
        }