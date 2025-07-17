"""
Pixel-Perfect Renderer - Professional CAD Visualization
Renders floor plans with exact visual specifications matching reference images
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import math

@dataclass
class RenderingStyle:
    """Professional rendering style configuration"""
    wall_color: str = '#6B7280'
    wall_width: float = 4.0
    restricted_color: str = '#3B82F6'
    restricted_opacity: float = 0.6
    entrance_color: str = '#EF4444'
    entrance_width: float = 3.0
    ilot_outline_color: str = '#F87171'
    ilot_fill_color: str = 'rgba(248, 113, 113, 0.3)'
    corridor_color: str = '#FCA5A5'
    corridor_opacity: float = 0.7
    text_color: str = '#1F2937'
    text_size: int = 12
    background_color: str = '#FFFFFF'
    grid_color: str = '#F3F4F6'
    show_grid: bool = True
    show_measurements: bool = True
    show_labels: bool = True
    professional_mode: bool = True

class PixelPerfectRenderer:
    """
    Professional renderer for pixel-perfect CAD visualization
    Matches exact specifications from reference images
    """

    def __init__(self, style: RenderingStyle = None):
        self.style = style or RenderingStyle()
        self.config = {
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
            'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d'],
            'displaylogo': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'floor_plan',
                'height': 1200,
                'width': 1600,
                'scale': 3
            }
        }

    def render_empty_floor_plan(self, walls: List, restricted_areas: List, 
                               entrances: List, bounds: Tuple[float, float, float, float]) -> go.Figure:
        """
        Render empty floor plan matching reference Image 1
        Clean architectural drawing with proper color coding
        """
        fig = go.Figure()

        # Set up the layout with professional appearance
        self._setup_professional_layout(fig, bounds, "Empty Floor Plan - Professional Architecture")

        # Render walls as thick gray lines (MUR)
        self._render_walls(fig, walls)

        # Render restricted areas as blue zones (NO ENTREE)
        self._render_restricted_areas(fig, restricted_areas)

        # Render entrances as red zones (ENTRÉE/SORTIE)
        self._render_entrances(fig, entrances)

        # Add professional grid if enabled
        if self.style.show_grid:
            self._add_professional_grid(fig, bounds)

        return fig

    def render_floor_plan_with_ilots(self, walls: List, restricted_areas: List, 
                                   entrances: List, ilots: List, 
                                   bounds: Tuple[float, float, float, float]) -> go.Figure:
        """
        Render floor plan with îlots matching reference Image 2
        Shows intelligent îlot placement with measurements
        """
        fig = go.Figure()

        # Set up layout
        self._setup_professional_layout(fig, bounds, "Floor Plan with Îlots - Smart Placement")

        # Render base elements
        self._render_walls(fig, walls)
        self._render_restricted_areas(fig, restricted_areas)
        self._render_entrances(fig, entrances)

        # Render îlots with professional styling
        self._render_ilots(fig, ilots)

        # Add measurements and labels
        if self.style.show_measurements:
            self._add_ilot_measurements(fig, ilots)

        return fig

    def render_floor_plan_with_corridors(self, walls: List, restricted_areas: List, 
                                       entrances: List, ilots: List, corridors: List,
                                       bounds: Tuple[float, float, float, float]) -> go.Figure:
        """
        Render complete floor plan with corridors matching reference Image 3
        Shows full layout with circulation paths and measurements
        """
        fig = go.Figure()

        # Set up layout
        self._setup_professional_layout(fig, bounds, "Complete Floor Plan - Circulation Network")

        # Render base elements
        self._render_walls(fig, walls)
        self._render_restricted_areas(fig, restricted_areas)
        self._render_entrances(fig, entrances)

        # Render corridors first (background)
        self._render_corridors(fig, corridors)

        # Render îlots on top
        self._render_ilots(fig, ilots)

        # Add comprehensive measurements
        if self.style.show_measurements:
            self._add_ilot_measurements(fig, ilots)
            self._add_corridor_measurements(fig, corridors)

        return fig

    def _setup_professional_layout(self, fig: go.Figure, bounds: Tuple[float, float, float, float], title: str):
        """Set up professional layout matching reference images"""
        min_x, min_y, max_x, max_y = bounds

        # Add margin around the drawing
        margin = max((max_x - min_x), (max_y - min_y)) * 0.1

        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'font': {
                    'size': 18,
                    'color': self.style.text_color,
                    'family': 'Arial, sans-serif'
                }
            },

            # Set exact aspect ratio and bounds
            xaxis=dict(
                range=[min_x - margin, max_x + margin],
                scaleanchor="y",
                scaleratio=1,
                showgrid=self.style.show_grid,
                gridcolor=self.style.grid_color,
                gridwidth=0.5,
                zeroline=False,
                showline=True,
                linecolor='#E5E7EB',
                title=dict(
                    text="Distance (meters)",
                    font=dict(size=12, color=self.style.text_color)
                )
            ),

            yaxis=dict(
                range=[min_y - margin, max_y + margin],
                showgrid=self.style.show_grid,
                gridcolor=self.style.grid_color,
                gridwidth=0.5,
                zeroline=False,
                showline=True,
                linecolor='#E5E7EB',
                title=dict(
                    text="Distance (meters)",
                    font=dict(size=12, color=self.style.text_color)
                )
            ),

            # Professional appearance
            plot_bgcolor=self.style.background_color,
            paper_bgcolor='white',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color=self.style.text_color
            ),

            # Legend configuration
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="rgba(0, 0, 0, 0.1)",
                borderwidth=1,
                font=dict(size=10)
            ),

            # Size and margins
            width=1200,
            height=800,
            margin=dict(l=50, r=150, t=80, b=50)
        )

    def _render_walls(self, fig: go.Figure, walls: List):
        """Render walls as thick gray lines matching reference"""
        for i, wall in enumerate(walls):
            if hasattr(wall, 'geometry'):
                geometry = wall.geometry
            else:
                # Handle dictionary format
                points = wall.get('points', [])
                if len(points) < 2:
                    continue
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]

            if hasattr(geometry, 'coords'):
                coords = list(geometry.coords)
                x_coords = [p[0] for p in coords]
                y_coords = [p[1] for p in coords]

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines',
                line=dict(
                    color=self.style.wall_color,
                    width=self.style.wall_width
                ),
                name='Walls (MUR)' if i == 0 else '',
                showlegend=(i == 0),
                hovertemplate="<b>Wall</b><br>Length: %{customdata:.1f}m<extra></extra>",
                customdata=[getattr(geometry, 'length', 0)] * len(x_coords) if 'geometry' in locals() else [0] * len(x_coords)
            ))

    def _render_restricted_areas(self, fig: go.Figure, restricted_areas: List):
        """Render restricted areas as blue zones (NO ENTREE)"""
        for i, area in enumerate(restricted_areas):
            if hasattr(area, 'geometry'):
                geometry = area.geometry
            else:
                points = area.get('points', [])
                if len(points) < 3:
                    continue
                x_coords = [p[0] for p in points] + [points[0][0]]
                y_coords = [p[1] for p in points] + [points[0][1]]

            if hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [p[0] for p in coords]
                y_coords = [p[1] for p in coords]

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                fill='toself',
                fillcolor=f'rgba({self._hex_to_rgb(self.style.restricted_color)}, {self.style.restricted_opacity})',
                line=dict(
                    color=self.style.restricted_color,
                    width=2
                ),
                mode='lines',
                name='Restricted Areas (NO ENTREE)' if i == 0 else '',
                showlegend=(i == 0),
                hovertemplate="<b>Restricted Area</b><br>Area: %{customdata:.1f}m²<extra></extra>",
                customdata=[getattr(geometry, 'area', 0)] * len(x_coords) if 'geometry' in locals() else [0] * len(x_coords)
            ))

    def _render_entrances(self, fig: go.Figure, entrances: List):
        """Render entrances as red zones (ENTRÉE/SORTIE)"""
        for i, entrance in enumerate(entrances):
            if hasattr(entrance, 'geometry'):
                geometry = entrance.geometry
            else:
                points = entrance.get('points', [])
                if len(points) < 2:
                    continue
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]

            if hasattr(geometry, 'coords'):
                coords = list(geometry.coords)
                x_coords = [p[0] for p in coords]
                y_coords = [p[1] for p in coords]
            elif hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [p[0] for p in coords]
                y_coords = [p[1] for p in coords]

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines',
                line=dict(
                    color=self.style.entrance_color,
                    width=self.style.entrance_width
                ),
                name='Entrances (ENTRÉE/SORTIE)' if i == 0 else '',
                showlegend=(i == 0),
                hovertemplate="<b>Entrance/Exit</b><br>Width: %{customdata:.1f}m<extra></extra>",
                customdata=[getattr(geometry, 'length', 0)] * len(x_coords) if 'geometry' in locals() else [0] * len(x_coords)
            ))

    def _render_ilots(self, fig: go.Figure, ilots: List):
        """Render îlots with professional styling and measurements"""
        for i, ilot in enumerate(ilots):
            # Handle different îlot formats
            if hasattr(ilot, 'polygon'):
                geometry = ilot.polygon
            elif 'polygon' in ilot:
                geometry = ilot['polygon']
            else:
                # Create polygon from position and dimensions
                x = ilot.get('x', 0)
                y = ilot.get('y', 0)
                width = ilot.get('width', 1)
                height = ilot.get('height', 1)

                x_coords = [x, x + width, x + width, x, x]
                y_coords = [y, y, y + height, y + height, y]

            if hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [p[0] for p in coords]
                y_coords = [p[1] for p in coords]

            # Get îlot properties
            area = ilot.get('area', getattr(geometry, 'area', 0) if 'geometry' in locals() else 0)
            category = ilot.get('category', 'Standard')

            # Color based on category
            if 'micro' in category.lower() or '0-1' in category:
                fill_color = 'rgba(254, 243, 242, 0.8)'
            elif 'small' in category.lower() or '1-3' in category:
                fill_color = 'rgba(254, 226, 226, 0.8)'
            elif 'medium' in category.lower() or '3-5' in category:
                fill_color = 'rgba(252, 231, 243, 0.8)'
            else:
                fill_color = 'rgba(243, 232, 255, 0.8)'

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                fill='toself',
                fillcolor=fill_color,
                line=dict(
                    color=self.style.ilot_outline_color,
                    width=2
                ),
                mode='lines',
                name=f'Îlots {category}' if i == 0 else '',
                showlegend=(i == 0),
                hovertemplate=f"<b>Îlot {i+1}</b><br>Area: {area:.1f}m²<br>Category: {category}<extra></extra>"
            ))

    def _render_corridors(self, fig: go.Figure, corridors: List):
        """Render corridors as pink circulation paths"""
        for i, corridor in enumerate(corridors):
            if hasattr(corridor, 'polygon'):
                geometry = corridor.polygon
            elif 'polygon' in corridor:
                geometry = corridor['polygon']
            else:
                continue

            if hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)
                x_coords = [p[0] for p in coords]
                y_coords = [p[1] for p in coords]

                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    fill='toself',
                    fillcolor=f'rgba({self._hex_to_rgb(self.style.corridor_color)}, {self.style.corridor_opacity})',
                    line=dict(
                        color=self.style.corridor_color,
                        width=2
                    ),
                    mode='lines',
                    name='Circulation Corridors' if i == 0 else '',
                    showlegend=(i == 0),
                    hovertemplate=f"<b>Corridor</b><br>Area: {geometry.area:.1f}m²<extra></extra>"
                ))

    def _add_ilot_measurements(self, fig: go.Figure, ilots: List):
        """Add area measurements to îlots matching reference Image 2"""
        for i, ilot in enumerate(ilots):
            # Get center position
            if hasattr(ilot, 'position'):
                center_x, center_y = ilot.position
            elif 'position' in ilot:
                center_x, center_y = ilot['position']
            else:
                x = ilot.get('x', 0)
                y = ilot.get('y', 0)
                width = ilot.get('width', 1)
                height = ilot.get('height', 1)
                center_x = x + width / 2
                center_y = y + height / 2

            # Get area
            area = ilot.get('area', 0)

            # Add text annotation
            fig.add_annotation(
                x=center_x,
                y=center_y,
                text=f"{area:.1f}m²",
                showarrow=False,
                font=dict(
                    size=10,
                    color=self.style.text_color,
                    family="Arial, sans-serif"
                ),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor=self.style.text_color,
                borderwidth=1
            )

    def _add_corridor_measurements(self, fig: go.Figure, corridors: List):
        """Add measurements to corridors"""
        for corridor in corridors:
            if hasattr(corridor, 'polygon'):
                geometry = corridor.polygon
                centroid = geometry.centroid

                fig.add_annotation(
                    x=centroid.x,
                    y=centroid.y,
                    text=f"Corridor\n{geometry.area:.1f}m²",
                    showarrow=False,
                    font=dict(
                        size=9,
                        color=self.style.text_color,
                        family="Arial, sans-serif"
                    ),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor=self.style.corridor_color,
                    borderwidth=1
                )

    def _add_professional_grid(self, fig: go.Figure, bounds: Tuple[float, float, float, float]):
        """Add professional grid matching architectural standards"""
        min_x, min_y, max_x, max_y = bounds

        # Grid spacing based on scale
        span_x = max_x - min_x
        span_y = max_y - min_y
        max_span = max(span_x, span_y)

        if max_span < 10:
            grid_spacing = 0.5  # 50cm
        elif max_span < 50:
            grid_spacing = 1.0  # 1m
        else:
            grid_spacing = 5.0  # 5m

        # Update grid in layout
        fig.update_xaxes(dtick=grid_spacing)
        fig.update_yaxes(dtick=grid_spacing)

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"

    def export_high_resolution_image(self, fig: go.Figure, filename: str) -> str:
        """Export high-resolution image for professional presentations"""
        try:
            fig.write_image(
                filename,
                format="png",
                width=1600,
                height=1200,
                scale=3
            )
            return filename
        except Exception as e:
            print(f"Export failed: {e}")
            return None