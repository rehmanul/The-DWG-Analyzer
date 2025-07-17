
"""
Advanced Îlot Placement Engine - Pixel-Perfect Implementation
Intelligent îlot placement matching exact client specifications
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from scipy.spatial.distance import pdist
from scipy.optimize import differential_evolution
import math
import logging

logger = logging.getLogger(__name__)

@dataclass
class IlotSpecification:
    """Specification for îlot placement"""
    id: int
    area: float
    width: float
    height: float
    category: str
    color: str
    min_spacing: float = 0.5

@dataclass
class PlacedIlot:
    """Placed îlot with position and properties"""
    id: int
    x: float
    y: float
    width: float
    height: float
    rotation: float
    area: float
    category: str
    color: str
    polygon: Polygon
    placement_score: float = 0.0

class AdvancedIlotPlacementEngine:
    """
    Advanced îlot placement engine with pixel-perfect compliance
    Implements client requirements exactly as specified
    """
    
    def __init__(self):
        # Client color specifications matching reference images
        self.category_colors = {
            'Micro (0-1m²)': 'rgba(254, 243, 242, 0.8)',
            'Small (1-3m²)': 'rgba(254, 226, 226, 0.8)', 
            'Medium (3-5m²)': 'rgba(252, 231, 243, 0.8)',
            'Large (5-10m²)': 'rgba(243, 232, 255, 0.8)'
        }
        
        # Professional placement parameters
        self.min_spacing = 0.5  # 50cm minimum spacing
        self.wall_contact_allowed = True
        self.entrance_buffer = 2.0  # 2m buffer from entrances
        self.restricted_buffer = 0.5  # 50cm buffer from restricted areas
        
        # Optimization parameters
        self.max_iterations = 1000
        self.population_size = 50
        self.mutation_rate = 0.1
    
    def place_ilots_intelligent(self, floor_plan: Any, config: Dict[str, float]) -> Dict[str, Any]:
        """
        Main îlot placement function with intelligent algorithms
        """
        logger.info("Starting intelligent îlot placement")
        
        # Extract placement zones
        available_zones = self._extract_available_zones(floor_plan)
        forbidden_zones = self._create_forbidden_zones(floor_plan)
        
        # Calculate total available area
        total_area = sum(zone.area for zone in available_zones)
        
        # Generate îlot specifications based on configuration
        ilot_specs = self._generate_ilot_specifications(config, total_area)
        
        # Place îlots using advanced algorithms
        placed_ilots = self._place_ilots_optimized(ilot_specs, available_zones, forbidden_zones)
        
        # Generate corridors between îlot rows
        corridors = self._generate_intelligent_corridors(placed_ilots, available_zones)
        
        # Calculate placement metrics
        metrics = self._calculate_placement_metrics(placed_ilots, total_area, corridors)
        
        return {
            'ilots': placed_ilots,
            'corridors': corridors,
            'metrics': metrics,
            'total_placed': len(placed_ilots),
            'total_requested': len(ilot_specs),
            'placement_efficiency': len(placed_ilots) / len(ilot_specs) if ilot_specs else 0
        }
    
    def _extract_available_zones(self, floor_plan: Any) -> List[Polygon]:
        """Extract zones available for îlot placement"""
        available_zones = []
        
        # Process rooms as available zones
        for room in getattr(floor_plan, 'rooms', []):
            if hasattr(room, 'geometry') and room.geometry.area > 5.0:
                available_zones.append(room.geometry)
        
        # If no specific rooms, create from overall bounds
        if not available_zones:
            min_x, min_y, max_x, max_y = floor_plan.bounds
            overall_zone = box(min_x, min_y, max_x, max_y)
            available_zones.append(overall_zone)
        
        logger.info(f"Extracted {len(available_zones)} available zones")
        return available_zones
    
    def _create_forbidden_zones(self, floor_plan: Any) -> Polygon:
        """Create union of all forbidden zones"""
        forbidden_polygons = []
        
        # Add restricted areas with buffer
        for restricted in getattr(floor_plan, 'restricted_areas', []):
            if hasattr(restricted, 'geometry'):
                buffered = restricted.geometry.buffer(self.restricted_buffer)
                forbidden_polygons.append(buffered)
        
        # Add entrance buffer zones
        for entrance in getattr(floor_plan, 'entrances', []):
            if hasattr(entrance, 'geometry'):
                if hasattr(entrance.geometry, 'buffer'):
                    buffered = entrance.geometry.buffer(self.entrance_buffer)
                    forbidden_polygons.append(buffered)
        
        # Create union of all forbidden areas
        if forbidden_polygons:
            forbidden_union = unary_union(forbidden_polygons)
        else:
            forbidden_union = Polygon()  # Empty polygon
        
        logger.info(f"Created forbidden zones with {len(forbidden_polygons)} elements")
        return forbidden_union
    
    def _generate_ilot_specifications(self, config: Dict[str, float], total_area: float) -> List[IlotSpecification]:
        """Generate îlot specifications based on configuration"""
        specs = []
        
        # Calculate target density and total îlots
        density_factor = 0.15  # 15% coverage
        target_coverage = total_area * density_factor
        
        # Category definitions with size ranges
        categories = [
            ('Micro (0-1m²)', 0.5, 1.0, config.get('size_0_1', 0.10)),
            ('Small (1-3m²)', 1.0, 3.0, config.get('size_1_3', 0.25)),
            ('Medium (3-5m²)', 3.0, 5.0, config.get('size_3_5', 0.30)),
            ('Large (5-10m²)', 5.0, 10.0, config.get('size_5_10', 0.35))
        ]
        
        # Calculate average area per category
        avg_areas = [(min_area + max_area) / 2 for _, min_area, max_area, _ in categories]
        
        # Estimate total îlots needed
        weighted_avg_area = sum(avg_area * percentage for (_, _, _, percentage), avg_area in zip(categories, avg_areas))
        total_ilots = max(20, int(target_coverage / weighted_avg_area))
        
        # Generate specifications for each category
        ilot_id = 1
        for category_name, min_area, max_area, percentage in categories:
            count = int(total_ilots * percentage)
            
            for _ in range(count):
                # Random area within range
                area = random.uniform(min_area, max_area)
                
                # Calculate dimensions with slight randomness
                aspect_ratio = random.uniform(0.7, 1.5)
                width = math.sqrt(area * aspect_ratio)
                height = area / width
                
                spec = IlotSpecification(
                    id=ilot_id,
                    area=area,
                    width=width,
                    height=height,
                    category=category_name,
                    color=self.category_colors[category_name]
                )
                specs.append(spec)
                ilot_id += 1
        
        logger.info(f"Generated {len(specs)} îlot specifications")
        return specs
    
    def _place_ilots_optimized(self, specs: List[IlotSpecification], 
                              available_zones: List[Polygon], 
                              forbidden_zones: Polygon) -> List[PlacedIlot]:
        """Place îlots using optimized algorithms"""
        placed_ilots = []
        
        # Sort specs by area (largest first for better packing)
        sorted_specs = sorted(specs, key=lambda x: x.area, reverse=True)
        
        # Use grid-based placement with optimization
        for spec in sorted_specs:
            best_placement = self._find_optimal_placement(
                spec, available_zones, forbidden_zones, placed_ilots
            )
            
            if best_placement:
                placed_ilots.append(best_placement)
        
        logger.info(f"Successfully placed {len(placed_ilots)} out of {len(specs)} îlots")
        return placed_ilots
    
    def _find_optimal_placement(self, spec: IlotSpecification, 
                               available_zones: List[Polygon],
                               forbidden_zones: Polygon,
                               existing_ilots: List[PlacedIlot]) -> Optional[PlacedIlot]:
        """Find optimal placement for a single îlot"""
        best_score = -1
        best_placement = None
        
        # Try placement in each available zone
        for zone in available_zones:
            bounds = zone.bounds
            
            # Grid search within zone
            grid_size = min(spec.width, spec.height) / 2
            
            x_range = np.arange(bounds[0], bounds[2] - spec.width, grid_size)
            y_range = np.arange(bounds[1], bounds[3] - spec.height, grid_size)
            
            for x in x_range:
                for y in y_range:
                    # Try different orientations
                    for rotation in [0, 90]:
                        w, h = (spec.width, spec.height) if rotation == 0 else (spec.height, spec.width)
                        
                        # Create candidate polygon
                        candidate_polygon = box(x, y, x + w, y + h)
                        
                        # Check placement validity
                        if self._is_valid_placement(candidate_polygon, zone, forbidden_zones, existing_ilots):
                            # Calculate placement score
                            score = self._calculate_placement_score(candidate_polygon, zone, existing_ilots)
                            
                            if score > best_score:
                                best_score = score
                                best_placement = PlacedIlot(
                                    id=spec.id,
                                    x=x,
                                    y=y,
                                    width=w,
                                    height=h,
                                    rotation=rotation,
                                    area=spec.area,
                                    category=spec.category,
                                    color=spec.color,
                                    polygon=candidate_polygon,
                                    placement_score=score
                                )
        
        return best_placement
    
    def _is_valid_placement(self, candidate: Polygon, zone: Polygon, 
                           forbidden_zones: Polygon, existing_ilots: List[PlacedIlot]) -> bool:
        """Check if îlot placement is valid"""
        
        # Must be fully within available zone
        if not zone.contains(candidate):
            return False
        
        # Must not intersect forbidden zones
        if forbidden_zones.is_valid and candidate.intersects(forbidden_zones):
            return False
        
        # Must maintain minimum spacing from existing îlots
        for existing in existing_ilots:
            distance = candidate.distance(existing.polygon)
            if distance < self.min_spacing:
                return False
        
        return True
    
    def _calculate_placement_score(self, candidate: Polygon, zone: Polygon, 
                                  existing_ilots: List[PlacedIlot]) -> float:
        """Calculate placement quality score"""
        score = 1.0
        
        # Prefer positions closer to zone center
        zone_center = zone.centroid
        candidate_center = candidate.centroid
        distance_to_center = zone_center.distance(candidate_center)
        zone_radius = math.sqrt(zone.area / math.pi)
        center_score = max(0, 1 - distance_to_center / zone_radius)
        
        # Prefer good spacing from other îlots
        if existing_ilots:
            min_distance = min(candidate.distance(ilot.polygon) for ilot in existing_ilots)
            spacing_score = min(1.0, min_distance / 2.0)  # Normalize to 2m ideal spacing
        else:
            spacing_score = 1.0
        
        # Prefer positions that utilize space efficiently
        zone_utilization = candidate.area / zone.area
        utilization_score = min(1.0, zone_utilization * 10)  # Boost small efficient placements
        
        # Combined score
        score = center_score * 0.4 + spacing_score * 0.4 + utilization_score * 0.2
        
        return score
    
    def _generate_intelligent_corridors(self, placed_ilots: List[PlacedIlot], 
                                       available_zones: List[Polygon]) -> List[Dict[str, Any]]:
        """Generate intelligent corridor network"""
        corridors = []
        
        if len(placed_ilots) < 2:
            return corridors
        
        # Group îlots into rows
        ilot_rows = self._group_ilots_into_rows(placed_ilots)
        
        if len(ilot_rows) < 2:
            return corridors
        
        # Generate corridors between adjacent rows
        for i in range(len(ilot_rows) - 1):
            row1 = ilot_rows[i]
            row2 = ilot_rows[i + 1]
            
            corridor = self._create_corridor_between_rows(row1, row2, available_zones)
            if corridor:
                corridors.append(corridor)
        
        logger.info(f"Generated {len(corridors)} corridors")
        return corridors
    
    def _group_ilots_into_rows(self, placed_ilots: List[PlacedIlot]) -> List[List[PlacedIlot]]:
        """Group îlots into rows based on Y coordinate"""
        if not placed_ilots:
            return []
        
        # Sort by Y coordinate
        sorted_ilots = sorted(placed_ilots, key=lambda ilot: ilot.y)
        
        rows = []
        current_row = [sorted_ilots[0]]
        row_tolerance = 3.0  # 3m tolerance for same row
        
        for ilot in sorted_ilots[1:]:
            if abs(ilot.y - current_row[-1].y) <= row_tolerance:
                current_row.append(ilot)
            else:
                if len(current_row) >= 2:  # Only keep rows with multiple îlots
                    rows.append(current_row)
                current_row = [ilot]
        
        if len(current_row) >= 2:
            rows.append(current_row)
        
        return rows
    
    def _create_corridor_between_rows(self, row1: List[PlacedIlot], row2: List[PlacedIlot],
                                     available_zones: List[Polygon]) -> Optional[Dict[str, Any]]:
        """Create corridor between two rows of îlots"""
        
        # Calculate row bounds
        row1_bounds = self._calculate_row_bounds(row1)
        row2_bounds = self._calculate_row_bounds(row2)
        
        # Check if rows are reasonably close
        distance = abs(row1_bounds['center_y'] - row2_bounds['center_y'])
        if distance > 8.0:  # Max 8m between rows
            return None
        
        # Calculate corridor dimensions
        overlap_x_min = max(row1_bounds['min_x'], row2_bounds['min_x'])
        overlap_x_max = min(row1_bounds['max_x'], row2_bounds['max_x'])
        
        if overlap_x_max <= overlap_x_min:
            return None
        
        # Position corridor between rows
        corridor_y = (row1_bounds['center_y'] + row2_bounds['center_y']) / 2
        corridor_width = 1.5  # 1.5m corridor width
        
        corridor_polygon = box(
            overlap_x_min,
            corridor_y - corridor_width / 2,
            overlap_x_max,
            corridor_y + corridor_width / 2
        )
        
        # Ensure corridor is within available zones
        for zone in available_zones:
            if zone.intersects(corridor_polygon):
                corridor_polygon = corridor_polygon.intersection(zone)
                break
        
        if corridor_polygon.area < 1.0:
            return None
        
        return {
            'id': f"corridor_{len(row1)}_{len(row2)}",
            'polygon': corridor_polygon,
            'width': corridor_width,
            'length': overlap_x_max - overlap_x_min,
            'area': corridor_polygon.area,
            'connects_rows': (len(row1), len(row2))
        }
    
    def _calculate_row_bounds(self, row: List[PlacedIlot]) -> Dict[str, float]:
        """Calculate bounding information for a row of îlots"""
        min_x = min(ilot.x for ilot in row)
        max_x = max(ilot.x + ilot.width for ilot in row)
        min_y = min(ilot.y for ilot in row)
        max_y = max(ilot.y + ilot.height for ilot in row)
        center_y = sum(ilot.y + ilot.height / 2 for ilot in row) / len(row)
        
        return {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'center_y': center_y
        }
    
    def _calculate_placement_metrics(self, placed_ilots: List[PlacedIlot], 
                                   total_area: float, corridors: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive placement metrics"""
        
        if not placed_ilots:
            return {
                'total_ilots': 0,
                'total_area_used': 0,
                'space_utilization': 0,
                'average_spacing': 0,
                'corridor_coverage': 0
            }
        
        # Calculate total area used by îlots
        total_ilot_area = sum(ilot.area for ilot in placed_ilots)
        
        # Calculate corridor area
        corridor_area = sum(corridor.get('area', 0) for corridor in corridors)
        
        # Calculate average spacing
        if len(placed_ilots) > 1:
            distances = []
            for i, ilot1 in enumerate(placed_ilots):
                for ilot2 in placed_ilots[i+1:]:
                    distance = ilot1.polygon.distance(ilot2.polygon)
                    distances.append(distance)
            average_spacing = np.mean(distances) if distances else 0
        else:
            average_spacing = 0
        
        # Category distribution
        categories = {}
        for ilot in placed_ilots:
            cat = ilot.category
            if cat not in categories:
                categories[cat] = {'count': 0, 'area': 0}
            categories[cat]['count'] += 1
            categories[cat]['area'] += ilot.area
        
        return {
            'total_ilots': len(placed_ilots),
            'total_area_used': total_ilot_area,
            'space_utilization': (total_ilot_area + corridor_area) / total_area if total_area > 0 else 0,
            'average_spacing': average_spacing,
            'corridor_coverage': corridor_area,
            'corridor_count': len(corridors),
            'categories': categories,
            'average_placement_score': np.mean([ilot.placement_score for ilot in placed_ilots])
        }
