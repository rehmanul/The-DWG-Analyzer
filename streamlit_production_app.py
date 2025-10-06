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
    page_title="Production Îlot Placement System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
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
                fillcolor='rgba(50, 50, 50, 0.8)',
                line=dict(color='black', width=2),
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
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ Production Îlot Placement System</h1>
        <p>Professional CAD Processing • Automatic Îlot Placement • Intelligent Corridor Generation</p>
        <p style="font-size: 0.9em; margin-top: 10px;">
            <strong>NO SIMULATIONS</strong> - Real architectural processing with production-grade algorithms
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.markdown("---")
        
        # Îlot size distribution
        st.subheader("📊 Îlot Size Distribution")
        st.markdown("*Define the percentage of each îlot size category*")
        
        size_0_1 = st.slider(
            "Micro (0-1 m²)",
            min_value=0.0, max_value=1.0, value=0.10, step=0.05,
            help="Percentage of îlots between 0-1 m²"
        )
        
        size_1_3 = st.slider(
            "Small (1-3 m²)",
            min_value=0.0, max_value=1.0, value=0.25, step=0.05,
            help="Percentage of îlots between 1-3 m²"
        )
        
        size_3_5 = st.slider(
            "Medium (3-5 m²)",
            min_value=0.0, max_value=1.0, value=0.30, step=0.05,
            help="Percentage of îlots between 3-5 m²"
        )
        
        size_5_10 = st.slider(
            "Large (5-10 m²)",
            min_value=0.0, max_value=1.0, value=0.35, step=0.05,
            help="Percentage of îlots between 5-10 m²"
        )
        
        # Validate total percentage
        total_pct = size_0_1 + size_1_3 + size_3_5 + size_5_10
        if abs(total_pct - 1.0) > 0.01:
            st.warning(f"⚠️ Total percentage: {total_pct*100:.0f}% (should be 100%)")
        else:
            st.success(f"✅ Total percentage: 100%")
        
        st.markdown("---")
        
        # Placement parameters
        st.subheader("🎯 Placement Parameters")
        
        total_ilots = st.number_input(
            "Target number of îlots",
            min_value=10, max_value=500, value=100, step=10,
            help="Total number of îlots to place"
        )
        
        min_spacing = st.slider(
            "Minimum spacing (m)",
            min_value=0.1, max_value=2.0, value=0.3, step=0.1,
            help="Minimum distance between îlots"
        )
        
        corridor_width = st.slider(
            "Corridor width (m)",
            min_value=1.0, max_value=3.0, value=1.5, step=0.1,
            help="Width of corridors between îlot rows"
        )
        
        st.markdown("---")
        st.markdown("### 📋 System Rules")
        st.markdown("""
        - **Black lines** = Walls (îlots CAN touch)
        - **Blue zones** = NO ENTREE (stairs, elevators)
        - **Red zones** = ENTREE/SORTIE (no îlot contact)
        - **Corridors** = Auto-generated between rows
        """)
    
    # Main content
    st.header("📁 Upload Floor Plan")
    
    uploaded_file = st.file_uploader(
        "Choose a DXF file",
        type=['dxf'],
        help="Upload your architectural floor plan in DXF format"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        try:
            # Process button
            if st.button("🚀 Process Floor Plan", type="primary"):
                with st.spinner("Processing floor plan..."):
                    # Create size configuration
                    size_config = IlotSizeConfig(
                        size_0_1_pct=size_0_1,
                        size_1_3_pct=size_1_3,
                        size_3_5_pct=size_3_5,
                        size_5_10_pct=size_5_10
                    )
                    
                    # Process
                    orchestrator = ProductionOrchestrator()
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
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Processing Complete!</strong><br>
                        Processed in {result.processing_time:.2f} seconds
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="warning-box">
                        <strong>⚠️ Processing Failed</strong><br>
                        {result.error_message}
                    </div>
                    """, unsafe_allow_html=True)
        
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
            st.header("📊 Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Îlots Placed", f"{len(result.ilots)}", 
                         f"{result.ilot_coverage_pct:.1f}% coverage")
            
            with col2:
                st.metric("Corridors", f"{len(result.corridors)}",
                         f"{result.corridor_coverage_pct:.1f}% area")
            
            with col3:
                st.metric("Total Coverage", f"{result.total_coverage_pct:.1f}%",
                         f"{result.total_area:.0f} m²")
            
            with col4:
                st.metric("Processing Time", f"{result.processing_time:.2f}s",
                         f"Score: {result.placement_score:.0f}")
            
            # Visualization tabs
            st.header("🎨 Visualization")
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📐 Floor Plan Only",
                "🟢 Îlot Placement",
                "🟣 Complete with Corridors",
                "📈 Analytics"
            ])
            
            with tab1:
                st.plotly_chart(create_visualization(result, 'plan'), use_container_width=True)
            
            with tab2:
                st.plotly_chart(create_visualization(result, 'ilots'), use_container_width=True)
            
            with tab3:
                st.plotly_chart(create_visualization(result, 'complete'), use_container_width=True)
            
            with tab4:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Îlot Distribution")
                    
                    # Category distribution
                    category_counts = {}
                    category_areas = {}
                    for ilot in result.ilots:
                        cat = ilot.category
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                        category_areas[cat] = category_areas.get(cat, 0) + ilot.area
                    
                    import pandas as pd
                    df = pd.DataFrame({
                        'Category': list(category_counts.keys()),
                        'Count': list(category_counts.values()),
                        'Total Area (m²)': [f"{a:.2f}" for a in category_areas.values()]
                    })
                    st.dataframe(df, use_container_width=True)
                
                with col2:
                    st.subheader("System Metrics")
                    
                    metrics_data = {
                        'Metric': [
                            'Total Floor Area',
                            'Open Space Area',
                            'Îlot Coverage',
                            'Corridor Coverage',
                            'Walls',
                            'Restricted Areas',
                            'Entrances'
                        ],
                        'Value': [
                            f"{result.total_area:.2f} m²",
                            f"{result.total_area:.2f} m²",
                            f"{result.ilot_coverage_pct:.1f}%",
                            f"{result.corridor_coverage_pct:.1f}%",
                            f"{len(result.walls)}",
                            f"{len(result.restricted_areas)}",
                            f"{len(result.entrances)}"
                        ]
                    }
                    st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)
    
    else:
        # Instructions
        st.markdown("""
        <div class="info-box">
            <h3>🎯 How to Use</h3>
            <ol>
                <li><strong>Upload</strong> your DXF floor plan file</li>
                <li><strong>Configure</strong> îlot size distribution in the sidebar</li>
                <li><strong>Adjust</strong> placement parameters (spacing, corridor width)</li>
                <li><strong>Click</strong> "Process Floor Plan" to start</li>
                <li><strong>View</strong> results and visualizations</li>
            </ol>
            
            <h4>📋 Color Coding Requirements:</h4>
            <ul>
                <li><strong>Black lines</strong> → Walls (îlots can touch)</li>
                <li><strong>Blue zones</strong> → Restricted areas (NO ENTREE - stairs, elevators)</li>
                <li><strong>Red zones</strong> → Entrances/Exits (ENTREE/SORTIE - no îlot contact)</li>
            </ul>
            
            <h4>✨ Features:</h4>
            <ul>
                <li>Real CAD entity processing (no simulations)</li>
                <li>Genetic algorithm for optimal placement</li>
                <li>Automatic corridor generation between rows</li>
                <li>Full constraint compliance</li>
                <li>Professional visualizations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
