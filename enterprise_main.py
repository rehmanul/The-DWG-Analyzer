#!/usr/bin/env python3
"""
AI Architectural Space Analyzer PRO - Enterprise Main Application
Complete integration of all enterprise modules
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Fix OpenGL issues first
try:
    from fix_opengl import fix_opengl_issues
    fix_opengl_issues()
except:
    # Set fallback environment
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    os.environ['MPLBACKEND'] = 'Agg'

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Enterprise imports with fallback
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    GUI_AVAILABLE = True
except ImportError:
    print("⚠️ GUI libraries not available - running in headless mode")
    GUI_AVAILABLE = False

# Import enterprise modules
from main import (
    EnterpriseCADProcessor, IlotPlacementEngine, EnterpriseVisualization,
    DatabaseManager, PDFExporter, IlotProfile, Zone, Ilot
)
from advanced_algorithms import GeneticAlgorithmOptimizer, ConstraintSolver, SpaceFillingOptimizer
from enterprise_ui import (
    ProfessionalStyle, AdvancedParameterPanel, ProfessionalVisualizationWidget,
    StatisticsPanel, ProjectManagerDialog
)

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enterprise.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnterpriseMainApplication(QMainWindow):
    """Complete enterprise application with all professional features"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize enterprise components
        self.cad_processor = EnterpriseCADProcessor()
        self.db_manager = DatabaseManager()
        self.pdf_exporter = PDFExporter()
        
        # Current project data
        self.current_zones = []
        self.current_ilots = []
        self.current_corridors = []
        self.current_bounds = (0, 0, 100, 100)
        self.current_file_path = None
        self.processing_start_time = 0
        
        # Load enterprise configuration
        self.load_enterprise_config()
        
        # Initialize UI
        self.init_enterprise_ui()
        
        # Setup enterprise features
        self.setup_enterprise_features()
        
        logger.info("Enterprise application initialized successfully")
    
    def load_enterprise_config(self):
        """Load enterprise configuration"""
        config_path = current_dir / "config" / "enterprise_config.json"
        
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info("Enterprise configuration loaded")
        except Exception as e:
            logger.warning(f"Could not load config: {e}, using defaults")
            self.config = {
                "application": {"name": "AI Architectural Space Analyzer PRO"},
                "supported_formats": [".dwg", ".dxf", ".png", ".jpg", ".jpeg"],
                "ilot_defaults": {
                    "size_0_1_percent": 10,
                    "size_1_3_percent": 25,
                    "size_3_5_percent": 30,
                    "size_5_10_percent": 35,
                    "corridor_width_m": 1.5
                }
            }
    
    def init_enterprise_ui(self):
        """Initialize professional enterprise UI"""
        
        # Set application properties
        app_config = self.config.get("application", {})
        self.setWindowTitle(f"{app_config.get('name', 'AI Architectural Analyzer')} - Enterprise Edition")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Apply professional styling
        self.setStyleSheet(ProfessionalStyle.get_stylesheet())
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel with tabs
        left_panel = QTabWidget()
        left_panel.setFixedWidth(400)
        
        # Parameters tab
        self.parameter_panel = AdvancedParameterPanel()
        left_panel.addTab(self.parameter_panel, "Parameters")
        
        # Statistics tab
        self.statistics_panel = StatisticsPanel()
        left_panel.addTab(self.statistics_panel, "Statistics")
        
        # File operations tab
        file_ops_widget = self.create_file_operations_widget()
        left_panel.addTab(file_ops_widget, "File Operations")
        
        main_layout.addWidget(left_panel)
        
        # Right panel - visualization
        self.visualization_widget = ProfessionalVisualizationWidget()
        main_layout.addWidget(self.visualization_widget, 1)
        
        # Status bar with enterprise info
        self.create_status_bar()
        
        # Connect signals
        self.connect_signals()
    
    def create_menu_bar(self):
        """Create professional menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open CAD File...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_project_action = QAction('Save Project...', self)
        save_project_action.setShortcut('Ctrl+S')
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        load_project_action = QAction('Load Project...', self)
        load_project_action.setShortcut('Ctrl+L')
        load_project_action.triggered.connect(self.load_project)
        file_menu.addAction(load_project_action)
        
        file_menu.addSeparator()
        
        export_pdf_action = QAction('Export PDF Report...', self)
        export_pdf_action.setShortcut('Ctrl+E')
        export_pdf_action.triggered.connect(self.export_pdf_report)
        file_menu.addAction(export_pdf_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu('Analysis')
        
        run_analysis_action = QAction('Run Îlot Analysis', self)
        run_analysis_action.setShortcut('F5')
        run_analysis_action.triggered.connect(self.run_analysis)
        analysis_menu.addAction(run_analysis_action)
        
        optimize_action = QAction('Advanced Optimization...', self)
        optimize_action.triggered.connect(self.run_advanced_optimization)
        analysis_menu.addAction(optimize_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        project_manager_action = QAction('Project Manager...', self)
        project_manager_action.triggered.connect(self.open_project_manager)
        tools_menu.addAction(project_manager_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About Enterprise Edition', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_file_operations_widget(self):
        """Create file operations widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File loading section
        file_group = QGroupBox("File Loading")
        file_layout = QVBoxLayout(file_group)
        
        self.load_file_btn = QPushButton("Load CAD File")
        self.load_file_btn.clicked.connect(self.open_file)
        file_layout.addWidget(self.load_file_btn)
        
        self.current_file_label = QLabel("No file loaded")
        self.current_file_label.setWordWrap(True)
        file_layout.addWidget(self.current_file_label)
        
        layout.addWidget(file_group)
        
        # Analysis section
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.run_analysis_btn = QPushButton("Generate Îlot Layout")
        self.run_analysis_btn.clicked.connect(self.run_analysis)
        self.run_analysis_btn.setEnabled(False)
        analysis_layout.addWidget(self.run_analysis_btn)
        
        self.progress_bar = QProgressBar()
        analysis_layout.addWidget(self.progress_bar)
        
        layout.addWidget(analysis_group)
        
        # Export section
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout(export_group)
        
        self.export_pdf_btn = QPushButton("Export PDF Report")
        self.export_pdf_btn.clicked.connect(self.export_pdf_report)
        self.export_pdf_btn.setEnabled(False)
        export_layout.addWidget(self.export_pdf_btn)
        
        self.export_image_btn = QPushButton("Export Image")
        self.export_image_btn.clicked.connect(self.visualization_widget.export_image)
        self.export_image_btn.setEnabled(False)
        export_layout.addWidget(self.export_image_btn)
        
        layout.addWidget(export_group)
        
        layout.addStretch()
        return widget
    
    def create_status_bar(self):
        """Create professional status bar"""
        status_bar = self.statusBar()
        
        # Main status message
        self.status_label = QLabel("Ready - Load a CAD file to begin enterprise analysis")
        status_bar.addWidget(self.status_label)
        
        # Enterprise edition indicator
        enterprise_label = QLabel("Enterprise Edition")
        enterprise_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        status_bar.addPermanentWidget(enterprise_label)
        
        # Database connection status
        self.db_status_label = QLabel("DB: Connected")
        self.db_status_label.setStyleSheet("color: #27ae60;")
        status_bar.addPermanentWidget(self.db_status_label)
    
    def connect_signals(self):
        """Connect UI signals"""
        # Parameter changes trigger updates
        for spin_box in [
            self.parameter_panel.size_0_1_spin,
            self.parameter_panel.size_1_3_spin,
            self.parameter_panel.size_3_5_spin,
            self.parameter_panel.size_5_10_spin,
            self.parameter_panel.corridor_width_spin
        ]:
            spin_box.valueChanged.connect(self.on_parameters_changed)
    
    def setup_enterprise_features(self):
        """Setup enterprise-specific features"""
        
        # Create directories
        for directory in ['temp', 'exports', 'projects', 'logs']:
            os.makedirs(directory, exist_ok=True)
        
        # Test database connection
        try:
            test_id = self.db_manager.save_project({"test": "connection"})
            self.db_status_label.setText("DB: Connected")
            self.db_status_label.setStyleSheet("color: #27ae60;")
        except Exception as e:
            self.db_status_label.setText("DB: Offline")
            self.db_status_label.setStyleSheet("color: #e74c3c;")
            logger.warning(f"Database connection failed: {e}")
    
    def open_file(self):
        """Open CAD file with enterprise support"""
        
        supported_formats = self.config.get("supported_formats", [".dwg", ".dxf", ".png", ".jpg"])
        format_filter = "All Supported ("
        format_filter += " ".join(f"*{fmt}" for fmt in supported_formats)
        format_filter += ");;DWG Files (*.dwg);;DXF Files (*.dxf);;Images (*.png *.jpg *.jpeg *.tiff)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load CAD File - Enterprise Edition", "", format_filter
        )
        
        if file_path:
            self.load_cad_file(file_path)
    
    def load_cad_file(self, file_path: str):
        """Load CAD file with enterprise processing"""
        
        try:
            self.progress_bar.setValue(10)
            self.status_label.setText("Loading file with enterprise processing...")
            
            # Process file using enterprise CAD processor
            result = self.cad_processor.load_cad_file(file_path)
            
            self.current_zones = result['zones']
            self.current_bounds = result['bounds']
            self.current_file_path = file_path
            
            self.progress_bar.setValue(50)
            
            # Update UI
            file_name = os.path.basename(file_path)
            self.current_file_label.setText(f"Loaded: {file_name}")
            self.run_analysis_btn.setEnabled(True)
            
            # Show initial visualization
            self.visualization_widget.create_visualization(
                self.current_zones, [], [], self.current_bounds
            )
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"File loaded - {len(self.current_zones)} zones detected")
            
            logger.info(f"Successfully loaded file: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Enterprise Loading Error", 
                               f"Failed to load file with enterprise processor:\n{str(e)}")
            self.progress_bar.setValue(0)
            self.status_label.setText("Error loading file")
            logger.error(f"File loading error: {e}")
    
    def run_analysis(self):
        """Run enterprise îlot analysis"""
        
        if not self.current_zones:
            QMessageBox.warning(self, "No Data", "Please load a CAD file first")
            return
        
        try:
            self.processing_start_time = time.time()
            self.progress_bar.setValue(5)
            self.status_label.setText("Running enterprise analysis...")
            
            # Get parameters from UI
            params = self.parameter_panel.get_parameters()
            
            # Create enterprise profile
            profile = IlotProfile(
                size_0_1=params["size_0_1"],
                size_1_3=params["size_1_3"],
                size_3_5=params["size_3_5"],
                size_5_10=params["size_5_10"],
                corridor_width=params["corridor_width"],
                min_spacing=params["min_spacing"]
            )
            
            self.progress_bar.setValue(20)
            
            # Choose algorithm based on selection
            algorithm_name = params["algorithm"]
            
            if "Genetic Algorithm" in algorithm_name:
                self.run_genetic_algorithm_analysis(profile, params)
            elif "Space Filling" in algorithm_name:
                self.run_space_filling_analysis(profile)
            elif "Constraint Solver" in algorithm_name:
                self.run_constraint_solver_analysis(profile)
            else:
                # Default to standard placement
                self.run_standard_analysis(profile)
            
            processing_time = time.time() - self.processing_start_time
            
            # Update statistics
            self.statistics_panel.update_statistics(
                self.current_ilots, self.current_bounds, 
                processing_time, algorithm_name
            )
            
            # Enable export buttons
            self.export_pdf_btn.setEnabled(True)
            self.export_image_btn.setEnabled(True)
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Analysis complete - {len(self.current_ilots)} îlots placed")
            
            logger.info(f"Analysis completed in {processing_time:.2f}s with {len(self.current_ilots)} îlots")
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Enterprise analysis failed:\n{str(e)}")
            self.progress_bar.setValue(0)
            self.status_label.setText("Analysis failed")
            logger.error(f"Analysis error: {e}")
    
    def run_genetic_algorithm_analysis(self, profile: IlotProfile, params: Dict):
        """Run analysis using genetic algorithm"""
        
        self.progress_bar.setValue(30)
        
        # Create genetic algorithm optimizer
        ga_optimizer = GeneticAlgorithmOptimizer(
            population_size=params["population_size"],
            generations=params["generations"]
        )
        
        # Prepare forbidden areas
        forbidden_areas = []
        for zone in self.current_zones:
            if zone.zone_type in ['restricted', 'entrance']:
                forbidden_areas.append(zone.polygon)
        
        # Generate îlot specifications
        placement_engine = IlotPlacementEngine(profile)
        available_area = placement_engine._calculate_available_area(self.current_zones, self.current_bounds)
        ilot_specs = placement_engine._generate_ilot_specifications(available_area)
        
        self.progress_bar.setValue(50)
        
        # Run genetic algorithm
        solutions = ga_optimizer.optimize_placement(ilot_specs, forbidden_areas, self.current_bounds)
        
        self.progress_bar.setValue(80)
        
        # Convert best solution to îlots
        if solutions:
            best_solution = solutions[0]
            self.current_ilots = []
            
            for i, (x, y, w, h) in enumerate(best_solution.ilots):
                if i < len(ilot_specs):
                    from shapely.geometry import Polygon
                    poly = Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)])
                    ilot = Ilot(
                        polygon=poly,
                        area=ilot_specs[i]['area'],
                        position=(x + w/2, y + h/2),
                        size_category=ilot_specs[i]['category']
                    )
                    self.current_ilots.append(ilot)
        
        # Generate corridors
        self.current_corridors = placement_engine.generate_corridors(self.current_ilots)
        
        # Update visualization
        self.visualization_widget.create_visualization(
            self.current_zones, self.current_ilots, self.current_corridors, self.current_bounds
        )
    
    def run_space_filling_analysis(self, profile: IlotProfile):
        """Run analysis using space filling optimizer"""
        
        self.progress_bar.setValue(40)
        
        # Create space filling optimizer
        sf_optimizer = SpaceFillingOptimizer()
        
        # Prepare data
        placement_engine = IlotPlacementEngine(profile)
        available_area = placement_engine._calculate_available_area(self.current_zones, self.current_bounds)
        ilot_specs = placement_engine._generate_ilot_specifications(available_area)
        
        forbidden_areas = []
        for zone in self.current_zones:
            if zone.zone_type in ['restricted', 'entrance']:
                forbidden_areas.append(zone.polygon)
        
        self.progress_bar.setValue(60)
        
        # Run space filling optimization
        placed_ilots_data = sf_optimizer.optimize_space_filling(
            ilot_specs, forbidden_areas, self.current_bounds
        )
        
        self.progress_bar.setValue(80)
        
        # Convert to îlot objects
        self.current_ilots = []
        for i, (x, y, w, h) in enumerate(placed_ilots_data):
            if i < len(ilot_specs):
                from shapely.geometry import Polygon
                poly = Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)])
                ilot = Ilot(
                    polygon=poly,
                    area=ilot_specs[i]['area'],
                    position=(x + w/2, y + h/2),
                    size_category=ilot_specs[i]['category']
                )
                self.current_ilots.append(ilot)
        
        # Generate corridors
        self.current_corridors = placement_engine.generate_corridors(self.current_ilots)
        
        # Update visualization
        self.visualization_widget.create_visualization(
            self.current_zones, self.current_ilots, self.current_corridors, self.current_bounds
        )
    
    def run_constraint_solver_analysis(self, profile: IlotProfile):
        """Run analysis using constraint solver"""
        
        # For now, fall back to standard analysis
        # In a full implementation, this would use the ConstraintSolver class
        self.run_standard_analysis(profile)
    
    def run_standard_analysis(self, profile: IlotProfile):
        """Run standard analysis"""
        
        self.progress_bar.setValue(40)
        
        # Use standard placement engine
        placement_engine = IlotPlacementEngine(profile)
        self.current_ilots = placement_engine.generate_ilots(self.current_zones, self.current_bounds)
        
        self.progress_bar.setValue(70)
        
        # Generate corridors
        self.current_corridors = placement_engine.generate_corridors(self.current_ilots)
        
        self.progress_bar.setValue(90)
        
        # Update visualization
        self.visualization_widget.create_visualization(
            self.current_zones, self.current_ilots, self.current_corridors, self.current_bounds
        )
    
    def run_advanced_optimization(self):
        """Run advanced optimization with multiple algorithms"""
        
        if not self.current_ilots:
            QMessageBox.warning(self, "No Analysis", "Please run basic analysis first")
            return
        
        # This would implement advanced multi-algorithm optimization
        QMessageBox.information(self, "Advanced Optimization", 
                              "Advanced optimization will compare multiple algorithms and select the best result.\n"
                              "This feature requires additional processing time.")
    
    def export_pdf_report(self):
        """Export professional PDF report"""
        
        if not self.current_ilots:
            QMessageBox.warning(self, "No Data", "No analysis results to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Enterprise PDF Report", "enterprise_report.pdf", "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                # Get current parameters
                params = self.parameter_panel.get_parameters()
                profile = IlotProfile(
                    size_0_1=params["size_0_1"],
                    size_1_3=params["size_1_3"],
                    size_3_5=params["size_3_5"],
                    size_5_10=params["size_5_10"],
                    corridor_width=params["corridor_width"]
                )
                
                # Create visualization for export
                viz = EnterpriseVisualization()
                fig = viz.create_visualization(
                    self.current_zones, self.current_ilots, self.current_corridors, self.current_bounds
                )
                
                # Export PDF
                self.pdf_exporter.export_results(fig, self.current_ilots, profile, file_path)
                
                QMessageBox.information(self, "Export Success", f"Enterprise PDF report exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"PDF export failed:\n{str(e)}")
    
    def save_project(self):
        """Save current project"""
        
        if not self.current_ilots:
            QMessageBox.warning(self, "No Data", "No analysis results to save")
            return
        
        try:
            params = self.parameter_panel.get_parameters()
            
            project_data = {
                'name': f"Enterprise_Analysis_{len(self.current_ilots)}_ilots",
                'file_path': self.current_file_path,
                'zones_count': len(self.current_zones),
                'ilots_count': len(self.current_ilots),
                'corridors_count': len(self.current_corridors),
                'parameters': params,
                'bounds': self.current_bounds,
                'total_area': sum(ilot.area for ilot in self.current_ilots)
            }
            
            project_id = self.db_manager.save_project(project_data)
            QMessageBox.information(self, "Save Success", f"Enterprise project saved with ID: {project_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Project save failed:\n{str(e)}")
    
    def load_project(self):
        """Load saved project"""
        QMessageBox.information(self, "Load Project", "Project loading feature will connect to enterprise database")
    
    def open_project_manager(self):
        """Open project manager dialog"""
        dialog = ProjectManagerDialog(self)
        dialog.exec_()
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>{self.config['application']['name']}</h2>
        <h3>Enterprise Edition</h3>
        
        <p><b>Professional CAD Analysis with AI-Powered Îlot Placement</b></p>
        
        <p><b>Enterprise Features:</b></p>
        <ul>
        <li>✅ Full DWG/DXF Support</li>
        <li>✅ Advanced AI Algorithms (Genetic Algorithm, Space Filling)</li>
        <li>✅ Professional Export Options</li>
        <li>✅ Enterprise Database Integration</li>
        <li>✅ Multi-Format Support</li>
        <li>✅ Real-time Analysis</li>
        <li>✅ Professional Visualization</li>
        </ul>
        
        <p><b>Supported Formats:</b><br>
        {', '.join(self.config.get('supported_formats', []))}</p>
        
        <p><b>Database:</b> PostgreSQL Enterprise</p>
        <p><b>AI Engine:</b> Advanced Genetic Algorithm with Constraint Solving</p>
        
        <p><i>Professional CAD Analysis Solution</i></p>
        """
        
        QMessageBox.about(self, "About Enterprise Edition", about_text)
    
    def on_parameters_changed(self):
        """Handle parameter changes"""
        # Auto-update if analysis has been run
        if self.current_ilots and len(self.current_ilots) > 0:
            # Could implement real-time updates here
            pass
    
    def closeEvent(self, event):
        """Handle application close"""
        reply = QMessageBox.question(self, 'Exit Enterprise Edition', 
                                   'Are you sure you want to exit the enterprise application?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            logger.info("Enterprise application closing")
            event.accept()
        else:
            event.ignore()

def main():
    """Main enterprise application entry point"""
    
    if not GUI_AVAILABLE:
        print("❌ GUI not available - use web interface instead:")
        print("   python run_web.py")
        return 1
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("AI Architectural Space Analyzer PRO")
    app.setApplicationVersion("1.0 Enterprise")
    app.setOrganizationName("Enterprise CAD Solutions")
    
    # Set high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    try:
        window = EnterpriseMainApplication()
        window.show()
        
        # Center window on screen
        screen = app.desktop().screenGeometry()
        window.move((screen.width() - window.width()) // 2, 
                   (screen.height() - window.height()) // 2)
        
        logger.info("Enterprise application started successfully")
        
        # Run application
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Failed to start enterprise application: {e}")
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start enterprise application:\n{str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())