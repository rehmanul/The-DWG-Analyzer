"""
Automated Professional Report Generation System
"""
import streamlit as st
from datetime import datetime
import json
from typing import Dict, List, Any
import pandas as pd

class AutomatedReportGenerator:
    def __init__(self):
        self.report_templates = {
            'executive_summary': self._generate_executive_summary,
            'technical_analysis': self._generate_technical_analysis,
            'construction_report': self._generate_construction_report,
            'space_utilization': self._generate_space_utilization,
            'cost_estimation': self._generate_cost_estimation
        }
    
    def generate_comprehensive_report(self, zones: List[Dict], 
                                    analysis_results: Dict) -> Dict:
        """Generate comprehensive automated report"""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_zones': len(zones),
                'analysis_type': analysis_results.get('analysis_type', 'standard'),
                'app_version': '2.0.0'
            },
            'sections': {}
        }
        
        # Generate all report sections
        for section_name, generator_func in self.report_templates.items():
            try:
                report['sections'][section_name] = generator_func(zones, analysis_results)
            except Exception as e:
                report['sections'][section_name] = {
                    'error': f"Failed to generate {section_name}: {str(e)}"
                }
        
        return report
    
    def _generate_executive_summary(self, zones: List[Dict], 
                                  analysis_results: Dict) -> Dict:
        """Generate executive summary"""
        total_area = sum(zone.get('area', 0) for zone in zones)
        total_furniture = analysis_results.get('total_boxes', 0)
        efficiency = analysis_results.get('optimization', {}).get('total_efficiency', 0.85)
        
        # Room type distribution
        room_types = {}
        for zone in zones:
            room_type = zone.get('zone_type', 'Unknown')
            room_types[room_type] = room_types.get(room_type, 0) + 1
        
        return {
            'project_overview': {
                'total_rooms': len(zones),
                'total_area_sqm': round(total_area, 2),
                'total_area_sqft': round(total_area * 10.764, 2),
                'furniture_items': total_furniture,
                'space_efficiency': f"{efficiency * 100:.1f}%"
            },
            'room_distribution': room_types,
            'key_insights': [
                f"Analyzed {len(zones)} rooms with total area of {total_area:.1f} m²",
                f"Optimal furniture placement achieved {efficiency*100:.1f}% efficiency",
                f"Most common room type: {max(room_types, key=room_types.get) if room_types else 'N/A'}",
                f"Average room size: {total_area/len(zones):.1f} m²" if zones else "No rooms"
            ]
        }
    
    def _generate_technical_analysis(self, zones: List[Dict], 
                                   analysis_results: Dict) -> Dict:
        """Generate technical analysis section"""
        rooms_data = analysis_results.get('rooms', {})
        
        technical_metrics = {
            'geometric_analysis': {},
            'spatial_relationships': {},
            'optimization_details': analysis_results.get('optimization', {})
        }
        
        # Geometric analysis
        areas = [zone.get('area', 0) for zone in zones]
        if areas:
            technical_metrics['geometric_analysis'] = {
                'min_room_area': min(areas),
                'max_room_area': max(areas),
                'avg_room_area': sum(areas) / len(areas),
                'total_perimeter': sum(self._calculate_perimeter(zone.get('points', [])) for zone in zones)
            }
        
        # Room confidence scores
        confidence_scores = []
        for room_info in rooms_data.values():
            confidence_scores.append(room_info.get('confidence', 0.0))
        
        if confidence_scores:
            technical_metrics['classification_accuracy'] = {
                'avg_confidence': sum(confidence_scores) / len(confidence_scores),
                'min_confidence': min(confidence_scores),
                'max_confidence': max(confidence_scores),
                'high_confidence_rooms': len([c for c in confidence_scores if c > 0.8])
            }
        
        return technical_metrics
    
    def _generate_construction_report(self, zones: List[Dict], 
                                    analysis_results: Dict) -> Dict:
        """Generate construction report"""
        total_wall_length = 0
        total_area = 0
        
        for zone in zones:
            points = zone.get('points', [])
            if len(points) >= 3:
                perimeter = self._calculate_perimeter(points)
                total_wall_length += perimeter
                total_area += zone.get('area', 0)
        
        # Material calculations
        wall_thickness = 0.2  # 20cm
        wall_height = 3.0     # 3m
        
        concrete_volume = total_wall_length * wall_thickness * wall_height
        concrete_blocks = int(total_wall_length * 20)  # 20 blocks per meter
        cement_bags = int(total_wall_length * 2)       # 2 bags per meter
        steel_bars = int(total_wall_length * 5)        # 5 bars per meter
        
        return {
            'structural_requirements': {
                'total_wall_length_m': round(total_wall_length, 2),
                'total_floor_area_m2': round(total_area, 2),
                'concrete_volume_m3': round(concrete_volume, 2),
                'wall_thickness_m': wall_thickness,
                'wall_height_m': wall_height
            },
            'materials_list': {
                'concrete_blocks': concrete_blocks,
                'cement_bags_50kg': cement_bags,
                'steel_reinforcement_bars': steel_bars,
                'estimated_doors': len(zones),  # Assume 1 door per room
                'estimated_windows': len(zones) * 2  # Assume 2 windows per room
            },
            'cost_estimates': {
                'concrete_blocks_usd': concrete_blocks * 2.5,
                'cement_usd': cement_bags * 8.0,
                'steel_usd': steel_bars * 15.0,
                'labor_estimate_usd': total_area * 50,
                'total_estimated_cost_usd': (concrete_blocks * 2.5 + cement_bags * 8.0 + 
                                           steel_bars * 15.0 + total_area * 50)
            }
        }
    
    def _generate_space_utilization(self, zones: List[Dict], 
                                  analysis_results: Dict) -> Dict:
        """Generate space utilization analysis"""
        placements = analysis_results.get('placements', {})
        
        utilization_data = {}
        total_furniture_area = 0
        total_floor_area = sum(zone.get('area', 0) for zone in zones)
        
        for i, zone in enumerate(zones):
            zone_name = f"zone_{i}"
            zone_area = zone.get('area', 0)
            zone_furniture = placements.get(zone_name, [])
            
            # Calculate furniture area in this zone
            furniture_area = 0
            for furniture in zone_furniture:
                size = furniture.get('size', (2.0, 1.5))
                furniture_area += size[0] * size[1]
            
            total_furniture_area += furniture_area
            
            utilization_data[zone_name] = {
                'room_type': zone.get('zone_type', 'Unknown'),
                'floor_area_m2': zone_area,
                'furniture_area_m2': furniture_area,
                'utilization_percentage': (furniture_area / zone_area * 100) if zone_area > 0 else 0,
                'furniture_count': len(zone_furniture)
            }
        
        overall_utilization = (total_furniture_area / total_floor_area * 100) if total_floor_area > 0 else 0
        
        return {
            'overall_metrics': {
                'total_floor_area_m2': total_floor_area,
                'total_furniture_area_m2': total_furniture_area,
                'overall_utilization_percentage': overall_utilization,
                'average_utilization_per_room': sum(data['utilization_percentage'] 
                                                  for data in utilization_data.values()) / len(utilization_data) if utilization_data else 0
            },
            'room_by_room_analysis': utilization_data,
            'recommendations': self._generate_utilization_recommendations(utilization_data)
        }
    
    def _generate_cost_estimation(self, zones: List[Dict], 
                                analysis_results: Dict) -> Dict:
        """Generate cost estimation"""
        # Construction costs
        construction_report = self._generate_construction_report(zones, analysis_results)
        construction_cost = construction_report['cost_estimates']['total_estimated_cost_usd']
        
        # Furniture costs
        total_furniture = analysis_results.get('total_boxes', 0)
        avg_furniture_cost = 500  # USD per furniture item
        furniture_cost = total_furniture * avg_furniture_cost
        
        # Additional costs
        total_area = sum(zone.get('area', 0) for zone in zones)
        finishing_cost = total_area * 30  # USD per m²
        electrical_cost = total_area * 25  # USD per m²
        plumbing_cost = len(zones) * 1500  # USD per room (bathrooms/kitchens)
        
        total_project_cost = (construction_cost + furniture_cost + 
                            finishing_cost + electrical_cost + plumbing_cost)
        
        return {
            'cost_breakdown': {
                'construction_usd': construction_cost,
                'furniture_usd': furniture_cost,
                'finishing_usd': finishing_cost,
                'electrical_usd': electrical_cost,
                'plumbing_usd': plumbing_cost,
                'total_project_cost_usd': total_project_cost
            },
            'cost_per_sqm': total_project_cost / total_area if total_area > 0 else 0,
            'financing_options': {
                'cash_payment_discount': total_project_cost * 0.95,
                'monthly_payment_24_months': total_project_cost / 24,
                'monthly_payment_36_months': total_project_cost / 36
            }
        }
    
    def _calculate_perimeter(self, points: List[tuple]) -> float:
        """Calculate perimeter of polygon"""
        if len(points) < 3:
            return 0
        
        perimeter = 0
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            perimeter += ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
        
        return perimeter
    
    def _generate_utilization_recommendations(self, utilization_data: Dict) -> List[str]:
        """Generate space utilization recommendations"""
        recommendations = []
        
        for zone_name, data in utilization_data.items():
            utilization = data['utilization_percentage']
            room_type = data['room_type']
            
            if utilization < 30:
                recommendations.append(f"{room_type}: Under-utilized space. Consider adding more furniture or storage.")
            elif utilization > 80:
                recommendations.append(f"{room_type}: Over-crowded space. Consider reducing furniture or expanding room.")
            elif 50 <= utilization <= 70:
                recommendations.append(f"{room_type}: Optimal space utilization achieved.")
        
        return recommendations
    
    def export_report_formats(self, report: Dict) -> Dict[str, str]:
        """Export report in multiple formats"""
        formats = {}
        
        # JSON format
        formats['json'] = json.dumps(report, indent=2, default=str)
        
        # CSV format (summary data)
        csv_data = []
        if 'sections' in report and 'space_utilization' in report['sections']:
            room_data = report['sections']['space_utilization'].get('room_by_room_analysis', {})
            for zone_name, data in room_data.items():
                csv_data.append({
                    'Zone': zone_name,
                    'Room Type': data.get('room_type', ''),
                    'Floor Area (m²)': data.get('floor_area_m2', 0),
                    'Furniture Area (m²)': data.get('furniture_area_m2', 0),
                    'Utilization (%)': data.get('utilization_percentage', 0),
                    'Furniture Count': data.get('furniture_count', 0)
                })
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            formats['csv'] = df.to_csv(index=False)
        
        return formats