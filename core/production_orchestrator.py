"""
Production System Orchestrator
Coordinates CAD parsing, îlot placement, and corridor generation
NO SIMULATIONS - Production-grade algorithms only
"""

import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from shapely.geometry import Polygon

from core.production_cad_parser import ProductionCADParser, ZoneType
from core.production_ilot_engine import ProductionIlotEngine, IlotSizeConfig, PlacedIlot
from core.production_corridor_generator import ProductionCorridorGenerator, Corridor

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Complete processing result"""
    # Input zones
    walls: List[Polygon]
    restricted_areas: List[Polygon]
    entrances: List[Polygon]
    open_spaces: List[Polygon]
    
    # Placed elements
    ilots: List[PlacedIlot]
    corridors: List[Corridor]
    
    # Metrics
    total_area: float
    ilot_coverage_pct: float
    corridor_coverage_pct: float
    total_coverage_pct: float
    placement_score: float
    
    # Processing info
    processing_time: float
    success: bool
    error_message: str = ""


class ProductionOrchestrator:
    """
    Main orchestrator for the complete system
    Handles: DXF parsing → Îlot placement → Corridor generation
    """
    
    def __init__(self):
        self.cad_parser = ProductionCADParser()
        
    def process_floor_plan(self, 
                          dxf_file_path: str,
                          size_config: IlotSizeConfig,
                          total_ilots: int = 100,
                          corridor_width: float = 1.5,
                          min_spacing: float = 0.3) -> ProcessingResult:
        """
        Complete processing pipeline
        
        Args:
            dxf_file_path: Path to DXF/DWG file
            size_config: Îlot size distribution configuration
            total_ilots: Target number of îlots
            corridor_width: Width of corridors in meters
            min_spacing: Minimum spacing between îlots
            
        Returns:
            ProcessingResult with all data and metrics
        """
        import time
        start_time = time.time()
        
        try:
            logger.info("="*60)
            logger.info("PRODUCTION SYSTEM - Starting Floor Plan Processing")
            logger.info("="*60)
            
            # Step 1: Parse CAD file
            logger.info("Step 1/3: Parsing CAD file...")
            walls, restricted_areas, entrances, open_spaces = self.cad_parser.parse_dxf(dxf_file_path)
            
            if not open_spaces:
                return ProcessingResult(
                    walls=walls,
                    restricted_areas=restricted_areas,
                    entrances=entrances,
                    open_spaces=[],
                    ilots=[],
                    corridors=[],
                    total_area=0,
                    ilot_coverage_pct=0,
                    corridor_coverage_pct=0,
                    total_coverage_pct=0,
                    placement_score=0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="No open spaces found in CAD file"
                )
            
            total_area = sum(space.area for space in open_spaces)
            logger.info(f"CAD parsing complete: {len(open_spaces)} open spaces, {total_area:.2f}m² total area")
            
            # Step 2: Place îlots
            logger.info("Step 2/3: Placing îlots using genetic algorithm...")
            ilot_engine = ProductionIlotEngine(
                config=size_config,
                total_ilots=total_ilots,
                min_spacing=min_spacing,
                corridor_width=corridor_width
            )
            
            placement_result = ilot_engine.place_ilots(
                open_spaces=open_spaces,
                walls=walls,
                restricted_areas=restricted_areas,
                entrances=entrances
            )
            
            ilots = placement_result['ilots']
            ilot_coverage_pct = placement_result['coverage_pct']
            placement_score = placement_result['placement_score']
            
            logger.info(f"Îlot placement complete: {len(ilots)} îlots placed, "
                       f"{ilot_coverage_pct:.1f}% coverage")
            
            # Step 3: Generate corridors
            logger.info("Step 3/3: Generating corridor network...")
            corridor_generator = ProductionCorridorGenerator(
                corridor_width=corridor_width,
                min_corridor_length=2.0
            )
            
            corridors = corridor_generator.generate_corridors(ilots, open_spaces)
            
            # Set corridor IDs
            for i, corridor in enumerate(corridors):
                corridor.id = i
            
            corridor_stats = corridor_generator.get_corridor_network_stats(corridors)
            corridor_coverage_pct = (corridor_stats['total_area'] / total_area * 100) if total_area > 0 else 0
            
            logger.info(f"Corridor generation complete: {len(corridors)} corridors, "
                       f"{corridor_coverage_pct:.1f}% coverage")
            
            # Calculate total metrics
            total_coverage_pct = ilot_coverage_pct + corridor_coverage_pct
            processing_time = time.time() - start_time
            
            logger.info("="*60)
            logger.info(f"PROCESSING COMPLETE in {processing_time:.2f}s")
            logger.info(f"  - Walls: {len(walls)}")
            logger.info(f"  - Restricted areas: {len(restricted_areas)}")
            logger.info(f"  - Entrances: {len(entrances)}")
            logger.info(f"  - Open spaces: {len(open_spaces)}")
            logger.info(f"  - Îlots placed: {len(ilots)} ({ilot_coverage_pct:.1f}% coverage)")
            logger.info(f"  - Corridors: {len(corridors)} ({corridor_coverage_pct:.1f}% coverage)")
            logger.info(f"  - Total coverage: {total_coverage_pct:.1f}%")
            logger.info("="*60)
            
            return ProcessingResult(
                walls=walls,
                restricted_areas=restricted_areas,
                entrances=entrances,
                open_spaces=open_spaces,
                ilots=ilots,
                corridors=corridors,
                total_area=total_area,
                ilot_coverage_pct=ilot_coverage_pct,
                corridor_coverage_pct=corridor_coverage_pct,
                total_coverage_pct=total_coverage_pct,
                placement_score=placement_score,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            return ProcessingResult(
                walls=[],
                restricted_areas=[],
                entrances=[],
                open_spaces=[],
                ilots=[],
                corridors=[],
                total_area=0,
                ilot_coverage_pct=0,
                corridor_coverage_pct=0,
                total_coverage_pct=0,
                placement_score=0,
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
