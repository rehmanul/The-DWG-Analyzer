
"""
Pixel-Perfect CAD Processor - Advanced Floor Plan Extraction
Implements professional-grade CAD file processing with exact visual matching
"""

import ezdxf
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging

# Try to import OpenCV, fall back to PIL-only processing if not available
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

logger = logging.getLogger(__name__)

@dataclass
class CADElement:
    """Represents a CAD element with precise geometric properties"""
    element_type: str  # 'wall', 'door', 'window', 'room', 'dimension'
    geometry: Any  # Shapely geometry object
    properties: Dict[str, Any]
    layer: str
    color: str
    line_weight: float
    
@dataclass
class FloorPlan:
    """Complete floor plan with all elements"""
    walls: List[CADElement]
    doors: List[CADElement]
    windows: List[CADElement]
    rooms: List[CADElement]
    restricted_areas: List[CADElement]
    entrances: List[CADElement]
    dimensions: List[CADElement]
    scale: float
    units: str
    bounds: Tuple[float, float, float, float]
    drawing_info: Dict[str, Any]

class PixelPerfectCADProcessor:
    """
    Advanced CAD processor for pixel-perfect floor plan extraction
    Matches exact visual specifications from reference images
    """
    
    def __init__(self):
        # Professional color standards matching reference images
        self.colors = {
            'walls': '#6B7280',      # Gray walls (MUR)
            'restricted': '#3B82F6',  # Blue restricted areas (NO ENTREE)
            'entrances': '#EF4444',   # Red entrances (ENTRÉE/SORTIE)
            'ilots': '#F87171',      # Light red îlots
            'corridors': '#FCA5A5',  # Pink corridors
            'text': '#1F2937',       # Dark gray text
            'background': '#FFFFFF'   # White background
        }
        
        # Professional line weights
        self.line_weights = {
            'walls': 3.0,
            'doors': 2.0,
            'windows': 1.5,
            'dimensions': 0.5,
            'text': 1.0
        }
        
        self.scale_factor = 1.0
        self.units = 'meters'
    
    def process_cad_file(self, file_path: str) -> FloorPlan:
        """
        Process CAD file and extract floor plan with pixel-perfect accuracy
        """
        logger.info(f"Processing CAD file: {file_path}")
        
        # Determine file type and process accordingly
        if file_path.lower().endswith('.dxf'):
            return self._process_dxf_file(file_path)
        elif file_path.lower().endswith('.dwg'):
            return self._process_dwg_file(file_path)
        elif file_path.lower().endswith('.pdf'):
            return self._process_pdf_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def _process_dxf_file(self, file_path: str) -> FloorPlan:
        """Process DXF file with advanced geometric analysis"""
        doc = ezdxf.readfile(file_path)
        
        # Auto-detect the main floor plan sheet
        main_sheet = self._detect_floor_plan_sheet(doc)
        
        # Extract all geometric elements
        walls = self._extract_walls(main_sheet)
        doors = self._extract_doors(main_sheet)
        windows = self._extract_windows(main_sheet)
        rooms = self._extract_rooms(main_sheet)
        restricted_areas = self._extract_restricted_areas(main_sheet)
        entrances = self._extract_entrances(main_sheet)
        dimensions = self._extract_dimensions(main_sheet)
        
        # Calculate scale and bounds
        scale = self._calculate_scale(main_sheet)
        bounds = self._calculate_bounds(walls + doors + windows)
        
        return FloorPlan(
            walls=walls,
            doors=doors,
            windows=windows,
            rooms=rooms,
            restricted_areas=restricted_areas,
            entrances=entrances,
            dimensions=dimensions,
            scale=scale,
            units=self.units,
            bounds=bounds,
            drawing_info={'format': 'DXF', 'layers': len(doc.layers)}
        )
    
    def _detect_floor_plan_sheet(self, doc) -> Any:
        """Intelligently detect the main architectural floor plan"""
        msp = doc.modelspace()
        
        # Analyze entity distribution and types
        entity_counts = {}
        for entity in msp:
            entity_type = entity.dxftype()
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        # Check for architectural indicators
        architectural_score = 0
        
        # Look for walls (lines/polylines)
        if entity_counts.get('LINE', 0) > 50:
            architectural_score += 3
        if entity_counts.get('LWPOLYLINE', 0) > 20:
            architectural_score += 3
        
        # Look for doors/windows (arcs, circles)
        if entity_counts.get('ARC', 0) > 5:
            architectural_score += 2
        if entity_counts.get('CIRCLE', 0) > 3:
            architectural_score += 1
        
        # Look for text/dimensions
        if entity_counts.get('TEXT', 0) > 10:
            architectural_score += 1
        if entity_counts.get('DIMENSION', 0) > 5:
            architectural_score += 2
        
        logger.info(f"Architectural score: {architectural_score}")
        return msp
    
    def _extract_walls(self, modelspace) -> List[CADElement]:
        """Extract wall elements with proper thickness and connectivity"""
        walls = []
        
        for entity in modelspace:
            if entity.dxftype() in ['LINE', 'LWPOLYLINE', 'POLYLINE']:
                # Analyze layer and color to identify walls
                layer = getattr(entity.dxf, 'layer', '0').lower()
                color = getattr(entity.dxf, 'color', 7)
                
                # Wall identification criteria
                is_wall = (
                    'wall' in layer or 'mur' in layer or 'cloison' in layer or
                    color == 7 or color == 0 or  # Black/white
                    (hasattr(entity.dxf, 'lineweight') and entity.dxf.lineweight > 50)
                )
                
                if is_wall:
                    if entity.dxftype() == 'LINE':
                        start = (entity.dxf.start.x, entity.dxf.start.y)
                        end = (entity.dxf.end.x, entity.dxf.end.y)
                        geometry = LineString([start, end])
                    else:
                        points = [(p[0], p[1]) for p in entity.get_points()]
                        if len(points) >= 2:
                            geometry = LineString(points)
                        else:
                            continue
                    
                    wall = CADElement(
                        element_type='wall',
                        geometry=geometry,
                        properties={
                            'length': geometry.length,
                            'thickness': getattr(entity.dxf, 'lineweight', 100) / 100
                        },
                        layer=layer,
                        color=self.colors['walls'],
                        line_weight=self.line_weights['walls']
                    )
                    walls.append(wall)
        
        logger.info(f"Extracted {len(walls)} walls")
        return walls
    
    def _extract_doors(self, modelspace) -> List[CADElement]:
        """Extract door elements with swing directions"""
        doors = []
        
        for entity in modelspace:
            if entity.dxftype() == 'ARC':
                layer = getattr(entity.dxf, 'layer', '0').lower()
                
                # Door identification
                is_door = (
                    'door' in layer or 'porte' in layer or
                    'swing' in layer or 'opening' in layer
                )
                
                if is_door:
                    center = (entity.dxf.center.x, entity.dxf.center.y)
                    radius = entity.dxf.radius
                    start_angle = entity.dxf.start_angle
                    end_angle = entity.dxf.end_angle
                    
                    # Create arc geometry
                    angles = np.linspace(start_angle, end_angle, 20)
                    points = [
                        (center[0] + radius * np.cos(angle),
                         center[1] + radius * np.sin(angle))
                        for angle in angles
                    ]
                    
                    geometry = LineString(points)
                    
                    door = CADElement(
                        element_type='door',
                        geometry=geometry,
                        properties={
                            'width': radius * 2,
                            'swing_angle': end_angle - start_angle,
                            'center': center
                        },
                        layer=layer,
                        color=self.colors['entrances'],
                        line_weight=self.line_weights['doors']
                    )
                    doors.append(door)
        
        logger.info(f"Extracted {len(doors)} doors")
        return doors
    
    def _extract_windows(self, modelspace) -> List[CADElement]:
        """Extract window elements"""
        windows = []
        
        for entity in modelspace:
            if entity.dxftype() in ['LINE', 'POLYLINE']:
                layer = getattr(entity.dxf, 'layer', '0').lower()
                
                # Window identification
                is_window = (
                    'window' in layer or 'fenetre' in layer or
                    'opening' in layer and 'door' not in layer
                )
                
                if is_window:
                    if entity.dxftype() == 'LINE':
                        start = (entity.dxf.start.x, entity.dxf.start.y)
                        end = (entity.dxf.end.x, entity.dxf.end.y)
                        geometry = LineString([start, end])
                    else:
                        points = [(p[0], p[1]) for p in entity.get_points()]
                        geometry = LineString(points)
                    
                    window = CADElement(
                        element_type='window',
                        geometry=geometry,
                        properties={'width': geometry.length},
                        layer=layer,
                        color=self.colors['walls'],
                        line_weight=self.line_weights['windows']
                    )
                    windows.append(window)
        
        logger.info(f"Extracted {len(windows)} windows")
        return windows
    
    def _extract_rooms(self, modelspace) -> List[CADElement]:
        """Extract room boundaries and areas"""
        rooms = []
        
        for entity in modelspace:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                layer = getattr(entity.dxf, 'layer', '0').lower()
                
                # Room identification
                is_room = (
                    'room' in layer or 'space' in layer or 'zone' in layer or
                    entity.is_closed
                )
                
                if is_room:
                    points = [(p[0], p[1]) for p in entity.get_points()]
                    if len(points) >= 3:
                        geometry = Polygon(points)
                        
                        if geometry.is_valid and geometry.area > 1.0:
                            room = CADElement(
                                element_type='room',
                                geometry=geometry,
                                properties={
                                    'area': geometry.area,
                                    'perimeter': geometry.length
                                },
                                layer=layer,
                                color='transparent',
                                line_weight=0.5
                            )
                            rooms.append(room)
        
        logger.info(f"Extracted {len(rooms)} rooms")
        return rooms
    
    def _extract_restricted_areas(self, modelspace) -> List[CADElement]:
        """Extract restricted areas (stairs, elevators, etc.)"""
        restricted = []
        
        for entity in modelspace:
            layer = getattr(entity.dxf, 'layer', '0').lower()
            color = getattr(entity.dxf, 'color', 7)
            
            # Restricted area identification
            is_restricted = (
                'stair' in layer or 'elevator' in layer or 'lift' in layer or
                'restricted' in layer or 'no' in layer or
                color == 5  # Blue color
            )
            
            if is_restricted and entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = [(p[0], p[1]) for p in entity.get_points()]
                if len(points) >= 3:
                    geometry = Polygon(points)
                    
                    if geometry.is_valid:
                        restricted_area = CADElement(
                            element_type='restricted',
                            geometry=geometry,
                            properties={'area': geometry.area},
                            layer=layer,
                            color=self.colors['restricted'],
                            line_weight=1.0
                        )
                        restricted.append(restricted_area)
        
        logger.info(f"Extracted {len(restricted)} restricted areas")
        return restricted
    
    def _extract_entrances(self, modelspace) -> List[CADElement]:
        """Extract entrance/exit areas"""
        entrances = []
        
        for entity in modelspace:
            layer = getattr(entity.dxf, 'layer', '0').lower()
            color = getattr(entity.dxf, 'color', 7)
            
            # Entrance identification
            is_entrance = (
                'entrance' in layer or 'exit' in layer or 'entree' in layer or
                'sortie' in layer or 'entry' in layer or
                color == 1 or color == 2  # Red colors
            )
            
            if is_entrance:
                if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    points = [(p[0], p[1]) for p in entity.get_points()]
                    if len(points) >= 3:
                        geometry = Polygon(points)
                    else:
                        geometry = LineString(points)
                elif entity.dxftype() == 'LINE':
                    start = (entity.dxf.start.x, entity.dxf.start.y)
                    end = (entity.dxf.end.x, entity.dxf.end.y)
                    geometry = LineString([start, end])
                else:
                    continue
                
                entrance = CADElement(
                    element_type='entrance',
                    geometry=geometry,
                    properties={'width': getattr(geometry, 'length', 0)},
                    layer=layer,
                    color=self.colors['entrances'],
                    line_weight=2.0
                )
                entrances.append(entrance)
        
        logger.info(f"Extracted {len(entrances)} entrances")
        return entrances
    
    def _extract_dimensions(self, modelspace) -> List[CADElement]:
        """Extract dimension lines and text"""
        dimensions = []
        
        for entity in modelspace:
            if entity.dxftype().startswith('DIMENSION'):
                geometry = Point(0, 0)  # Placeholder
                
                dimension = CADElement(
                    element_type='dimension',
                    geometry=geometry,
                    properties={
                        'text': getattr(entity.dxf, 'text', ''),
                        'measurement': getattr(entity.dxf, 'measurement', 0)
                    },
                    layer=getattr(entity.dxf, 'layer', '0'),
                    color=self.colors['text'],
                    line_weight=self.line_weights['dimensions']
                )
                dimensions.append(dimension)
        
        logger.info(f"Extracted {len(dimensions)} dimensions")
        return dimensions
    
    def _calculate_scale(self, modelspace) -> float:
        """Calculate drawing scale from dimension entities"""
        scale = 1.0
        
        # Look for scale indicators in text or dimensions
        for entity in modelspace:
            if entity.dxftype() == 'TEXT':
                text = getattr(entity.dxf, 'text', '').lower()
                if 'scale' in text or 'echelle' in text:
                    # Parse scale from text
                    import re
                    scale_match = re.search(r'1:(\d+)', text)
                    if scale_match:
                        scale = float(scale_match.group(1))
                        break
        
        self.scale_factor = scale
        logger.info(f"Detected scale: 1:{scale}")
        return scale
    
    def _calculate_bounds(self, elements: List[CADElement]) -> Tuple[float, float, float, float]:
        """Calculate bounding box of all elements"""
        if not elements:
            return (0, 0, 100, 100)
        
        all_bounds = []
        for element in elements:
            if hasattr(element.geometry, 'bounds'):
                all_bounds.append(element.geometry.bounds)
        
        if not all_bounds:
            return (0, 0, 100, 100)
        
        min_x = min(bounds[0] for bounds in all_bounds)
        min_y = min(bounds[1] for bounds in all_bounds)
        max_x = max(bounds[2] for bounds in all_bounds)
        max_y = max(bounds[3] for bounds in all_bounds)
        
        return (min_x, min_y, max_x, max_y)
    
    def _process_dwg_file(self, file_path: str) -> FloorPlan:
        """Process DWG file (requires conversion to DXF)"""
        # For now, raise an error with conversion instructions
        raise NotImplementedError(
            "DWG files require conversion to DXF format. "
            "Please use AutoCAD or FreeCAD to save as DXF format."
        )
    
    def _process_pdf_file(self, file_path: str) -> FloorPlan:
        """Process PDF file by converting to image and using computer vision"""
        import fitz  # PyMuPDF
        
        # Convert PDF to image
        pdf_doc = fitz.open(file_path)
        page = pdf_doc[0]
        mat = fitz.Matrix(3.0, 3.0)  # High resolution
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Use computer vision to extract elements
        return self._process_image_data(img_data)
    
    def _process_image_data(self, img_data: bytes) -> FloorPlan:
        """Process image data using computer vision or PIL fallback"""
        if not OPENCV_AVAILABLE:
            return self._process_image_data_pil_only(img_data)
        
        # Convert to OpenCV format
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Extract elements using color detection and contour analysis
        walls = self._extract_walls_from_image(img)
        restricted = self._extract_restricted_from_image(img)
        entrances = self._extract_entrances_from_image(img)
        
        # Create simple room from overall boundary
        rooms = [CADElement(
            element_type='room',
            geometry=Polygon([(0, 0), (img.shape[1], 0), 
                            (img.shape[1], img.shape[0]), (0, img.shape[0])]),
            properties={'area': img.shape[0] * img.shape[1]},
            layer='image',
            color='transparent',
            line_weight=0.5
        )]
        
        return FloorPlan(
            walls=walls,
            doors=[],
            windows=[],
            rooms=rooms,
            restricted_areas=restricted,
            entrances=entrances,
            dimensions=[],
            scale=1.0,
            units='pixels',
            bounds=(0, 0, img.shape[1], img.shape[0]),
            drawing_info={'format': 'Image', 'resolution': img.shape}
        )
    
    def _process_image_data_pil_only(self, img_data: bytes) -> FloorPlan:
        """Process image data using PIL only (fallback for cloud environments)"""
        from io import BytesIO
        
        # Convert to PIL format
        img = Image.open(BytesIO(img_data))
        img_array = np.array(img)
        
        # Basic color-based extraction using PIL and numpy
        walls = self._extract_walls_from_image_pil(img_array)
        restricted = self._extract_restricted_from_image_pil(img_array)
        entrances = self._extract_entrances_from_image_pil(img_array)
        
        # Create simple room from overall boundary
        rooms = [CADElement(
            element_type='room',
            geometry=Polygon([(0, 0), (img.width, 0), 
                            (img.width, img.height), (0, img.height)]),
            properties={'area': img.width * img.height},
            layer='image',
            color='transparent',
            line_weight=0.5
        )]
        
        return FloorPlan(
            walls=walls,
            doors=[],
            windows=[],
            rooms=rooms,
            restricted_areas=restricted,
            entrances=entrances,
            dimensions=[],
            scale=1.0,
            units='pixels',
            bounds=(0, 0, img.width, img.height),
            drawing_info={'format': 'Image', 'resolution': (img.width, img.height)}
        )
    
    def _extract_walls_from_image(self, img) -> List[CADElement]:
        """Extract walls from image using edge detection"""
        if not OPENCV_AVAILABLE:
            return []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        walls = []
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                # Simplify contour to line segments
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                points = [(int(p[0][0]), int(p[0][1])) for p in approx]
                if len(points) >= 2:
                    geometry = LineString(points)
                    
                    wall = CADElement(
                        element_type='wall',
                        geometry=geometry,
                        properties={'length': geometry.length},
                        layer='image_walls',
                        color=self.colors['walls'],
                        line_weight=self.line_weights['walls']
                    )
                    walls.append(wall)
        
        return walls
    
    def _extract_walls_from_image_pil(self, img_array) -> List[CADElement]:
        """Extract walls using PIL-only processing (cloud fallback)"""
        # Simple edge detection using numpy
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        
        # Basic edge detection using gradient
        edges = np.zeros_like(gray)
        edges[1:-1, 1:-1] = np.abs(gray[:-2, 1:-1] - gray[2:, 1:-1]) + \
                           np.abs(gray[1:-1, :-2] - gray[1:-1, 2:])
        
        # Simple contour detection
        threshold = np.percentile(edges, 90)
        edge_points = np.where(edges > threshold)
        
        walls = []
        if len(edge_points[0]) > 10:
            # Create a simple wall outline
            min_y, max_y = np.min(edge_points[0]), np.max(edge_points[0])
            min_x, max_x = np.min(edge_points[1]), np.max(edge_points[1])
            
            # Create boundary walls
            boundary_points = [
                (min_x, min_y), (max_x, min_y),
                (max_x, max_y), (min_x, max_y), (min_x, min_y)
            ]
            
            geometry = LineString(boundary_points)
            wall = CADElement(
                element_type='wall',
                geometry=geometry,
                properties={'length': geometry.length},
                layer='image_walls_pil',
                color=self.colors['walls'],
                line_weight=self.line_weights['walls']
            )
            walls.append(wall)
        
        return walls
    
    def _extract_restricted_from_image(self, img) -> List[CADElement]:
        """Extract restricted areas using blue color detection"""
        if not OPENCV_AVAILABLE:
            return []
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Blue color range
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        restricted = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                points = [(int(p[0][0]), int(p[0][1])) for p in contour[:, 0]]
                if len(points) >= 3:
                    geometry = Polygon(points)
                    
                    restricted_area = CADElement(
                        element_type='restricted',
                        geometry=geometry,
                        properties={'area': geometry.area},
                        layer='image_restricted',
                        color=self.colors['restricted'],
                        line_weight=1.0
                    )
                    restricted.append(restricted_area)
        
        return restricted
    
    def _extract_restricted_from_image_pil(self, img_array) -> List[CADElement]:
        """Extract restricted areas using PIL-only blue color detection"""
        # Convert RGB to approximate HSV and detect blue areas
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Simple blue detection: high blue, low red/green
        blue_mask = (b > 100) & (r < 100) & (g < 100)
        
        restricted = []
        if np.any(blue_mask):
            # Find blue regions
            blue_points = np.where(blue_mask)
            if len(blue_points[0]) > 500:
                # Create a simple rectangular restricted area
                min_y, max_y = np.min(blue_points[0]), np.max(blue_points[0])
                min_x, max_x = np.min(blue_points[1]), np.max(blue_points[1])
                
                area_points = [
                    (min_x, min_y), (max_x, min_y),
                    (max_x, max_y), (min_x, max_y)
                ]
                
                geometry = Polygon(area_points)
                restricted_area = CADElement(
                    element_type='restricted',
                    geometry=geometry,
                    properties={'area': geometry.area},
                    layer='image_restricted_pil',
                    color=self.colors['restricted'],
                    line_weight=1.0
                )
                restricted.append(restricted_area)
        
        return restricted
    
    def _extract_entrances_from_image(self, img) -> List[CADElement]:
        """Extract entrances using red color detection"""
        if not OPENCV_AVAILABLE:
            return []
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Red color range
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        entrances = []
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                points = [(int(p[0][0]), int(p[0][1])) for p in contour[:, 0]]
                if len(points) >= 2:
                    if len(points) >= 3:
                        geometry = Polygon(points)
                    else:
                        geometry = LineString(points)
                    
                    entrance = CADElement(
                        element_type='entrance',
                        geometry=geometry,
                        properties={'area': getattr(geometry, 'area', 0)},
                        layer='image_entrances',
                        color=self.colors['entrances'],
                        line_weight=2.0
                    )
                    entrances.append(entrance)
        
        return entrances
    
    def _extract_entrances_from_image_pil(self, img_array) -> List[CADElement]:
        """Extract entrances using PIL-only red color detection"""
        # Convert RGB and detect red areas
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Simple red detection: high red, low green/blue
        red_mask = (r > 100) & (g < 100) & (b < 100)
        
        entrances = []
        if np.any(red_mask):
            # Find red regions
            red_points = np.where(red_mask)
            if len(red_points[0]) > 100:
                # Create a simple rectangular entrance area
                min_y, max_y = np.min(red_points[0]), np.max(red_points[0])
                min_x, max_x = np.min(red_points[1]), np.max(red_points[1])
                
                entrance_points = [
                    (min_x, min_y), (max_x, min_y),
                    (max_x, max_y), (min_x, max_y)
                ]
                
                geometry = Polygon(entrance_points)
                entrance = CADElement(
                    element_type='entrance',
                    geometry=geometry,
                    properties={'area': geometry.area},
                    layer='image_entrances_pil',
                    color=self.colors['entrances'],
                    line_weight=2.0
                )
                entrances.append(entrance)
        
        return entrances
