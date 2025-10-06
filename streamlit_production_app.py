"""
Production Îlot Placement System - Streamlit Application
Professional floor plan processing with automatic îlot and corridor placement
NO SIMULATIONS - Production-grade processing only
"""

import streamlit as st
import plotly.graph_objects as go
import tempfile
import os
from pathlib import Path
import logging

from core.production_orchestrator import ProductionOrchestrator
from core.production_ilot_engine import IlotSizeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🏗️ Îlot Placement",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def create_visualization(result, view_mode='complete'):
    """Create interactive Plotly visualization"""
    fig = go.Figure()
    
    # Draw open spaces (light gray background)
    if view_mode in ['plan', 'complete', 'ilots', 'corridors']:
        for i, space in enumerate(result.open_spaces):
            coords = list(space.exterior.coords)
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(240, 240, 240, 0.5)',
                line=dict(color='lightgray', width=1),
                name='Open Spaces' if i == 0 else None,
                legendgroup='spaces',
                showlegend=(i == 0),
                hoverinfo='skip'
            ))
    
    # Draw walls (black)
    if view_mode in ['plan', 'complete', 'ilots', 'corridors']:
        for i, wall in enumerate(result.walls):
            coords = list(wall.exterior.coords)
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(26, 26, 26, 0.95)',
                line=dict(color='black', width=4),
                name='⬛ Walls (MUR)' if i == 0 else None,
                legendgroup='walls',
                showlegend=(i == 0),
                hovertext='Wall - Îlots can touch',
                hoverinfo='text'
            ))
    
    # Draw restricted areas (blue - NO ENTREE)
    if view_mode in ['plan', 'complete', 'ilots', 'corridors']:
        for i, restricted in enumerate(result.restricted_areas):
            coords = list(restricted.exterior.coords)
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(70, 130, 255, 0.7)',
                line=dict(color='blue', width=3),
                name='🔵 Restricted (NO ENTREE)' if i == 0 else None,
                legendgroup='restricted',
                showlegend=(i == 0),
                hovertext='Restricted Area - Stairs/Elevators',
                hoverinfo='text'
            ))
    
    # Draw entrances (red - ENTREE/SORTIE)
    if view_mode in ['plan', 'complete', 'ilots', 'corridors']:
        for i, entrance in enumerate(result.entrances):
            coords = list(entrance.exterior.coords)
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(255, 68, 68, 0.7)',
                line=dict(color='red', width=4),
                name='🔴 Entrances (ENTREE/SORTIE)' if i == 0 else None,
                legendgroup='entrances',
                showlegend=(i == 0),
                hovertext='Entrance/Exit - No îlot contact',
                hoverinfo='text'
            ))
    
    # Draw îlots (green)
    if view_mode in ['ilots', 'complete', 'corridors']:
        for i, ilot in enumerate(result.ilots):
            coords = list(ilot.polygon.exterior.coords)
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(46, 204, 113, 0.8)',
                line=dict(color='darkgreen', width=2),
                name=f'🟢 Îlots ({len(result.ilots)} total)' if i == 0 else None,
                legendgroup='ilots',
                showlegend=(i == 0),
                hovertext=f'Îlot #{ilot.id}<br>Area: {ilot.area:.2f}m²<br>Category: {ilot.category}',
                hoverinfo='text'
            ))
    
    # Draw corridors (purple)
    if view_mode in ['corridors', 'complete']:
        for i, corridor in enumerate(result.corridors):
            coords = list(corridor.polygon.exterior.coords)
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                fill='toself',
                fillcolor='rgba(155, 89, 182, 0.6)',
                line=dict(color='purple', width=2),
                name=f'🟣 Corridors ({len(result.corridors)} total)' if i == 0 else None,
                legendgroup='corridors',
                showlegend=(i == 0),
                hovertext=f'Corridor #{corridor.id}<br>Width: {corridor.width:.2f}m<br>Length: {corridor.length:.2f}m',
                hoverinfo='text'
            ))
    
    # Update layout
    fig.update_layout(
        title=f"Floor Plan - {view_mode.title()} View",
        xaxis_title="X (meters)",
        yaxis_title="Y (meters)",
        showlegend=True,
        height=700,
        template="plotly_white",
        xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=True, gridcolor='lightgray'),
        yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=True, gridcolor='lightgray'),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="gray",
            borderwidth=1
        ),
        hovermode='closest'
    )
    
    return fig


def main():
    # Minimal header
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ Îlot Placement</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️")
        
        size_0_1 = st.slider("0-1m²", 0.0, 1.0, 0.10, 0.05)
        size_1_3 = st.slider("1-3m²", 0.0, 1.0, 0.25, 0.05)
        size_3_5 = st.slider("3-5m²", 0.0, 1.0, 0.30, 0.05)
        size_5_10 = st.slider("5-10m²", 0.0, 1.0, 0.35, 0.05)
        
        total_pct = size_0_1 + size_1_3 + size_3_5 + size_5_10
        if abs(total_pct - 1.0) > 0.01:
            st.warning(f"⚠️ {total_pct*100:.0f}%")
        else:
            st.success(f"✅ 100%")
        
        st.markdown("---")
        total_ilots = st.number_input("Îlots", 10, 500, 100, 10)
        min_spacing = st.slider("Spacing (m)", 0.1, 2.0, 0.3, 0.1)
        corridor_width = st.slider("Corridor (m)", 1.0, 3.0, 1.5, 0.1)
        wall_thickness = st.slider("Walls (m)", 0.10, 0.50, 0.25, 0.05)
    
    # Main content
    uploaded_file = st.file_uploader("📁 DXF File", type=['dxf'])
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        try:
            # Process button
            if st.button("🚀 Generate", type="primary"):
                with st.spinner("Processing..."):
                    # Create size configuration
                    size_config = IlotSizeConfig(
                        size_0_1_pct=size_0_1,
                        size_1_3_pct=size_1_3,
                        size_3_5_pct=size_3_5,
                        size_5_10_pct=size_5_10
                    )
                    
                    # Process with wall thickness
                    orchestrator = ProductionOrchestrator()
                    orchestrator.cad_parser.wall_buffer = wall_thickness
                    result = orchestrator.process_floor_plan(
                        dxf_file_path=tmp_file_path,
                        size_config=size_config,
                        total_ilots=total_ilots,
                        corridor_width=corridor_width,
                        min_spacing=min_spacing
                    )
                    
                    # Store result in session state
                    st.session_state['result'] = result
                
                # Display results
                if result.success:
                    st.success(f"✅ {result.processing_time:.2f}s")
                else:
                    st.error(f"⚠️ {result.error_message}")
        
        finally:
            # Cleanup temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    # Display results if available
    if 'result' in st.session_state:
        result = st.session_state['result']
        
        if result.success:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Îlots", f"{len(result.ilots)}", f"{result.ilot_coverage_pct:.1f}%")
            
            with col2:
                st.metric("Corridors", f"{len(result.corridors)}", f"{result.corridor_coverage_pct:.1f}%")
            
            with col3:
                st.metric("Coverage", f"{result.total_coverage_pct:.1f}%", f"{result.total_area:.0f}m²")
            
            with col4:
                st.metric("Time", f"{result.processing_time:.2f}s")
            
            # Visualization tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📐 Plan", "🟢 Îlots", "🟣 Complete", "📈 Data"])
            
            with tab1:
                st.plotly_chart(create_visualization(result, 'plan'), use_container_width=True)
            
            with tab2:
                st.plotly_chart(create_visualization(result, 'ilots'), use_container_width=True)
            
            with tab3:
                st.plotly_chart(create_visualization(result, 'complete'), use_container_width=True)
            
            with tab4:
                col1, col2 = st.columns(2)
                
                with col1:
                    category_counts = {}
                    category_areas = {}
                    for ilot in result.ilots:
                        cat = ilot.category
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                        category_areas[cat] = category_areas.get(cat, 0) + ilot.area
                    
                    import pandas as pd
                    df = pd.DataFrame({
                        'Size': list(category_counts.keys()),
                        'Count': list(category_counts.values()),
                        'Area': [f"{a:.1f}" for a in category_areas.values()]
                    })
                    st.dataframe(df, use_container_width=True)
                
                with col2:
                    metrics_data = {
                        'Element': ['Area', 'Walls', 'Restricted', 'Entrances'],
                        'Value': [
                            f"{result.total_area:.0f}m²",
                            f"{len(result.walls)}",
                            f"{len(result.restricted_areas)}",
                            f"{len(result.entrances)}"
                        ]
                    }
                    st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)
    
    else:
        # Minimal legend
        st.markdown("""
        <div class="info-box">
            <h4>📋 Legend</h4>
            <ul>
                <li>⬛ <strong>Walls</strong> → îlots CAN touch</li>
                <li>🔵 <strong>Restricted</strong> → NO ENTREE</li>
                <li>🔴 <strong>Entrances</strong> → No îlot contact</li>
                <li>🟢 <strong>Îlots</strong> → Placed units</li>
                <li>🟣 <strong>Corridors</strong> → Auto-generated</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
