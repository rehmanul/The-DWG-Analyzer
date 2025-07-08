"""
Professional Architectural Visualization Engine
Creates high-quality visualizations matching client expectations
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, Point, box
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st

class ProfessionalVisualizationEngine:
    """Professional visualization engine for architectural layouts"""
    
    def __init__(self):
        self.color_schemes = {
            'walls': '#2C3E50',
            'restricted': '#3498DB',  # Blue for restricted areas
            'entrances': '#E74C3C',   # Red for entrances
            'corridors': '#ECF0F1',   # Light gray for corridors
            'ilots': {
                'small': '#27AE60',   # Green for small îlots
                'medium': '#F39C12',  # Orange for medium îlots
                'large': '#9B59B6',   # Purple for large îlots
                'extra_large': '#E67E22'  # Dark orange for extra large
            },
            'furniture': {
                'desk': '#8B4513',
                'chair': '#2F4F4F',
                'table': '#CD853F',
                'cabinet': '#556B2F'
            }
        }
        
        # Professional styling settings
        self.plot_settings = {
            'background_color': '#FFFFFF',
            'grid_color': '#E8E8E8',
            'text_color': '#2C3E50',
            'line_width': 2,
            'font_family': 'Arial, sans-serif',
            'font_size': 12
        }
    
    def create_professional_floor_plan(self, 
                                     zones: Dict[str, List[Dict]], 
                                     ilots: List[Dict],
                                     corridors: List[Dict],
                                     bounds: Tuple[float, float, float, float]) -> go.Figure:
        """Create professional floor plan visualization"""
        
        fig = go.Figure()
        
        # Set professional layout
        fig.update_layout(
            title={
                'text': 'Professional Architectural Floor Plan Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': self.plot_settings['font_family']}
            },
            xaxis=dict(
                title='Distance (meters)',
                showgrid=True,
                gridcolor=self.plot_settings['grid_color'],
                zeroline=False,
                showline=True,
                linecolor='black',
                mirror=True
            ),
            yaxis=dict(
                title='Distance (meters)',
                showgrid=True,
                gridcolor=self.plot_settings['grid_color'],
                zeroline=False,
                showline=True,
                linecolor='black',
                mirror=True,
                scaleanchor="x",
                scaleratio=1
            ),
            plot_bgcolor=self.plot_settings['background_color'],
            paper_bgcolor=self.plot_settings['background_color'],
            font=dict(family=self.plot_settings['font_family'], size=self.plot_settings['font_size']),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='black',
                borderwidth=1
            ),
            width=1200,
            height=800
        )
        
        # Add walls with professional styling
        self._add_walls_professional(fig, zones.get('walls', []))
        
        # Add restricted areas (blue zones)
        self._add_restricted_areas_professional(fig, zones.get('restricted', []))
        
        # Add entrances (red zones)
        self._add_entrances_professional(fig, zones.get('entrances', []))
        
        # Add corridors
        self._add_corridors_professional(fig, corridors)
        
        # Add îlots with detailed styling
        self._add_ilots_professional(fig, ilots)
        
        # Add furniture representations
        self._add_furniture_representations(fig, ilots)
        
        # Add annotations and labels
        self._add_professional_annotations(fig, zones, ilots, bounds)
        
        return fig
    
    def _add_walls_professional(self, fig: go.Figure, walls: List[Dict]):
        """Add walls with professional styling"""
        for i, wall in enumerate(walls):
            points = wall.get('points', [])
            if len(points) >= 2:
                x_coords = [p[0] for p in points] + [points[0][0]]
                y_coords = [p[1] for p in points] + [points[0][1]]
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines',
                    line=dict(color=self.color_schemes['walls'], width=4),
                    name='Walls' if i == 0 else None,
                    showlegend=i == 0,
                    hoverinfo='text',
                    hovertext='Wall structure'
                ))
    
    def _add_restricted_areas_professional(self, fig: go.Figure, restricted: List[Dict]):
        """Add restricted areas with professional blue styling"""
        for i, area in enumerate(restricted):
            points = area.get('points', [])
            if len(points) >= 3:
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines',
                    fill='toself',
                    fillcolor='rgba(52, 152, 219, 0.3)',
                    line=dict(color=self.color_schemes['restricted'], width=2),
                    name='Restricted Areas' if i == 0 else None,
                    showlegend=i == 0,
                    hoverinfo='text',
                    hovertext='Restricted Area (Stairs, Elevators, etc.)'
                ))
    
    def _add_entrances_professional(self, fig: go.Figure, entrances: List[Dict]):
        """Add entrances with professional red styling"""
        for i, entrance in enumerate(entrances):
            points = entrance.get('points', [])
            if len(points) >= 2:
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='lines+markers',
                    line=dict(color=self.color_schemes['entrances'], width=4),
                    marker=dict(size=8, color=self.color_schemes['entrances']),
                    name='Entrances/Exits' if i == 0 else None,
                    showlegend=i == 0,
                    hoverinfo='text',
                    hovertext='Entrance/Exit'
                ))
    
    def _add_corridors_professional(self, fig: go.Figure, corridors: List[Dict]):
        """Add corridors with professional styling"""
        for i, corridor in enumerate(corridors):
            if 'geometry' in corridor:
                geom = corridor['geometry']
                if hasattr(geom, 'exterior'):
                    x_coords, y_coords = geom.exterior.xy
                    
                    fig.add_trace(go.Scatter(
                        x=list(x_coords),
                        y=list(y_coords),
                        mode='lines',
                        fill='toself',
                        fillcolor='rgba(236, 240, 241, 0.7)',
                        line=dict(color=self.color_schemes['corridors'], width=1),
                        name='Corridors' if i == 0 else None,
                        showlegend=i == 0,
                        hoverinfo='text',
                        hovertext='Corridor'
                    ))
    
    def _add_ilots_professional(self, fig: go.Figure, ilots: List[Dict]):
        """Add îlots with professional styling and size-based coloring"""
        size_categories = {}
        
        for ilot in ilots:
            category = ilot.get('category', 'medium')
            area = ilot.get('area', 0)
            
            if category not in size_categories:
                size_categories[category] = []
            size_categories[category].append(ilot)
        
        # Add îlots by category
        for category, ilot_list in size_categories.items():
            color = self.color_schemes['ilots'].get(category, self.color_schemes['ilots']['medium'])
            
            for i, ilot in enumerate(ilot_list):
                if 'geometry' in ilot:
                    geom = ilot['geometry']
                    if hasattr(geom, 'exterior'):
                        x_coords, y_coords = geom.exterior.xy
                        
                        fig.add_trace(go.Scatter(
                            x=list(x_coords),
                            y=list(y_coords),
                            mode='lines',
                            fill='toself',
                            fillcolor=f'rgba({self._hex_to_rgb(color)}, 0.6)',
                            line=dict(color=color, width=2),
                            name=f'Îlots ({category})' if i == 0 else None,
                            showlegend=i == 0,
                            hoverinfo='text',
                            hovertext=f'Îlot: {ilot.get("area", 0):.1f}m² ({category})'
                        ))
    
    def _add_furniture_representations(self, fig: go.Figure, ilots: List[Dict]):
        """Add furniture representations inside îlots"""
        for ilot in ilots:
            if 'geometry' in ilot:
                geom = ilot['geometry']
                if hasattr(geom, 'centroid'):
                    center = geom.centroid
                    area = ilot.get('area', 0)
                    
                    # Add furniture based on îlot size
                    if area < 5:  # Small îlot - single desk
                        fig.add_trace(go.Scatter(
                            x=[center.x],
                            y=[center.y],
                            mode='markers',
                            marker=dict(
                                size=12,
                                color=self.color_schemes['furniture']['desk'],
                                symbol='square',
                                line=dict(color='black', width=1)
                            ),
                            name='Furniture',
                            showlegend=False,
                            hoverinfo='text',
                            hovertext='Desk'
                        ))
                    elif area < 15:  # Medium îlot - desk and chair
                        fig.add_trace(go.Scatter(
                            x=[center.x - 0.3, center.x + 0.3],
                            y=[center.y, center.y],
                            mode='markers',
                            marker=dict(
                                size=[12, 8],
                                color=[self.color_schemes['furniture']['desk'], 
                                      self.color_schemes['furniture']['chair']],
                                symbol=['square', 'circle'],
                                line=dict(color='black', width=1)
                            ),
                            name='Furniture',
                            showlegend=False,
                            hoverinfo='text',
                            hovertext='Desk & Chair'
                        ))
                    else:  # Large îlot - meeting table
                        fig.add_trace(go.Scatter(
                            x=[center.x],
                            y=[center.y],
                            mode='markers',
                            marker=dict(
                                size=16,
                                color=self.color_schemes['furniture']['table'],
                                symbol='diamond',
                                line=dict(color='black', width=1)
                            ),
                            name='Furniture',
                            showlegend=False,
                            hoverinfo='text',
                            hovertext='Meeting Table'
                        ))
    
    def _add_professional_annotations(self, fig: go.Figure, zones: Dict, ilots: List[Dict], bounds: Tuple):
        """Add professional annotations and labels"""
        # Add scale indicator
        scale_length = 5  # 5 meters
        scale_x = bounds[0] + 1
        scale_y = bounds[1] + 1
        
        fig.add_trace(go.Scatter(
            x=[scale_x, scale_x + scale_length],
            y=[scale_y, scale_y],
            mode='lines',
            line=dict(color='black', width=3),
            name='Scale',
            showlegend=False
        ))
        
        fig.add_annotation(
            x=scale_x + scale_length/2,
            y=scale_y - 0.5,
            text=f"{scale_length}m",
            showarrow=False,
            font=dict(size=12, color='black')
        )
        
        # Add north arrow
        north_x = bounds[2] - 2
        north_y = bounds[3] - 2
        
        fig.add_annotation(
            x=north_x,
            y=north_y,
            text="N ↑",
            showarrow=False,
            font=dict(size=16, color='black', family='Arial Black')
        )
        
        # Add area statistics
        total_area = sum(ilot.get('area', 0) for ilot in ilots)
        ilot_count = len(ilots)
        
        fig.add_annotation(
            x=bounds[0] + 1,
            y=bounds[3] - 2,
            text=f"Total Îlots: {ilot_count}<br>Total Area: {total_area:.1f}m²",
            showarrow=False,
            font=dict(size=12, color='black'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='black',
            borderwidth=1
        )
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{rgb[0]}, {rgb[1]}, {rgb[2]}"
    
    def create_3d_isometric_view(self, zones: Dict, ilots: List[Dict], bounds: Tuple) -> go.Figure:
        """Create 3D isometric view similar to the client's expectations"""
        fig = go.Figure()
        
        # Add 3D walls
        for wall in zones.get('walls', []):
            points = wall.get('points', [])
            if len(points) >= 2:
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                z_coords = [0] * len(points)
                z_top = [3] * len(points)  # 3m height
                
                # Create wall surfaces
                for i in range(len(points) - 1):
                    fig.add_trace(go.Mesh3d(
                        x=[x_coords[i], x_coords[i+1], x_coords[i+1], x_coords[i]],
                        y=[y_coords[i], y_coords[i+1], y_coords[i+1], y_coords[i]],
                        z=[0, 0, 3, 3],
                        i=[0, 0, 1],
                        j=[1, 2, 2],
                        k=[2, 3, 3],
                        color=self.color_schemes['walls'],
                        opacity=0.8,
                        showscale=False
                    ))
        
        # Add 3D îlots with height variation
        for ilot in ilots:
            if 'geometry' in ilot:
                geom = ilot['geometry']
                if hasattr(geom, 'exterior'):
                    x_coords, y_coords = geom.exterior.xy
                    area = ilot.get('area', 0)
                    height = min(2.5, max(0.1, area / 10))  # Height based on area
                    
                    # Create îlot as 3D block
                    fig.add_trace(go.Mesh3d(
                        x=list(x_coords) * 2,
                        y=list(y_coords) * 2,
                        z=[0] * len(x_coords) + [height] * len(x_coords),
                        alphahull=0,
                        color=self.color_schemes['ilots']['medium'],
                        opacity=0.7,
                        showscale=False
                    ))
        
        # Configure 3D layout
        fig.update_layout(
            title='3D Isometric View - Professional Layout',
            scene=dict(
                xaxis_title='Distance (meters)',
                yaxis_title='Distance (meters)',
                zaxis_title='Height (meters)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            width=1000,
            height=800
        )
        
        return fig
    
    def create_compliance_report(self, zones: Dict, ilots: List[Dict]) -> Dict[str, Any]:
        """Create compliance report matching client requirements"""
        report = {
            'total_ilots': len(ilots),
            'total_area': sum(ilot.get('area', 0) for ilot in ilots),
            'size_distribution': {},
            'compliance_status': 'COMPLIANT',
            'warnings': [],
            'zone_analysis': {}
        }
        
        # Analyze size distribution
        for ilot in ilots:
            category = ilot.get('category', 'unknown')
            if category not in report['size_distribution']:
                report['size_distribution'][category] = 0
            report['size_distribution'][category] += 1
        
        # Check compliance
        restricted_count = len(zones.get('restricted', []))
        entrance_count = len(zones.get('entrances', []))
        
        if restricted_count == 0:
            report['warnings'].append("No restricted areas detected")
        if entrance_count == 0:
            report['warnings'].append("No entrances detected")
        
        report['zone_analysis'] = {
            'walls': len(zones.get('walls', [])),
            'restricted_areas': restricted_count,
            'entrances': entrance_count
        }
        
        return report