"""
Advanced Professional Visualization System
High-quality 2D/3D rendering for architectural plans
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import streamlit as st

class AdvancedVisualizer:
    def __init__(self):
        self.colors = {
            'wall': '#2C3E50',
            'floor': '#ECF0F1', 
            'door': '#E74C3C',
            'window': '#3498DB',
            'furniture': '#F39C12',
            'room_fill': 'rgba(52, 152, 219, 0.1)',
            'text': '#34495E'
        }
        
    def create_professional_2d_plan(self, zones: List[Dict], analysis_results: Dict = None, 
                                   show_furniture: bool = True, show_dimensions: bool = True) -> go.Figure:
        """Create professional 2D architectural plan"""
        fig = go.Figure()
        
        # Add room zones with professional styling
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
                
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            # Room fill
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor=self.colors['room_fill'],
                line=dict(color=self.colors['wall'], width=3),
                mode='lines',
                name=f"Room {i+1}",
                hovertemplate=f"<b>{zone.get('zone_type', 'Room')}</b><br>" +
                             f"Area: {zone.get('area', 0):.1f} m²<br>" +
                             f"<extra></extra>",
                showlegend=False
            ))
            
            # Add room label
            centroid = self._calculate_centroid(points)
            fig.add_annotation(
                x=centroid[0], y=centroid[1],
                text=f"<b>{zone.get('zone_type', f'Room {i+1}')}</b><br>{zone.get('area', 0):.1f} m²",
                showarrow=False,
                font=dict(size=12, color=self.colors['text']),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor=self.colors['wall'],
                borderwidth=1
            )
            
            # Add dimensions if requested
            if show_dimensions:
                self._add_dimensions_to_room(fig, points)
        
        # Add furniture if analysis results available
        if show_furniture and analysis_results:
            self._add_furniture_to_2d(fig, analysis_results)
        
        # Professional layout
        fig.update_layout(
            title=dict(
                text="<b>Professional Architectural Plan</b>",
                x=0.5, font=dict(size=20, color=self.colors['text'])
            ),
            xaxis=dict(
                title="Distance (meters)",
                showgrid=True, gridwidth=1, gridcolor='lightgray',
                scaleanchor="y", scaleratio=1
            ),
            yaxis=dict(
                title="Distance (meters)", 
                showgrid=True, gridwidth=1, gridcolor='lightgray'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=1000, height=700,
            showlegend=True
        )
        
        return fig
    
    def create_advanced_3d_model(self, zones: List[Dict], analysis_results: Dict = None,
                                show_furniture: bool = True, wall_height: float = 3.0) -> go.Figure:
        """Create advanced 3D architectural model"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            # Create 3D room with walls and floor
            self._add_3d_room_advanced(fig, points, zone, wall_height, i)
            
        # Add furniture in 3D
        if show_furniture and analysis_results:
            self._add_furniture_to_3d_advanced(fig, analysis_results)
        
        # Advanced 3D layout
        fig.update_layout(
            title=dict(
                text="<b>3D Architectural Model</b>",
                x=0.5, font=dict(size=20)
            ),
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)", 
                zaxis_title="Z (meters)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2),
                    center=dict(x=0, y=0, z=0)
                ),
                aspectmode='cube',
                bgcolor='rgba(240,240,240,0.1)'
            ),
            width=1000, height=700
        )
        
        return fig
    
    def create_construction_plan_2d(self, zones: List[Dict], show_details: bool = True) -> go.Figure:
        """Create detailed construction plan"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            # Wall outlines (thicker for construction)
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='#2C3E50', width=6),
                name=f"Wall {i+1}",
                showlegend=False
            ))
            
            # Add construction details
            if show_details:
                self._add_construction_details(fig, points, zone, i)
        
        # Construction plan styling
        fig.update_layout(
            title="<b>Construction Plan - Structural Layout</b>",
            xaxis=dict(
                title="Distance (meters)",
                showgrid=True, gridwidth=1, gridcolor='gray',
                scaleanchor="y", scaleratio=1
            ),
            yaxis=dict(
                title="Distance (meters)",
                showgrid=True, gridwidth=1, gridcolor='gray'
            ),
            plot_bgcolor='white',
            width=1000, height=700
        )
        
        return fig
    
    def create_construction_plan_3d(self, zones: List[Dict], show_structure: bool = True) -> go.Figure:
        """Create 3D construction model with structural elements"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            # Structural walls (thicker)
            self._add_structural_walls_3d(fig, points, zone, i)
            
            if show_structure:
                # Add foundation
                self._add_foundation_3d(fig, points)
                # Add roof structure
                self._add_roof_structure_3d(fig, points)
        
        fig.update_layout(
            title="<b>3D Construction Model</b>",
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)",
                zaxis_title="Z (meters)",
                camera=dict(eye=dict(x=2, y=2, z=1.5)),
                aspectmode='cube'
            ),
            width=1000, height=700
        )
        
        return fig
    
    def _add_3d_room_advanced(self, fig: go.Figure, points: List[Tuple], zone: Dict, 
                             wall_height: float, room_id: int):
        """Add advanced 3D room with realistic materials"""
        # Floor
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        z_floor = [0] * len(points)
        
        fig.add_trace(go.Mesh3d(
            x=x_coords, y=y_coords, z=z_floor,
            color='lightgray',
            opacity=0.3,
            name=f"Floor {room_id+1}",
            showlegend=False
        ))
        
        # Walls with realistic height and thickness
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            
            # Wall vertices (with thickness)
            wall_thickness = 0.2
            direction = np.array([end[1] - start[1], start[0] - end[0]])
            direction = direction / np.linalg.norm(direction) * wall_thickness / 2
            
            x_wall = [start[0] - direction[0], end[0] - direction[0], 
                     end[0] + direction[0], start[0] + direction[0]]
            y_wall = [start[1] - direction[1], end[1] - direction[1],
                     end[1] + direction[1], start[1] + direction[1]]
            z_wall = [0, 0, wall_height, wall_height]
            
            fig.add_trace(go.Mesh3d(
                x=x_wall * 2, y=y_wall * 2, z=z_wall * 2,
                color='#34495E',
                opacity=0.8,
                name=f"Wall {room_id+1}-{i+1}",
                showlegend=False
            ))
    
    def _add_furniture_to_2d(self, fig: go.Figure, analysis_results: Dict):
        """Add furniture to 2D plan with realistic representation"""
        placements = analysis_results.get('placements', {})
        
        for zone_name, furniture_list in placements.items():
            for furniture in furniture_list:
                pos = furniture.get('position', (0, 0))
                size = furniture.get('size', (2, 1.5))
                rotation = furniture.get('rotation', 0)
                
                # Create furniture rectangle
                corners = self._get_rotated_rectangle(pos, size, rotation)
                x_coords = [c[0] for c in corners] + [corners[0][0]]
                y_coords = [c[1] for c in corners] + [corners[0][1]]
                
                fig.add_trace(go.Scatter(
                    x=x_coords, y=y_coords,
                    fill='toself',
                    fillcolor='rgba(243, 156, 18, 0.6)',
                    line=dict(color='#F39C12', width=2),
                    mode='lines',
                    name='Furniture',
                    showlegend=False,
                    hovertemplate=f"<b>Furniture</b><br>Size: {size[0]:.1f}×{size[1]:.1f}m<extra></extra>"
                ))
    
    def _add_furniture_to_3d_advanced(self, fig: go.Figure, analysis_results: Dict):
        """Add realistic 3D furniture"""
        placements = analysis_results.get('placements', {})
        
        for zone_name, furniture_list in placements.items():
            for furniture in furniture_list:
                pos = furniture.get('position', (0, 0))
                size = furniture.get('size', (2, 1.5))
                
                # 3D furniture box
                x_range = [pos[0] - size[0]/2, pos[0] + size[0]/2]
                y_range = [pos[1] - size[1]/2, pos[1] + size[1]/2]
                z_range = [0, 0.8]  # Furniture height
                
                # Create 3D box
                vertices = []
                for x in x_range:
                    for y in y_range:
                        for z in z_range:
                            vertices.append([x, y, z])
                
                fig.add_trace(go.Mesh3d(
                    x=[v[0] for v in vertices],
                    y=[v[1] for v in vertices], 
                    z=[v[2] for v in vertices],
                    color='#E67E22',
                    opacity=0.7,
                    name='Furniture',
                    showlegend=False
                ))
    
    def _add_construction_details(self, fig: go.Figure, points: List[Tuple], zone: Dict, room_id: int):
        """Add construction details like dimensions and annotations"""
        # Add wall dimensions
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            
            # Calculate wall length
            length = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            mid_point = ((start[0] + end[0])/2, (start[1] + end[1])/2)
            
            # Add dimension annotation
            fig.add_annotation(
                x=mid_point[0], y=mid_point[1],
                text=f"{length:.2f}m",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='red',
                font=dict(size=10, color='red'),
                bgcolor='white',
                bordercolor='red',
                borderwidth=1
            )
    
    def _add_structural_walls_3d(self, fig: go.Figure, points: List[Tuple], zone: Dict, room_id: int):
        """Add structural walls for construction view"""
        wall_height = 3.0
        wall_thickness = 0.3  # Thicker for construction
        
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            
            # Create thick structural wall
            direction = np.array([end[1] - start[1], start[0] - end[0]])
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction) * wall_thickness / 2
            
                x_wall = [start[0] - direction[0], end[0] - direction[0], 
                         end[0] + direction[0], start[0] + direction[0]]
                y_wall = [start[1] - direction[1], end[1] - direction[1],
                         end[1] + direction[1], start[1] + direction[1]]
                
                # Bottom face
                fig.add_trace(go.Mesh3d(
                    x=x_wall, y=y_wall, z=[0]*4,
                    color='#7F8C8D',
                    opacity=0.9,
                    name=f"Foundation Wall {room_id+1}",
                    showlegend=False
                ))
                
                # Top face  
                fig.add_trace(go.Mesh3d(
                    x=x_wall, y=y_wall, z=[wall_height]*4,
                    color='#95A5A6',
                    opacity=0.9,
                    name=f"Wall Top {room_id+1}",
                    showlegend=False
                ))
    
    def _add_foundation_3d(self, fig: go.Figure, points: List[Tuple]):
        """Add foundation structure"""
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        z_foundation = [-0.5] * len(points)  # Below ground level
        
        fig.add_trace(go.Mesh3d(
            x=x_coords, y=y_coords, z=z_foundation,
            color='#34495E',
            opacity=0.8,
            name="Foundation",
            showlegend=False
        ))
    
    def _add_roof_structure_3d(self, fig: go.Figure, points: List[Tuple]):
        """Add roof structure"""
        # Simple flat roof
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        z_roof = [3.2] * len(points)  # Above wall height
        
        fig.add_trace(go.Mesh3d(
            x=x_coords, y=y_coords, z=z_roof,
            color='#E74C3C',
            opacity=0.7,
            name="Roof",
            showlegend=False
        ))
    
    def _calculate_centroid(self, points: List[Tuple]) -> Tuple[float, float]:
        """Calculate centroid of polygon"""
        if not points:
            return (0, 0)
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)
    
    def _get_rotated_rectangle(self, center: Tuple, size: Tuple, rotation: float) -> List[Tuple]:
        """Get corners of rotated rectangle"""
        cos_r = np.cos(rotation)
        sin_r = np.sin(rotation)
        
        corners = [
            (-size[0]/2, -size[1]/2),
            (size[0]/2, -size[1]/2),
            (size[0]/2, size[1]/2),
            (-size[0]/2, size[1]/2)
        ]
        
        rotated_corners = []
        for corner in corners:
            x = corner[0] * cos_r - corner[1] * sin_r + center[0]
            y = corner[0] * sin_r + corner[1] * cos_r + center[1]
            rotated_corners.append((x, y))
        
        return rotated_corners
    
    def _add_dimensions_to_room(self, fig: go.Figure, points: List[Tuple]):
        """Add dimension lines to room"""
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            
            length = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            mid_point = ((start[0] + end[0])/2, (start[1] + end[1])/2)
            
            # Add dimension line
            fig.add_trace(go.Scatter(
                x=[start[0], end[0]], y=[start[1], end[1]],
                mode='lines',
                line=dict(color='red', width=1, dash='dot'),
                showlegend=False,
                hovertemplate=f"Wall Length: {length:.2f}m<extra></extra>"
            ))