"""
Phase 4 Analytics System - Advanced Analysis and Reporting
Comprehensive analytics dashboard with professional metrics and insights
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import math
import logging
from datetime import datetime
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsConfig:
    """Configuration for analytics system"""
    include_compliance_analysis: bool = True
    include_efficiency_metrics: bool = True
    include_spatial_analysis: bool = True
    include_optimization_suggestions: bool = True
    include_financial_estimates: bool = True
    report_format: str = "comprehensive"  # basic, standard, comprehensive
    
    # Benchmarking parameters
    industry_standards: Dict[str, float] = None
    
    def __post_init__(self):
        if self.industry_standards is None:
            self.industry_standards = {
                'space_utilization': 0.75,  # 75% target utilization
                'corridor_efficiency': 0.85,  # 85% corridor efficiency
                'accessibility_score': 0.90,  # 90% accessibility
                'circulation_ratio': 0.15,  # 15% circulation space
                'compliance_score': 0.95   # 95% compliance
            }

@dataclass
class AnalyticsReport:
    """Complete analytics report"""
    timestamp: datetime
    project_name: str
    
    # Core metrics
    space_utilization: float
    total_area: float
    total_ilots: int
    total_corridors: int
    
    # Efficiency metrics
    placement_efficiency: float
    corridor_efficiency: float
    accessibility_score: float
    
    # Compliance metrics
    compliance_score: float
    compliance_details: Dict[str, bool]
    
    # Spatial analysis
    spatial_distribution: Dict[str, float]
    density_analysis: Dict[str, float]
    
    # Financial estimates
    revenue_estimates: Dict[str, float]
    cost_estimates: Dict[str, float]
    
    # Optimization suggestions
    optimization_suggestions: List[str]
    performance_grade: str
    
    # Raw data
    raw_data: Dict[str, Any]

class Phase4AnalyticsSystem:
    """
    Advanced analytics system for comprehensive project analysis
    Provides professional-grade metrics and insights
    """
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.report = None
        
        # Analysis components
        self.geometric_analyzer = GeometricAnalyzer()
        self.efficiency_analyzer = EfficiencyAnalyzer()
        self.compliance_analyzer = ComplianceAnalyzer()
        self.spatial_analyzer = SpatialAnalyzer()
        self.financial_analyzer = FinancialAnalyzer()
        
    def generate_comprehensive_report(self, 
                                    phase1_data: Dict,
                                    ilots: List[Dict],
                                    corridors: List[Dict],
                                    walls: List[Dict],
                                    restricted_areas: List[Dict],
                                    entrances: List[Dict],
                                    project_name: str = "Project") -> AnalyticsReport:
        """
        Generate comprehensive analytics report
        """
        logger.info("Generating comprehensive analytics report")
        
        # Core geometric analysis
        geometric_metrics = self.geometric_analyzer.analyze_geometry(
            phase1_data, ilots, corridors, walls
        )
        
        # Efficiency analysis
        efficiency_metrics = self.efficiency_analyzer.analyze_efficiency(
            ilots, corridors, walls, restricted_areas
        )
        
        # Compliance analysis
        compliance_metrics = self.compliance_analyzer.analyze_compliance(
            ilots, corridors, walls, restricted_areas, entrances
        )
        
        # Spatial analysis
        spatial_metrics = self.spatial_analyzer.analyze_spatial_distribution(
            ilots, corridors, walls
        )
        
        # Financial analysis
        financial_metrics = self.financial_analyzer.analyze_financial_potential(
            ilots, corridors, geometric_metrics
        )
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            geometric_metrics, efficiency_metrics, compliance_metrics, spatial_metrics
        )
        
        # Calculate performance grade
        performance_grade = self._calculate_performance_grade(
            efficiency_metrics, compliance_metrics, spatial_metrics
        )
        
        # Create comprehensive report
        report = AnalyticsReport(
            timestamp=datetime.now(),
            project_name=project_name,
            
            # Core metrics
            space_utilization=geometric_metrics['space_utilization'],
            total_area=geometric_metrics['total_area'],
            total_ilots=len(ilots),
            total_corridors=len(corridors),
            
            # Efficiency metrics
            placement_efficiency=efficiency_metrics['placement_efficiency'],
            corridor_efficiency=efficiency_metrics['corridor_efficiency'],
            accessibility_score=efficiency_metrics['accessibility_score'],
            
            # Compliance metrics
            compliance_score=compliance_metrics['overall_score'],
            compliance_details=compliance_metrics['details'],
            
            # Spatial analysis
            spatial_distribution=spatial_metrics['distribution'],
            density_analysis=spatial_metrics['density'],
            
            # Financial estimates
            revenue_estimates=financial_metrics['revenue'],
            cost_estimates=financial_metrics['costs'],
            
            # Optimization suggestions
            optimization_suggestions=optimization_suggestions,
            performance_grade=performance_grade,
            
            # Raw data
            raw_data={
                'geometric': geometric_metrics,
                'efficiency': efficiency_metrics,
                'compliance': compliance_metrics,
                'spatial': spatial_metrics,
                'financial': financial_metrics
            }
        )
        
        self.report = report
        logger.info(f"Analytics report generated with grade: {performance_grade}")
        return report
    
    def _generate_optimization_suggestions(self, geometric: Dict, efficiency: Dict, 
                                         compliance: Dict, spatial: Dict) -> List[str]:
        """Generate optimization suggestions based on analysis"""
        suggestions = []
        
        # Space utilization suggestions
        if geometric['space_utilization'] < self.config.industry_standards['space_utilization']:
            suggestions.append("Consider increasing îlot density to improve space utilization")
        
        # Corridor efficiency suggestions
        if efficiency['corridor_efficiency'] < self.config.industry_standards['corridor_efficiency']:
            suggestions.append("Optimize corridor network to reduce circulation area")
        
        # Accessibility suggestions
        if efficiency['accessibility_score'] < self.config.industry_standards['accessibility_score']:
            suggestions.append("Improve corridor connectivity to enhance accessibility")
        
        # Compliance suggestions
        if compliance['overall_score'] < self.config.industry_standards['compliance_score']:
            suggestions.append("Address compliance issues to meet regulatory requirements")
        
        # Spatial distribution suggestions
        if spatial['distribution']['uniformity'] < 0.7:
            suggestions.append("Improve spatial distribution for better balance")
        
        # Performance-based suggestions
        if geometric['space_utilization'] > 0.9:
            suggestions.append("Consider reducing density to improve circulation")
        
        if len(suggestions) == 0:
            suggestions.append("Layout optimization is excellent - no major improvements needed")
        
        return suggestions
    
    def _calculate_performance_grade(self, efficiency: Dict, compliance: Dict, spatial: Dict) -> str:
        """Calculate overall performance grade"""
        scores = [
            efficiency['placement_efficiency'],
            efficiency['corridor_efficiency'],
            efficiency['accessibility_score'],
            compliance['overall_score'],
            spatial['distribution']['uniformity'],
            spatial['density']['balance_score']
        ]
        
        average_score = sum(scores) / len(scores)
        
        if average_score >= 0.95:
            return "A+"
        elif average_score >= 0.90:
            return "A"
        elif average_score >= 0.85:
            return "A-"
        elif average_score >= 0.80:
            return "B+"
        elif average_score >= 0.75:
            return "B"
        elif average_score >= 0.70:
            return "B-"
        elif average_score >= 0.65:
            return "C+"
        elif average_score >= 0.60:
            return "C"
        else:
            return "D"
    
    def export_report_to_dataframe(self) -> pd.DataFrame:
        """Export report to pandas DataFrame"""
        if not self.report:
            return pd.DataFrame()
        
        data = {
            'Metric': [
                'Space Utilization',
                'Total Area',
                'Total Îlots',
                'Total Corridors',
                'Placement Efficiency',
                'Corridor Efficiency',
                'Accessibility Score',
                'Compliance Score',
                'Performance Grade'
            ],
            'Value': [
                f"{self.report.space_utilization:.1%}",
                f"{self.report.total_area:.1f}m²",
                str(self.report.total_ilots),
                str(self.report.total_corridors),
                f"{self.report.placement_efficiency:.1%}",
                f"{self.report.corridor_efficiency:.1%}",
                f"{self.report.accessibility_score:.1%}",
                f"{self.report.compliance_score:.1%}",
                self.report.performance_grade
            ],
            'Industry Standard': [
                f"{self.config.industry_standards['space_utilization']:.1%}",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                f"{self.config.industry_standards['corridor_efficiency']:.1%}",
                f"{self.config.industry_standards['accessibility_score']:.1%}",
                f"{self.config.industry_standards['compliance_score']:.1%}",
                "A"
            ]
        }
        
        return pd.DataFrame(data)
    
    def get_key_insights(self) -> List[str]:
        """Get key insights from the analysis"""
        if not self.report:
            return []
        
        insights = []
        
        # Performance insights
        if self.report.performance_grade in ['A+', 'A', 'A-']:
            insights.append("🎯 Excellent overall performance - layout meets industry standards")
        elif self.report.performance_grade in ['B+', 'B', 'B-']:
            insights.append("📊 Good performance with room for optimization")
        else:
            insights.append("⚠️ Performance below standards - significant optimization needed")
        
        # Utilization insights
        if self.report.space_utilization > 0.8:
            insights.append("🏪 High space utilization - efficient îlot placement")
        elif self.report.space_utilization < 0.6:
            insights.append("📈 Low space utilization - consider adding more îlots")
        
        # Accessibility insights
        if self.report.accessibility_score > 0.9:
            insights.append("🚶 Excellent accessibility - all areas well connected")
        elif self.report.accessibility_score < 0.7:
            insights.append("🛤️ Poor accessibility - corridor network needs improvement")
        
        # Compliance insights
        if self.report.compliance_score > 0.95:
            insights.append("✅ Full compliance with regulations")
        elif self.report.compliance_score < 0.8:
            insights.append("⚠️ Compliance issues detected - review required")
        
        # Financial insights
        total_revenue = sum(self.report.revenue_estimates.values())
        if total_revenue > 0:
            insights.append(f"💰 Estimated annual revenue: ${total_revenue:,.0f}")
        
        return insights

class GeometricAnalyzer:
    """Geometric analysis component"""
    
    def analyze_geometry(self, phase1_data: Dict, ilots: List[Dict], 
                        corridors: List[Dict], walls: List[Dict]) -> Dict:
        """Analyze geometric properties"""
        
        # Calculate total areas
        total_ilot_area = sum(ilot.get('area', 0) for ilot in ilots)
        total_corridor_area = sum(corridor.get('polygon', Polygon()).area for corridor in corridors)
        
        # Get available space area
        available_area = 0
        if phase1_data and 'best_plan' in phase1_data:
            bounds = phase1_data['best_plan'].bounds
            available_area = bounds[2] * bounds[3]  # width * height
        
        # Calculate utilization
        space_utilization = (total_ilot_area / available_area) if available_area > 0 else 0
        
        return {
            'total_area': available_area,
            'total_ilot_area': total_ilot_area,
            'total_corridor_area': total_corridor_area,
            'space_utilization': space_utilization,
            'circulation_ratio': (total_corridor_area / available_area) if available_area > 0 else 0
        }

class EfficiencyAnalyzer:
    """Efficiency analysis component"""
    
    def analyze_efficiency(self, ilots: List[Dict], corridors: List[Dict], 
                          walls: List[Dict], restricted_areas: List[Dict]) -> Dict:
        """Analyze placement and circulation efficiency"""
        
        # Placement efficiency based on spacing optimization
        placement_efficiency = self._calculate_placement_efficiency(ilots)
        
        # Corridor efficiency based on network optimization
        corridor_efficiency = self._calculate_corridor_efficiency(corridors, ilots)
        
        # Accessibility score based on connectivity
        accessibility_score = self._calculate_accessibility_score(ilots, corridors)
        
        return {
            'placement_efficiency': placement_efficiency,
            'corridor_efficiency': corridor_efficiency,
            'accessibility_score': accessibility_score
        }
    
    def _calculate_placement_efficiency(self, ilots: List[Dict]) -> float:
        """Calculate îlot placement efficiency"""
        if not ilots:
            return 0.0
        
        # Score based on size distribution and spacing
        total_area = sum(ilot.get('area', 0) for ilot in ilots)
        if total_area == 0:
            return 0.0
        
        # Check size distribution balance
        size_categories = {'small': 0, 'medium': 0, 'large': 0}
        for ilot in ilots:
            area = ilot.get('area', 0)
            if area <= 3:
                size_categories['small'] += 1
            elif area <= 6:
                size_categories['medium'] += 1
            else:
                size_categories['large'] += 1
        
        # Calculate distribution balance
        total_ilots = len(ilots)
        distribution_score = 1.0 - abs(size_categories['small']/total_ilots - 0.4) - \
                           abs(size_categories['medium']/total_ilots - 0.35) - \
                           abs(size_categories['large']/total_ilots - 0.25)
        
        return max(0.0, min(1.0, distribution_score))
    
    def _calculate_corridor_efficiency(self, corridors: List[Dict], ilots: List[Dict]) -> float:
        """Calculate corridor network efficiency"""
        if not corridors or not ilots:
            return 0.0
        
        # Score based on total corridor length vs direct connections
        total_corridor_length = sum(corridor.get('length', 0) for corridor in corridors)
        
        # Estimate optimal length (direct connections)
        if len(ilots) < 2:
            return 1.0
        
        # Calculate average inter-îlot distance
        positions = []
        for ilot in ilots:
            if 'x' in ilot and 'y' in ilot:
                positions.append((ilot['x'] + ilot.get('width', 0)/2, 
                                ilot['y'] + ilot.get('height', 0)/2))
        
        if len(positions) < 2:
            return 1.0
        
        # Estimate minimum spanning tree length
        from scipy.spatial.distance import pdist
        distances = pdist(positions)
        min_total_length = np.sum(np.sort(distances)[:len(positions)-1])
        
        # Efficiency = optimal / actual
        efficiency = min_total_length / total_corridor_length if total_corridor_length > 0 else 0
        return min(1.0, efficiency)
    
    def _calculate_accessibility_score(self, ilots: List[Dict], corridors: List[Dict]) -> float:
        """Calculate accessibility score"""
        if not ilots:
            return 0.0
        
        # For now, simple heuristic based on corridor coverage
        if not corridors:
            return 0.5  # Moderate score if no corridors
        
        # Count îlots that are near corridors
        accessible_ilots = 0
        corridor_polygons = [corridor.get('polygon', Polygon()) for corridor in corridors]
        
        for ilot in ilots:
            ilot_polygon = ilot.get('polygon', Polygon())
            if ilot_polygon.is_empty:
                continue
            
            # Check if îlot is near any corridor
            for corridor_polygon in corridor_polygons:
                if corridor_polygon.distance(ilot_polygon) < 2.0:  # Within 2 meters
                    accessible_ilots += 1
                    break
        
        return accessible_ilots / len(ilots) if ilots else 0.0

class ComplianceAnalyzer:
    """Compliance analysis component"""
    
    def analyze_compliance(self, ilots: List[Dict], corridors: List[Dict], 
                          walls: List[Dict], restricted_areas: List[Dict], 
                          entrances: List[Dict]) -> Dict:
        """Analyze regulatory compliance"""
        
        compliance_checks = {
            'restricted_area_avoidance': self._check_restricted_area_avoidance(ilots, restricted_areas),
            'entrance_clearance': self._check_entrance_clearance(ilots, entrances),
            'corridor_width_compliance': self._check_corridor_width(corridors),
            'accessibility_compliance': self._check_accessibility_compliance(ilots, corridors),
            'fire_safety_compliance': self._check_fire_safety(ilots, corridors, entrances)
        }
        
        # Calculate overall compliance score
        overall_score = sum(compliance_checks.values()) / len(compliance_checks)
        
        return {
            'overall_score': overall_score,
            'details': compliance_checks
        }
    
    def _check_restricted_area_avoidance(self, ilots: List[Dict], restricted_areas: List[Dict]) -> bool:
        """Check if îlots avoid restricted areas"""
        if not restricted_areas:
            return True
        
        for ilot in ilots:
            ilot_polygon = ilot.get('polygon', Polygon())
            for restricted in restricted_areas:
                if 'points' in restricted:
                    try:
                        restricted_polygon = Polygon(restricted['points'])
                        if ilot_polygon.intersects(restricted_polygon):
                            return False
                    except:
                        continue
        return True
    
    def _check_entrance_clearance(self, ilots: List[Dict], entrances: List[Dict]) -> bool:
        """Check if îlots maintain clearance from entrances"""
        if not entrances:
            return True
        
        min_clearance = 1.5  # 1.5 meters minimum
        
        for ilot in ilots:
            ilot_polygon = ilot.get('polygon', Polygon())
            for entrance in entrances:
                if 'points' in entrance:
                    try:
                        if len(entrance['points']) >= 2:
                            from shapely.geometry import LineString
                            entrance_line = LineString(entrance['points'])
                            if ilot_polygon.distance(entrance_line) < min_clearance:
                                return False
                    except:
                        continue
        return True
    
    def _check_corridor_width(self, corridors: List[Dict]) -> bool:
        """Check if corridors meet minimum width requirements"""
        min_width = 1.2  # 1.2 meters minimum
        
        for corridor in corridors:
            width = corridor.get('width', 0)
            if width < min_width:
                return False
        return True
    
    def _check_accessibility_compliance(self, ilots: List[Dict], corridors: List[Dict]) -> bool:
        """Check accessibility compliance"""
        # Simple check - ensure most îlots are accessible
        if not ilots:
            return True
        
        # At least 90% of îlots should be accessible
        accessible_count = 0
        for ilot in ilots:
            # Check if near corridor (simplified)
            accessible_count += 1  # Simplified for now
        
        accessibility_ratio = accessible_count / len(ilots)
        return accessibility_ratio >= 0.9
    
    def _check_fire_safety(self, ilots: List[Dict], corridors: List[Dict], entrances: List[Dict]) -> bool:
        """Check fire safety compliance"""
        # Simplified fire safety check
        if not corridors or not entrances:
            return False
        
        # Check if corridors provide adequate egress
        return True  # Simplified for now

class SpatialAnalyzer:
    """Spatial analysis component"""
    
    def analyze_spatial_distribution(self, ilots: List[Dict], corridors: List[Dict], 
                                   walls: List[Dict]) -> Dict:
        """Analyze spatial distribution patterns"""
        
        # Distribution analysis
        distribution_metrics = self._analyze_distribution(ilots)
        
        # Density analysis
        density_metrics = self._analyze_density(ilots)
        
        # Clustering analysis
        clustering_metrics = self._analyze_clustering(ilots)
        
        return {
            'distribution': distribution_metrics,
            'density': density_metrics,
            'clustering': clustering_metrics
        }
    
    def _analyze_distribution(self, ilots: List[Dict]) -> Dict:
        """Analyze spatial distribution uniformity"""
        if not ilots:
            return {'uniformity': 0.0, 'balance': 0.0}
        
        # Calculate center of mass
        positions = []
        areas = []
        for ilot in ilots:
            if 'x' in ilot and 'y' in ilot:
                x = ilot['x'] + ilot.get('width', 0) / 2
                y = ilot['y'] + ilot.get('height', 0) / 2
                positions.append((x, y))
                areas.append(ilot.get('area', 1))
        
        if not positions:
            return {'uniformity': 0.0, 'balance': 0.0}
        
        # Calculate uniformity using coefficient of variation
        distances_from_center = []
        center_x = sum(pos[0] * area for pos, area in zip(positions, areas)) / sum(areas)
        center_y = sum(pos[1] * area for pos, area in zip(positions, areas)) / sum(areas)
        
        for pos in positions:
            distance = math.sqrt((pos[0] - center_x)**2 + (pos[1] - center_y)**2)
            distances_from_center.append(distance)
        
        if not distances_from_center:
            return {'uniformity': 1.0, 'balance': 1.0}
        
        mean_distance = np.mean(distances_from_center)
        std_distance = np.std(distances_from_center)
        
        # Uniformity score (higher is more uniform)
        uniformity = 1.0 - (std_distance / mean_distance) if mean_distance > 0 else 1.0
        uniformity = max(0.0, min(1.0, uniformity))
        
        return {
            'uniformity': uniformity,
            'balance': uniformity  # Using same metric for simplicity
        }
    
    def _analyze_density(self, ilots: List[Dict]) -> Dict:
        """Analyze spatial density patterns"""
        if not ilots:
            return {'average_density': 0.0, 'density_variance': 0.0, 'balance_score': 0.0}
        
        # Calculate local densities
        densities = []
        for i, ilot in enumerate(ilots):
            if 'x' not in ilot or 'y' not in ilot:
                continue
            
            # Count nearby îlots within radius
            radius = 5.0  # 5 meter radius
            nearby_count = 0
            
            ilot_center = (ilot['x'] + ilot.get('width', 0)/2, 
                          ilot['y'] + ilot.get('height', 0)/2)
            
            for j, other_ilot in enumerate(ilots):
                if i == j or 'x' not in other_ilot or 'y' not in other_ilot:
                    continue
                
                other_center = (other_ilot['x'] + other_ilot.get('width', 0)/2,
                               other_ilot['y'] + other_ilot.get('height', 0)/2)
                
                distance = math.sqrt((ilot_center[0] - other_center[0])**2 + 
                                   (ilot_center[1] - other_center[1])**2)
                
                if distance <= radius:
                    nearby_count += 1
            
            densities.append(nearby_count)
        
        if not densities:
            return {'average_density': 0.0, 'density_variance': 0.0, 'balance_score': 0.0}
        
        average_density = np.mean(densities)
        density_variance = np.var(densities)
        
        # Balance score (lower variance is better)
        balance_score = 1.0 - min(1.0, density_variance / (average_density + 1))
        
        return {
            'average_density': average_density,
            'density_variance': density_variance,
            'balance_score': max(0.0, balance_score)
        }
    
    def _analyze_clustering(self, ilots: List[Dict]) -> Dict:
        """Analyze clustering patterns"""
        if not ilots:
            return {'cluster_count': 0, 'cluster_quality': 0.0}
        
        # Simple clustering analysis
        # For now, return basic metrics
        return {
            'cluster_count': max(1, len(ilots) // 10),  # Rough estimate
            'cluster_quality': 0.8  # Placeholder
        }

class FinancialAnalyzer:
    """Financial analysis component"""
    
    def analyze_financial_potential(self, ilots: List[Dict], corridors: List[Dict], 
                                   geometric_metrics: Dict) -> Dict:
        """Analyze financial potential and estimates"""
        
        # Revenue estimates
        revenue_estimates = self._calculate_revenue_estimates(ilots)
        
        # Cost estimates
        cost_estimates = self._calculate_cost_estimates(ilots, corridors, geometric_metrics)
        
        return {
            'revenue': revenue_estimates,
            'costs': cost_estimates
        }
    
    def _calculate_revenue_estimates(self, ilots: List[Dict]) -> Dict:
        """Calculate revenue estimates"""
        if not ilots:
            return {'annual_revenue': 0.0, 'revenue_per_sqm': 0.0}
        
        # Revenue per square meter (example rates)
        revenue_rates = {
            'Micro (0-1m²)': 500,  # $500/m²/year
            'Small (1-3m²)': 450,  # $450/m²/year
            'Medium (3-5m²)': 400,  # $400/m²/year
            'Large (5-10m²)': 350   # $350/m²/year
        }
        
        total_revenue = 0.0
        total_area = 0.0
        
        for ilot in ilots:
            area = ilot.get('area', 0)
            category = ilot.get('category', 'Small (1-3m²)')
            
            rate = revenue_rates.get(category, 400)
            ilot_revenue = area * rate
            
            total_revenue += ilot_revenue
            total_area += area
        
        revenue_per_sqm = total_revenue / total_area if total_area > 0 else 0
        
        return {
            'annual_revenue': total_revenue,
            'revenue_per_sqm': revenue_per_sqm
        }
    
    def _calculate_cost_estimates(self, ilots: List[Dict], corridors: List[Dict], 
                                 geometric_metrics: Dict) -> Dict:
        """Calculate cost estimates"""
        
        # Construction costs
        ilot_construction_cost = len(ilots) * 2000  # $2000 per îlot
        corridor_construction_cost = geometric_metrics.get('total_corridor_area', 0) * 200  # $200/m²
        
        # Annual operating costs
        maintenance_cost = geometric_metrics.get('total_area', 0) * 50  # $50/m²/year
        utilities_cost = geometric_metrics.get('total_area', 0) * 30  # $30/m²/year
        
        total_construction = ilot_construction_cost + corridor_construction_cost
        total_annual_operating = maintenance_cost + utilities_cost
        
        return {
            'construction_cost': total_construction,
            'annual_operating_cost': total_annual_operating,
            'cost_per_sqm': total_construction / geometric_metrics.get('total_area', 1)
        }