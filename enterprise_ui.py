"""
Enterprise UI Components for Professional CAD Analysis
Advanced Qt5 interface with professional styling and features
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional
import json

class ProfessionalStyle:
    """Professional styling for enterprise application"""
    
    @staticmethod
    def get_stylesheet() -> str:
        return """
        QMainWindow {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #2c3e50;
        }
        
        QPushButton {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            font-size: 14px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #21618c;
        }
        
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        QDoubleSpinBox, QSpinBox {
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            padding: 5px;
            background-color: white;
        }
        
        QDoubleSpinBox:focus, QSpinBox:focus {
            border-color: #3498db;
        }
        
        QProgressBar {
            border: 2px solid #bdc3c7;
            border-radius: 4px;
            text-align: center;
            background-color: #ecf0f1;
        }
        
        QProgressBar::chunk {
            background-color: #27ae60;
            border-radius: 2px;
        }
        
        QLabel {
            color: #2c3e50;
        }
        
        QStatusBar {
            background-color: #34495e;
            color: white;
            font-weight: bold;
        }
        
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            border: none;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #34495e;
        }
        
        QMenu {
            background-color: white;
            border: 1px solid #bdc3c7;
        }
        
        QMenu::item:selected {
            background-color: #3498db;
            color: white;
        }
        
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #ecf0f1;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #3498db;
            color: white;
        }
        """

class AdvancedParameterPanel(QWidget):
    """Advanced parameter configuration panel"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Basic Profile Section
        basic_group = QGroupBox("Basic Îlot Profile")
        basic_layout = QFormLayout(basic_group)
        
        self.size_0_1_spin = QDoubleSpinBox()
        self.size_0_1_spin.setRange(0, 1)
        self.size_0_1_spin.setSingleStep(0.01)
        self.size_0_1_spin.setValue(0.10)
        self.size_0_1_spin.setDecimals(2)
        basic_layout.addRow("0-1m² îlots (%):", self.size_0_1_spin)
        
        self.size_1_3_spin = QDoubleSpinBox()
        self.size_1_3_spin.setRange(0, 1)
        self.size_1_3_spin.setSingleStep(0.01)
        self.size_1_3_spin.setValue(0.25)
        self.size_1_3_spin.setDecimals(2)
        basic_layout.addRow("1-3m² îlots (%):", self.size_1_3_spin)
        
        self.size_3_5_spin = QDoubleSpinBox()
        self.size_3_5_spin.setRange(0, 1)
        self.size_3_5_spin.setSingleStep(0.01)
        self.size_3_5_spin.setValue(0.30)
        self.size_3_5_spin.setDecimals(2)
        basic_layout.addRow("3-5m² îlots (%):", self.size_3_5_spin)
        
        self.size_5_10_spin = QDoubleSpinBox()
        self.size_5_10_spin.setRange(0, 1)
        self.size_5_10_spin.setSingleStep(0.01)
        self.size_5_10_spin.setValue(0.35)
        self.size_5_10_spin.setDecimals(2)
        basic_layout.addRow("5-10m² îlots (%):", self.size_5_10_spin)
        
        layout.addWidget(basic_group)
        
        # Advanced Settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        
        self.corridor_width_spin = QDoubleSpinBox()
        self.corridor_width_spin.setRange(0.5, 5.0)
        self.corridor_width_spin.setSingleStep(0.1)
        self.corridor_width_spin.setValue(1.5)
        self.corridor_width_spin.setSuffix(" m")
        advanced_layout.addRow("Corridor Width:", self.corridor_width_spin)
        
        self.min_spacing_spin = QDoubleSpinBox()
        self.min_spacing_spin.setRange(0.1, 2.0)
        self.min_spacing_spin.setSingleStep(0.1)
        self.min_spacing_spin.setValue(0.5)
        self.min_spacing_spin.setSuffix(" m")
        advanced_layout.addRow("Min Spacing:", self.min_spacing_spin)
        
        self.entrance_buffer_spin = QDoubleSpinBox()
        self.entrance_buffer_spin.setRange(0.5, 5.0)
        self.entrance_buffer_spin.setSingleStep(0.1)
        self.entrance_buffer_spin.setValue(2.0)
        self.entrance_buffer_spin.setSuffix(" m")
        advanced_layout.addRow("Entrance Buffer:", self.entrance_buffer_spin)
        
        layout.addWidget(advanced_group)
        
        # Algorithm Selection
        algorithm_group = QGroupBox("Optimization Algorithm")
        algorithm_layout = QVBoxLayout(algorithm_group)
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "Genetic Algorithm (Recommended)",
            "Space Filling Optimizer",
            "Constraint Solver",
            "Hybrid Approach"
        ])
        algorithm_layout.addWidget(self.algorithm_combo)
        
        # Algorithm parameters
        self.population_size_spin = QSpinBox()
        self.population_size_spin.setRange(50, 500)
        self.population_size_spin.setValue(100)
        
        self.generations_spin = QSpinBox()
        self.generations_spin.setRange(50, 1000)
        self.generations_spin.setValue(200)
        
        algo_params_layout = QFormLayout()
        algo_params_layout.addRow("Population Size:", self.population_size_spin)
        algo_params_layout.addRow("Generations:", self.generations_spin)
        algorithm_layout.addLayout(algo_params_layout)
        
        layout.addWidget(algorithm_group)
        
        # Preset buttons
        preset_group = QGroupBox("Quick Presets")
        preset_layout = QHBoxLayout(preset_group)
        
        retail_btn = QPushButton("Retail Store")
        retail_btn.clicked.connect(lambda: self.load_preset("retail"))
        preset_layout.addWidget(retail_btn)
        
        office_btn = QPushButton("Office Space")
        office_btn.clicked.connect(lambda: self.load_preset("office"))
        preset_layout.addWidget(office_btn)
        
        warehouse_btn = QPushButton("Warehouse")
        warehouse_btn.clicked.connect(lambda: self.load_preset("warehouse"))
        preset_layout.addWidget(warehouse_btn)
        
        layout.addWidget(preset_group)
        
        layout.addStretch()
    
    def load_preset(self, preset_type: str):
        """Load predefined presets"""
        presets = {
            "retail": {
                "size_0_1": 0.05,
                "size_1_3": 0.30,
                "size_3_5": 0.40,
                "size_5_10": 0.25,
                "corridor_width": 2.0,
                "min_spacing": 0.8
            },
            "office": {
                "size_0_1": 0.15,
                "size_1_3": 0.35,
                "size_3_5": 0.35,
                "size_5_10": 0.15,
                "corridor_width": 1.2,
                "min_spacing": 0.3
            },
            "warehouse": {
                "size_0_1": 0.02,
                "size_1_3": 0.08,
                "size_3_5": 0.30,
                "size_5_10": 0.60,
                "corridor_width": 3.0,
                "min_spacing": 1.0
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            self.size_0_1_spin.setValue(preset["size_0_1"])
            self.size_1_3_spin.setValue(preset["size_1_3"])
            self.size_3_5_spin.setValue(preset["size_3_5"])
            self.size_5_10_spin.setValue(preset["size_5_10"])
            self.corridor_width_spin.setValue(preset["corridor_width"])
            self.min_spacing_spin.setValue(preset["min_spacing"])
    
    def get_parameters(self) -> Dict:
        """Get current parameter values"""
        return {
            "size_0_1": self.size_0_1_spin.value(),
            "size_1_3": self.size_1_3_spin.value(),
            "size_3_5": self.size_3_5_spin.value(),
            "size_5_10": self.size_5_10_spin.value(),
            "corridor_width": self.corridor_width_spin.value(),
            "min_spacing": self.min_spacing_spin.value(),
            "entrance_buffer": self.entrance_buffer_spin.value(),
            "algorithm": self.algorithm_combo.currentText(),
            "population_size": self.population_size_spin.value(),
            "generations": self.generations_spin.value()
        }

class ProfessionalVisualizationWidget(QWidget):
    """Professional visualization widget with advanced features"""
    
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setMaximumWidth(40)
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.setMaximumWidth(40)
        self.reset_view_btn = QPushButton("Reset View")
        self.toggle_grid_btn = QPushButton("Grid")
        self.toggle_grid_btn.setCheckable(True)
        self.toggle_labels_btn = QPushButton("Labels")
        self.toggle_labels_btn.setCheckable(True)
        self.toggle_labels_btn.setChecked(True)
        
        toolbar.addWidget(QLabel("View:"))
        toolbar.addWidget(self.zoom_in_btn)
        toolbar.addWidget(self.zoom_out_btn)
        toolbar.addWidget(self.reset_view_btn)
        toolbar.addWidget(QLabel("|"))
        toolbar.addWidget(self.toggle_grid_btn)
        toolbar.addWidget(self.toggle_labels_btn)
        toolbar.addStretch()
        
        # Export options
        self.export_btn = QPushButton("Export Image")
        toolbar.addWidget(self.export_btn)
        
        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)
        
        # Connect signals
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_view_btn.clicked.connect(self.reset_view)
        self.export_btn.clicked.connect(self.export_image)
        
        self.current_ax = None
        
    def create_visualization(self, zones, ilots, corridors, bounds):
        """Create professional visualization"""
        self.figure.clear()
        
        # Create subplot with professional styling
        self.current_ax = self.figure.add_subplot(111)
        self.current_ax.set_aspect('equal')
        
        # Set professional color scheme
        self.figure.patch.set_facecolor('white')
        self.current_ax.set_facecolor('#f8f9fa')
        
        # Draw zones with professional styling
        for zone in zones:
            if zone.polygon.is_valid:
                x, y = zone.polygon.exterior.xy
                
                if zone.zone_type == 'wall':
                    self.current_ax.plot(x, y, color='#2c3e50', linewidth=3, solid_capstyle='round')
                elif zone.zone_type == 'entrance':
                    self.current_ax.fill(x, y, color='#e74c3c', alpha=0.4, edgecolor='#c0392b', linewidth=2)
                elif zone.zone_type == 'restricted':
                    self.current_ax.fill(x, y, color='#3498db', alpha=0.3, edgecolor='#2980b9', linewidth=1)
        
        # Professional îlot colors
        ilot_colors = {
            '0-1m²': '#fff5f5',
            '1-3m²': '#f0f8ff', 
            '3-5m²': '#f0fff0',
            '5-10m²': '#fffaf0'
        }
        
        ilot_edge_colors = {
            '0-1m²': '#ff6b6b',
            '1-3m²': '#4ecdc4', 
            '3-5m²': '#45b7d1',
            '5-10m²': '#f9ca24'
        }
        
        # Draw îlots with professional styling
        for ilot in ilots:
            if ilot.polygon.is_valid:
                x, y = ilot.polygon.exterior.xy
                face_color = ilot_colors.get(ilot.size_category, '#f0f0f0')
                edge_color = ilot_edge_colors.get(ilot.size_category, '#333333')
                
                self.current_ax.fill(x, y, color=face_color, alpha=0.8, 
                                   edgecolor=edge_color, linewidth=2)
                
                # Add professional labels
                if self.toggle_labels_btn.isChecked():
                    centroid = ilot.polygon.centroid
                    self.current_ax.text(centroid.x, centroid.y, f'{ilot.area:.1f}m²', 
                                       ha='center', va='center', fontsize=9, 
                                       weight='bold', color='#2c3e50',
                                       bbox=dict(boxstyle="round,pad=0.3", 
                                               facecolor='white', alpha=0.8))
        
        # Draw corridors with professional styling
        for corridor in corridors:
            if corridor.is_valid:
                x, y = corridor.exterior.xy
                self.current_ax.fill(x, y, color='#f39c12', alpha=0.6, 
                                   edgecolor='#e67e22', linewidth=2, linestyle='--')
        
        # Professional grid
        if self.toggle_grid_btn.isChecked():
            self.current_ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # Set bounds with margin
        min_x, min_y, max_x, max_y = bounds
        margin = max((max_x - min_x), (max_y - min_y)) * 0.05
        self.current_ax.set_xlim(min_x - margin, max_x + margin)
        self.current_ax.set_ylim(min_y - margin, max_y + margin)
        
        # Professional labels and title
        self.current_ax.set_title('AI Architectural Space Analyzer PRO - Enterprise Results', 
                                fontsize=16, weight='bold', color='#2c3e50', pad=20)
        self.current_ax.set_xlabel('X Coordinate (meters)', fontsize=12, color='#34495e')
        self.current_ax.set_ylabel('Y Coordinate (meters)', fontsize=12, color='#34495e')
        
        # Professional legend
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#2c3e50', label='Walls'),
            plt.Rectangle((0,0),1,1, facecolor='#e74c3c', alpha=0.4, label='Entrances/Exits'),
            plt.Rectangle((0,0),1,1, facecolor='#3498db', alpha=0.3, label='Restricted Areas'),
            plt.Rectangle((0,0),1,1, facecolor='#f39c12', alpha=0.6, label='Corridors'),
            plt.Rectangle((0,0),1,1, facecolor='#fff5f5', edgecolor='#ff6b6b', label='Îlots 0-1m²'),
            plt.Rectangle((0,0),1,1, facecolor='#f0f8ff', edgecolor='#4ecdc4', label='Îlots 1-3m²'),
            plt.Rectangle((0,0),1,1, facecolor='#f0fff0', edgecolor='#45b7d1', label='Îlots 3-5m²'),
            plt.Rectangle((0,0),1,1, facecolor='#fffaf0', edgecolor='#f9ca24', label='Îlots 5-10m²')
        ]
        
        self.current_ax.legend(handles=legend_elements, loc='center left', 
                             bbox_to_anchor=(1, 0.5), frameon=True, 
                             fancybox=True, shadow=True)
        
        # Tight layout for professional appearance
        self.figure.tight_layout()
        self.canvas.draw()
    
    def zoom_in(self):
        """Zoom in functionality"""
        if self.current_ax:
            xlim = self.current_ax.get_xlim()
            ylim = self.current_ax.get_ylim()
            
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            
            x_range = (xlim[1] - xlim[0]) * 0.8
            y_range = (ylim[1] - ylim[0]) * 0.8
            
            self.current_ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.current_ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.canvas.draw()
    
    def zoom_out(self):
        """Zoom out functionality"""
        if self.current_ax:
            xlim = self.current_ax.get_xlim()
            ylim = self.current_ax.get_ylim()
            
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            
            x_range = (xlim[1] - xlim[0]) * 1.25
            y_range = (ylim[1] - ylim[0]) * 1.25
            
            self.current_ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.current_ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.canvas.draw()
    
    def reset_view(self):
        """Reset view to original bounds"""
        if self.current_ax:
            self.current_ax.autoscale()
            self.canvas.draw()
    
    def export_image(self):
        """Export current visualization as image"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Visualization",
            "visualization.png",
            "PNG Files (*.png);;JPG Files (*.jpg);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        
        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight', 
                              facecolor='white', edgecolor='none')
            QMessageBox.information(self, "Success", f"Image exported to:\n{file_path}")

class StatisticsPanel(QWidget):
    """Professional statistics and analysis panel"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Statistics display
        stats_group = QGroupBox("Analysis Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.total_ilots_label = QLabel("0")
        self.total_area_label = QLabel("0.00 m²")
        self.coverage_label = QLabel("0.00%")
        self.efficiency_label = QLabel("0.00%")
        
        stats_layout.addRow("Total Îlots:", self.total_ilots_label)
        stats_layout.addRow("Total Area:", self.total_area_label)
        stats_layout.addRow("Area Coverage:", self.coverage_label)
        stats_layout.addRow("Space Efficiency:", self.efficiency_label)
        
        layout.addWidget(stats_group)
        
        # Category breakdown
        category_group = QGroupBox("Îlot Categories")
        self.category_layout = QFormLayout(category_group)
        
        layout.addWidget(category_group)
        
        # Performance metrics
        performance_group = QGroupBox("Performance Metrics")
        performance_layout = QFormLayout(performance_group)
        
        self.processing_time_label = QLabel("0.00 s")
        self.algorithm_label = QLabel("None")
        self.optimization_score_label = QLabel("0.00")
        
        performance_layout.addRow("Processing Time:", self.processing_time_label)
        performance_layout.addRow("Algorithm Used:", self.algorithm_label)
        performance_layout.addRow("Optimization Score:", self.optimization_score_label)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
    
    def update_statistics(self, ilots, bounds, processing_time=0, algorithm="Unknown"):
        """Update statistics display"""
        if not ilots:
            return
        
        # Basic statistics
        total_ilots = len(ilots)
        total_area = sum(ilot.area for ilot in ilots)
        
        # Calculate available area
        min_x, min_y, max_x, max_y = bounds
        total_space = (max_x - min_x) * (max_y - min_y)
        coverage = (total_area / total_space) * 100 if total_space > 0 else 0
        
        # Update labels
        self.total_ilots_label.setText(str(total_ilots))
        self.total_area_label.setText(f"{total_area:.2f} m²")
        self.coverage_label.setText(f"{coverage:.2f}%")
        self.efficiency_label.setText(f"{min(coverage * 1.2, 100):.2f}%")
        
        self.processing_time_label.setText(f"{processing_time:.2f} s")
        self.algorithm_label.setText(algorithm)
        
        # Category breakdown
        categories = {}
        for ilot in ilots:
            cat = ilot.size_category
            if cat not in categories:
                categories[cat] = {'count': 0, 'area': 0}
            categories[cat]['count'] += 1
            categories[cat]['area'] += ilot.area
        
        # Clear existing category widgets
        for i in reversed(range(self.category_layout.count())):
            self.category_layout.itemAt(i).widget().setParent(None)
        
        # Add category statistics
        for category, data in categories.items():
            count_area_text = f"{data['count']} îlots ({data['area']:.1f} m²)"
            self.category_layout.addRow(f"{category}:", QLabel(count_area_text))

class ProjectManagerDialog(QDialog):
    """Professional project management dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Manager - Enterprise")
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Project list
        self.project_list = QListWidget()
        layout.addWidget(QLabel("Recent Projects:"))
        layout.addWidget(self.project_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load Project")
        self.save_btn = QPushButton("Save Current")
        self.delete_btn = QPushButton("Delete")
        self.export_btn = QPushButton("Export")
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Load recent projects
        self.load_recent_projects()
    
    def load_recent_projects(self):
        """Load recent projects from database or local storage"""
        # This would connect to the database in a real implementation
        sample_projects = [
            "Office Layout - 45 îlots",
            "Retail Store - 32 îlots", 
            "Warehouse - 78 îlots",
            "Mixed Use - 56 îlots"
        ]
        
        for project in sample_projects:
            self.project_list.addItem(project)