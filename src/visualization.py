
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any


class PlanVisualizer:
    """Visualization class for architectural plans"""

    def __init__(self):
        pass

    def create_basic_plot(self, zones):
        """Create basic 2D plot of zones"""
        fig = go.Figure()

        if not zones:
            fig.update_layout(title="No zones to display")
            return fig

        for i, zone in enumerate(zones):
            try:
                # Handle different point formats more robustly
                points = zone.get('points', [])
                if not points:
                    continue

                x_coords = []
                y_coords = []

                # Handle various point formats
                if isinstance(points, list) and len(points) > 0:
                    if isinstance(points[0], (list, tuple)) and len(points[0]) >= 2:
                        # Format: [(x1, y1), (x2, y2), ...]
                        x_coords = [p[0] for p in points]
                        y_coords = [p[1] for p in points]
                    elif len(points) >= 2 and isinstance(points[0], list):
                        # Format: [[x1, x2, ...], [y1, y2, ...]]
                        x_coords = points[0] if points[0] else []
                        y_coords = points[1] if len(points) > 1 and points[1] else []
                    elif isinstance(points[0], (int, float)):
                        # Format: [x1, y1, x2, y2, ...]
                        if len(points) >= 4:
                            x_coords = points[::2]
                            y_coords = points[1::2]

                if len(x_coords) >= 3 and len(y_coords) >= 3:
                    # Close the polygon
                    if x_coords[-1] != x_coords[0] or y_coords[-1] != y_coords[0]:
                        x_coords.append(x_coords[0])
                        y_coords.append(y_coords[0])

                    fig.add_trace(
                        go.Scatter(
                            x=x_coords,
                            y=y_coords,
                            fill="toself",
                            mode='lines',
                            name=f"Zone {zone.get('id', i)}",
                            line=dict(width=2),
                            fillcolor=f'rgba({50 + i*30 % 200}, {100 + i*25 % 150}, {150 + i*20 % 100}, 0.3)',
                            hovertemplate=f"<b>Zone {i}</b><br>Type: {zone.get('zone_type', 'Unknown')}<br>Area: {zone.get('area', 0):.1f} m²<extra></extra>"
                        )
                    )
            except Exception as e:
                st.warning(f"Could not display zone {i}: {str(e)}")
                continue

        fig.update_layout(
            title="Floor Plan Visualization",
            xaxis_title="X Coordinate (m)",
            yaxis_title="Y Coordinate (m)",
            showlegend=True,
            hovermode='closest',
            width=800,
            height=600,
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )

        return fig

    def create_interactive_plot(self, zones, analysis_results, show_zones=True, 
                              show_boxes=True, show_labels=True, color_by_type=True,
                              show_entry_zones=True, show_no_entry_zones=True,
                              show_walls=True, show_pathways=True, show_annotations=True,
                              annotations=None):
        """Create interactive plot with analysis results and enhanced features"""
        fig = go.Figure()

        if not zones:
            fig.update_layout(title="No zones to display")
            return fig

        # Color mapping for room types
        color_map = {
            'Office': 'lightblue',
            'Conference Room': 'lightgreen', 
            'Meeting Room': 'lightcoral',
            'Kitchen': 'orange',
            'Bathroom': 'pink',
            'Storage': 'lightgray',
            'Storage/WC': 'lightpink',
            'Small Office': 'lightyellow',
            'Open Office': 'lightsteelblue',
            'Hall/Auditorium': 'lightcyan',
            'Corridor': 'wheat',
            'Unknown': 'white'
        }

        # Custom colors for entry/no entry/walls zones
        special_zone_colors = {
            'entry': 'rgba(255, 0, 0, 0.5)',       # Red for entry/exit
            'no_entry': 'rgba(0, 0, 255, 0.5)',    # Blue for no entry
            'wall': 'rgba(128, 128, 128, 0.7)'     # Gray for walls
        }

        if show_zones:
            for i, zone in enumerate(zones):
                try:
                    points = zone.get('points', [])
                    if not points:
                        continue

                    x_coords = []
                    y_coords = []

                    # Handle various point formats
                    if isinstance(points, list) and len(points) > 0:
                        if isinstance(points[0], (list, tuple)) and len(points[0]) >= 2:
                            x_coords = [p[0] for p in points]
                            y_coords = [p[1] for p in points]
                        elif len(points) >= 2 and isinstance(points[0], list):
                            x_coords = points[0] if points[0] else []
                            y_coords = points[1] if len(points) > 1 and points[1] else []
                        elif isinstance(points[0], (int, float)) and len(points) >= 4:
                            x_coords = points[::2]
                            y_coords = points[1::2]

                    if len(x_coords) >= 3 and len(y_coords) >= 3:
                        # Close the polygon
                        if x_coords[-1] != x_coords[0] or y_coords[-1] != y_coords[0]:
                            x_coords.append(x_coords[0])
                            y_coords.append(y_coords[0])

                        # Determine fill color based on zone type and special flags
                        fill_color = None
                        zone_type = zone.get('zone_type', 'Unknown').lower()
                        if zone_type == 'entry' and show_entry_zones:
                            fill_color = special_zone_colors['entry']
                        elif zone_type == 'no_entry' and show_no_entry_zones:
                            fill_color = special_zone_colors['no_entry']
                        elif zone_type == 'wall' and show_walls:
                            fill_color = special_zone_colors['wall']
                        else:
                            # Default color by room type
                            room_type = 'Unknown'
                            if color_by_type and analysis_results and 'rooms' in analysis_results:
                                zone_key = f"Zone_{i}"
                                if zone_key in analysis_results['rooms']:
                                    room_type = analysis_results['rooms'][zone_key].get('type', 'Unknown')
                            fill_color = color_map.get(room_type, 'lightgray')

                        fig.add_trace(go.Scatter(
                            x=x_coords,
                            y=y_coords,
                            fill="toself",
                            mode='lines+text' if show_labels else 'lines',
                            name=f"Zone {i}: {zone.get('zone_type', 'Unknown')}",
                            fillcolor=fill_color,
                            line=dict(width=2, color='black'),
                            text=f"Zone {i}" if show_labels else None,
                            textposition="middle center",
                            hovertemplate=f"<b>Zone {i}</b><br>Type: {zone.get('zone_type', 'Unknown')}<br>Area: {zone.get('area', 0):.1f} m²<extra></extra>"
                        ))

                except Exception as e:
                    continue

        # Add box placements if available
        if show_boxes and analysis_results and 'placements' in analysis_results:
            box_count = 0
            for zone_name, placements in analysis_results['placements'].items():
                if isinstance(placements, list):
                    for j, placement in enumerate(placements):
                        try:
                            if isinstance(placement, dict) and 'position' in placement:
                                x, y = placement['position']
                                size = placement.get('size', (2.0, 1.5))
                                
                                fig.add_trace(go.Scatter(
                                    x=[x], y=[y],
                                    mode='markers',
                                    marker=dict(size=15, color='red', symbol='square'),
                                    name='Furniture' if box_count == 0 else None,
                                    showlegend=(box_count == 0),
                                    hovertemplate=f"<b>Furniture Placement</b><br>Position: ({x:.1f}, {y:.1f})<br>Size: {size[0]:.1f}×{size[1]:.1f}m<br>Zone: {zone_name}<extra></extra>"
                                ))
                                box_count += 1
                        except Exception as e:
                            continue

        # Add pathway/flow visualization with arrows
        if show_pathways and analysis_results and 'spatial_relationships' in analysis_results:
            pathways = analysis_results['spatial_relationships'].get('pathways', [])
            for path in pathways:
                try:
                    x_coords = [point[0] for point in path['points']]
                    y_coords = [point[1] for point in path['points']]
                    fig.add_trace(go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode='lines+markers',
                        line=dict(color='green', width=3, dash='dot'),
                        marker=dict(symbol='arrow-up', size=10, angleref='previous'),
                        name='Pathway',
                        hoverinfo='none',
                        showlegend=False
                    ))
                except Exception as e:
                    continue

        # Add annotations if provided
        if show_annotations and annotations:
            for annotation in annotations:
                try:
                    x = annotation.get('x')
                    y = annotation.get('y')
                    text = annotation.get('text')
                    if x is not None and y is not None and text:
                        fig.add_annotation(
                            x=x,
                            y=y,
                            text=text,
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=-40,
                            bgcolor='yellow',
                            bordercolor='black',
                            borderwidth=1
                        )
                except Exception as e:
                    continue

        fig.update_layout(
            title="Interactive Floor Plan Analysis",
            xaxis_title="X Coordinate (m)",
            yaxis_title="Y Coordinate (m)", 
            showlegend=True,
            hovermode='closest',
            height=600,
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )

        return fig

    def create_3d_plot(self, zones, analysis_results):
        """Create 3D visualization"""
        fig = go.Figure()

        if not zones:
            fig.update_layout(title="No zones to display")
            return fig

        # Base height for 3D view
        base_height = 3.0

        for i, zone in enumerate(zones):
            try:
                points = zone.get('points', [])
                if not points:
                    continue

                x_coords = []
                y_coords = []

                # Handle various point formats
                if isinstance(points, list) and len(points) > 0:
                    if isinstance(points[0], (list, tuple)) and len(points[0]) >= 2:
                        x_coords = [p[0] for p in points]
                        y_coords = [p[1] for p in points]
                    elif len(points) >= 2 and isinstance(points[0], list):
                        x_coords = points[0] if points[0] else []
                        y_coords = points[1] if len(points) > 1 and points[1] else []

                if len(x_coords) >= 3 and len(y_coords) >= 3:
                    # Close the polygon
                    if x_coords[-1] != x_coords[0] or y_coords[-1] != y_coords[0]:
                        x_coords.append(x_coords[0])
                        y_coords.append(y_coords[0])

                    z_coords = [0] * len(x_coords)
                    z_top = [base_height] * len(x_coords)

                    # Add floor
                    fig.add_trace(
                        go.Scatter3d(x=x_coords,
                                     y=y_coords,
                                     z=z_coords,
                                     mode='lines',
                                     name=f'Zone {i} Floor',
                                     line=dict(color='blue', width=3)))

                    # Add ceiling
                    fig.add_trace(
                        go.Scatter3d(x=x_coords,
                                     y=y_coords,
                                     z=z_top,
                                     mode='lines',
                                     name=f'Zone {i} Ceiling',
                                     line=dict(color='lightblue', width=2)))

            except Exception as e:
                continue

        # Add furniture placements in 3D
        if analysis_results and 'placements' in analysis_results:
            for zone_name, placements in analysis_results['placements'].items():
                if isinstance(placements, list):
                    for placement in placements:
                        try:
                            if isinstance(placement, dict) and 'position' in placement:
                                x, y = placement['position']
                                fig.add_trace(go.Scatter3d(
                                    x=[x], y=[y], z=[1.0],  # 1m height for furniture
                                    mode='markers',
                                    marker=dict(size=8, color='red', symbol='cube'),
                                    name='Furniture',
                                    showlegend=False,
                                    hovertemplate=f"<b>Furniture</b><br>Position: ({x:.1f}, {y:.1f})<br>Zone: {zone_name}<extra></extra>"
                                ))
                        except Exception as e:
                            continue

        fig.update_layout(title="3D Floor Plan Visualization",
                          scene=dict(aspectmode='data',
                                     camera=dict(up=dict(x=0, y=0, z=1),
                                                 center=dict(x=0, y=0, z=0),
                                                 eye=dict(x=1.5, y=1.5, z=1.5)),
                                     xaxis_title="X (meters)",
                                     yaxis_title="Y (meters)",
                                     zaxis_title="Z (meters)"),
                          height=600)

        return fig

    def display_statistics(self, results):
        """Display detailed statistics with fixed Plotly configuration"""
        if not results:
            st.info("Run AI analysis to see statistics")
            return

        # Overall statistics
        st.subheader("📈 Overall Statistics")

        col1, col2 = st.columns(2)

        with col1:
            # Room type distribution
            room_types = []
            rooms_data = results.get('rooms', {})
            
            if rooms_data:
                for room_info in rooms_data.values():
                    if isinstance(room_info, dict):
                        room_type = room_info.get('type', 'Unknown')
                        room_types.append(room_type)

            if room_types:
                room_type_counts = pd.Series(room_types).value_counts()

                fig_pie = px.pie(
                    values=room_type_counts.values,
                    names=room_type_counts.index,
                    title="Room Type Distribution"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No room type data available")

        with col2:
            # Box placement by room
            placement_counts = {}
            placements_data = results.get('placements', {})
            
            if placements_data:
                for zone, placements in placements_data.items():
                    if isinstance(placements, list):
                        placement_counts[zone] = len(placements)

            if placement_counts:
                fig_bar = go.Figure(data=[
                    go.Bar(x=list(placement_counts.keys()),
                           y=list(placement_counts.values()),
                           marker_color='lightblue')
                ])
                fig_bar.update_layout(
                    title="Boxes per Zone",
                    xaxis=dict(title="Zone", tickangle=45),
                    yaxis=dict(title="Number of Boxes"),
                    margin=dict(t=50, l=50, r=50, b=100),
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No placement data available")

        # Efficiency metrics
        st.subheader("⚡ Efficiency Metrics")

        # Calculate metrics safely
        try:
            total_room_area = 0
            if rooms_data:
                for room_info in rooms_data.values():
                    if isinstance(room_info, dict):
                        area = room_info.get('area', 0.0)
                        if isinstance(area, (int, float)):
                            total_room_area += area

            total_boxes = results.get('total_boxes', 0)
            if not isinstance(total_boxes, (int, float)):
                total_boxes = 0

            box_size = results.get('parameters', {}).get('box_size', [2.0, 1.5])
            if isinstance(box_size, (list, tuple)) and len(box_size) >= 2:
                total_box_area = total_boxes * box_size[0] * box_size[1]
            else:
                total_box_area = total_boxes * 3.0  # Default area

            space_utilization = (total_box_area / total_room_area) * 100 if total_room_area > 0 else 0

            # Display metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

            with metrics_col1:
                st.metric("Space Utilization", f"{space_utilization:.1f}%")

            with metrics_col2:
                avg_suitability = 0
                if placements_data:
                    all_scores = []
                    for placements in placements_data.values():
                        if isinstance(placements, list):
                            for placement in placements:
                                if isinstance(placement, dict):
                                    score = placement.get('suitability_score', 0)
                                    if isinstance(score, (int, float)):
                                        all_scores.append(score)
                    avg_suitability = sum(all_scores) / len(all_scores) if all_scores else 0
                st.metric("Avg. Suitability Score", f"{avg_suitability:.2f}")

            with metrics_col3:
                boxes_per_m2 = total_boxes / total_room_area if total_room_area > 0 else 0
                st.metric("Boxes per m²", f"{boxes_per_m2:.2f}")

        except Exception as e:
            st.error(f"Error calculating statistics: {str(e)}")
            st.info("Some statistics may be unavailable due to data format issues")
