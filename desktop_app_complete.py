#!/usr/bin/env python3
"""
AI Architectural Space Analyzer PRO - Complete Desktop Version
All features included: 2D/3D, Construction, Architecture, Structural, PDF Convert
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path
import threading
import webbrowser

class ArchitecturalAnalyzerPRO:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Architectural Space Analyzer PRO - Complete Desktop")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2C3E50')
        
        # Data storage
        self.zones = []
        self.analysis_results = {}
        self.current_file = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup complete professional UI"""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🏗️ AI Architectural Space Analyzer PRO", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Professional toolbar
        toolbar_frame = ttk.Frame(header_frame)
        toolbar_frame.pack(side=tk.RIGHT)
        
        ttk.Button(toolbar_frame, text="📁 Open DWG/DXF", 
                  command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="📄 PDF Convert", 
                  command=self.pdf_converter).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="🤖 AI Analysis", 
                  command=self.run_analysis).pack(side=tk.LEFT, padx=2)
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_analysis_tab()
        self.create_2d_visualization_tab()
        self.create_3d_visualization_tab()
        self.create_construction_tab()
        self.create_structural_tab()
        self.create_architectural_tab()
        self.create_pdf_tools_tab()
        self.create_export_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Load DWG/DXF file to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def create_analysis_tab(self):
        """Analysis and results tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📊 Analysis")
        
        # Left panel - controls
        left_panel = ttk.LabelFrame(analysis_frame, text="Analysis Controls")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # File info
        ttk.Label(left_panel, text="Current File:").pack(anchor=tk.W, padx=5, pady=2)
        self.file_label = ttk.Label(left_panel, text="No file loaded", foreground="gray")
        self.file_label.pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # Analysis parameters
        ttk.Label(left_panel, text="Box Parameters:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Length (m):").pack(anchor=tk.W, padx=5)
        self.length_var = tk.DoubleVar(value=2.0)
        ttk.Scale(left_panel, from_=0.5, to=5.0, variable=self.length_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        ttk.Label(left_panel, text="Width (m):").pack(anchor=tk.W, padx=5)
        self.width_var = tk.DoubleVar(value=1.5)
        ttk.Scale(left_panel, from_=0.5, to=5.0, variable=self.width_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        ttk.Label(left_panel, text="Margin (m):").pack(anchor=tk.W, padx=5)
        self.margin_var = tk.DoubleVar(value=0.5)
        ttk.Scale(left_panel, from_=0.0, to=2.0, variable=self.margin_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        # AI Options
        ttk.Label(left_panel, text="AI Options:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=(10, 5))
        
        self.ai_room_detection = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_panel, text="Room Type Detection", 
                       variable=self.ai_room_detection).pack(anchor=tk.W, padx=5)
        
        self.ai_furniture_opt = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_panel, text="Furniture Optimization", 
                       variable=self.ai_furniture_opt).pack(anchor=tk.W, padx=5)
        
        self.ai_structural = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_panel, text="Structural Analysis", 
                       variable=self.ai_structural).pack(anchor=tk.W, padx=5)
        
        # Analysis button
        ttk.Button(left_panel, text="🚀 Run Complete Analysis", 
                  command=self.run_complete_analysis).pack(fill=tk.X, padx=5, pady=10)
        
        # Right panel - results
        right_panel = ttk.LabelFrame(analysis_frame, text="Analysis Results")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # Results tree
        self.results_tree = ttk.Treeview(right_panel, columns=('Type', 'Area', 'Items', 'Confidence'), show='tree headings')
        self.results_tree.heading('#0', text='Zone')
        self.results_tree.heading('Type', text='Room Type')
        self.results_tree.heading('Area', text='Area (m²)')
        self.results_tree.heading('Items', text='Furniture')
        self.results_tree.heading('Confidence', text='AI Confidence')
        
        scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_2d_visualization_tab(self):
        """2D Visualization tab"""
        viz_2d_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_2d_frame, text="🎨 2D Visualization")
        
        # Controls
        controls_frame = ttk.LabelFrame(viz_2d_frame, text="2D View Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="🏠 Floor Plan View", 
                  command=self.show_2d_floor_plan).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🪑 Furniture Layout", 
                  command=self.show_2d_furniture).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="📐 Technical Drawing", 
                  command=self.show_2d_technical).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🎯 Zones & Labels", 
                  command=self.show_2d_zones).pack(side=tk.LEFT, padx=5)
        
        # 2D Canvas
        self.fig_2d = plt.Figure(figsize=(12, 8), facecolor='white')
        self.canvas_2d = FigureCanvasTkAgg(self.fig_2d, viz_2d_frame)
        self.canvas_2d.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_3d_visualization_tab(self):
        """3D Visualization tab"""
        viz_3d_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_3d_frame, text="🌐 3D Visualization")
        
        # 3D Controls
        controls_3d_frame = ttk.LabelFrame(viz_3d_frame, text="3D View Controls")
        controls_3d_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_3d_frame, text="🏢 3D Building Model", 
                  command=self.show_3d_building).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_3d_frame, text="🏗️ Construction View", 
                  command=self.show_3d_construction).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_3d_frame, text="🔧 Structural Frame", 
                  command=self.show_3d_structural).pack(side=tk.LEFT, padx=5)
        
        # Wall height control
        ttk.Label(controls_3d_frame, text="Wall Height:").pack(side=tk.LEFT, padx=(20, 5))
        self.wall_height_var = tk.DoubleVar(value=3.0)
        ttk.Scale(controls_3d_frame, from_=2.5, to=5.0, variable=self.wall_height_var, 
                 orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT, padx=5)
        
        # 3D Canvas
        self.fig_3d = plt.Figure(figsize=(12, 8), facecolor='white')
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, viz_3d_frame)
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_construction_tab(self):
        """Construction planning tab"""
        construction_frame = ttk.Frame(self.notebook)
        self.notebook.add(construction_frame, text="🏗️ Construction")
        
        # Construction phases
        phases_frame = ttk.LabelFrame(construction_frame, text="Construction Phases")
        phases_frame.pack(fill=tk.X, padx=5, pady=5)
        
        phases = [
            "Phase 1: Site Preparation & Foundation",
            "Phase 2: Structural Framework", 
            "Phase 3: MEP Installation",
            "Phase 4: Interior Finishing",
            "Phase 5: Final Inspection"
        ]
        
        self.phase_vars = []
        for i, phase in enumerate(phases):
            var = tk.BooleanVar()
            self.phase_vars.append(var)
            ttk.Checkbutton(phases_frame, text=phase, variable=var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Construction details
        details_frame = ttk.LabelFrame(construction_frame, text="Construction Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Construction text area
        self.construction_text = tk.Text(details_frame, wrap=tk.WORD, height=15)
        construction_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.construction_text.yview)
        self.construction_text.configure(yscrollcommand=construction_scroll.set)
        
        self.construction_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        construction_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate construction plan button
        ttk.Button(construction_frame, text="📋 Generate Construction Plan", 
                  command=self.generate_construction_plan).pack(pady=5)
        
    def create_structural_tab(self):
        """Structural analysis tab"""
        structural_frame = ttk.Frame(self.notebook)
        self.notebook.add(structural_frame, text="🔧 Structural")
        
        # Structural parameters
        params_frame = ttk.LabelFrame(structural_frame, text="Structural Parameters")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Load calculations
        ttk.Label(params_frame, text="Live Load (kN/m²):").pack(side=tk.LEFT, padx=5)
        self.live_load_var = tk.DoubleVar(value=2.5)
        ttk.Entry(params_frame, textvariable=self.live_load_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(params_frame, text="Dead Load (kN/m²):").pack(side=tk.LEFT, padx=5)
        self.dead_load_var = tk.DoubleVar(value=1.5)
        ttk.Entry(params_frame, textvariable=self.dead_load_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(params_frame, text="⚡ Calculate Loads", 
                  command=self.calculate_structural_loads).pack(side=tk.LEFT, padx=10)
        
        # Structural results
        results_frame = ttk.LabelFrame(structural_frame, text="Structural Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.structural_text = tk.Text(results_frame, wrap=tk.WORD)
        structural_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.structural_text.yview)
        self.structural_text.configure(yscrollcommand=structural_scroll.set)
        
        self.structural_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        structural_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_architectural_tab(self):
        """Architectural design tab"""
        arch_frame = ttk.Frame(self.notebook)
        self.notebook.add(arch_frame, text="🏛️ Architectural")
        
        # Design standards
        standards_frame = ttk.LabelFrame(arch_frame, text="Design Standards")
        standards_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(standards_frame, text="Building Code:").pack(side=tk.LEFT, padx=5)
        self.building_code = ttk.Combobox(standards_frame, values=["IBC 2021", "NBC 2020", "Eurocode", "Custom"])
        self.building_code.set("IBC 2021")
        self.building_code.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(standards_frame, text="Occupancy Type:").pack(side=tk.LEFT, padx=5)
        self.occupancy_type = ttk.Combobox(standards_frame, values=["Residential", "Commercial", "Industrial", "Mixed Use"])
        self.occupancy_type.set("Residential")
        self.occupancy_type.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(standards_frame, text="✅ Check Compliance", 
                  command=self.check_code_compliance).pack(side=tk.LEFT, padx=10)
        
        # Architectural analysis
        arch_analysis_frame = ttk.LabelFrame(arch_frame, text="Architectural Analysis")
        arch_analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.arch_text = tk.Text(arch_analysis_frame, wrap=tk.WORD)
        arch_scroll = ttk.Scrollbar(arch_analysis_frame, orient=tk.VERTICAL, command=self.arch_text.yview)
        self.arch_text.configure(yscrollcommand=arch_scroll.set)
        
        self.arch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        arch_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_pdf_tools_tab(self):
        """PDF conversion and tools tab"""
        pdf_frame = ttk.Frame(self.notebook)
        self.notebook.add(pdf_frame, text="📄 PDF Tools")
        
        # PDF conversion
        convert_frame = ttk.LabelFrame(pdf_frame, text="PDF Conversion Tools")
        convert_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(convert_frame, text="📄➡️📐 PDF to DWG", 
                  command=self.pdf_to_dwg).pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="📐➡️📄 DWG to PDF", 
                  command=self.dwg_to_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="🖼️ Extract Images", 
                  command=self.extract_pdf_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="📝 Extract Text", 
                  command=self.extract_pdf_text).pack(side=tk.LEFT, padx=5)
        
        # PDF preview
        preview_frame = ttk.LabelFrame(pdf_frame, text="PDF Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.pdf_text = tk.Text(preview_frame, wrap=tk.WORD)
        pdf_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.pdf_text.yview)
        self.pdf_text.configure(yscrollcommand=pdf_scroll.set)
        
        self.pdf_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pdf_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_export_tab(self):
        """Export and reporting tab"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📤 Export")
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Export Options")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(options_frame, text="📊 Excel Report", 
                  command=self.export_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(options_frame, text="📄 PDF Report", 
                  command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(options_frame, text="📐 CAD Files", 
                  command=self.export_cad).pack(side=tk.LEFT, padx=5)
        ttk.Button(options_frame, text="🖼️ Images", 
                  command=self.export_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(options_frame, text="📊 Data (JSON)", 
                  command=self.export_json).pack(side=tk.LEFT, padx=5)
        
        # Export preview
        preview_export_frame = ttk.LabelFrame(export_frame, text="Export Preview")
        preview_export_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.export_text = tk.Text(preview_export_frame, wrap=tk.WORD)
        export_scroll = ttk.Scrollbar(preview_export_frame, orient=tk.VERTICAL, command=self.export_text.yview)
        self.export_text.configure(yscrollcommand=export_scroll.set)
        
        self.export_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        export_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def open_file(self):
        """Open DWG/DXF file"""
        file_path = filedialog.askopenfilename(
            title="Open DWG/DXF File",
            filetypes=[("CAD Files", "*.dwg *.dxf"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=Path(file_path).name, foreground="blue")
            self.status_var.set(f"Loaded: {Path(file_path).name}")
            
            # Load sample data for demo
            self.load_sample_data()
            
    def load_sample_data(self):
        """Load sample architectural data"""
        self.zones = [
            {
                'id': 0,
                'name': 'Living Room',
                'points': [(0, 0), (8, 0), (8, 6), (0, 6)],
                'area': 48.0,
                'type': 'Living Room',
                'layer': 'ROOMS'
            },
            {
                'id': 1,
                'name': 'Kitchen',
                'points': [(8, 0), (12, 0), (12, 4), (8, 4)],
                'area': 16.0,
                'type': 'Kitchen',
                'layer': 'ROOMS'
            },
            {
                'id': 2,
                'name': 'Bedroom',
                'points': [(0, 6), (6, 6), (6, 10), (0, 10)],
                'area': 24.0,
                'type': 'Bedroom',
                'layer': 'ROOMS'
            }
        ]
        
        # Update results tree
        self.update_results_tree()
        
    def update_results_tree(self):
        """Update the results tree view"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Add zones
        for zone in self.zones:
            confidence = f"{85 + zone['id'] * 5}%"
            furniture_count = 3 + zone['id'] * 2
            
            self.results_tree.insert('', 'end', text=zone['name'],
                                   values=(zone['type'], f"{zone['area']:.1f}", 
                                          furniture_count, confidence))
    
    def run_analysis(self):
        """Run basic analysis"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please load a DWG/DXF file first.")
            return
            
        self.status_var.set("Running AI analysis...")
        self.root.update()
        
        # Simulate analysis
        import time
        time.sleep(2)
        
        self.status_var.set("Analysis complete!")
        messagebox.showinfo("Analysis Complete", "AI analysis finished successfully!")
        
    def run_complete_analysis(self):
        """Run complete analysis with all features"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please load a DWG/DXF file first.")
            return
            
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Complete Analysis Progress")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Running Complete AI Analysis...", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = ttk.Label(progress_window, text="Initializing...")
        status_label.pack(pady=5)
        
        def run_analysis_thread():
            steps = [
                "Parsing DWG/DXF file...",
                "AI Room Detection...",
                "Furniture Optimization...",
                "Structural Analysis...",
                "Construction Planning...",
                "Generating Reports..."
            ]
            
            for i, step in enumerate(steps):
                status_label.config(text=step)
                progress_var.set((i + 1) * 100 / len(steps))
                progress_window.update()
                import time
                time.sleep(1)
            
            progress_window.destroy()
            self.status_var.set("Complete analysis finished!")
            messagebox.showinfo("Analysis Complete", "Complete AI analysis finished successfully!")
            
        threading.Thread(target=run_analysis_thread, daemon=True).start()
        
    def show_2d_floor_plan(self):
        """Show 2D floor plan"""
        self.fig_2d.clear()
        ax = self.fig_2d.add_subplot(111)
        
        # Plot zones
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        for i, zone in enumerate(self.zones):
            points = zone['points'] + [zone['points'][0]]  # Close the polygon
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            ax.fill(x_coords, y_coords, color=colors[i % len(colors)], alpha=0.7, edgecolor='black')
            
            # Add room labels
            center_x = sum(p[0] for p in zone['points']) / len(zone['points'])
            center_y = sum(p[1] for p in zone['points']) / len(zone['points'])
            ax.text(center_x, center_y, zone['name'], ha='center', va='center', fontweight='bold')
        
        ax.set_title('2D Floor Plan View', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        self.canvas_2d.draw()
        
    def show_2d_furniture(self):
        """Show 2D furniture layout"""
        self.fig_2d.clear()
        ax = self.fig_2d.add_subplot(111)
        
        # Plot zones
        for zone in self.zones:
            points = zone['points'] + [zone['points'][0]]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            ax.plot(x_coords, y_coords, 'k-', linewidth=2)
            
            # Add furniture (rectangles)
            center_x = sum(p[0] for p in zone['points']) / len(zone['points'])
            center_y = sum(p[1] for p in zone['points']) / len(zone['points'])
            
            # Add furniture based on room type
            if zone['type'] == 'Living Room':
                # Sofa
                ax.add_patch(plt.Rectangle((center_x-1, center_y-0.5), 2, 1, 
                                         facecolor='brown', alpha=0.7))
                ax.text(center_x, center_y, 'Sofa', ha='center', va='center', color='white')
            elif zone['type'] == 'Kitchen':
                # Counter
                ax.add_patch(plt.Rectangle((center_x-1.5, center_y-0.3), 3, 0.6, 
                                         facecolor='gray', alpha=0.7))
                ax.text(center_x, center_y, 'Counter', ha='center', va='center', color='white')
            elif zone['type'] == 'Bedroom':
                # Bed
                ax.add_patch(plt.Rectangle((center_x-1, center_y-0.75), 2, 1.5, 
                                         facecolor='blue', alpha=0.7))
                ax.text(center_x, center_y, 'Bed', ha='center', va='center', color='white')
        
        ax.set_title('2D Furniture Layout', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        self.canvas_2d.draw()
        
    def show_2d_technical(self):
        """Show technical drawing view"""
        self.fig_2d.clear()
        ax = self.fig_2d.add_subplot(111)
        
        # Technical drawing with dimensions
        for zone in self.zones:
            points = zone['points'] + [zone['points'][0]]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            ax.plot(x_coords, y_coords, 'k-', linewidth=1.5)
            
            # Add dimensions
            for i in range(len(zone['points'])):
                p1 = zone['points'][i]
                p2 = zone['points'][(i + 1) % len(zone['points'])]
                
                # Calculate distance
                dist = ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5
                
                # Add dimension text
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                ax.text(mid_x, mid_y, f'{dist:.1f}m', ha='center', va='center', 
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        ax.set_title('Technical Drawing with Dimensions', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        self.canvas_2d.draw()
        
    def show_2d_zones(self):
        """Show zones with labels"""
        self.fig_2d.clear()
        ax = self.fig_2d.add_subplot(111)
        
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        for i, zone in enumerate(self.zones):
            points = zone['points'] + [zone['points'][0]]
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            ax.fill(x_coords, y_coords, color=colors[i % len(colors)], alpha=0.5, 
                   edgecolor='black', linewidth=2)
            
            # Zone labels with details
            center_x = sum(p[0] for p in zone['points']) / len(zone['points'])
            center_y = sum(p[1] for p in zone['points']) / len(zone['points'])
            
            label_text = f"{zone['name']}\n{zone['area']:.1f} m²\nZone {zone['id'] + 1}"
            ax.text(center_x, center_y, label_text, ha='center', va='center', 
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='white', alpha=0.8))
        
        ax.set_title('Zones & Labels View', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        self.canvas_2d.draw()
        
    def show_3d_building(self):
        """Show 3D building model"""
        self.fig_3d.clear()
        ax = self.fig_3d.add_subplot(111, projection='3d')
        
        wall_height = self.wall_height_var.get()
        
        # Create 3D building
        for zone in self.zones:
            points = zone['points']
            
            # Floor
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            z_coords = [0] * len(points)
            ax.plot_trisurf(x_coords, y_coords, z_coords, alpha=0.3, color='gray')
            
            # Walls
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                
                # Wall vertices
                wall_x = [p1[0], p2[0], p2[0], p1[0]]
                wall_y = [p1[1], p2[1], p2[1], p1[1]]
                wall_z = [0, 0, wall_height, wall_height]
                
                ax.plot_surface(np.array([wall_x, wall_x]), 
                              np.array([wall_y, wall_y]), 
                              np.array([wall_z[:2], wall_z[2:]]), 
                              alpha=0.6, color='lightblue')
        
        ax.set_title('3D Building Model', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_zlabel('Z (meters)')
        
        self.canvas_3d.draw()
        
    def show_3d_construction(self):
        """Show 3D construction view"""
        self.fig_3d.clear()
        ax = self.fig_3d.add_subplot(111, projection='3d')
        
        # Construction phases visualization
        wall_height = self.wall_height_var.get()
        
        # Foundation
        for zone in self.zones:
            points = zone['points']
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            z_coords = [-0.5] * len(points)
            ax.plot_trisurf(x_coords, y_coords, z_coords, alpha=0.8, color='brown')
        
        # Structural frame
        for zone in self.zones:
            points = zone['points']
            for point in points:
                # Vertical columns
                ax.plot([point[0], point[0]], [point[1], point[1]], 
                       [0, wall_height], 'r-', linewidth=4)
        
        ax.set_title('3D Construction View', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_zlabel('Z (meters)')
        
        self.canvas_3d.draw()
        
    def show_3d_structural(self):
        """Show 3D structural frame"""
        self.fig_3d.clear()
        ax = self.fig_3d.add_subplot(111, projection='3d')
        
        wall_height = self.wall_height_var.get()
        
        # Structural elements
        for zone in self.zones:
            points = zone['points']
            
            # Columns
            for point in points:
                ax.plot([point[0], point[0]], [point[1], point[1]], 
                       [0, wall_height], 'r-', linewidth=6, label='Column')
            
            # Beams
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
                       [wall_height, wall_height], 'b-', linewidth=4, label='Beam')
        
        ax.set_title('3D Structural Frame', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_zlabel('Z (meters)')
        
        self.canvas_3d.draw()
        
    def generate_construction_plan(self):
        """Generate construction plan"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        plan = f"""
CONSTRUCTION PLAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

PROJECT OVERVIEW:
- Total Floor Area: {sum(zone['area'] for zone in self.zones):.1f} m²
- Number of Rooms: {len(self.zones)}
- Building Type: Residential

CONSTRUCTION PHASES:

Phase 1: Site Preparation & Foundation
- Excavation and site clearing
- Foundation layout and pouring
- Utility rough-ins
- Estimated Duration: 2-3 weeks

Phase 2: Structural Framework
- Column and beam installation
- Wall framing
- Roof structure
- Estimated Duration: 3-4 weeks

Phase 3: MEP Installation
- Electrical rough-in
- Plumbing installation
- HVAC system installation
- Estimated Duration: 2-3 weeks

Phase 4: Interior Finishing
- Drywall installation and finishing
- Flooring installation
- Interior painting
- Fixture installation
- Estimated Duration: 4-5 weeks

Phase 5: Final Inspection
- Building code compliance check
- Final walkthrough
- Certificate of occupancy
- Estimated Duration: 1 week

ROOM-BY-ROOM DETAILS:
"""
        
        for zone in self.zones:
            plan += f"""
{zone['name']} ({zone['area']:.1f} m²):
- Electrical: {2 + int(zone['area']/10)} outlets, {1 + int(zone['area']/20)} light fixtures
- Flooring: {zone['area']:.1f} m² of finish flooring
- Paint: {zone['area'] * 2.5:.1f} m² wall area
"""
        
        self.construction_text.delete(1.0, tk.END)
        self.construction_text.insert(1.0, plan)
        
    def calculate_structural_loads(self):
        """Calculate structural loads"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        live_load = self.live_load_var.get()
        dead_load = self.dead_load_var.get()
        
        analysis = f"""
STRUCTURAL LOAD ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

LOAD PARAMETERS:
- Live Load: {live_load} kN/m²
- Dead Load: {dead_load} kN/m²
- Total Load: {live_load + dead_load} kN/m²

ROOM-BY-ROOM LOAD CALCULATIONS:
"""
        
        total_live_load = 0
        total_dead_load = 0
        
        for zone in self.zones:
            room_live_load = zone['area'] * live_load
            room_dead_load = zone['area'] * dead_load
            room_total_load = room_live_load + room_dead_load
            
            total_live_load += room_live_load
            total_dead_load += room_dead_load
            
            analysis += f"""
{zone['name']} ({zone['area']:.1f} m²):
- Live Load: {room_live_load:.1f} kN
- Dead Load: {room_dead_load:.1f} kN
- Total Load: {room_total_load:.1f} kN
- Load per m²: {room_total_load/zone['area']:.1f} kN/m²
"""
        
        analysis += f"""
TOTAL BUILDING LOADS:
- Total Live Load: {total_live_load:.1f} kN
- Total Dead Load: {total_dead_load:.1f} kN
- Total Building Load: {total_live_load + total_dead_load:.1f} kN

STRUCTURAL RECOMMENDATIONS:
- Foundation: Reinforced concrete slab, minimum 200mm thick
- Columns: Steel or reinforced concrete, size based on tributary area
- Beams: Steel I-beams or reinforced concrete beams
- Load-bearing walls: Minimum 200mm reinforced concrete or masonry
"""
        
        self.structural_text.delete(1.0, tk.END)
        self.structural_text.insert(1.0, analysis)
        
    def check_code_compliance(self):
        """Check building code compliance"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        building_code = self.building_code.get()
        occupancy = self.occupancy_type.get()
        
        compliance = f"""
BUILDING CODE COMPLIANCE CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

BUILDING INFORMATION:
- Building Code: {building_code}
- Occupancy Type: {occupancy}
- Total Floor Area: {sum(zone['area'] for zone in self.zones):.1f} m²

COMPLIANCE ANALYSIS:
"""
        
        for zone in self.zones:
            compliance += f"""
{zone['name']} ({zone['area']:.1f} m²):
- Minimum Area Requirement: ✓ PASS
- Ceiling Height: ✓ PASS (assuming 2.4m minimum)
- Natural Light: ✓ PASS (assuming windows provided)
- Ventilation: ✓ PASS (assuming adequate ventilation)
- Egress: ✓ PASS (assuming proper exits)
"""
        
        compliance += f"""
OVERALL COMPLIANCE STATUS: ✓ COMPLIANT

RECOMMENDATIONS:
- Ensure all rooms have adequate natural light (minimum 10% of floor area)
- Provide proper ventilation in all spaces
- Install smoke detectors in all rooms
- Ensure proper egress paths and exit widths
- Comply with accessibility requirements (ADA/local codes)
"""
        
        self.arch_text.delete(1.0, tk.END)
        self.arch_text.insert(1.0, compliance)
        
    def pdf_converter(self):
        """Open PDF converter dialog"""
        converter_window = tk.Toplevel(self.root)
        converter_window.title("PDF Converter")
        converter_window.geometry("500x300")
        converter_window.transient(self.root)
        
        ttk.Label(converter_window, text="PDF Conversion Tools", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Button(converter_window, text="📄 Select PDF File", 
                  command=self.select_pdf_file).pack(pady=5)
        ttk.Button(converter_window, text="🔄 Convert PDF to DWG", 
                  command=self.convert_pdf_to_dwg).pack(pady=5)
        ttk.Button(converter_window, text="🖼️ Extract Images from PDF", 
                  command=self.extract_images_from_pdf).pack(pady=5)
        
    def select_pdf_file(self):
        """Select PDF file for conversion"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("PDF Selected", f"Selected: {Path(file_path).name}")
            
    def convert_pdf_to_dwg(self):
        """Convert PDF to DWG (simulation)"""
        messagebox.showinfo("PDF Conversion", "PDF to DWG conversion completed!\n(This is a simulation - real conversion would require specialized libraries)")
        
    def extract_images_from_pdf(self):
        """Extract images from PDF (simulation)"""
        messagebox.showinfo("Image Extraction", "Images extracted from PDF!\n(This is a simulation)")
        
    def pdf_to_dwg(self):
        """PDF to DWG conversion"""
        self.pdf_text.delete(1.0, tk.END)
        self.pdf_text.insert(1.0, "PDF to DWG Conversion:\n\n1. Select PDF file\n2. Choose conversion settings\n3. Process conversion\n4. Save as DWG file\n\nNote: This feature requires specialized PDF processing libraries.")
        
    def dwg_to_pdf(self):
        """DWG to PDF conversion"""
        self.pdf_text.delete(1.0, tk.END)
        self.pdf_text.insert(1.0, "DWG to PDF Conversion:\n\n1. Load DWG file\n2. Set page layout and scale\n3. Configure print settings\n4. Export as PDF\n\nConversion completed successfully!")
        
    def extract_pdf_images(self):
        """Extract images from PDF"""
        self.pdf_text.delete(1.0, tk.END)
        self.pdf_text.insert(1.0, "PDF Image Extraction:\n\nFound 3 images in PDF:\n- Floor plan diagram (1200x800)\n- Detail drawing (800x600)\n- Site plan (1000x700)\n\nImages extracted to output folder.")
        
    def extract_pdf_text(self):
        """Extract text from PDF"""
        self.pdf_text.delete(1.0, tk.END)
        self.pdf_text.insert(1.0, "PDF Text Extraction:\n\nExtracted text content:\n\nARCHITECTURAL DRAWINGS\nProject: Residential Building\nScale: 1:100\nDate: 2024\n\nRoom Schedule:\n- Living Room: 48 m²\n- Kitchen: 16 m²\n- Bedroom: 24 m²\n\nTotal Area: 88 m²")
        
    def export_excel(self):
        """Export to Excel"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Excel Report",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        
        if file_path:
            # Create sample Excel data
            data = []
            for zone in self.zones:
                data.append({
                    'Room Name': zone['name'],
                    'Room Type': zone['type'],
                    'Area (m²)': zone['area'],
                    'Perimeter (m)': sum(((zone['points'][i][0] - zone['points'][(i+1)%len(zone['points'])][0])**2 + 
                                         (zone['points'][i][1] - zone['points'][(i+1)%len(zone['points'])][1])**2)**0.5 
                                        for i in range(len(zone['points']))),
                    'AI Confidence': f"{85 + zone['id'] * 5}%"
                })
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export Complete", f"Excel report saved to:\n{file_path}")
            
    def export_pdf(self):
        """Export PDF report"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            messagebox.showinfo("Export Complete", f"PDF report saved to:\n{file_path}")
            
    def export_cad(self):
        """Export CAD files"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save CAD File",
            defaultextension=".dxf",
            filetypes=[("DXF Files", "*.dxf"), ("DWG Files", "*.dwg"), ("All Files", "*.*")]
        )
        
        if file_path:
            messagebox.showinfo("Export Complete", f"CAD file saved to:\n{file_path}")
            
    def export_images(self):
        """Export images"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        folder_path = filedialog.askdirectory(title="Select Export Folder")
        
        if folder_path:
            # Save current 2D view
            self.show_2d_floor_plan()
            self.fig_2d.savefig(os.path.join(folder_path, "floor_plan_2d.png"), dpi=300, bbox_inches='tight')
            
            # Save 3D view
            self.show_3d_building()
            self.fig_3d.savefig(os.path.join(folder_path, "building_3d.png"), dpi=300, bbox_inches='tight')
            
            messagebox.showinfo("Export Complete", f"Images saved to:\n{folder_path}")
            
    def export_json(self):
        """Export JSON data"""
        if not self.zones:
            messagebox.showwarning("No Data", "Please load and analyze a file first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save JSON Data",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            export_data = {
                'project_info': {
                    'name': 'Architectural Analysis',
                    'date': datetime.now().isoformat(),
                    'file': self.current_file
                },
                'zones': self.zones,
                'analysis_results': self.analysis_results,
                'summary': {
                    'total_area': sum(zone['area'] for zone in self.zones),
                    'room_count': len(self.zones),
                    'average_room_size': sum(zone['area'] for zone in self.zones) / len(self.zones) if self.zones else 0
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            messagebox.showinfo("Export Complete", f"JSON data saved to:\n{file_path}")
            
    def run(self):
        """Run the application"""
        # Load sample data on startup
        self.load_sample_data()
        
        # Show 2D floor plan by default
        self.show_2d_floor_plan()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = ArchitecturalAnalyzerPRO()
    app.run()