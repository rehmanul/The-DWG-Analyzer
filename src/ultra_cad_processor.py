"""
Ultra CAD Processor - Phase 1: Advanced CAD File Processing & Floor Plan Extraction
Pixel-perfect CAD processing with intelligent floor plan detection
"""

import logging
import os
import tempfile
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import ezdxf
import fitz  # PyMuPDF
from PIL import Image
import math
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
import pandas as pd

logger = logging.getLogger(__name__)

class ElementType(Enum):
    WALL = "wall"
    DOOR = "door" 
    WINDOW = "window"
    ROOM_BOUNDARY = "room_boundary"
    DIMENSION = "dimension"
    TEXT = "text"
    FURNITURE = "furniture"
    RESTRICTED = "restricted"
    ENTRANCE = "entrance"

@dataclass
class CADElement:
    """Represents a CAD element with full geometric and metadata"""
    element_type: ElementType
    geometry: Union[List[Tuple[float, float]], Polygon, LineString]
    layer: str
    color: int
    line_weight: float
    properties: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class FloorPlan:
    """Represents an extracted floor plan with all elements"""
    elements: List[CADElement]
    bounds: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y
    scale: float
    units: str
    sheet_info: Dict[str, Any]
    confidence_score: float

class UltraCADProcessor:
    """
    Ultra high-performance CAD processor for pixel-perfect floor plan extraction
    Handles DXF, DWG, PDF files with intelligent floor plan detection
    """
    
    def __init__(self):
        self.supported_formats = {'.dxf', '.dwg', '.pdf', '.png', '.jpg', '.jpeg', '.tiff'}
        self.wall_layers = {'wall', 'walls', 'mur', 'murs', 'boundary', 'outline', 'structure'}
        self.door_layers = {'door', 'doors', 'porte', 'portes', 'opening', 'openings'}
        self.window_layers = {'window', 'windows', 'fenetre', 'fenetres', 'glazing'}
        self.dimension_layers = {'dimension', 'dim', 'dims', 'quote', 'quotes', 'text'}
        self.restricted_layers = {'restricted', 'no_entry', 'stair', 'stairs', 'escalier', 'elevator', 'lift'}
        
        # Color mappings for intelligent classification
        self.color_classifications = {
            0: ElementType.WALL,     # Black - walls
            7: ElementType.WALL,     # White/Black - walls  
            1: ElementType.ENTRANCE, # Red - entrances
            2: ElementType.ENTRANCE, # Red variation
            5: ElementType.RESTRICTED, # Blue - restricted areas
            3: ElementType.FURNITURE,  # Green - furniture
            4: ElementType.WINDOW,     # Cyan - windows
            6: ElementType.DOOR,       # Magenta - doors
        }

    def process_cad_file(self, file_path: str, extract_all_sheets: bool = True) -> List[FloorPlan]:
        """
        Main entry point - processes CAD file and extracts floor plans
        Returns list of floor plans found (multi-sheet support)
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        logger.info(f"Processing CAD file: {file_path}")
        
        try:
            if file_ext == '.dxf':
                return self._process_dxf_file(file_path, extract_all_sheets)
            elif file_ext == '.dwg':
                return self._process_dwg_file(file_path, extract_all_sheets)
            elif file_ext == '.pdf':
                return self._process_pdf_file(file_path, extract_all_sheets)
            elif file_ext in {'.png', '.jpg', '.jpeg', '.tiff'}:
                return self._process_image_file(file_path)
            else:
                raise ValueError(f"Format {file_ext} not implemented yet")
                
        except Exception as e:
            logger.error(f"Error processing CAD file {file_path}: {e}")
            raise

    def _process_dxf_file(self, file_path: str, extract_all_sheets: bool) -> List[FloorPlan]:
        """Enhanced DXF processing with multi-sheet support and intelligent element detection"""
        try:
            doc = ezdxf.readfile(file_path)
            floor_plans = []
            
            # Process model space (main drawing)
            model_space = doc.modelspace()
            main_plan = self._extract_floor_plan_from_space(model_space, "ModelSpace")
            if main_plan and main_plan.confidence_score > 0.5:
                floor_plans.append(main_plan)
            
            # Process paper space layouts if requested
            if extract_all_sheets:
                for layout_name in doc.layout_names():
                    if layout_name != "Model":
                        layout = doc.layout(layout_name)
                        layout_plan = self._extract_floor_plan_from_space(layout, layout_name)
                        if layout_plan and layout_plan.confidence_score > 0.5:
                            floor_plans.append(layout_plan)
            
            # Sort by confidence score (best first)
            floor_plans.sort(key=lambda x: x.confidence_score, reverse=True)
            return floor_plans
            
        except Exception as e:
            logger.error(f"DXF processing failed: {e}")
            raise

    def _extract_floor_plan_from_space(self, space, sheet_name: str) -> Optional[FloorPlan]:
        """Extract floor plan from DXF model space or layout with intelligent element classification"""
        elements = []
        all_points = []
        
        # Statistics for confidence scoring
        wall_count = 0
        room_count = 0
        total_entities = 0
        
        for entity in space:
            total_entities += 1
            cad_element = self._classify_dxf_entity(entity)
            
            if cad_element:
                elements.append(cad_element)
                
                # Extract points for bounds calculation
                if hasattr(cad_element.geometry, '__iter__') and not isinstance(cad_element.geometry, str):
                    if isinstance(cad_element.geometry, list):
                        all_points.extend(cad_element.geometry)
                    elif hasattr(cad_element.geometry, 'exterior'):
                        all_points.extend(list(cad_element.geometry.exterior.coords))
                
                # Update statistics
                if cad_element.element_type == ElementType.WALL:
                    wall_count += 1
                elif cad_element.element_type == ElementType.ROOM_BOUNDARY:
                    room_count += 1
        
        if not elements or not all_points:
            return None
        
        # Calculate bounds
        x_coords = [p[0] for p in all_points if len(p) >= 2]
        y_coords = [p[1] for p in all_points if len(p) >= 2]
        
        if not x_coords or not y_coords:
            return None
            
        bounds = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
        
        # Calculate confidence score based on architectural elements
        confidence_score = self._calculate_confidence_score(
            wall_count, room_count, total_entities, bounds
        )
        
        # Determine scale and units
        scale, units = self._determine_scale_and_units(bounds, elements)
        
        return FloorPlan(
            elements=elements,
            bounds=bounds,
            scale=scale,
            units=units,
            sheet_info={'name': sheet_name, 'entity_count': total_entities},
            confidence_score=confidence_score
        )

    def _classify_dxf_entity(self, entity) -> Optional[CADElement]:
        """Intelligently classify DXF entity into architectural elements"""
        try:
            entity_type = entity.dxftype()
            layer = getattr(entity.dxf, 'layer', '0').lower()
            color = getattr(entity.dxf, 'color', 7)
            line_weight = getattr(entity.dxf, 'lineweight', 0.25)
            
            # Extract geometry based on entity type
            geometry = None
            element_type = None
            properties = {}
            
            if entity_type in ['LWPOLYLINE', 'POLYLINE']:
                points = self._extract_polyline_points(entity)
                if len(points) >= 2:
                    geometry = points
                    element_type = self._classify_by_layer_and_color(layer, color)
                    properties['closed'] = getattr(entity.dxf, 'closed', False)
                    
            elif entity_type == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                geometry = [(start[0], start[1]), (end[0], end[1])]
                element_type = self._classify_by_layer_and_color(layer, color)
                
            elif entity_type == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                # Convert circle to polygon
                angles = np.linspace(0, 2*np.pi, 32)
                points = [(center[0] + radius*np.cos(a), center[1] + radius*np.sin(a)) for a in angles]
                geometry = points
                element_type = self._classify_by_layer_and_color(layer, color)
                properties['radius'] = radius
                properties['center'] = (center[0], center[1])
                
            elif entity_type == 'ARC':
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                
                # Convert arc to polyline
                angle_diff = end_angle - start_angle
                if angle_diff < 0:
                    angle_diff += 2 * np.pi
                num_points = max(8, int(angle_diff / (np.pi/8)))
                angles = np.linspace(start_angle, end_angle, num_points)
                points = [(center[0] + radius*np.cos(a), center[1] + radius*np.sin(a)) for a in angles]
                geometry = points
                element_type = ElementType.DOOR if 'door' in layer else ElementType.WALL
                properties['radius'] = radius
                properties['start_angle'] = start_angle
                properties['end_angle'] = end_angle
                
            elif entity_type == 'TEXT':
                position = entity.dxf.insert
                text_content = entity.dxf.text
                geometry = [(position[0], position[1])]
                element_type = ElementType.TEXT
                properties['text'] = text_content
                properties['height'] = getattr(entity.dxf, 'height', 2.5)
                
            elif entity_type == 'MTEXT':
                position = entity.dxf.insert
                text_content = entity.text
                geometry = [(position[0], position[1])]
                element_type = ElementType.TEXT
                properties['text'] = text_content
                properties['height'] = getattr(entity.dxf, 'char_height', 2.5)
                
            else:
                # Skip unsupported entity types
                return None
            
            if geometry and element_type:
                return CADElement(
                    element_type=element_type,
                    geometry=geometry,
                    layer=layer,
                    color=color,
                    line_weight=line_weight,
                    properties=properties,
                    metadata={'dxf_type': entity_type}
                )
                
        except Exception as e:
            logger.warning(f"Error classifying entity {entity.dxftype()}: {e}")
            
        return None

    def _extract_polyline_points(self, entity) -> List[Tuple[float, float]]:
        """Extract points from polyline entity"""
        points = []
        try:
            if hasattr(entity, 'get_points'):
                point_list = list(entity.get_points())
                points = [(p[0], p[1]) for p in point_list if len(p) >= 2]
            elif hasattr(entity, 'vertices'):
                for vertex in entity.vertices:
                    if hasattr(vertex, 'dxf'):
                        loc = vertex.dxf.location
                        points.append((loc[0], loc[1]))
        except Exception as e:
            logger.warning(f"Error extracting polyline points: {e}")
        return points

    def _classify_by_layer_and_color(self, layer: str, color: int) -> ElementType:
        """Classify element type based on layer name and color"""
        # Layer-based classification (most reliable)
        layer_lower = layer.lower()
        
        if any(wall_layer in layer_lower for wall_layer in self.wall_layers):
            return ElementType.WALL
        elif any(door_layer in layer_lower for door_layer in self.door_layers):
            return ElementType.DOOR
        elif any(window_layer in layer_lower for window_layer in self.window_layers):
            return ElementType.WINDOW
        elif any(restricted_layer in layer_lower for restricted_layer in self.restricted_layers):
            return ElementType.RESTRICTED
        elif any(dim_layer in layer_lower for dim_layer in self.dimension_layers):
            return ElementType.DIMENSION
        
        # Color-based classification (fallback)
        if color in self.color_classifications:
            return self.color_classifications[color]
        
        # Default classification
        return ElementType.ROOM_BOUNDARY

    def _calculate_confidence_score(self, wall_count: int, room_count: int, 
                                  total_entities: int, bounds: Tuple[float, float, float, float]) -> float:
        """Calculate confidence score for floor plan detection"""
        if total_entities == 0:
            return 0.0
        
        # Base score from architectural elements
        architectural_ratio = (wall_count + room_count) / total_entities
        base_score = min(architectural_ratio * 2, 1.0)  # Max 1.0
        
        # Bonus for sufficient architectural elements
        if wall_count >= 4:  # Minimum walls for a room
            base_score += 0.2
        if room_count >= 1:  # At least one room
            base_score += 0.1
        
        # Bonus for reasonable drawing size
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        if 10 <= width <= 1000 and 10 <= height <= 1000:  # Reasonable building size
            base_score += 0.1
        
        return min(base_score, 1.0)

    def _determine_scale_and_units(self, bounds: Tuple[float, float, float, float], 
                                 elements: List[CADElement]) -> Tuple[float, str]:
        """Determine drawing scale and units from geometry analysis"""
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Analyze coordinate ranges to guess units
        max_dimension = max(width, height)
        
        if max_dimension < 100:
            # Likely meters
            return 1.0, "meters"
        elif max_dimension < 1000:
            # Could be meters or millimeters
            # Check for typical room sizes
            room_elements = [e for e in elements if e.element_type == ElementType.ROOM_BOUNDARY]
            if room_elements:
                # Analyze room sizes to determine units
                avg_room_size = max_dimension / max(len(room_elements), 1)
                if 20 <= avg_room_size <= 200:  # Typical room size in meters
                    return 1.0, "meters"
                else:
                    return 0.001, "millimeters"  # Convert mm to m
            return 1.0, "meters"
        else:
            # Likely millimeters
            return 0.001, "millimeters"

    def _process_dwg_file(self, file_path: str, extract_all_sheets: bool) -> List[FloorPlan]:
        """Process DWG files (requires conversion or specialized library)"""
        # For now, provide clear guidance for DWG processing
        # In production, this would use a DWG library like Open Design Alliance
        logger.warning("DWG processing requires specialized libraries. Converting to DXF recommended.")
        
        # Attempt to find converted DXF version
        dxf_path = file_path.replace('.dwg', '.dxf').replace('.DWG', '.DXF')
        if os.path.exists(dxf_path):
            logger.info(f"Found DXF version: {dxf_path}")
            return self._process_dxf_file(dxf_path, extract_all_sheets)
        
        raise NotImplementedError(
            "DWG processing requires conversion to DXF format. "
            "Please convert using AutoCAD, FreeCAD, or online converters."
        )

    def _process_pdf_file(self, file_path: str, extract_all_sheets: bool) -> List[FloorPlan]:
        """Process PDF files with CAD drawings using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            floor_plans = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to high-resolution image
                matrix = fitz.Matrix(4, 4)  # 4x zoom for high resolution
                pix = page.get_pixmap(matrix=matrix)
                img_data = pix.tobytes("png")
                
                # Create temporary image file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(img_data)
                    tmp_path = tmp_file.name
                
                try:
                    # Process as image
                    page_plans = self._process_image_file(tmp_path)
                    for plan in page_plans:
                        plan.sheet_info['pdf_page'] = page_num + 1
                        plan.sheet_info['name'] = f"Page_{page_num + 1}"
                    floor_plans.extend(page_plans)
                finally:
                    os.unlink(tmp_path)
                
                if not extract_all_sheets and floor_plans:
                    break
            
            doc.close()
            return floor_plans
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise

    def _process_image_file(self, file_path: str) -> List[FloorPlan]:
        """Process image files using advanced computer vision"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            height, width = image.shape[:2]
            
            # Advanced image processing for architectural drawing detection
            elements = self._extract_elements_from_image(image)
            
            if not elements:
                return []
            
            # Calculate bounds from image dimensions
            bounds = (0, 0, width * 0.1, height * 0.1)  # Convert pixels to approximate meters
            
            # Calculate confidence based on detected architectural elements
            wall_count = len([e for e in elements if e.element_type == ElementType.WALL])
            room_count = len([e for e in elements if e.element_type == ElementType.ROOM_BOUNDARY])
            confidence = self._calculate_confidence_score(wall_count, room_count, len(elements), bounds)
            
            floor_plan = FloorPlan(
                elements=elements,
                bounds=bounds,
                scale=0.1,  # Pixel to meter conversion
                units="meters",
                sheet_info={'name': Path(file_path).stem, 'format': 'image'},
                confidence_score=confidence
            )
            
            return [floor_plan]
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise

    def _extract_elements_from_image(self, image: np.ndarray) -> List[CADElement]:
        """Extract architectural elements from image using computer vision"""
        elements = []
        
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Advanced color detection for walls (black/dark lines)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        black_mask = cv2.inRange(hsv, lower_black, upper_black)
        
        # Detect walls using contour analysis
        wall_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in wall_contours:
            if cv2.contourArea(contour) > 100:  # Filter noise
                # Simplify contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                points = [(float(p[0][0] * 0.1), float(p[0][1] * 0.1)) for p in approx]
                if len(points) >= 2:
                    elements.append(CADElement(
                        element_type=ElementType.WALL,
                        geometry=points,
                        layer='walls',
                        color=0,
                        line_weight=2.0,
                        properties={'area': cv2.contourArea(contour)},
                        metadata={'source': 'image_processing'}
                    ))
        
        # Detect blue restricted areas
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in blue_contours:
            if cv2.contourArea(contour) > 500:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                points = [(float(p[0][0] * 0.1), float(p[0][1] * 0.1)) for p in approx]
                if len(points) >= 3:
                    elements.append(CADElement(
                        element_type=ElementType.RESTRICTED,
                        geometry=points,
                        layer='restricted',
                        color=5,
                        line_weight=1.0,
                        properties={'area': cv2.contourArea(contour)},
                        metadata={'source': 'image_processing'}
                    ))
        
        # Detect red entrance areas
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in red_contours:
            if cv2.contourArea(contour) > 50:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                points = [(float(p[0][0] * 0.1), float(p[0][1] * 0.1)) for p in approx]
                if len(points) >= 2:
                    elements.append(CADElement(
                        element_type=ElementType.ENTRANCE,
                        geometry=points,
                        layer='entrances',
                        color=1,
                        line_weight=1.0,
                        properties={'area': cv2.contourArea(contour)},
                        metadata={'source': 'image_processing'}
                    ))
        
        return elements

    def get_best_floor_plan(self, floor_plans: List[FloorPlan]) -> Optional[FloorPlan]:
        """Get the floor plan with highest confidence score"""
        if not floor_plans:
            return None
        return max(floor_plans, key=lambda x: x.confidence_score)

    def export_floor_plan_analysis(self, floor_plan: FloorPlan) -> Dict[str, Any]:
        """Export comprehensive floor plan analysis"""
        if not floor_plan:
            return {}
        
        analysis = {
            'summary': {
                'total_elements': len(floor_plan.elements),
                'confidence_score': floor_plan.confidence_score,
                'bounds': floor_plan.bounds,
                'scale': floor_plan.scale,
                'units': floor_plan.units,
                'sheet_info': floor_plan.sheet_info
            },
            'elements_by_type': {},
            'wall_analysis': {},
            'room_analysis': {},
            'spatial_metrics': {}
        }
        
        # Group elements by type
        for element_type in ElementType:
            elements_of_type = [e for e in floor_plan.elements if e.element_type == element_type]
            analysis['elements_by_type'][element_type.value] = {
                'count': len(elements_of_type),
                'elements': [self._element_to_dict(e) for e in elements_of_type]
            }
        
        # Wall analysis
        walls = [e for e in floor_plan.elements if e.element_type == ElementType.WALL]
        if walls:
            total_wall_length = sum(self._calculate_element_length(w) for w in walls)
            analysis['wall_analysis'] = {
                'total_count': len(walls),
                'total_length': total_wall_length,
                'average_thickness': 0.2  # Default wall thickness
            }
        
        # Room analysis
        rooms = [e for e in floor_plan.elements if e.element_type == ElementType.ROOM_BOUNDARY]
        if rooms:
            total_area = sum(self._calculate_element_area(r) for r in rooms)
            analysis['room_analysis'] = {
                'total_count': len(rooms),
                'total_area': total_area,
                'average_room_size': total_area / len(rooms) if rooms else 0
            }
        
        # Spatial metrics
        width = floor_plan.bounds[2] - floor_plan.bounds[0]
        height = floor_plan.bounds[3] - floor_plan.bounds[1]
        analysis['spatial_metrics'] = {
            'total_width': width,
            'total_height': height,
            'total_footprint': width * height,
            'aspect_ratio': width / height if height > 0 else 1.0
        }
        
        return analysis

    def _element_to_dict(self, element: CADElement) -> Dict[str, Any]:
        """Convert CADElement to dictionary"""
        return {
            'type': element.element_type.value,
            'geometry': element.geometry,
            'layer': element.layer,
            'color': element.color,
            'line_weight': element.line_weight,
            'properties': element.properties,
            'metadata': element.metadata
        }

    def _calculate_element_length(self, element: CADElement) -> float:
        """Calculate length of linear element"""
        if isinstance(element.geometry, list) and len(element.geometry) >= 2:
            total_length = 0.0
            for i in range(len(element.geometry) - 1):
                p1 = element.geometry[i]
                p2 = element.geometry[i + 1]
                total_length += math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            return total_length
        return 0.0

    def _calculate_element_area(self, element: CADElement) -> float:
        """Calculate area of polygon element"""
        if isinstance(element.geometry, list) and len(element.geometry) >= 3:
            try:
                polygon = Polygon(element.geometry)
                return polygon.area
            except:
                return 0.0
        return 0.0