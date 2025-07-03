"""
Enterprise Export Functions - Professional export capabilities for all analysis results
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import numpy as np

def export_layout_report(enterprise_data):
    """Export comprehensive layout analysis report"""
    dxf_data = enterprise_data['dxf_data']
    layout_data = enterprise_data['layout_data']
    metrics = layout_data.get('layout_metrics', {})
    validation = layout_data.get('validation', {})
    
    report = f"""ENTERPRISE LAYOUT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILE INFORMATION:
File: {enterprise_data['file_info']['name']}
Size: {enterprise_data['file_info']['size']} bytes
Type: {enterprise_data['file_info']['type']}

DXF ANALYSIS RESULTS:
Walls Detected: {len(dxf_data.get('walls', []))}
Restricted Areas: {len(dxf_data.get('restricted_areas', []))}
Entrances/Exits: {len(dxf_data.get('entrances_exits', []))}
Rooms Identified: {len(dxf_data.get('rooms', []))}

ÎLOT LAYOUT RESULTS:
Total Îlots: {metrics.get('total_ilots', 0)}
Placed Îlots: {metrics.get('placed_ilots', 0)}
Placement Rate: {metrics.get('placement_rate', 0):.1%}
Space Utilization: {metrics.get('space_utilization', 0):.1%}
Circulation Ratio: {metrics.get('circulation_ratio', 0):.2f}

COMPLIANCE STATUS:
Overall Score: {validation.get('compliance_score', 0):.1%}
Layout Valid: {'Yes' if validation.get('valid', False) else 'No'}
Warnings: {len(validation.get('warnings', []))}
Errors: {len(validation.get('errors', []))}

CORRIDOR SYSTEM:
Total Length: {metrics.get('total_corridor_length', 0):.1f} cm
Total Area: {layout_data.get('corridors', {}).get('total_area', 0):.1f} cm²
Average Width: {metrics.get('avg_corridor_width', 0):.1f} cm
"""
    
    # Add detailed îlot information
    ilots = layout_data.get('ilots', [])
    if ilots:
        report += "\nÎLOT DETAILS:\n"
        for ilot in ilots:
            if ilot.get('placed', False):
                profile_name = ilot.get('profile', {}).name if hasattr(ilot.get('profile', {}), 'name') else 'Unknown'
                report += f"\n{ilot.get('id', 'Unknown')}:"
                report += f"\n  Profile: {profile_name}"
                report += f"\n  Area: {ilot.get('area', 0):.1f} cm²"
                report += f"\n  Position: {ilot.get('position', (0, 0))}"
                report += f"\n  Score: {ilot.get('placement_score', 0):.2f}"
    
    st.download_button(
        "📅 Download Layout Report",
        data=report,
        file_name=f"layout_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def export_compliance_report(enterprise_data):
    """Export compliance analysis report"""
    layout_data = enterprise_data['layout_data']
    validation = layout_data.get('validation', {})
    
    data = []
    
    # Add îlot compliance data
    for ilot in layout_data.get('ilots', []):
        if ilot.get('placed', False):
            profile_name = ilot.get('profile', {}).name if hasattr(ilot.get('profile', {}), 'name') else 'Unknown'
            data.append({
                'Element_Type': 'Ilot',
                'Element_ID': ilot.get('id', 'Unknown'),
                'Profile': profile_name,
                'Area_cm2': ilot.get('area', 0),
                'Placement_Score': ilot.get('placement_score', 0),
                'Compliance_Status': 'Compliant' if ilot.get('placement_score', 0) > 0.5 else 'Review Required'
            })
    
    # Add corridor compliance data
    for corridor in layout_data.get('corridors', {}).get('corridors', []):
        width = corridor.get('width', 0)
        compliance_status = 'Compliant' if width >= 120 else 'Non-Compliant'
        
        data.append({
            'Element_Type': 'Corridor',
            'Element_ID': corridor.get('id', 'Unknown'),
            'Profile': corridor.get('type', 'Unknown'),
            'Area_cm2': corridor.get('area', 0),
            'Width_cm': width,
            'Compliance_Status': compliance_status
        })
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        "📅 Download Compliance Report",
        data=csv,
        file_name=f"compliance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_security_report(enterprise_data):
    """Export security analysis report"""
    dxf_data = enterprise_data['dxf_data']
    spatial_analysis = dxf_data.get('spatial_analysis', {})
    access_analysis = spatial_analysis.get('access_analysis', {})
    
    report = f"""SECURITY ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACCESS CONTROL ANALYSIS:
Total Entrances: {access_analysis.get('total_entrances', 0)}
Restricted Access Points: {access_analysis.get('restricted_access_points', 0)}
Security Risk Score: {access_analysis.get('security_risk_score', 0):.1%}

RESTRICTED AREAS:
"""
    
    restricted_areas = dxf_data.get('restricted_areas', [])
    if restricted_areas:
        for i, area in enumerate(restricted_areas):
            report += f"\nRestricted Area {i+1}:"
            report += f"\n  Type: {area.get('restriction_type', 'Unknown')}"
            report += f"\n  Area: {area.get('area', 0):.1f} cm²"
            report += f"\n  Detection Method: {area.get('detection_method', 'Unknown')}"
    else:
        report += "\nNo restricted areas detected."
    
    # Security zones
    security_zones = spatial_analysis.get('security_zones', [])
    if security_zones:
        report += "\n\nSECURITY ZONES:"
        for i, zone in enumerate(security_zones):
            report += f"\nSecurity Zone {i+1}:"
            report += f"\n  Security Level: {zone.get('security_level', 'Unknown')}"
            report += f"\n  Area: {zone.get('area_size', 0):.1f} cm²"
            report += f"\n  Access Points: {zone.get('access_points', 0)}"
            report += f"\n  Access Control Required: {'Yes' if zone.get('access_control_required', False) else 'No'}"
    
    st.download_button(
        "📅 Download Security Report",
        data=report,
        file_name=f"security_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def export_enhanced_dxf(enterprise_data):
    """Export enhanced DXF with all detected elements"""
    dxf_data = enterprise_data['dxf_data']
    
    dxf_content = """0
SECTION
2
ENTITIES
"""
    
    # Export walls
    for i, wall in enumerate(dxf_data.get('walls', [])):
        if 'start_point' in wall and 'end_point' in wall:
            start = wall['start_point']
            end = wall['end_point']
            dxf_content += f"""0
LINE
8
WALLS
10
{start[0]:.3f}
20
{start[1]:.3f}
11
{end[0]:.3f}
21
{end[1]:.3f}
"""
    
    # Export restricted areas
    for i, area in enumerate(dxf_data.get('restricted_areas', [])):
        if 'geometry' in area:
            points = area['geometry']
            dxf_content += f"""0
LWPOLYLINE
8
RESTRICTED
90
{len(points)}
70
1
"""
            for point in points:
                dxf_content += f"""10
{point[0]:.3f}
20
{point[1]:.3f}
"""
    
    dxf_content += """0
ENDSEC
0
EOF
"""
    
    st.download_button(
        "📅 Download Enhanced DXF",
        data=dxf_content,
        file_name=f"enhanced_dxf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf",
        mime="application/octet-stream"
    )

def export_ilot_dxf(enterprise_data):
    """Export îlot layout as DXF"""
    layout_data = enterprise_data['layout_data']
    
    dxf_content = """0
SECTION
2
ENTITIES
"""
    
    # Export placed îlots
    for ilot in layout_data.get('ilots', []):
        if ilot.get('placed', False) and 'geometry' in ilot:
            geometry = ilot['geometry']
            if hasattr(geometry, 'exterior'):
                coords = list(geometry.exterior.coords)[:-1]  # Remove duplicate last point
                
                dxf_content += f"""0
LWPOLYLINE
8
ILOTS
90
{len(coords)}
70
1
"""
                for coord in coords:
                    dxf_content += f"""10
{coord[0]:.3f}
20
{coord[1]:.3f}
"""
    
    # Export corridors
    for corridor in layout_data.get('corridors', {}).get('geometry', []):
        geometry = corridor.get('geometry')
        if geometry and hasattr(geometry, 'exterior'):
            coords = list(geometry.exterior.coords)[:-1]
            
            dxf_content += f"""0
LWPOLYLINE
8
CORRIDORS
90
{len(coords)}
70
1
"""
            for coord in coords:
                dxf_content += f"""10
{coord[0]:.3f}
20
{coord[1]:.3f}
"""
    
    dxf_content += """0
ENDSEC
0
EOF
"""
    
    st.download_button(
        "📅 Download Îlot Layout DXF",
        data=dxf_content,
        file_name=f"ilot_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dxf",
        mime="application/octet-stream"
    )

def export_visualization_images(enterprise_data):
    """Export visualization images"""
    st.success("✅ Visualization images export feature coming soon!")
    st.info("💡 This will export high-resolution 2D and 3D visualizations")

def export_complete_dataset(enterprise_data):
    """Export complete dataset as CSV"""
    # Combine all data into comprehensive dataset
    all_data = []
    
    # Add DXF elements
    for wall in enterprise_data['dxf_data'].get('walls', []):
        all_data.append({
            'Element_Type': 'Wall',
            'Element_ID': f"wall_{len(all_data)}",
            'Layer': wall.get('layer', 'Unknown'),
            'Length_cm': wall.get('length', 0),
            'Detection_Method': wall.get('source', 'Unknown')
        })
    
    # Add îlots
    for ilot in enterprise_data['layout_data'].get('ilots', []):
        if ilot.get('placed', False):
            profile_name = ilot.get('profile', {}).name if hasattr(ilot.get('profile', {}), 'name') else 'Unknown'
            all_data.append({
                'Element_Type': 'Ilot',
                'Element_ID': ilot.get('id', 'Unknown'),
                'Profile': profile_name,
                'Area_cm2': ilot.get('area', 0),
                'Position_X': ilot.get('position', (0, 0))[0],
                'Position_Y': ilot.get('position', (0, 0))[1],
                'Placement_Score': ilot.get('placement_score', 0)
            })
    
    df = pd.DataFrame(all_data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        "📅 Download Complete Dataset",
        data=csv,
        file_name=f"complete_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_json_data(enterprise_data):
    """Export data as JSON"""
    # Create exportable JSON structure
    export_data = {
        'metadata': {
            'export_timestamp': datetime.now().isoformat(),
            'file_info': enterprise_data['file_info']
        },
        'dxf_analysis': enterprise_data['dxf_data'],
        'layout_analysis': enterprise_data['layout_data']
    }
    
    # Convert to JSON string
    json_data = json.dumps(export_data, indent=2, default=str)
    
    st.download_button(
        "📅 Download JSON Data",
        data=json_data,
        file_name=f"enterprise_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def export_pdf_report(enterprise_data):
    """Export comprehensive PDF report"""
    st.success("✅ PDF report export feature coming soon!")
    st.info("💡 This will generate a comprehensive PDF report with visualizations and analysis")