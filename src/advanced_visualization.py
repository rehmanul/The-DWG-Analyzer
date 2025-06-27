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
        """Create detailed construction plan from real zone data"""
        fig = go.Figure()
        
        if not zones:
            fig.add_annotation(
                text="No zones loaded. Please upload and analyze a DWG/DXF file first.",
                x=0.5, y=0.5, xref="paper", yref="paper",
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Use actual zone data for construction plan
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            # Real wall outlines from actual DWG data
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            # Color code by room type
            room_type = zone.get('zone_type', 'Unknown')
            color = self._get_room_color(room_type)
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines+markers',
                line=dict(color=color, width=4),
                marker=dict(size=6, color=color),
                name=f"{room_type} - {zone.get('area', 0):.1f}m²",
                hovertemplate=f"<b>{room_type}</b><br>Area: {zone.get('area', 0):.1f} m²<br>Layer: {zone.get('layer', 'Unknown')}<extra></extra>"
            ))
            
            # Add real construction details from zone data
            if show_details:
                self._add_real_construction_details(fig, points, zone, i)
        
        # Auto-scale to actual drawing bounds
        all_x = [p[0] for zone in zones for p in zone.get('points', [])]
        all_y = [p[1] for zone in zones for p in zone.get('points', [])]
        
        if all_x and all_y:
            x_range = [min(all_x) - 5, max(all_x) + 5]
            y_range = [min(all_y) - 5, max(all_y) + 5]
        else:
            x_range = [-10, 10]
            y_range = [-10, 10]
        
        fig.update_layout(
            title=f"<b>Construction Plan - {len(zones)} Real Zones from DWG</b>",
            xaxis=dict(
                title="Distance (meters)",
                showgrid=True, gridwidth=1, gridcolor='lightgray',
                scaleanchor="y", scaleratio=1,
                range=x_range
            ),
            yaxis=dict(
                title="Distance (meters)",
                showgrid=True, gridwidth=1, gridcolor='lightgray',
                range=y_range
            ),
            plot_bgcolor='white',
            width=1000, height=700,
            showlegend=True
        )
        
        return fig
    
    def create_construction_plan_3d(self, zones: List[Dict], show_structure: bool = True) -> go.Figure:
        """Create 3D construction model from real zone data"""
        fig = go.Figure()
        
        if not zones:
            fig.add_scatter3d(
                x=[0], y=[0], z=[0],
                mode='text',
                text=["No zones loaded. Upload DWG/DXF file first."],
                textfont=dict(size=16)
            )
            return fig
        
        # Use real zone data for 3D construction
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            # Real structural walls from actual DWG geometry
            self._add_real_structural_walls_3d(fig, points, zone, i)
            
            if show_structure:
                # Real foundation based on actual room footprint
                self._add_real_foundation_3d(fig, points, zone)
                # Real roof structure based on actual geometry
                self._add_real_roof_structure_3d(fig, points, zone)
        
        # Auto-calculate bounds from real data
        all_x = [p[0] for zone in zones for p in zone.get('points', [])]
        all_y = [p[1] for zone in zones for p in zone.get('points', [])]
        
        if all_x and all_y:
            center_x = (min(all_x) + max(all_x)) / 2
            center_y = (min(all_y) + max(all_y)) / 2
            range_x = max(all_x) - min(all_x)
            range_y = max(all_y) - min(all_y)
            max_range = max(range_x, range_y)
        else:
            center_x = center_y = 0
            max_range = 20
        
        fig.update_layout(
            title=f"<b>3D Construction Model - {len(zones)} Real Zones</b>",
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)",
                zaxis_title="Z (meters)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2),
                    center=dict(x=center_x/max_range, y=center_y/max_range, z=0)
                ),
                aspectmode='cube',
                xaxis=dict(range=[center_x-max_range/2, center_x+max_range/2]),
                yaxis=dict(range=[center_y-max_range/2, center_y+max_range/2]),
                zaxis=dict(range=[0, 4])
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
    
    def _get_room_color(self, room_type: str) -> str:
        """Get color based on actual room type"""
        colors = {
            'Kitchen': '#E74C3C',
            'Bathroom': '#3498DB', 
            'Bedroom': '#9B59B6',
            'Living Room': '#2ECC71',
            'Office': '#F39C12',
            'Dining Room': '#E67E22',
            'Hallway': '#95A5A6',
            'Closet': '#34495E'
        }
        return colors.get(room_type, '#2C3E50')
    
    def _add_real_construction_details(self, fig: go.Figure, points: List[Tuple], zone: Dict, room_id: int):
        """Add real construction details from zone data"""
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
    
    def _add_real_structural_walls_3d(self, fig: go.Figure, points: List[Tuple], zone: Dict, room_id: int):
        """Add real structural walls based on actual zone geometry"""
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
    
    def _add_real_foundation_3d(self, fig: go.Figure, points: List[Tuple], zone: Dict):
        """Add real foundation based on actual room footprint"""
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
    
    def _add_real_roof_structure_3d(self, fig: go.Figure, points: List[Tuple], zone: Dict):
        """Add real roof structure based on actual geometry"""
        # Real roof based on actual room geometry
        room_type = zone.get('zone_type', 'Room')
        area = zone.get('area', 0)
        
        # Roof height based on room type and area
        if 'Kitchen' in room_type or area > 50:
            roof_height = 3.5  # Higher ceiling for large rooms
        else:
            roof_height = 3.2
        
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        z_roof = [roof_height] * len(points)
        
        # Color roof based on room type
        roof_color = self._get_room_color(room_type)
        
        fig.add_trace(go.Mesh3d(
            x=x_coords, y=y_coords, z=z_roof,
            color=roof_color,
            opacity=0.6,
            name=f"Roof - {room_type}",
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
    
    def create_structural_plan_2d(self, zones: List[Dict]) -> go.Figure:
        """Create structural engineering plan"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='#8B4513', width=8),
                name=f"Load-bearing Wall {i+1}"
            ))
        
        fig.update_layout(title="<b>Structural Engineering Plan</b>")
        return fig
    
    def create_architectural_plan_2d(self, zones: List[Dict]) -> go.Figure:
        """Create architectural design plan"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            room_type = zone.get('zone_type', 'Room')
            color = '#2E8B57' if 'Kitchen' in room_type else '#4169E1'
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor=f'rgba(46, 139, 87, 0.2)',
                line=dict(color=color, width=3),
                name=f"{room_type}"
            ))
        
        fig.update_layout(title="<b>Architectural Design Plan</b>")
        return fig
    
    def create_structural_plan_3d(self, zones: List[Dict]) -> go.Figure:
        """Create 3D structural plan"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            z_coords = [4.0] * len(points)
            
            fig.add_trace(go.Mesh3d(
                x=x_coords, y=y_coords, z=z_coords,
                color='#8B4513',
                opacity=0.7,
                name=f"Structural {i+1}"
            ))
        
        fig.update_layout(title="<b>3D Structural Model</b>")
        return fig
    
    def create_architectural_plan_3d(self, zones: List[Dict]) -> go.Figure:
        """Create 3D architectural plan"""
        fig = go.Figure()
        
        for i, zone in enumerate(zones):
            points = zone.get('points', [])
            if len(points) < 3:
                continue
            
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            z_coords = [3.0] * len(points)
            
            fig.add_trace(go.Mesh3d(
                x=x_coords, y=y_coords, z=z_coords,
                color='#FFD700',
                opacity=0.6,
                name=f"Room {i+1}"
            ))
        
        fig.update_layout(title="<b>3D Architectural Model</b>")
        return fig