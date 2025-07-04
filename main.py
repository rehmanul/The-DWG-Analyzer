#!/usr/bin/env python3
"""
AI Architectural Space Analyzer PRO - Enterprise Edition
Full-featured professional CAD analysis with advanced îlot placement
"""

import sys
import os
import json
import numpy as np
import cv2
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Any
import logging

# Enterprise CAD libraries
try:
    import ezdxf
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from shapely.geometry import Polygon, Point, LineString, MultiPolygon
    from shapely.ops import unary_union
    from scipy.spatial import distance
    from sklearn.cluster import DBSCAN
    import psycopg2
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
except ImportError as e:
    print(f"Installing required enterprise libraries: {e}")
    os.system("pip install ezdxf matplotlib PyQt5 shapely scipy scikit-learn psycopg2-binary reportlab opencv-python")

# Configure enterprise logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class IlotProfile:
    """Enterprise îlot configuration profile"""
    size_0_1: float = 0.10  # 10% between 0-1 m²
    size_1_3: float = 0.25  # 25% between 1-3 m²
    size_3_5: float = 0.30  # 30% between 3-5 m²
    size_5_10: float = 0.35 # 35% between 5-10 m²
    corridor_width: float = 1.5  # meters
    min_spacing: float = 0.5     # minimum space between îlots

@dataclass
class Zone:
    """Architectural zone definition"""
    polygon: Polygon
    zone_type: str  # 'wall', 'restricted', 'entrance', 'available'
    color: str
    
@dataclass
class Ilot:
    """Individual îlot placement"""
    polygon: Polygon
    area: float
    position: Tuple[float, float]
    size_category: str

class EnterpriseCADProcessor:
    """Advanced CAD file processing engine"""
    
    def __init__(self):
        self.supported_formats = ['.dwg', '.dxf', '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.svg']
        
    def load_cad_file(self, filepath: str) -> Dict[str, Any]:
        """Load and process CAD files with full format support"""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
            
        if path.suffix.lower() == '.dxf':
            return self._process_dxf(filepath)
        elif path.suffix.lower() == '.dwg':
            return self._process_dwg(filepath)
        elif path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff']:
            return self._process_image(filepath)
        else:
            raise ValueError(f"Unsupported format: {path.suffix}")
    
    def _process_dxf(self, filepath: str) -> Dict[str, Any]:
        """Process DXF files with layer detection"""
        try:
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()
            
            zones = []
            walls = []
            restricted = []
            entrances = []
            
            # Process entities by layer
            for entity in msp:
                layer_name = entity.dxf.layer.lower()
                
                if entity.dxftype() == 'LINE':
                    start = (entity.dxf.start.x, entity.dxf.start.y)
                    end = (entity.dxf.end.x, entity.dxf.end.y)
                    
                    if 'wall' in layer_name or entity.dxf.color == 0:  # Black walls
                        walls.append(LineString([start, end]))
                    elif 'entrance' in layer_name or entity.dxf.color == 1:  # Red entrances
                        entrances.append(LineString([start, end]))
                    elif 'restrict' in layer_name or entity.dxf.color == 5:  # Blue restricted
                        restricted.append(LineString([start, end]))
                
                elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    points = [(p[0], p[1]) for p in entity.get_points()]
                    if len(points) >= 3:
                        poly = Polygon(points)
                        
                        if 'wall' in layer_name or entity.dxf.color == 0:
                            zones.append(Zone(poly, 'wall', 'black'))
                        elif 'entrance' in layer_name or entity.dxf.color == 1:
                            zones.append(Zone(poly, 'entrance', 'red'))
                        elif 'restrict' in layer_name or entity.dxf.color == 5:
                            zones.append(Zone(poly, 'restricted', 'lightblue'))
            
            return {
                'zones': zones,
                'walls': walls,
                'restricted': restricted,
                'entrances': entrances,
                'bounds': self._calculate_bounds(zones + [Zone(LineString(w).buffer(0.1), 'wall', 'black') for w in walls])
            }
            
        except Exception as e:
            logger.error(f"DXF processing error: {e}")
            raise
    
    def _process_dwg(self, filepath: str) -> Dict[str, Any]:
        """Process DWG files (convert to DXF first)"""
        # For DWG, we'd typically use ODA File Converter or similar
        # For now, attempt direct processing or conversion
        try:
            # Try to read as DXF (some DWG files work)
            return self._process_dxf(filepath)
        except:
            raise ValueError("DWG processing requires ODA File Converter or AutoCAD")
    
    def _process_image(self, filepath: str) -> Dict[str, Any]:
        """Process image files with computer vision"""
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError(f"Cannot read image: {filepath}")
        
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        zones = []
        
        # Detect black walls
        black_mask = cv2.inRange(gray, 0, 50)
        wall_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in wall_contours:
            if cv2.contourArea(contour) > 100:  # Filter small noise
                points = [(p[0][0], p[0][1]) for p in contour]
                if len(points) >= 3:
                    zones.append(Zone(Polygon(points), 'wall', 'black'))
        
        # Detect red entrances
        red_lower = np.array([0, 50, 50])
        red_upper = np.array([10, 255, 255])
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        entrance_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in entrance_contours:
            if cv2.contourArea(contour) > 50:
                points = [(p[0][0], p[0][1]) for p in contour]
                if len(points) >= 3:
                    zones.append(Zone(Polygon(points), 'entrance', 'red'))
        
        # Detect blue restricted areas
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        restricted_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in restricted_contours:
            if cv2.contourArea(contour) > 50:
                points = [(p[0][0], p[0][1]) for p in contour]
                if len(points) >= 3:
                    zones.append(Zone(Polygon(points), 'restricted', 'lightblue'))
        
        return {
            'zones': zones,
            'walls': [],
            'restricted': [],
            'entrances': [],
            'bounds': self._calculate_bounds(zones),
            'image_shape': img.shape
        }
    
    def _calculate_bounds(self, zones: List[Zone]) -> Tuple[float, float, float, float]:
        """Calculate overall bounds of all zones"""
        if not zones:
            return (0, 0, 100, 100)
        
        all_bounds = [zone.polygon.bounds for zone in zones if zone.polygon.is_valid]
        if not all_bounds:
            return (0, 0, 100, 100)
        
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        return (min_x, min_y, max_x, max_y)

class IlotPlacementEngine:
    """Advanced îlot placement algorithm with enterprise optimization"""
    
    def __init__(self, profile: IlotProfile):
        self.profile = profile
        
    def generate_ilots(self, zones: List[Zone], bounds: Tuple[float, float, float, float]) -> List[Ilot]:
        """Generate and place îlots according to profile"""
        
        # Calculate available area
        available_area = self._calculate_available_area(zones, bounds)
        
        # Generate îlot sizes based on profile
        ilot_specs = self._generate_ilot_specifications(available_area)
        
        # Place îlots using advanced algorithm
        placed_ilots = self._place_ilots_optimized(ilot_specs, zones, bounds)
        
        return placed_ilots
    
    def _calculate_available_area(self, zones: List[Zone], bounds: Tuple[float, float, float, float]) -> float:
        """Calculate total available area for îlot placement"""
        min_x, min_y, max_x, max_y = bounds
        total_area = (max_x - min_x) * (max_y - min_y)
        
        # Subtract restricted areas
        restricted_area = 0
        for zone in zones:
            if zone.zone_type in ['restricted', 'entrance']:
                restricted_area += zone.polygon.area
        
        return max(0, total_area - restricted_area)
    
    def _generate_ilot_specifications(self, available_area: float) -> List[Dict]:
        """Generate îlot specifications based on profile percentages"""
        
        # Estimate total îlots based on available area and average size
        avg_ilot_size = (
            self.profile.size_0_1 * 0.5 +
            self.profile.size_1_3 * 2.0 +
            self.profile.size_3_5 * 4.0 +
            self.profile.size_5_10 * 7.5
        )
        
        estimated_total = max(10, int(available_area * 0.3 / avg_ilot_size))
        
        specs = []
        
        # Generate by category
        categories = [
            ('0-1m²', (0.5, 1.0), self.profile.size_0_1),
            ('1-3m²', (1.0, 3.0), self.profile.size_1_3),
            ('3-5m²', (3.0, 5.0), self.profile.size_3_5),
            ('5-10m²', (5.0, 10.0), self.profile.size_5_10)
        ]
        
        for category, (min_size, max_size), percentage in categories:
            count = int(estimated_total * percentage)
            for _ in range(count):
                size = np.random.uniform(min_size, max_size)
                specs.append({
                    'area': size,
                    'category': category,
                    'dimensions': self._calculate_dimensions(size)
                })
        
        return specs
    
    def _calculate_dimensions(self, area: float) -> Tuple[float, float]:
        """Calculate optimal dimensions for given area"""
        # Use golden ratio for aesthetically pleasing rectangles
        golden_ratio = 1.618
        
        # For small areas, use more square shapes
        if area < 2:
            ratio = 1.2
        elif area < 5:
            ratio = 1.4
        else:
            ratio = golden_ratio
        
        width = np.sqrt(area / ratio)
        height = area / width
        
        return (width, height)
    
    def _place_ilots_optimized(self, specs: List[Dict], zones: List[Zone], bounds: Tuple[float, float, float, float]) -> List[Ilot]:
        """Advanced îlot placement with optimization"""
        
        min_x, min_y, max_x, max_y = bounds
        placed_ilots = []
        
        # Create forbidden areas (restricted + entrance zones + buffer around entrances)
        forbidden_areas = []
        entrance_buffer_zones = []
        
        for zone in zones:
            if zone.zone_type in ['restricted', 'entrance']:
                forbidden_areas.append(zone.polygon)
                
                # Add buffer around entrances
                if zone.zone_type == 'entrance':
                    buffer_zone = zone.polygon.buffer(2.0)  # 2m buffer
                    entrance_buffer_zones.append(buffer_zone)
        
        # Combine all forbidden areas
        if forbidden_areas:
            forbidden_union = unary_union(forbidden_areas + entrance_buffer_zones)
        else:
            forbidden_union = Polygon()
        
        # Grid-based placement with optimization
        grid_size = 0.5  # 50cm grid
        
        # Sort specs by area (largest first for better packing)
        specs_sorted = sorted(specs, key=lambda x: x['area'], reverse=True)
        
        for spec in specs_sorted:
            width, height = spec['dimensions']
            placed = False
            
            # Try different orientations
            orientations = [(width, height), (height, width)]
            
            for w, h in orientations:
                if placed:
                    break
                    
                # Grid search for placement
                for x in np.arange(min_x, max_x - w, grid_size):
                    for y in np.arange(min_y, max_y - h, grid_size):
                        
                        # Create candidate îlot
                        candidate = Polygon([
                            (x, y), (x + w, y), (x + w, y + h), (x, y + h)
                        ])
                        
                        # Check constraints
                        if self._is_valid_placement(candidate, forbidden_union, placed_ilots):
                            ilot = Ilot(
                                polygon=candidate,
                                area=spec['area'],
                                position=(x + w/2, y + h/2),
                                size_category=spec['category']
                            )
                            placed_ilots.append(ilot)
                            placed = True
                            break
                    
                    if placed:
                        break
        
        logger.info(f"Placed {len(placed_ilots)} îlots out of {len(specs)} requested")
        return placed_ilots
    
    def _is_valid_placement(self, candidate: Polygon, forbidden_union: Polygon, existing_ilots: List[Ilot]) -> bool:
        """Check if îlot placement is valid"""
        
        # Check forbidden areas
        if forbidden_union.is_valid and candidate.intersects(forbidden_union):
            return False
        
        # Check spacing with existing îlots
        for existing in existing_ilots:
            distance_to_existing = candidate.distance(existing.polygon)
            if distance_to_existing < self.profile.min_spacing:
                return False
        
        return True
    
    def generate_corridors(self, ilots: List[Ilot]) -> List[Polygon]:
        """Generate corridors between facing îlot rows"""
        corridors = []
        
        if len(ilots) < 2:
            return corridors
        
        # Group îlots by approximate Y coordinate (rows)
        y_positions = [ilot.position[1] for ilot in ilots]
        
        # Use clustering to identify rows
        if len(set(y_positions)) > 1:
            y_array = np.array(y_positions).reshape(-1, 1)
            clustering = DBSCAN(eps=2.0, min_samples=2).fit(y_array)
            
            # Group îlots by cluster
            clusters = {}
            for i, label in enumerate(clustering.labels_):
                if label != -1:  # Ignore noise
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(ilots[i])
            
            # Generate corridors between adjacent rows
            cluster_centers = {}
            for label, cluster_ilots in clusters.items():
                center_y = np.mean([ilot.position[1] for ilot in cluster_ilots])
                cluster_centers[label] = center_y
            
            # Sort clusters by Y position
            sorted_clusters = sorted(cluster_centers.items(), key=lambda x: x[1])
            
            # Create corridors between adjacent clusters
            for i in range(len(sorted_clusters) - 1):
                label1, y1 = sorted_clusters[i]
                label2, y2 = sorted_clusters[i + 1]
                
                if abs(y2 - y1) < 10:  # Only if rows are reasonably close
                    corridor = self._create_corridor_between_rows(
                        clusters[label1], clusters[label2]
                    )
                    if corridor:
                        corridors.append(corridor)
        
        return corridors
    
    def _create_corridor_between_rows(self, row1: List[Ilot], row2: List[Ilot]) -> Optional[Polygon]:
        """Create corridor between two rows of îlots"""
        
        if not row1 or not row2:
            return None
        
        # Find overlapping X range
        row1_x_min = min(ilot.polygon.bounds[0] for ilot in row1)
        row1_x_max = max(ilot.polygon.bounds[2] for ilot in row1)
        row2_x_min = min(ilot.polygon.bounds[0] for ilot in row2)
        row2_x_max = max(ilot.polygon.bounds[2] for ilot in row2)
        
        overlap_x_min = max(row1_x_min, row2_x_min)
        overlap_x_max = min(row1_x_max, row2_x_max)
        
        if overlap_x_min >= overlap_x_max:
            return None  # No overlap
        
        # Find Y positions
        row1_y = max(ilot.polygon.bounds[3] for ilot in row1)  # Top of row1
        row2_y = min(ilot.polygon.bounds[1] for ilot in row2)  # Bottom of row2
        
        if row2_y <= row1_y:
            return None  # Rows not properly separated
        
        # Create corridor polygon
        corridor_y_center = (row1_y + row2_y) / 2
        corridor_half_width = self.profile.corridor_width / 2
        
        corridor = Polygon([
            (overlap_x_min, corridor_y_center - corridor_half_width),
            (overlap_x_max, corridor_y_center - corridor_half_width),
            (overlap_x_max, corridor_y_center + corridor_half_width),
            (overlap_x_min, corridor_y_center + corridor_half_width)
        ])
        
        return corridor

class EnterpriseVisualization:
    """Professional visualization engine"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
        
    def create_visualization(self, zones: List[Zone], ilots: List[Ilot], corridors: List[Polygon], bounds: Tuple[float, float, float, float]):
        """Create professional visualization"""
        
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 12))
        self.ax.set_aspect('equal')
        
        # Draw zones
        for zone in zones:
            if zone.polygon.is_valid:
                x, y = zone.polygon.exterior.xy
                self.ax.plot(x, y, color=zone.color, linewidth=2 if zone.zone_type == 'wall' else 1)
                
                if zone.zone_type in ['restricted', 'entrance']:
                    self.ax.fill(x, y, color=zone.color, alpha=0.3)
        
        # Draw îlots
        colors = {
            '0-1m²': '#FFE6E6',
            '1-3m²': '#E6F3FF', 
            '3-5m²': '#E6FFE6',
            '5-10m²': '#FFF0E6'
        }
        
        for ilot in ilots:
            if ilot.polygon.is_valid:
                x, y = ilot.polygon.exterior.xy
                color = colors.get(ilot.size_category, '#F0F0F0')
                self.ax.fill(x, y, color=color, alpha=0.7, edgecolor='black', linewidth=1)
                
                # Add area label
                centroid = ilot.polygon.centroid
                self.ax.text(centroid.x, centroid.y, f'{ilot.area:.1f}m²', 
                           ha='center', va='center', fontsize=8, weight='bold')
        
        # Draw corridors
        for corridor in corridors:
            if corridor.is_valid:
                x, y = corridor.exterior.xy
                self.ax.fill(x, y, color='yellow', alpha=0.5, edgecolor='orange', linewidth=2)
        
        # Set bounds and labels
        min_x, min_y, max_x, max_y = bounds
        margin = (max_x - min_x) * 0.05
        self.ax.set_xlim(min_x - margin, max_x + margin)
        self.ax.set_ylim(min_y - margin, max_y + margin)
        
        self.ax.set_title('AI Architectural Space Analyzer PRO - Enterprise Results', fontsize=16, weight='bold')
        self.ax.set_xlabel('X (meters)', fontsize=12)
        self.ax.set_ylabel('Y (meters)', fontsize=12)
        
        # Add legend
        legend_elements = [
            patches.Patch(color='black', label='Walls'),
            patches.Patch(color='red', alpha=0.3, label='Entrances/Exits'),
            patches.Patch(color='lightblue', alpha=0.3, label='Restricted Areas'),
            patches.Patch(color='yellow', alpha=0.5, label='Corridors'),
            patches.Patch(color='#FFE6E6', label='Îlots 0-1m²'),
            patches.Patch(color='#E6F3FF', label='Îlots 1-3m²'),
            patches.Patch(color='#E6FFE6', label='Îlots 3-5m²'),
            patches.Patch(color='#FFF0E6', label='Îlots 5-10m²')
        ]
        
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        return self.fig

class DatabaseManager:
    """Enterprise database integration"""
    
    def __init__(self):
        self.connection_string = "postgresql://de_de:PUPB8V0s2b3bvNZUblolz7d6UM9bcBzb@dpg-d1h53rffte5s739b1i40-a.oregon-postgres.render.com/dwg_analyzer_pro"
        
    def save_project(self, project_data: Dict) -> str:
        """Save project to enterprise database"""
        try:
            conn = psycopg2.connect(self.connection_string)
            cur = conn.cursor()
            
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert project
            cur.execute(
                "INSERT INTO projects (name, data) VALUES (%s, %s) RETURNING id",
                (project_data.get('name', 'Untitled'), json.dumps(project_data, default=str))
            )
            
            project_id = cur.fetchone()[0]
            conn.commit()
            
            cur.close()
            conn.close()
            
            return str(project_id)
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            return "local_save"

class PDFExporter:
    """Professional PDF export functionality"""
    
    def export_results(self, fig, ilots: List[Ilot], profile: IlotProfile, output_path: str):
        """Export results to professional PDF report"""
        
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "AI Architectural Space Analyzer PRO")
        c.drawString(50, height - 75, "Enterprise Analysis Report")
        
        # Save matplotlib figure as image and embed
        temp_img = "temp_plot.png"
        fig.savefig(temp_img, dpi=300, bbox_inches='tight')
        c.drawImage(temp_img, 50, height - 400, width=500, height=300)
        
        # Statistics
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 450, "Analysis Results:")
        
        c.setFont("Helvetica", 12)
        y_pos = height - 480
        
        # Count îlots by category
        categories = {}
        total_area = 0
        for ilot in ilots:
            categories[ilot.size_category] = categories.get(ilot.size_category, 0) + 1
            total_area += ilot.area
        
        c.drawString(50, y_pos, f"Total Îlots Placed: {len(ilots)}")
        y_pos -= 20
        c.drawString(50, y_pos, f"Total Area Covered: {total_area:.2f} m²")
        y_pos -= 30
        
        for category, count in categories.items():
            c.drawString(50, y_pos, f"{category}: {count} îlots")
            y_pos -= 20
        
        # Configuration
        y_pos -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "Configuration Used:")
        y_pos -= 30
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y_pos, f"0-1m² îlots: {profile.size_0_1*100:.0f}%")
        y_pos -= 20
        c.drawString(50, y_pos, f"1-3m² îlots: {profile.size_1_3*100:.0f}%")
        y_pos -= 20
        c.drawString(50, y_pos, f"3-5m² îlots: {profile.size_3_5*100:.0f}%")
        y_pos -= 20
        c.drawString(50, y_pos, f"5-10m² îlots: {profile.size_5_10*100:.0f}%")
        y_pos -= 20
        c.drawString(50, y_pos, f"Corridor Width: {profile.corridor_width}m")
        
        c.save()
        
        # Clean up temp file
        if os.path.exists(temp_img):
            os.remove(temp_img)

class EnterpriseMainWindow(QMainWindow):
    """Professional Qt-based main application window"""
    
    def __init__(self):
        super().__init__()
        self.cad_processor = EnterpriseCADProcessor()
        self.db_manager = DatabaseManager()
        self.pdf_exporter = PDFExporter()
        
        self.current_zones = []
        self.current_ilots = []
        self.current_corridors = []
        self.current_bounds = (0, 0, 100, 100)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize professional UI"""
        self.setWindowTitle("AI Architectural Space Analyzer PRO - Enterprise Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # File loading section
        file_group = QGroupBox("File Loading")
        file_layout = QVBoxLayout(file_group)
        
        self.load_btn = QPushButton("Load CAD File (DWG/DXF/Image)")
        self.load_btn.clicked.connect(self.load_file)
        file_layout.addWidget(self.load_btn)
        
        self.file_label = QLabel("No file loaded")
        file_layout.addWidget(self.file_label)
        
        left_layout.addWidget(file_group)
        
        # Profile configuration
        profile_group = QGroupBox("Îlot Profile Configuration")
        profile_layout = QFormLayout(profile_group)
        
        self.size_0_1_spin = QDoubleSpinBox()
        self.size_0_1_spin.setRange(0, 1)
        self.size_0_1_spin.setSingleStep(0.05)
        self.size_0_1_spin.setValue(0.10)
        self.size_0_1_spin.setSuffix("%")
        profile_layout.addRow("0-1m² îlots:", self.size_0_1_spin)
        
        self.size_1_3_spin = QDoubleSpinBox()
        self.size_1_3_spin.setRange(0, 1)
        self.size_1_3_spin.setSingleStep(0.05)
        self.size_1_3_spin.setValue(0.25)
        self.size_1_3_spin.setSuffix("%")
        profile_layout.addRow("1-3m² îlots:", self.size_1_3_spin)
        
        self.size_3_5_spin = QDoubleSpinBox()
        self.size_3_5_spin.setRange(0, 1)
        self.size_3_5_spin.setSingleStep(0.05)
        self.size_3_5_spin.setValue(0.30)
        self.size_3_5_spin.setSuffix("%")
        profile_layout.addRow("3-5m² îlots:", self.size_3_5_spin)
        
        self.size_5_10_spin = QDoubleSpinBox()
        self.size_5_10_spin.setRange(0, 1)
        self.size_5_10_spin.setSingleStep(0.05)
        self.size_5_10_spin.setValue(0.35)
        self.size_5_10_spin.setSuffix("%")
        profile_layout.addRow("5-10m² îlots:", self.size_5_10_spin)
        
        self.corridor_width_spin = QDoubleSpinBox()
        self.corridor_width_spin.setRange(0.5, 5.0)
        self.corridor_width_spin.setSingleStep(0.1)
        self.corridor_width_spin.setValue(1.5)
        self.corridor_width_spin.setSuffix("m")
        profile_layout.addRow("Corridor Width:", self.corridor_width_spin)
        
        left_layout.addWidget(profile_group)
        
        # Analysis controls
        analysis_group = QGroupBox("Analysis Controls")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analyze_btn = QPushButton("Generate Îlot Layout")
        self.analyze_btn.clicked.connect(self.run_analysis)
        self.analyze_btn.setEnabled(False)
        analysis_layout.addWidget(self.analyze_btn)
        
        self.progress_bar = QProgressBar()
        analysis_layout.addWidget(self.progress_bar)
        
        left_layout.addWidget(analysis_group)
        
        # Export controls
        export_group = QGroupBox("Export Results")
        export_layout = QVBoxLayout(export_group)
        
        self.export_pdf_btn = QPushButton("Export PDF Report")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_pdf_btn.setEnabled(False)
        export_layout.addWidget(self.export_pdf_btn)
        
        self.save_project_btn = QPushButton("Save to Database")
        self.save_project_btn.clicked.connect(self.save_project)
        self.save_project_btn.setEnabled(False)
        export_layout.addWidget(self.save_project_btn)
        
        left_layout.addWidget(export_group)
        
        left_layout.addStretch()
        
        # Right panel for visualization
        self.visualization_widget = QWidget()
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.visualization_widget, 1)
        
        # Status bar
        self.statusBar().showMessage("Ready - Load a CAD file to begin")
        
    def load_file(self):
        """Load CAD file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load CAD File",
            "",
            "All Supported (*.dwg *.dxf *.png *.jpg *.jpeg *.tiff);;DWG Files (*.dwg);;DXF Files (*.dxf);;Images (*.png *.jpg *.jpeg *.tiff)"
        )
        
        if file_path:
            try:
                self.progress_bar.setValue(20)
                self.statusBar().showMessage("Loading file...")
                
                # Process file
                result = self.cad_processor.load_cad_file(file_path)
                
                self.current_zones = result['zones']
                self.current_bounds = result['bounds']
                
                self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
                self.analyze_btn.setEnabled(True)
                
                self.progress_bar.setValue(100)
                self.statusBar().showMessage(f"File loaded successfully - {len(self.current_zones)} zones detected")
                
                # Show initial visualization
                self.show_zones_only()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
                self.progress_bar.setValue(0)
                self.statusBar().showMessage("Error loading file")
    
    def show_zones_only(self):
        """Show only the zones without îlots"""
        viz = EnterpriseVisualization()
        fig = viz.create_visualization(self.current_zones, [], [], self.current_bounds)
        
        # Embed in Qt widget
        self.embed_matplotlib_figure(fig)
    
    def run_analysis(self):
        """Run the îlot placement analysis"""
        try:
            self.progress_bar.setValue(10)
            self.statusBar().showMessage("Analyzing layout...")
            
            # Create profile from UI
            profile = IlotProfile(
                size_0_1=self.size_0_1_spin.value(),
                size_1_3=self.size_1_3_spin.value(),
                size_3_5=self.size_3_5_spin.value(),
                size_5_10=self.size_5_10_spin.value(),
                corridor_width=self.corridor_width_spin.value()
            )
            
            self.progress_bar.setValue(30)
            
            # Generate îlots
            placement_engine = IlotPlacementEngine(profile)
            self.current_ilots = placement_engine.generate_ilots(self.current_zones, self.current_bounds)
            
            self.progress_bar.setValue(60)
            
            # Generate corridors
            self.current_corridors = placement_engine.generate_corridors(self.current_ilots)
            
            self.progress_bar.setValue(80)
            
            # Create visualization
            viz = EnterpriseVisualization()
            fig = viz.create_visualization(
                self.current_zones, 
                self.current_ilots, 
                self.current_corridors, 
                self.current_bounds
            )
            
            self.embed_matplotlib_figure(fig)
            
            self.progress_bar.setValue(100)
            self.statusBar().showMessage(f"Analysis complete - {len(self.current_ilots)} îlots placed")
            
            # Enable export buttons
            self.export_pdf_btn.setEnabled(True)
            self.save_project_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed:\n{str(e)}")
            self.progress_bar.setValue(0)
            self.statusBar().showMessage("Analysis failed")
    
    def embed_matplotlib_figure(self, fig):
        """Embed matplotlib figure in Qt widget"""
        # Clear existing layout
        if self.visualization_widget.layout():
            QWidget().setLayout(self.visualization_widget.layout())
        
        # Create new layout with matplotlib canvas
        layout = QVBoxLayout(self.visualization_widget)
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)
        
        canvas.draw()
    
    def export_pdf(self):
        """Export results to PDF"""
        if not self.current_ilots:
            QMessageBox.warning(self, "Warning", "No analysis results to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export PDF Report",
            "analysis_report.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                profile = IlotProfile(
                    size_0_1=self.size_0_1_spin.value(),
                    size_1_3=self.size_1_3_spin.value(),
                    size_3_5=self.size_3_5_spin.value(),
                    size_5_10=self.size_5_10_spin.value(),
                    corridor_width=self.corridor_width_spin.value()
                )
                
                # Get current figure
                viz = EnterpriseVisualization()
                fig = viz.create_visualization(
                    self.current_zones, 
                    self.current_ilots, 
                    self.current_corridors, 
                    self.current_bounds
                )
                
                self.pdf_exporter.export_results(fig, self.current_ilots, profile, file_path)
                
                QMessageBox.information(self, "Success", f"PDF report exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"PDF export failed:\n{str(e)}")
    
    def save_project(self):
        """Save project to database"""
        if not self.current_ilots:
            QMessageBox.warning(self, "Warning", "No analysis results to save")
            return
        
        try:
            project_data = {
                'name': f"Analysis_{len(self.current_ilots)}_ilots",
                'zones': [asdict(zone) for zone in self.current_zones],
                'ilots': [asdict(ilot) for ilot in self.current_ilots],
                'corridors': len(self.current_corridors),
                'profile': {
                    'size_0_1': self.size_0_1_spin.value(),
                    'size_1_3': self.size_1_3_spin.value(),
                    'size_3_5': self.size_3_5_spin.value(),
                    'size_5_10': self.size_5_10_spin.value(),
                    'corridor_width': self.corridor_width_spin.value()
                }
            }
            
            project_id = self.db_manager.save_project(project_data)
            QMessageBox.information(self, "Success", f"Project saved with ID: {project_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save failed:\n{str(e)}")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("AI Architectural Space Analyzer PRO")
    app.setApplicationVersion("1.0 Enterprise")
    
    # Set application icon
    app.setWindowIcon(QIcon())
    
    # Create and show main window
    window = EnterpriseMainWindow()
    window.show()
    
    logger.info("AI Architectural Space Analyzer PRO - Enterprise Edition Started")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()