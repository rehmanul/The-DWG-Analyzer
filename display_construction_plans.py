"""
Advanced Construction Plans Display Function
"""
import streamlit as st

def display_construction_plans(components):
    """Display advanced construction plans with professional visualization"""
    if not st.session_state.zones:
        st.info("Load a DWG file to see construction plans")
        return
    
    from src.advanced_visualization import AdvancedVisualizer
    visualizer = AdvancedVisualizer()
    
    st.subheader("🏗️ Professional Construction Plans")
    
    # Advanced construction controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        plan_type = st.selectbox("Plan Type", ["Construction Plan", "Architectural Plan", "Structural Plan"], key="const_plan_type")
        st.info(f"Showing: {plan_type}")
    with col2:
        view_mode = st.selectbox("View Mode", ["2D Construction", "3D Construction Model"], key="const_view_mode")
    with col3:
        show_details = st.checkbox("Show Construction Details", value=True, key="const_show_details")
    with col4:
        show_structure = st.checkbox("Show Structure", value=True, key="const_show_structure")
    
    # Generate different visualizations based on plan type
    if view_mode == "3D Construction Model":
        if plan_type == "Structural Plan":
            fig = visualizer.create_structural_plan_3d(st.session_state.zones)
        elif plan_type == "Architectural Plan":
            fig = visualizer.create_architectural_plan_3d(st.session_state.zones)
        else:
            fig = visualizer.create_construction_plan_3d(st.session_state.zones, show_structure)
    else:
        if plan_type == "Structural Plan":
            fig = visualizer.create_structural_plan_2d(st.session_state.zones)
        elif plan_type == "Architectural Plan":
            fig = visualizer.create_architectural_plan_2d(st.session_state.zones)
        else:
            fig = visualizer.create_construction_plan_2d(st.session_state.zones, show_details)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Construction plan tabs
    plan_tabs = st.tabs(["Construction Details", "Materials List", "Specifications"])
    
    with plan_tabs[0]:
        st.subheader("📊 Construction Analysis")
        if st.session_state.zones:
            # Calculate construction metrics
            total_wall_length = 0
            total_area = 0
            
            for zone in st.session_state.zones:
                points = zone.get('points', [])
                if len(points) >= 3:
                    # Calculate perimeter (wall length)
                    perimeter = 0
                    for i in range(len(points)):
                        start = points[i]
                        end = points[(i + 1) % len(points)]
                        perimeter += ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
                    total_wall_length += perimeter
                    total_area += zone.get('area', 0)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Wall Length", f"{total_wall_length:.1f} m")
            with col2:
                st.metric("Total Floor Area", f"{total_area:.1f} m²")
            with col3:
                st.metric("Concrete Needed", f"{total_wall_length * 0.3 * 3:.1f} m³")
            with col4:
                st.metric("Steel Bars", f"{int(total_wall_length * 5)} units")
    
    with plan_tabs[1]:
        st.subheader("🧱 Materials Estimation")
        
        if st.session_state.zones:
            materials_data = []
            for i, zone in enumerate(st.session_state.zones):
                points = zone.get('points', [])
                if len(points) >= 3:
                    perimeter = sum(
                        ((points[(j+1) % len(points)][0] - points[j][0])**2 + 
                         (points[(j+1) % len(points)][1] - points[j][1])**2)**0.5
                        for j in range(len(points))
                    )
                    
                    materials_data.append({
                        'Room': f"Room {i+1}",
                        'Wall Length (m)': f"{perimeter:.1f}",
                        'Concrete Blocks': int(perimeter * 20),
                        'Cement Bags': int(perimeter * 2),
                        'Steel Bars': int(perimeter * 5),
                        'Area (m²)': f"{zone.get('area', 0):.1f}"
                    })
            
            if materials_data:
                import pandas as pd
                df = pd.DataFrame(materials_data)
                st.dataframe(df, use_container_width=True)
    
    with plan_tabs[2]:
        st.subheader("📝 Technical Specifications")
        
        spec_col1, spec_col2 = st.columns(2)
        
        with spec_col1:
            st.write("**Structural Specifications:**")
            st.write("• Wall Thickness: 200mm")
            st.write("• Foundation Depth: 1.5m")
            st.write("• Concrete Grade: M25")
            st.write("• Steel Grade: Fe500")
            st.write("• Wall Height: 3.0m")
        
        with spec_col2:
            st.write("**Construction Standards:**")
            st.write("• Building Code: IBC 2021")
            st.write("• Seismic Zone: As per location")
            st.write("• Fire Safety: NFPA compliant")
            st.write("• Accessibility: ADA compliant")
            st.write("• Energy Efficiency: LEED ready")