"""
Pixel-Perfect Renderer - Professional architectural visualization
Exact color matching and pixel-perfect rendering for floor plans
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import math
from shapely.geometry import Polygon, Point, LineString
import logging

logger = logging.getLogger(__name__)

# Professional color palette - exact hex values for pixel-perfect matching
class ArchitecturalColors:
    # Primary colors (from reference images)
    WALL_GRAY = "#6B7280"          # Walls (MUR)
    RESTRICTED_BLUE = "#3B82F6"    # Restricted areas (NO ENTREE)
    ENTRANCE_RED = "#EF4444"       # Entrances/exits (ENTRÉE/SORTIE)
    
    # Secondary colors
    ILOT_LIGHT_PINK = "#FEE2E2"    # Light pink for îlots
    ILOT_BORDER_RED = "#DC2626"    # Red borders for îlots
    CORRIDOR_PINK = "#FCE7F3"      # Pink corridors
    CORRIDOR_BORDER = "#BE185D"    # Dark pink corridor borders
    
    # Background and UI
    BACKGROUND_WHITE = "#FFFFFF"
    GRID_LIGHT_GRAY = "#F3F4F6"
    TEXT_DARK = "#1F2937"
    MEASUREMENT_TEXT = "#374151"
    
    # Line weights (in pixels for web rendering)
    WALL_THICKNESS = 3.0
    BORDER_THICKNESS = 1.5
    CORRIDOR_THICKNESS = 1.0
    GRID_THICKNESS = 0.5

@dataclass
class RenderingStyle:
    """Professional rendering style configuration"""
    show_grid: bool = True
    show_measurements: bool = True
    show_labels: bool = True
    high_contrast: bool = False
    print_ready: bool = False
    scale_factor: float = 1.0

class PixelPerfectRenderer:
    """
    Professional renderer for architectural floor plans
    Produces pixel-perfect visualizations matching reference images
    """
    
    def __init__(self, style: RenderingStyle = None):
        self.style = style or RenderingStyle()
        self.colors = ArchitecturalColors()
        
        # Configure plotly for high-quality rendering
        self.config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'floor_plan',
                'height': 1200,
                'width': 1600,
                'scale': 2  # High DPI
            }
        }

    def render_empty_floor_plan(self, walls: List, restricted_areas: List, 
                               entrances: List, bounds: Tuple[float, float, float, float]) -> go.Figure:
        """
        Render empty floor plan (Phase 2 - Image 1 equivalent)
        Clean architectural drawing with walls, restricted areas, and entrances
        """
        fig = go.Figure()
        
        # Set up the layout for pixel-perfect rendering
        self._setup_figure_layout(fig, bounds)
        
        # Render walls (thick gray lines - MUR)
        for wall in walls:
            self._render_wall(fig, wall)
        
        # Render restricted areas (blue zones - NO ENTREE)
        for area in restricted_areas:
            self._render_restricted_area(fig, area)
        
        # Render entrances (red zones with door swings - ENTRÉE/SORTIE)
        for entrance in entrances:
            self._render_entrance(fig, entrance)
        
        # Add professional grid if enabled
        if self.style.show_grid:
            self._add_professional_grid(fig, bounds)
        
        # Add title and annotations
        fig.update_layout(
            title={
                'text': "Floor Plan - Architectural Drawing",
                'x': 0.5,
                'font': {'size': 16, 'color': self.colors.TEXT_DARK}
            }
        )
        
        return fig

    def render_floor_plan_with_ilots(self, walls: List, restricted_areas: List, 
                                   entrances: List, ilots: List, 
                                   bounds: Tuple[float, float, float, float]) -> go.Figure:
        """
        Render floor plan with îlots placed (Phase 3 - Image 2 equivalent)
        Includes all architectural elements plus optimally placed îlots
        """
        # Start with empty floor plan
        fig = self.render_empty_floor_plan(walls, restricted_areas, entrances, bounds)
        
        # Add îlots with proper sizing and color coding
        for i, ilot in enumerate(ilots):
            self._render_ilot(fig, ilot, i)
        
        # Update title
        fig.update_layout(
            title={
                'text': f"Floor Plan with Îlots - {len(ilots)} Units Placed",
                'x': 0.5,
                'font': {'size': 16, 'color': self.colors.TEXT_DARK}
            }
        )
        
        return fig

    def render_floor_plan_with_corridors(self, walls: List, restricted_areas: List, 
                                       entrances: List, ilots: List, corridors: List,
                                       bounds: Tuple[float, float, float, float]) -> go.Figure:
        """
        Render complete floor plan with corridor network (Phase 4 - Image 3 equivalent)
        Full visualization with îlots, corridors, and area measurements
        """
        # Start with îlots floor plan
        fig = self.render_floor_plan_with_ilots(walls, restricted_areas, entrances, ilots, bounds)
        
        # Add corridor network (pink lines connecting îlots)
        for corridor in corridors:
            self._render_corridor(fig, corridor)
        
        # Add area measurements for each îlot
        for i, ilot in enumerate(ilots):
            self._add_ilot_measurement(fig, ilot, i)
        
        # Update title
        total_area = sum(ilot.get('area', 0) for ilot in ilots)
        fig.update_layout(
            title={
                'text': f"Complete Floor Plan - {len(ilots)} Îlots, {total_area:.1f}m² Total",
                'x': 0.5,
                'font': {'size': 16, 'color': self.colors.TEXT_DARK}
            }
        )
        
        return fig

    def _setup_figure_layout(self, fig: go.Figure, bounds: Tuple[float, float, float, float]):
        """Configure figure layout for professional architectural presentation"""
        min_x, min_y, max_x, max_y = bounds
        
        # Add margin for annotations and measurements
        margin = max((max_x - min_x) * 0.1, (max_y - min_y) * 0.1)
        
        fig.update_layout(
            # Remove default plotly styling for clean architectural look
            plot_bgcolor=self.colors.BACKGROUND_WHITE,
            paper_bgcolor=self.colors.BACKGROUND_WHITE,
            
            # Professional axis styling
            xaxis=dict(
                range=[min_x - margin, max_x + margin],
                showgrid=False,
                showline=True,
                linecolor=self.colors.TEXT_DARK,
                title="Distance (meters)",
                title_font=dict(size=12, color=self.colors.TEXT_DARK),
                tickfont=dict(size=10, color=self.colors.MEASUREMENT_TEXT),
                dtick=5.0  # 5-meter intervals
            ),
            yaxis=dict(
                range=[min_y - margin, max_y + margin],
                showgrid=False,
                showline=True,
                linecolor=self.colors.TEXT_DARK,
                title="Distance (meters)",
                title_font=dict(size=12, color=self.colors.TEXT_DARK),
                tickfont=dict(size=10, color=self.colors.MEASUREMENT_TEXT),
                dtick=5.0,
                scaleanchor="x",
                scaleratio=1
            ),
            
            # Professional layout
            width=1200,
            height=800,
            margin=dict(l=80, r=80, t=80, b=80),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=self.colors.TEXT_DARK,
                borderwidth=1
            )
        )

    def _render_wall(self, fig: go.Figure, wall):
        """Render wall with proper thickness and color (MUR style)"""
        if hasattr(wall, 'geometry'):
            points = wall.geometry
        elif hasattr(wall, 'points'):
            points = wall.points
        else:
            return
        
        if len(points) < 2:
            return
        
        # Extract coordinates
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        # Add wall as thick line
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines',
            line=dict(
                color=self.colors.WALL_GRAY,
                width=self.colors.WALL_THICKNESS
            ),
            name='Walls (MUR)',
            legendgroup='walls',
            showlegend=True,
            hovertemplate='Wall<br>Length: %{customdata:.1f}m<extra></extra>',
            customdata=[self._calculate_total_length(points)] * len(points)
        ))

    def _render_restricted_area(self, fig: go.Figure, area):
        """Render restricted area with blue fill (NO ENTREE style)"""
        if hasattr(area, 'geometry'):
            points = area.geometry
        elif hasattr(area, 'points'):
            points = area.points
        else:
            return
        
        if len(points) < 3:
            return
        
        # Extract coordinates and close polygon
        x_coords = [p[0] for p in points] + [points[0][0]]
        y_coords = [p[1] for p in points] + [points[0][1]]
        
        # Add filled area
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            fill='toself',
            fillcolor=f'rgba({self._hex_to_rgb(self.colors.RESTRICTED_BLUE)}, 0.3)',
            line=dict(
                color=self.colors.RESTRICTED_BLUE,
                width=self.colors.BORDER_THICKNESS
            ),
            mode='lines',
            name='Restricted (NO ENTREE)',
            legendgroup='restricted',
            showlegend=True,
            hovertemplate='Restricted Area<br>Area: %{customdata:.1f}m²<extra></extra>',
            customdata=[self._calculate_polygon_area(points)] * len(x_coords)
        ))

    def _render_entrance(self, fig: go.Figure, entrance):
        """Render entrance with red styling and door swing (ENTRÉE/SORTIE style)"""
        if hasattr(entrance, 'geometry'):
            points = entrance.geometry
        elif hasattr(entrance, 'points'):
            points = entrance.points
        else:
            return
        
        if len(points) < 2:
            return
        
        # For line entrances (door openings)
        if len(points) == 2:
            x_coords = [points[0][0], points[1][0]]
            y_coords = [points[0][1], points[1][1]]
            
            # Add door opening line
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines',
                line=dict(
                    color=self.colors.ENTRANCE_RED,
                    width=self.colors.WALL_THICKNESS
                ),
                name='Entrance (ENTRÉE)',
                legendgroup='entrances',
                showlegend=True,
                hovertemplate='Entrance<br>Width: %{customdata:.1f}m<extra></extra>',
                customdata=[self._calculate_distance(points[0], points[1])] * len(x_coords)
            ))
            
            # Add door swing arc if this is a door
            self._add_door_swing(fig, points[0], points[1])
        
        # For area entrances (entrance zones)
        elif len(points) >= 3:
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                fill='toself',
                fillcolor=f'rgba({self._hex_to_rgb(self.colors.ENTRANCE_RED)}, 0.2)',
                line=dict(
                    color=self.colors.ENTRANCE_RED,
                    width=self.colors.BORDER_THICKNESS
                ),
                mode='lines',
                name='Entrance Zone',
                legendgroup='entrances',
                showlegend=True,
                hovertemplate='Entrance Zone<br>Area: %{customdata:.1f}m²<extra></extra>',
                customdata=[self._calculate_polygon_area(points)] * len(x_coords)
            ))

    def _add_door_swing(self, fig: go.Figure, start_point: Tuple[float, float], 
                       end_point: Tuple[float, float]):
        """Add door swing arc visualization"""
        door_width = self._calculate_distance(start_point, end_point)
        
        # Create 90-degree door swing arc
        center = start_point
        radius = door_width
        
        # Calculate swing arc points
        start_angle = math.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])
        angles = np.linspace(start_angle, start_angle + math.pi/2, 20)
        
        arc_x = [center[0] + radius * math.cos(a) for a in angles]
        arc_y = [center[1] + radius * math.sin(a) for a in angles]
        
        # Add door swing arc
        fig.add_trace(go.Scatter(
            x=arc_x,
            y=arc_y,
            mode='lines',
            line=dict(
                color=self.colors.ENTRANCE_RED,
                width=1.0,
                dash='dash'
            ),
            name='Door Swing',
            legendgroup='entrances',
            showlegend=False,
            hoverinfo='skip'
        ))

    def _render_ilot(self, fig: go.Figure, ilot: Dict, index: int):
        """Render îlot with proper sizing and color coding"""
        if 'polygon' not in ilot and 'points' not in ilot:
            return
        
        # Get îlot geometry
        if 'polygon' in ilot:
            if hasattr(ilot['polygon'], 'exterior'):
                x_coords, y_coords = ilot['polygon'].exterior.xy
                x_coords, y_coords = list(x_coords), list(y_coords)
            else:
                return
        else:
            points = ilot['points']
            x_coords = [p[0] for p in points] + [points[0][0]]
            y_coords = [p[1] for p in points] + [points[0][1]]
        
        area = ilot.get('area', 0)
        category = ilot.get('category', 'Standard')
        
        # Color coding by size
        if area <= 1:
            fill_color = '#FEF3F2'  # Very light pink
            border_color = '#F97316'  # Orange
        elif area <= 3:
            fill_color = '#FEE2E2'  # Light pink
            border_color = '#DC2626'  # Red
        elif area <= 5:
            fill_color = '#FCE7F3'  # Medium pink
            border_color = '#BE185D'  # Dark pink
        else:
            fill_color = '#F3E8FF'  # Light purple
            border_color = '#7C3AED'  # Purple
        
        # Add îlot shape
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            fill='toself',
            fillcolor=fill_color,
            line=dict(
                color=border_color,
                width=self.colors.BORDER_THICKNESS
            ),
            mode='lines',
            name=f'Îlot {category}',
            legendgroup='ilots',
            showlegend=(index == 0),  # Only show legend for first îlot
            hovertemplate=f'Îlot {index + 1}<br>Area: {area:.2f}m²<br>Category: {category}<extra></extra>'
        ))

    def _render_corridor(self, fig: go.Figure, corridor: Dict):
        """Render corridor with pink styling"""
        if 'points' not in corridor:
            return
        
        points = corridor['points']
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        # Add corridor line
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines',
            line=dict(
                color=self.colors.CORRIDOR_BORDER,
                width=self.colors.CORRIDOR_THICKNESS * 2
            ),
            name='Corridors',
            legendgroup='corridors',
            showlegend=True,
            hovertemplate='Corridor<br>Length: %{customdata:.1f}m<extra></extra>',
            customdata=[self._calculate_total_length(points)] * len(points)
        ))

    def _add_ilot_measurement(self, fig: go.Figure, ilot: Dict, index: int):
        """Add area measurement text to îlot"""
        if not self.style.show_measurements:
            return
        
        # Calculate centroid for text placement
        if 'polygon' in ilot and hasattr(ilot['polygon'], 'centroid'):
            centroid = ilot['polygon'].centroid
            x, y = centroid.x, centroid.y
        elif 'points' in ilot:
            points = ilot['points']
            x = sum(p[0] for p in points) / len(points)
            y = sum(p[1] for p in points) / len(points)
        else:
            return
        
        area = ilot.get('area', 0)
        
        # Add measurement annotation
        fig.add_annotation(
            x=x,
            y=y,
            text=f"{area:.1f}m²",
            showarrow=False,
            font=dict(
                size=10,
                color=self.colors.TEXT_DARK,
                family="Arial Black"
            ),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=self.colors.TEXT_DARK,
            borderwidth=1
        )

    def _add_professional_grid(self, fig: go.Figure, bounds: Tuple[float, float, float, float]):
        """Add professional grid for technical drawings"""
        min_x, min_y, max_x, max_y = bounds
        
        # Grid spacing based on drawing size
        width = max_x - min_x
        height = max_y - min_y
        max_dim = max(width, height)
        
        if max_dim <= 20:
            grid_spacing = 1.0  # 1m grid for small drawings
        elif max_dim <= 50:
            grid_spacing = 2.5  # 2.5m grid for medium drawings
        else:
            grid_spacing = 5.0  # 5m grid for large drawings
        
        # Vertical grid lines
        x_start = math.floor(min_x / grid_spacing) * grid_spacing
        x_end = math.ceil(max_x / grid_spacing) * grid_spacing
        
        for x in np.arange(x_start, x_end + grid_spacing, grid_spacing):
            fig.add_shape(
                type="line",
                x0=x, y0=min_y, x1=x, y1=max_y,
                line=dict(
                    color=self.colors.GRID_LIGHT_GRAY,
                    width=self.colors.GRID_THICKNESS
                )
            )
        
        # Horizontal grid lines
        y_start = math.floor(min_y / grid_spacing) * grid_spacing
        y_end = math.ceil(max_y / grid_spacing) * grid_spacing
        
        for y in np.arange(y_start, y_end + grid_spacing, grid_spacing):
            fig.add_shape(
                type="line",
                x0=min_x, y0=y, x1=max_x, y1=y,
                line=dict(
                    color=self.colors.GRID_LIGHT_GRAY,
                    width=self.colors.GRID_THICKNESS
                )
            )

    # Utility methods
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"

    def _calculate_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate distance between two points"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def _calculate_total_length(self, points: List[Tuple[float, float]]) -> float:
        """Calculate total length of point sequence"""
        if len(points) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(points) - 1):
            total += self._calculate_distance(points[i], points[i + 1])
        return total

    def _calculate_polygon_area(self, points: List[Tuple[float, float]]) -> float:
        """Calculate area of polygon using shoelace formula"""
        if len(points) < 3:
            return 0.0
        
        area = 0.0
        n = len(points)
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2.0

    def export_high_resolution_image(self, fig: go.Figure, filename: str, 
                                   width: int = 1600, height: int = 1200, scale: int = 2) -> str:
        """Export figure as high-resolution image"""
        try:
            img_bytes = fig.to_image(
                format="png",
                width=width,
                height=height,
                scale=scale,
                engine="kaleido"
            )
            
            with open(filename, "wb") as f:
                f.write(img_bytes)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting image: {e}")
            return ""

    def create_comparison_view(self, figures: List[go.Figure], titles: List[str]) -> go.Figure:
        """Create side-by-side comparison of different phases"""
        from plotly.subplots import make_subplots
        
        rows = 1
        cols = len(figures)
        
        subplot_fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=titles,
            horizontal_spacing=0.05
        )
        
        for i, fig in enumerate(figures):
            col = i + 1
            
            # Copy traces from original figure
            for trace in fig.data:
                subplot_fig.add_trace(trace, row=1, col=col)
        
        # Update layout for comparison view
        subplot_fig.update_layout(
            title="Floor Plan Development Phases",
            showlegend=True,
            width=1800,
            height=600
        )
        
        return subplot_fig