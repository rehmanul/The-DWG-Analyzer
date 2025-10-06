"""
Production Corridor Generator
Automatically generates corridors between îlot rows
NO SIMULATIONS - Real geometric algorithms only
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union
from scipy.cluster.hierarchy import fclusterdata

logger = logging.getLogger(__name__)


@dataclass
class Corridor:
    """Represents a corridor"""
    id: int
    polygon: Polygon
    width: float
    length: float
    connects_rows: Tuple[int, int]  # (row1_id, row2_id)
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    
    @property
    def area(self) -> float:
        return self.polygon.area


class ProductionCorridorGenerator:
    """
    Production-grade corridor generator
    Creates corridors between facing rows of îlots
    Ensures corridors never cut through îlots
    """
    
    def __init__(self, corridor_width: float = 1.5, min_corridor_length: float = 2.0):
        """
        Initialize corridor generator
        
        Args:
            corridor_width: Width of corridors in meters (user-configurable)
            min_corridor_length: Minimum corridor length in meters
        """
        self.corridor_width = corridor_width
        self.min_corridor_length = min_corridor_length
        self.row_tolerance = 3.0  # Distance tolerance for grouping îlots into rows
        
    def generate_corridors(self, ilots: List, open_spaces: List[Polygon]) -> List[Corridor]:
        """
        Generate corridors between îlot rows
        
        Args:
            ilots: List of PlacedIlot objects
            open_spaces: Available spaces for corridor routing
            
        Returns:
            List of Corridor objects
        """
        logger.info(f"Generating corridors for {len(ilots)} îlots")
        
        if len(ilots) < 4:
            logger.warning("Not enough îlots to create meaningful corridors")
            return []
        
        # Step 1: Group îlots into rows
        rows = self._group_ilots_into_rows(ilots)
        logger.info(f"Identified {len(rows)} rows of îlots")
        
        if len(rows) < 2:
            logger.warning("Need at least 2 rows to create corridors")
            return []
        
        # Step 2: Generate corridors between adjacent rows
        corridors = []
        for i in range(len(rows) - 1):
            row1 = rows[i]
            row2 = rows[i + 1]
            
            corridor = self._create_corridor_between_rows(
                row1, row2, i, i + 1, ilots, open_spaces
            )
            
            if corridor:
                corridors.append(corridor)
        
        logger.info(f"Generated {len(corridors)} corridors")
        return corridors
    
    def _group_ilots_into_rows(self, ilots: List) -> List[List]:
        """
        Group îlots into horizontal rows based on Y-coordinate
        Uses hierarchical clustering for robust row detection
        """
        if not ilots:
            return []
        
        # Extract Y-coordinates of îlot centers
        positions = np.array([ilot.position for ilot in ilots])
        y_coords = positions[:, 1].reshape(-1, 1)
        
        # Hierarchical clustering to identify rows
        try:
            # Use Ward linkage for clustering
            labels = fclusterdata(y_coords, t=self.row_tolerance, criterion='distance', method='ward')
            
            # Group îlots by cluster label
            rows_dict = {}
            for ilot, label in zip(ilots, labels):
                if label not in rows_dict:
                    rows_dict[label] = []
                rows_dict[label].append(ilot)
            
            # Sort rows by average Y-coordinate (bottom to top)
            rows = []
            for label, row_ilots in rows_dict.items():
                avg_y = np.mean([ilot.position[1] for ilot in row_ilots])
                rows.append((avg_y, row_ilots))
            
            rows.sort(key=lambda x: x[0])
            
            # Filter out rows with less than 2 îlots
            valid_rows = [row_ilots for _, row_ilots in rows if len(row_ilots) >= 2]
            
            logger.info(f"Clustered îlots into {len(valid_rows)} valid rows")
            return valid_rows
            
        except Exception as e:
            logger.error(f"Failed to cluster îlots into rows: {e}")
            # Fallback to simple Y-coordinate sorting
            return self._simple_row_grouping(ilots)
    
    def _simple_row_grouping(self, ilots: List) -> List[List]:
        """Fallback method for row grouping using simple Y-coordinate binning"""
        # Sort by Y-coordinate
        sorted_ilots = sorted(ilots, key=lambda i: i.position[1])
        
        rows = []
        current_row = [sorted_ilots[0]]
        current_y = sorted_ilots[0].position[1]
        
        for ilot in sorted_ilots[1:]:
            if abs(ilot.position[1] - current_y) <= self.row_tolerance:
                current_row.append(ilot)
            else:
                if len(current_row) >= 2:
                    rows.append(current_row)
                current_row = [ilot]
                current_y = ilot.position[1]
        
        # Add last row
        if len(current_row) >= 2:
            rows.append(current_row)
        
        return rows
    
    def _create_corridor_between_rows(self, row1: List, row2: List, 
                                     row1_id: int, row2_id: int,
                                     all_ilots: List, open_spaces: List[Polygon]) -> Optional[Corridor]:
        """
        Create a corridor between two rows of îlots
        Ensures corridor touches both rows but never cuts through any îlot
        """
        
        # Calculate row bounds
        row1_bounds = self._get_row_bounds(row1)
        row2_bounds = self._get_row_bounds(row2)
        
        # Check if rows are reasonably close
        gap_distance = abs(row2_bounds['min_y'] - row1_bounds['max_y'])
        if gap_distance > 10:  # Max 10m gap
            logger.debug(f"Rows {row1_id} and {row2_id} too far apart ({gap_distance:.2f}m)")
            return None
        
        # Calculate corridor X-range (overlap of both rows)
        corridor_min_x = max(row1_bounds['min_x'], row2_bounds['min_x'])
        corridor_max_x = min(row1_bounds['max_x'], row2_bounds['max_x'])
        
        if corridor_max_x <= corridor_min_x:
            logger.debug(f"Rows {row1_id} and {row2_id} don't overlap horizontally")
            return None
        
        corridor_length = corridor_max_x - corridor_min_x
        if corridor_length < self.min_corridor_length:
            logger.debug(f"Corridor too short between rows {row1_id} and {row2_id}")
            return None
        
        # Calculate corridor Y-position (midpoint between rows)
        corridor_y_center = (row1_bounds['max_y'] + row2_bounds['min_y']) / 2
        corridor_y_min = corridor_y_center - self.corridor_width / 2
        corridor_y_max = corridor_y_center + self.corridor_width / 2
        
        # Create corridor polygon
        corridor_poly = box(corridor_min_x, corridor_y_min, corridor_max_x, corridor_y_max)
        
        # Validate corridor doesn't cut through îlots
        if self._corridor_intersects_ilots(corridor_poly, all_ilots):
            logger.debug(f"Corridor between rows {row1_id} and {row2_id} intersects îlots")
            return None
        
        # Validate corridor is within open spaces
        if not self._corridor_in_open_space(corridor_poly, open_spaces):
            logger.debug(f"Corridor between rows {row1_id} and {row2_id} not in open space")
            # Try to clip corridor to open spaces
            corridor_poly = self._clip_corridor_to_open_space(corridor_poly, open_spaces)
            if corridor_poly is None or corridor_poly.area < self.min_corridor_length * self.corridor_width * 0.5:
                return None
        
        # Create corridor object
        corridor = Corridor(
            id=len([]),  # Will be set by caller
            polygon=corridor_poly,
            width=self.corridor_width,
            length=corridor_length,
            connects_rows=(row1_id, row2_id),
            start_point=(corridor_min_x, corridor_y_center),
            end_point=(corridor_max_x, corridor_y_center)
        )
        
        logger.debug(f"Created corridor between rows {row1_id} and {row2_id}: "
                    f"length={corridor_length:.2f}m, width={self.corridor_width:.2f}m")
        
        return corridor
    
    def _get_row_bounds(self, row: List) -> Dict[str, float]:
        """Get bounding box of a row of îlots"""
        if not row:
            return {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0}
        
        all_bounds = [ilot.bounds for ilot in row]
        
        return {
            'min_x': min(b[0] for b in all_bounds),
            'min_y': min(b[1] for b in all_bounds),
            'max_x': max(b[2] for b in all_bounds),
            'max_y': max(b[3] for b in all_bounds),
        }
    
    def _corridor_intersects_ilots(self, corridor_poly: Polygon, ilots: List) -> bool:
        """Check if corridor intersects any îlot"""
        for ilot in ilots:
            if corridor_poly.intersects(ilot.polygon):
                # Allow touching at edges, but not overlapping
                intersection = corridor_poly.intersection(ilot.polygon)
                if intersection.area > 0.01:  # More than 1cm² overlap
                    return True
        return False
    
    def _corridor_in_open_space(self, corridor_poly: Polygon, open_spaces: List[Polygon]) -> bool:
        """Check if corridor is within open spaces"""
        for space in open_spaces:
            if space.contains(corridor_poly):
                return True
        return False
    
    def _clip_corridor_to_open_space(self, corridor_poly: Polygon, 
                                    open_spaces: List[Polygon]) -> Optional[Polygon]:
        """Clip corridor to open spaces"""
        if not open_spaces:
            return None
        
        try:
            open_space_union = unary_union(open_spaces)
            clipped = corridor_poly.intersection(open_space_union)
            
            if clipped.geom_type == 'Polygon' and clipped.is_valid and clipped.area > 0:
                return clipped
            elif clipped.geom_type == 'MultiPolygon':
                # Take largest polygon
                largest = max(clipped.geoms, key=lambda p: p.area)
                if largest.area > 0:
                    return largest
        except Exception as e:
            logger.warning(f"Failed to clip corridor: {e}")
        
        return None
    
    def get_corridor_network_stats(self, corridors: List[Corridor]) -> Dict:
        """Calculate statistics about corridor network"""
        if not corridors:
            return {
                'total_corridors': 0,
                'total_length': 0,
                'total_area': 0,
                'avg_length': 0,
                'avg_width': 0
            }
        
        total_length = sum(c.length for c in corridors)
        total_area = sum(c.area for c in corridors)
        
        return {
            'total_corridors': len(corridors),
            'total_length': total_length,
            'total_area': total_area,
            'avg_length': total_length / len(corridors),
            'avg_width': self.corridor_width
        }
