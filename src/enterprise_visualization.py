"""
ENTERPRISE VISUALIZATION ENGINE - Advanced 2D and 3D visualization with client-matching expectations
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import cv2

class EnterpriseVisualizationEngine:
    """Enterprise-grade visualization engine for architectural layouts"""
    
    def __init__(self):
        self.color_schemes = {
            'professional': {
                'walls': '#2C3E50',
                'restricted': '#E74C3C',
                'entrances': '#27AE60',
                'corridors': '#F8F9FA',
                'ilots': {
                    'standard_office': '#3498DB',
                    'executive_office': '#E74C3C',
                    'meeting_room': '#F39C12',
                    'open_workspace': '#27AE60',
                    'collaboration_zone': '#9B59B6',
                    'storage_unit': '#95A5A6',
                    'reception_area': '#E67E22'
                }
            },
            'accessibility': {
                'accessible_paths': '#27AE60',
                'barriers': '#E74C3C',
                'ramps': '#F39C12',
                'elevators': '#3498DB'
            },
            'security': {
                'high_security': '#C0392B',
                'medium_security': '#E67E22',
                'low_security': '#F1C40F',
                'public_access': '#27AE60'
            }
        }
        
        self.visualization_settings = {
            'dpi': 300,
            'figure_size': (16, 12),
            'line_width': 2,
            'font_size': 12,
            'title_font_size': 16,
            'grid_alpha': 0.3
        }
    
    def create_comprehensive_layout_visualization(self, 
                                                layout_data: Dict[str, Any],
                                                dxf_data: Dict[str, Any],
                                                view_type: str = '2d') -> Dict[str, Any]:
        """Create comprehensive layout visualization matching client expectations"""
        
        if view_type == '2d':
            return self._create_2d_comprehensive_view(layout_data, dxf_data)
        elif view_type == '3d':
            return self._create_3d_comprehensive_view(layout_data, dxf_data)
        elif view_type == 'both':
            return {
                '2d_view': self._create_2d_comprehensive_view(layout_data, dxf_data),
                '3d_view': self._create_3d_comprehensive_view(layout_data, dxf_data)
            }
        else:
            raise ValueError("view_type must be '2d', '3d', or 'both'")
    
    def _create_2d_comprehensive_view(self, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive 2D visualization"""
        
        fig = go.Figure()
        
        # Add walls with precise styling
        self._add_walls_to_2d_plot(fig, dxf_data.get('walls', []))
        
        # Add restricted areas with color coding
        self._add_restricted_areas_to_2d_plot(fig, dxf_data.get('restricted_areas', []))
        
        # Add entrances/exits with clear marking
        self._add_entrances_to_2d_plot(fig, dxf_data.get('entrances_exits', []))
        
        # Add îlots with profile-based styling
        self._add_ilots_to_2d_plot(fig, layout_data.get('ilots', []))
        
        # Add corridor system
        self._add_corridors_to_2d_plot(fig, layout_data.get('corridors', {}))
        
        # Add annotations and labels
        self._add_2d_annotations(fig, layout_data, dxf_data)
        
        # Configure layout
        self._configure_2d_layout(fig, layout_data, dxf_data)
        
        return fig
    
    def _create_3d_comprehensive_view(self, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive 3D visualization"""
        
        fig = go.Figure()
        
        # Add 3D walls with height
        self._add_walls_to_3d_plot(fig, dxf_data.get('walls', []))
        
        # Add 3D îlots with varying heights
        self._add_ilots_to_3d_plot(fig, layout_data.get('ilots', []))
        
        # Add 3D corridor system
        self._add_corridors_to_3d_plot(fig, layout_data.get('corridors', {}))
        
        # Add 3D restricted areas
        self._add_restricted_areas_to_3d_plot(fig, dxf_data.get('restricted_areas', []))
        
        # Add 3D entrances
        self._add_entrances_to_3d_plot(fig, dxf_data.get('entrances_exits', []))
        
        # Configure 3D layout
        self._configure_3d_layout(fig, layout_data, dxf_data)
        
        return fig
    
    def _add_walls_to_2d_plot(self, fig: go.Figure, walls: List[Dict[str, Any]]):
        """Add walls to 2D plot with precise styling"""
        
        for wall in walls:
            if 'start_point' in wall and 'end_point' in wall:
                start = wall['start_point']
                end = wall['end_point']
                
                # Determine wall color based on type/layer
                wall_color = self._get_wall_color(wall)
                wall_width = self._get_wall_width(wall)
                
                fig.add_trace(go.Scatter(
                    x=[start[0], end[0]],
                    y=[start[1], end[1]],
                    mode='lines',
                    line=dict(
                        color=wall_color,
                        width=wall_width
                    ),
                    name=f"Wall ({wall.get('layer', 'Unknown')})",
                    showlegend=False,
                    hovertemplate=f"<b>Wall</b><br>Layer: {wall.get('layer', 'Unknown')}<br>Length: {wall.get('length', 0):.1f}cm<extra></extra>"
                ))
            
            elif 'points' in wall:
                points = wall['points']
                if len(points) >= 2:
                    x_coords = [p[0] for p in points] + [points[0][0]]
                    y_coords = [p[1] for p in points] + [points[0][1]]
                    
                    wall_color = self._get_wall_color(wall)
                    
                    fig.add_trace(go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode='lines',
                        line=dict(
                            color=wall_color,
                            width=4
                        ),
                        fill='toself',
                        fillcolor=f"rgba{self._hex_to_rgba(wall_color, 0.1)}",
                        name=f"Wall System ({wall.get('layer', 'Unknown')})",
                        showlegend=False
                    ))
    
    def _add_restricted_areas_to_2d_plot(self, fig: go.Figure, restricted_areas: List[Dict[str, Any]]):
        """Add restricted areas with color coding"""
        
        restriction_colors = {
            'NO_ACCESS': '#C0392B',
            'LIMITED_ACCESS': '#E67E22',
            'SECURITY_ZONE': '#8E44AD',
            'RESTRICTED': '#E74C3C'
        }
        
        for area in restricted_areas:
            if 'geometry' in area:
                points = area['geometry']
                if len(points) >= 3:
                    x_coords = [p[0] for p in points] + [points[0][0]]
                    y_coords = [p[1] for p in points] + [points[0][1]]
                    
                    restriction_type = area.get('restriction_type', 'RESTRICTED')
                    color = restriction_colors.get(restriction_type, '#E74C3C')
                    
                    fig.add_trace(go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode='lines',
                        line=dict(
                            color=color,
                            width=3,
                            dash='dash'
                        ),
                        fill='toself',
                        fillcolor=f"rgba{self._hex_to_rgba(color, 0.3)}",
                        name=f"Restricted: {restriction_type}",
                        hovertemplate=f"<b>Restricted Area</b><br>Type: {restriction_type}<br>Area: {area.get('area', 0):.1f}cm²<extra></extra>"
                    ))
    
    def _add_entrances_to_2d_plot(self, fig: go.Figure, entrances: List[Dict[str, Any]]):
        """Add entrances/exits with clear marking"""
        
        entrance_symbols = {
            'ENTRANCE': 'triangle-up',
            'EXIT': 'triangle-down',
            'DOOR': 'square',
            'ARC_DOOR': 'circle'
        }
        
        for entrance in entrances:
            location = entrance.get('location', (0, 0))
            entrance_type = entrance.get('type', 'ENTRANCE')
            symbol = entrance_symbols.get(entrance_type, 'diamond')
            
            fig.add_trace(go.Scatter(
                x=[location[0]],
                y=[location[1]],
                mode='markers',
                marker=dict(
                    symbol=symbol,
                    size=15,
                    color='#27AE60',
                    line=dict(color='#1E8449', width=2)
                ),
                name=f"{entrance_type}",
                hovertemplate=f"<b>{entrance_type}</b><br>Location: ({location[0]:.1f}, {location[1]:.1f})<br>Method: {entrance.get('detection_method', 'Unknown')}<extra></extra>"
            ))
    
    def _add_ilots_to_2d_plot(self, fig: go.Figure, ilots: List[Dict[str, Any]]):
        """Add îlots with profile-based styling"""
        
        for ilot in ilots:
            if not ilot.get('placed', False):
                continue
            
            geometry = ilot.get('geometry')
            if geometry and hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [c[0] for c in coords]
                y_coords = [c[1] for c in coords]
                
                profile_name = ilot.get('profile', {}).name if hasattr(ilot.get('profile', {}), 'name') else 'Unknown'
                color = ilot.get('color', '#3498DB')
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines',
                    line=dict(
                        color=color,
                        width=3
                    ),
                    fill='toself',
                    fillcolor=f"rgba{self._hex_to_rgba(color, 0.6)}",
                    name=f"Îlot: {profile_name}",
                    hovertemplate=f"<b>{profile_name}</b><br>ID: {ilot.get('id', 'Unknown')}<br>Area: {ilot.get('area', 0):.1f}cm²<br>Score: {ilot.get('placement_score', 0):.2f}<extra></extra>"
                ))
                
                # Add îlot label
                centroid = geometry.centroid
                fig.add_annotation(
                    x=centroid.x,
                    y=centroid.y,
                    text=f"<b>{ilot.get('id', '')}</b>",
                    showarrow=False,
                    font=dict(size=10, color='white'),
                    bgcolor=color,
                    bordercolor='white',
                    borderwidth=1
                )
    
    def _add_corridors_to_2d_plot(self, fig: go.Figure, corridor_system: Dict[str, Any]):
        """Add corridor system to 2D plot"""
        
        corridor_geometries = corridor_system.get('geometry', [])
        
        for corridor in corridor_geometries:
            geometry = corridor.get('geometry')
            if geometry and hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [c[0] for c in coords]
                y_coords = [c[1] for c in coords]
                
                corridor_type = corridor.get('type', 'secondary_circulation')
                color = '#BDC3C7' if corridor_type == 'secondary_circulation' else '#85929E'
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines',
                    line=dict(
                        color=color,
                        width=2
                    ),
                    fill='toself',
                    fillcolor=f"rgba{self._hex_to_rgba(color, 0.4)}",
                    name=f"Corridor: {corridor_type}",
                    showlegend=False,
                    hovertemplate=f"<b>Corridor</b><br>Type: {corridor_type}<br>Width: {corridor.get('width', 0):.1f}cm<br>Length: {corridor.get('length', 0):.1f}cm<extra></extra>"
                ))
    
    def _add_2d_annotations(self, fig: go.Figure, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]):
        """Add annotations and labels to 2D plot"""
        
        # Add title annotation
        metrics = layout_data.get('layout_metrics', {})
        
        title_text = f"<b>Enterprise Layout Plan</b><br>"
        title_text += f"Îlots: {metrics.get('placed_ilots', 0)}/{metrics.get('total_ilots', 0)} | "
        title_text += f"Space Utilization: {metrics.get('space_utilization', 0):.1%} | "
        title_text += f"Compliance: {layout_data.get('validation', {}).get('compliance_score', 0):.1%}"
        
        fig.add_annotation(
            x=0.5,
            y=1.05,
            xref='paper',
            yref='paper',
            text=title_text,
            showarrow=False,
            font=dict(size=14),
            align='center'
        )
        
        # Add legend for color coding
        self._add_color_legend(fig)
    
    def _configure_2d_layout(self, fig: go.Figure, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]):
        """Configure 2D plot layout"""
        
        fig.update_layout(
            title="Enterprise Architectural Layout - 2D View",
            xaxis=dict(
                title="X Coordinate (cm)",
                scaleanchor="y",
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                title="Y Coordinate (cm)",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=800,
            width=1200
        )
    
    def _add_walls_to_3d_plot(self, fig: go.Figure, walls: List[Dict[str, Any]]):
        """Add walls to 3D plot with height"""
        
        wall_height = 280  # 2.8m standard wall height
        
        for wall in walls:
            if 'start_point' in wall and 'end_point' in wall:
                start = wall['start_point']
                end = wall['end_point']
                
                # Create wall as 3D surface
                wall_vertices = self._create_3d_wall_vertices(start, end, wall_height)
                
                fig.add_trace(go.Mesh3d(
                    x=wall_vertices['x'],
                    y=wall_vertices['y'],
                    z=wall_vertices['z'],
                    i=wall_vertices['i'],
                    j=wall_vertices['j'],
                    k=wall_vertices['k'],
                    color='#2C3E50',
                    opacity=0.8,
                    name=f"Wall ({wall.get('layer', 'Unknown')})",
                    showlegend=False
                ))
    
    def _add_ilots_to_3d_plot(self, fig: go.Figure, ilots: List[Dict[str, Any]]):
        """Add îlots to 3D plot with varying heights"""
        
        for ilot in ilots:
            if not ilot.get('placed', False):
                continue
            
            geometry = ilot.get('geometry')
            if geometry and hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)[:-1]  # Remove duplicate last point
                
                # Determine îlot height based on type
                ilot_height = self._get_ilot_3d_height(ilot)
                color = ilot.get('color', '#3498DB')
                
                # Create 3D îlot
                vertices = self._create_3d_ilot_vertices(coords, ilot_height)
                
                fig.add_trace(go.Mesh3d(
                    x=vertices['x'],
                    y=vertices['y'],
                    z=vertices['z'],
                    i=vertices['i'],
                    j=vertices['j'],
                    k=vertices['k'],
                    color=color,
                    opacity=0.7,
                    name=f"Îlot: {ilot.get('id', 'Unknown')}",
                    hovertemplate=f"<b>{ilot.get('id', 'Unknown')}</b><br>Height: {ilot_height}cm<extra></extra>"
                ))
    
    def _add_corridors_to_3d_plot(self, fig: go.Figure, corridor_system: Dict[str, Any]):
        """Add corridor system to 3D plot"""
        
        corridor_geometries = corridor_system.get('geometry', [])
        corridor_height = 20  # 20cm raised floor for corridors
        
        for corridor in corridor_geometries:
            geometry = corridor.get('geometry')
            if geometry and hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)[:-1]
                
                # Create 3D corridor
                vertices = self._create_3d_ilot_vertices(coords, corridor_height)
                
                fig.add_trace(go.Mesh3d(
                    x=vertices['x'],
                    y=vertices['y'],
                    z=vertices['z'],
                    i=vertices['i'],
                    j=vertices['j'],
                    k=vertices['k'],
                    color='#BDC3C7',
                    opacity=0.5,
                    name=f"Corridor",
                    showlegend=False
                ))
    
    def _add_restricted_areas_to_3d_plot(self, fig: go.Figure, restricted_areas: List[Dict[str, Any]]):
        """Add restricted areas to 3D plot"""
        
        for area in restricted_areas:
            if 'geometry' in area:
                points = area['geometry']
                if len(points) >= 3:
                    # Create elevated restricted area
                    vertices = self._create_3d_ilot_vertices(points, 50)  # 50cm height
                    
                    fig.add_trace(go.Mesh3d(
                        x=vertices['x'],
                        y=vertices['y'],
                        z=vertices['z'],
                        i=vertices['i'],
                        j=vertices['j'],
                        k=vertices['k'],
                        color='#E74C3C',
                        opacity=0.6,
                        name=f"Restricted Area",
                        showlegend=False
                    ))
    
    def _add_entrances_to_3d_plot(self, fig: go.Figure, entrances: List[Dict[str, Any]]):
        """Add entrances to 3D plot"""
        
        for entrance in entrances:
            location = entrance.get('location', (0, 0))
            
            # Create 3D entrance marker
            fig.add_trace(go.Scatter3d(
                x=[location[0]],
                y=[location[1]],
                z=[150],  # 1.5m height
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=10,
                    color='#27AE60'
                ),
                name=f"Entrance",
                showlegend=False
            ))
    
    def _configure_3d_layout(self, fig: go.Figure, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]):
        """Configure 3D plot layout"""
        
        fig.update_layout(
            title="Enterprise Architectural Layout - 3D View",
            scene=dict(
                xaxis=dict(title="X Coordinate (cm)"),
                yaxis=dict(title="Y Coordinate (cm)"),
                zaxis=dict(title="Height (cm)"),
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1
            ),
            font=dict(size=12),
            height=800,
            width=1200
        )
    
    def create_analysis_dashboard(self, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]) -> go.Figure:
        """Create comprehensive analysis dashboard"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                'Space Utilization', 'Îlot Distribution', 'Corridor Analysis',
                'Compliance Metrics', 'Accessibility Analysis', 'Security Zones'
            ],
            specs=[
                [{'type': 'indicator'}, {'type': 'pie'}, {'type': 'bar'}],
                [{'type': 'bar'}, {'type': 'scatter'}, {'type': 'heatmap'}]
            ]
        )
        
        metrics = layout_data.get('layout_metrics', {})
        validation = layout_data.get('validation', {})
        
        # Space Utilization Gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=metrics.get('space_utilization', 0) * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Space Utilization %"},
                delta={'reference': 75},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Îlot Distribution Pie Chart
        ilot_types = {}
        for ilot in layout_data.get('ilots', []):
            if ilot.get('placed', False):
                profile_name = ilot.get('profile', {}).name if hasattr(ilot.get('profile', {}), 'name') else 'Unknown'
                ilot_types[profile_name] = ilot_types.get(profile_name, 0) + 1
        
        if ilot_types:
            fig.add_trace(
                go.Pie(
                    labels=list(ilot_types.keys()),
                    values=list(ilot_types.values()),
                    name="Îlot Types"
                ),
                row=1, col=2
            )
        
        # Corridor Analysis Bar Chart
        corridor_data = layout_data.get('corridors', {})
        corridor_types = {}
        for corridor in corridor_data.get('corridors', []):
            corridor_type = corridor.get('type', 'Unknown')
            corridor_types[corridor_type] = corridor_types.get(corridor_type, 0) + corridor.get('length', 0)
        
        if corridor_types:
            fig.add_trace(
                go.Bar(
                    x=list(corridor_types.keys()),
                    y=list(corridor_types.values()),
                    name="Corridor Length by Type"
                ),
                row=1, col=3
            )
        
        # Compliance Metrics
        compliance_categories = ['Placement Rate', 'Accessibility', 'Fire Safety', 'Space Efficiency']
        compliance_scores = [
            metrics.get('placement_rate', 0) * 100,
            85,  # Placeholder for accessibility score
            90,  # Placeholder for fire safety score
            metrics.get('space_utilization', 0) * 100
        ]
        
        fig.add_trace(
            go.Bar(
                x=compliance_categories,
                y=compliance_scores,
                name="Compliance Scores",
                marker_color=['green' if score >= 80 else 'orange' if score >= 60 else 'red' for score in compliance_scores]
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title="Enterprise Layout Analysis Dashboard",
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_accessibility_analysis(self, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]) -> go.Figure:
        """Create accessibility analysis visualization"""
        
        fig = go.Figure()
        
        # Add base layout elements
        self._add_walls_to_2d_plot(fig, dxf_data.get('walls', []))
        self._add_ilots_to_2d_plot(fig, layout_data.get('ilots', []))
        
        # Add accessibility paths
        corridor_system = layout_data.get('corridors', {})
        for corridor in corridor_system.get('geometry', []):
            geometry = corridor.get('geometry')
            if geometry and hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [c[0] for c in coords]
                y_coords = [c[1] for c in coords]
                
                # Color code based on accessibility compliance
                width = corridor.get('width', 0)
                if width >= 150:  # Wheelchair accessible
                    color = '#27AE60'
                    opacity = 0.7
                elif width >= 120:  # Minimum accessible
                    color = '#F39C12'
                    opacity = 0.6
                else:  # Not accessible
                    color = '#E74C3C'
                    opacity = 0.5
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines',
                    line=dict(color=color, width=4),
                    fill='toself',
                    fillcolor=f"rgba{self._hex_to_rgba(color, opacity)}",
                    name=f"Accessibility: {'Full' if width >= 150 else 'Limited' if width >= 120 else 'None'}",
                    hovertemplate=f"<b>Corridor Width: {width}cm</b><br>Accessibility: {'Full' if width >= 150 else 'Limited' if width >= 120 else 'None'}<extra></extra>"
                ))
        
        fig.update_layout(
            title="Accessibility Analysis - Corridor Width Compliance",
            xaxis=dict(title="X Coordinate (cm)", scaleanchor="y", scaleratio=1),
            yaxis=dict(title="Y Coordinate (cm)"),
            showlegend=True,
            height=700
        )
        
        return fig
    
    def create_security_analysis(self, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]) -> go.Figure:
        """Create security analysis visualization"""
        
        fig = go.Figure()
        
        # Add base layout
        self._add_walls_to_2d_plot(fig, dxf_data.get('walls', []))
        
        # Add security zones from spatial analysis
        spatial_analysis = dxf_data.get('spatial_analysis', {})
        security_zones = spatial_analysis.get('security_zones', [])
        
        security_colors = {
            'HIGH': '#C0392B',
            'MEDIUM': '#E67E22',
            'LOW': '#F1C40F'
        }
        
        for zone in security_zones:
            geometry = zone.get('area_geometry', [])
            if len(geometry) >= 3:
                x_coords = [p[0] for p in geometry] + [geometry[0][0]]
                y_coords = [p[1] for p in geometry] + [geometry[0][1]]
                
                security_level = zone.get('security_level', 'LOW')
                color = security_colors.get(security_level, '#F1C40F')
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines',
                    line=dict(color=color, width=3),
                    fill='toself',
                    fillcolor=f"rgba{self._hex_to_rgba(color, 0.4)}",
                    name=f"Security: {security_level}",
                    hovertemplate=f"<b>Security Level: {security_level}</b><br>Access Points: {zone.get('access_points', 0)}<br>Area: {zone.get('area_size', 0):.1f}cm²<extra></extra>"
                ))
        
        # Add entrances with security context
        self._add_entrances_to_2d_plot(fig, dxf_data.get('entrances_exits', []))
        
        fig.update_layout(
            title="Security Analysis - Access Control Zones",
            xaxis=dict(title="X Coordinate (cm)", scaleanchor="y", scaleratio=1),
            yaxis=dict(title="Y Coordinate (cm)"),
            showlegend=True,
            height=700
        )
        
        return fig
    
    def export_visualization_data(self, layout_data: Dict[str, Any], dxf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export visualization data for external use"""
        
        export_data = {
            'metadata': {
                'export_type': 'visualization_data',
                'timestamp': pd.Timestamp.now().isoformat(),
                'version': '1.0.0'
            },
            'layout_elements': {
                'walls': self._export_walls_data(dxf_data.get('walls', [])),
                'ilots': self._export_ilots_data(layout_data.get('ilots', [])),
                'corridors': self._export_corridors_data(layout_data.get('corridors', {})),
                'restricted_areas': self._export_restricted_areas_data(dxf_data.get('restricted_areas', [])),
                'entrances': self._export_entrances_data(dxf_data.get('entrances_exits', []))
            },
            'color_schemes': self.color_schemes,
            'metrics': layout_data.get('layout_metrics', {}),
            'validation': layout_data.get('validation', {})
        }
        
        return export_data
    
    # Helper methods
    
    def _get_wall_color(self, wall: Dict[str, Any]) -> str:
        """Get wall color based on properties"""
        layer = wall.get('layer', '').upper()
        
        if 'EXTERIOR' in layer or 'EXTERNAL' in layer:
            return '#1B2631'
        elif 'INTERIOR' in layer or 'INTERNAL' in layer:
            return '#2C3E50'
        else:
            return '#34495E'
    
    def _get_wall_width(self, wall: Dict[str, Any]) -> int:
        """Get wall line width based on properties"""
        thickness = wall.get('thickness', 0.25)
        
        if thickness > 0.5:
            return 6
        elif thickness > 0.3:
            return 4
        else:
            return 3
    
    def _get_ilot_3d_height(self, ilot: Dict[str, Any]) -> float:
        """Get îlot 3D height based on type"""
        profile = ilot.get('profile', {})
        
        if hasattr(profile, 'name'):
            profile_name = profile.name
        else:
            profile_name = 'standard_office'
        
        height_mapping = {
            'standard_office': 120,
            'executive_office': 150,
            'meeting_room': 100,
            'open_workspace': 80,
            'collaboration_zone': 90,
            'storage_unit': 200,
            'reception_area': 110
        }
        
        return height_mapping.get(profile_name, 120)
    
    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to rgba string"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
    
    def _create_3d_wall_vertices(self, start: Tuple[float, float], end: Tuple[float, float], height: float) -> Dict[str, List]:
        """Create 3D wall vertices"""
        
        # Calculate wall thickness (assume 20cm)
        thickness = 20
        
        # Calculate perpendicular vector
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = np.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return {'x': [], 'y': [], 'z': [], 'i': [], 'j': [], 'k': []}
        
        perp_x = -dy / length * thickness / 2
        perp_y = dx / length * thickness / 2
        
        # Create 8 vertices for the wall box
        vertices = [
            [start[0] + perp_x, start[1] + perp_y, 0],
            [end[0] + perp_x, end[1] + perp_y, 0],
            [end[0] - perp_x, end[1] - perp_y, 0],
            [start[0] - perp_x, start[1] - perp_y, 0],
            [start[0] + perp_x, start[1] + perp_y, height],
            [end[0] + perp_x, end[1] + perp_y, height],
            [end[0] - perp_x, end[1] - perp_y, height],
            [start[0] - perp_x, start[1] - perp_y, height]
        ]
        
        x = [v[0] for v in vertices]
        y = [v[1] for v in vertices]
        z = [v[2] for v in vertices]
        
        # Define faces (triangles)
        i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        j = [1, 4, 2, 5, 3, 6, 0, 7, 5, 7, 6, 4]
        k = [4, 5, 5, 6, 6, 7, 7, 4, 7, 6, 4, 5]
        
        return {'x': x, 'y': y, 'z': z, 'i': i, 'j': j, 'k': k}
    
    def _create_3d_ilot_vertices(self, coords: List[Tuple[float, float]], height: float) -> Dict[str, List]:
        """Create 3D îlot vertices"""
        
        n = len(coords)
        if n < 3:
            return {'x': [], 'y': [], 'z': [], 'i': [], 'j': [], 'k': []}
        
        # Bottom vertices
        x = [c[0] for c in coords]
        y = [c[1] for c in coords]
        z = [0] * n
        
        # Top vertices
        x.extend([c[0] for c in coords])
        y.extend([c[1] for c in coords])
        z.extend([height] * n)
        
        # Create triangular faces
        i, j, k = [], [], []
        
        # Bottom face
        for i_idx in range(1, n - 1):
            i.extend([0, 0, 0])
            j.extend([i_idx, i_idx, i_idx])
            k.extend([i_idx + 1, i_idx + 1, i_idx + 1])
        
        # Top face
        for i_idx in range(1, n - 1):
            i.extend([n, n, n])
            j.extend([n + i_idx + 1, n + i_idx + 1, n + i_idx + 1])
            k.extend([n + i_idx, n + i_idx, n + i_idx])
        
        # Side faces
        for i_idx in range(n):
            next_idx = (i_idx + 1) % n
            # Two triangles per side face
            i.extend([i_idx, i_idx])
            j.extend([next_idx, n + i_idx])
            k.extend([n + i_idx, n + next_idx])
            
            i.extend([next_idx, next_idx])
            j.extend([n + next_idx, n + next_idx])
            k.extend([n + i_idx, n + i_idx])
        
        return {'x': x, 'y': y, 'z': z, 'i': i, 'j': j, 'k': k}
    
    def _add_color_legend(self, fig: go.Figure):
        """Add color legend for different elements"""
        
        legend_items = [
            {'name': 'Walls', 'color': '#2C3E50'},
            {'name': 'Restricted Areas', 'color': '#E74C3C'},
            {'name': 'Entrances/Exits', 'color': '#27AE60'},
            {'name': 'Corridors', 'color': '#BDC3C7'},
            {'name': 'Standard Office', 'color': '#3498DB'},
            {'name': 'Executive Office', 'color': '#E74C3C'},
            {'name': 'Meeting Room', 'color': '#F39C12'}
        ]
        
        for item in legend_items:
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=item['color']),
                name=item['name'],
                showlegend=True
            ))
    
    def _export_walls_data(self, walls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export walls data for visualization"""
        exported_walls = []
        
        for wall in walls:
            wall_data = {
                'type': wall.get('type', 'WALL'),
                'layer': wall.get('layer', 'Unknown'),
                'color': self._get_wall_color(wall),
                'width': self._get_wall_width(wall)
            }
            
            if 'start_point' in wall and 'end_point' in wall:
                wall_data.update({
                    'geometry_type': 'line',
                    'start_point': wall['start_point'],
                    'end_point': wall['end_point'],
                    'length': wall.get('length', 0)
                })
            elif 'points' in wall:
                wall_data.update({
                    'geometry_type': 'polyline',
                    'points': wall['points']
                })
            
            exported_walls.append(wall_data)
        
        return exported_walls
    
    def _export_ilots_data(self, ilots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export îlots data for visualization"""
        exported_ilots = []
        
        for ilot in ilots:
            if ilot.get('placed', False):
                geometry = ilot.get('geometry')
                coords = list(geometry.exterior.coords) if geometry and hasattr(geometry, 'exterior') else []
                
                ilot_data = {
                    'id': ilot.get('id', 'Unknown'),
                    'profile_name': ilot.get('profile', {}).name if hasattr(ilot.get('profile', {}), 'name') else 'Unknown',
                    'position': ilot.get('position', (0, 0)),
                    'rotation': ilot.get('rotation', 0),
                    'color': ilot.get('color', '#3498DB'),
                    'geometry': coords,
                    'area': ilot.get('area', 0),
                    'placement_score': ilot.get('placement_score', 0),
                    'height_3d': self._get_ilot_3d_height(ilot)
                }
                
                exported_ilots.append(ilot_data)
        
        return exported_ilots
    
    def _export_corridors_data(self, corridor_system: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export corridors data for visualization"""
        exported_corridors = []
        
        for corridor in corridor_system.get('geometry', []):
            geometry = corridor.get('geometry')
            coords = list(geometry.exterior.coords) if geometry and hasattr(geometry, 'exterior') else []
            
            corridor_data = {
                'id': corridor.get('id', 'Unknown'),
                'type': corridor.get('type', 'secondary_circulation'),
                'width': corridor.get('width', 0),
                'length': corridor.get('length', 0),
                'geometry': coords,
                'color': '#BDC3C7' if corridor.get('type') == 'secondary_circulation' else '#85929E'
            }
            
            exported_corridors.append(corridor_data)
        
        return exported_corridors
    
    def _export_restricted_areas_data(self, restricted_areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export restricted areas data for visualization"""
        exported_areas = []
        
        restriction_colors = {
            'NO_ACCESS': '#C0392B',
            'LIMITED_ACCESS': '#E67E22',
            'SECURITY_ZONE': '#8E44AD',
            'RESTRICTED': '#E74C3C'
        }
        
        for area in restricted_areas:
            area_data = {
                'type': area.get('type', 'RESTRICTED_AREA'),
                'restriction_type': area.get('restriction_type', 'RESTRICTED'),
                'geometry': area.get('geometry', []),
                'area': area.get('area', 0),
                'centroid': area.get('centroid', (0, 0)),
                'color': restriction_colors.get(area.get('restriction_type', 'RESTRICTED'), '#E74C3C'),
                'detection_method': area.get('detection_method', 'Unknown')
            }
            
            exported_areas.append(area_data)
        
        return exported_areas
    
    def _export_entrances_data(self, entrances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export entrances data for visualization"""
        exported_entrances = []
        
        entrance_symbols = {
            'ENTRANCE': 'triangle-up',
            'EXIT': 'triangle-down',
            'DOOR': 'square',
            'ARC_DOOR': 'circle'
        }
        
        for entrance in entrances:
            entrance_data = {
                'type': entrance.get('type', 'ENTRANCE'),
                'location': entrance.get('location', (0, 0)),
                'symbol': entrance_symbols.get(entrance.get('type', 'ENTRANCE'), 'diamond'),
                'color': '#27AE60',
                'detection_method': entrance.get('detection_method', 'Unknown')
            }
            
            if 'rotation' in entrance:
                entrance_data['rotation'] = entrance['rotation']
            if 'width' in entrance:
                entrance_data['width'] = entrance['width']
            
            exported_entrances.append(entrance_data)
        
        return exported_entrances