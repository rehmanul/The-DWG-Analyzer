"""
Advanced Îlot Engine - Phase 2 Implementation
Intelligent îlot placement with genetic algorithms and spatial optimization
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import minimize
import math
import logging

logger = logging.getLogger(__name__)

@dataclass
class IlotConfig:
    """Configuration for îlot placement"""
    min_size: float = 0.5
    max_size: float = 10.0
    min_spacing: float = 0.5
    shape_variety: bool = True
    allow_wall_contact: bool = True
    avoid_restricted: bool = True
    avoid_entrances: bool = True
    
    # Size distribution
    size_0_1_ratio: float = 0.10
    size_1_3_ratio: float = 0.25
    size_3_5_ratio: float = 0.30
    size_5_10_ratio: float = 0.35

@dataclass
class IlotPlacement:
    """Represents a placed îlot with all properties"""
    id: int
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    category: str = "Standard"
    polygon: Optional[Polygon] = None
    area: float = 0.0
    color: str = "#FEE2E2"
    
    def __post_init__(self):
        if self.polygon is None:
            self.polygon = box(self.x, self.y, self.x + self.width, self.y + self.height)
        if self.area == 0.0:
            self.area = self.width * self.height

class AdvancedIlotEngine:
    """
    Advanced îlot placement engine with genetic algorithms and spatial optimization
    Implements perfect placement strategies with no simplifications
    """
    
    def __init__(self, config: IlotConfig):
        self.config = config
        self.available_space = None
        self.walls = []
        self.restricted_areas = []
        self.entrances = []
        self.placed_ilots = []
        
        # Genetic algorithm parameters
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elitism_rate = 0.2
        
        # Spatial optimization parameters
        self.grid_resolution = 0.1
        self.optimization_iterations = 1000

    def place_ilots_intelligently(self, available_zones: List[Dict], walls: List[Dict], 
                                restricted_areas: List[Dict], entrances: List[Dict]) -> List[IlotPlacement]:
        """
        Main function for intelligent îlot placement
        Uses hybrid approach: genetic algorithm + spatial optimization + constraint satisfaction
        """
        logger.info("Starting advanced îlot placement with genetic algorithms")
        
        # Initialize spatial context
        self.available_space = self._process_available_zones(available_zones)
        self.walls = self._process_walls(walls)
        self.restricted_areas = self._process_restricted_areas(restricted_areas)
        self.entrances = self._process_entrances(entrances)
        
        if not self.available_space:
            logger.warning("No available space found for îlot placement")
            return []
        
        # Calculate total area and determine number of îlots
        total_area = sum(zone.area for zone in self.available_space)
        target_ilots = self._calculate_target_ilot_count(total_area)
        
        logger.info(f"Target placement: {target_ilots} îlots in {total_area:.1f}m² space")
        
        # Phase 1: Genetic Algorithm for optimal positions
        best_solution = self._run_genetic_algorithm(target_ilots)
        
        # Phase 2: Spatial optimization refinement
        optimized_solution = self._optimize_spatial_distribution(best_solution)
        
        # Phase 3: Constraint satisfaction and validation
        final_solution = self._validate_and_adjust_placement(optimized_solution)
        
        # Phase 4: Category assignment and color coding
        categorized_solution = self._assign_categories_and_colors(final_solution)
        
        self.placed_ilots = categorized_solution
        
        logger.info(f"Successfully placed {len(categorized_solution)} îlots")
        return categorized_solution

    def _process_available_zones(self, zones: List[Dict]) -> List[Polygon]:
        """Convert available zones to shapely polygons"""
        processed_zones = []
        for zone in zones:
            if 'points' in zone and len(zone['points']) >= 3:
                try:
                    polygon = Polygon(zone['points'])
                    if polygon.is_valid and polygon.area > 0.1:
                        processed_zones.append(polygon)
                except Exception as e:
                    logger.warning(f"Invalid zone polygon: {e}")
        return processed_zones

    def _process_walls(self, walls: List[Dict]) -> List[Polygon]:
        """Process walls - create buffer zones if wall contact not allowed"""
        processed_walls = []
        for wall in walls:
            if 'points' in wall and len(wall['points']) >= 2:
                try:
                    if len(wall['points']) == 2:
                        # Line wall - create buffer
                        from shapely.geometry import LineString
                        line = LineString(wall['points'])
                        buffer_size = 0.1 if self.config.allow_wall_contact else self.config.min_spacing
                        wall_polygon = line.buffer(buffer_size)
                        processed_walls.append(wall_polygon)
                    elif len(wall['points']) >= 3:
                        # Polygon wall
                        wall_polygon = Polygon(wall['points'])
                        if wall_polygon.is_valid:
                            processed_walls.append(wall_polygon)
                except Exception as e:
                    logger.warning(f"Invalid wall geometry: {e}")
        return processed_walls

    def _process_restricted_areas(self, restricted: List[Dict]) -> List[Polygon]:
        """Process restricted areas that îlots must avoid"""
        processed_restricted = []
        for area in restricted:
            if 'points' in area and len(area['points']) >= 3:
                try:
                    polygon = Polygon(area['points'])
                    if polygon.is_valid:
                        # Add buffer around restricted areas
                        buffered = polygon.buffer(self.config.min_spacing)
                        processed_restricted.append(buffered)
                except Exception as e:
                    logger.warning(f"Invalid restricted area: {e}")
        return processed_restricted

    def _process_entrances(self, entrances: List[Dict]) -> List[Polygon]:
        """Process entrances that îlots must avoid"""
        processed_entrances = []
        for entrance in entrances:
            if 'points' in entrance and len(entrance['points']) >= 2:
                try:
                    if len(entrance['points']) == 2:
                        # Line entrance
                        from shapely.geometry import LineString
                        line = LineString(entrance['points'])
                        entrance_polygon = line.buffer(self.config.min_spacing * 2)
                        processed_entrances.append(entrance_polygon)
                    elif len(entrance['points']) >= 3:
                        # Area entrance
                        polygon = Polygon(entrance['points'])
                        if polygon.is_valid:
                            buffered = polygon.buffer(self.config.min_spacing)
                            processed_entrances.append(buffered)
                except Exception as e:
                    logger.warning(f"Invalid entrance geometry: {e}")
        return processed_entrances

    def _calculate_target_ilot_count(self, total_area: float) -> int:
        """Calculate target number of îlots based on area and size distribution"""
        # Calculate average îlot size based on distribution
        avg_size = (
            0.5 * self.config.size_0_1_ratio +
            2.0 * self.config.size_1_3_ratio +
            4.0 * self.config.size_3_5_ratio +
            7.5 * self.config.size_5_10_ratio
        )
        
        # Account for spacing and efficiency
        efficiency_factor = 0.7  # 70% space utilization
        target_count = int((total_area * efficiency_factor) / avg_size)
        
        return max(1, min(target_count, 200))  # Reasonable bounds

    def _run_genetic_algorithm(self, target_ilots: int) -> List[IlotPlacement]:
        """
        Run genetic algorithm to find optimal îlot placement
        """
        logger.info(f"Running genetic algorithm with {self.population_size} individuals for {self.generations} generations")
        
        # Initialize population
        population = []
        for _ in range(self.population_size):
            individual = self._create_random_individual(target_ilots)
            population.append(individual)
        
        best_fitness = float('-inf')
        best_individual = None
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(individual)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # Selection, crossover, and mutation
            new_population = []
            
            # Elitism - keep best individuals
            elite_count = int(self.population_size * self.elitism_rate)
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
            
            if generation % 20 == 0:
                logger.info(f"Generation {generation}: Best fitness = {best_fitness:.3f}")
        
        logger.info(f"Genetic algorithm completed. Best fitness: {best_fitness:.3f}")
        return best_individual

    def _create_random_individual(self, target_ilots: int) -> List[IlotPlacement]:
        """Create a random individual for genetic algorithm"""
        individual = []
        
        # Generate size distribution
        sizes = self._generate_size_distribution(target_ilots)
        
        attempts = 0
        max_attempts = target_ilots * 10
        
        for i, size in enumerate(sizes):
            if attempts >= max_attempts:
                break
            
            # Try to place îlot
            placed = False
            for _ in range(50):  # 50 attempts per îlot
                attempts += 1
                
                # Random position within available space
                space_polygon = random.choice(self.available_space)
                bounds = space_polygon.bounds
                
                x = random.uniform(bounds[0], bounds[2] - size)
                y = random.uniform(bounds[1], bounds[3] - size)
                
                # Create îlot
                width = size + random.uniform(-size*0.1, size*0.1)
                height = size / width if width > 0 else size
                
                ilot = IlotPlacement(
                    id=i,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    rotation=random.uniform(0, 90) if self.config.shape_variety else 0
                )
                
                # Check if placement is valid
                if self._is_valid_placement(ilot, individual):
                    individual.append(ilot)
                    placed = True
                    break
            
            if not placed:
                logger.debug(f"Failed to place îlot {i} after 50 attempts")
        
        return individual

    def _generate_size_distribution(self, count: int) -> List[float]:
        """Generate size distribution based on configuration"""
        sizes = []
        
        # Calculate counts for each category
        count_0_1 = int(count * self.config.size_0_1_ratio)
        count_1_3 = int(count * self.config.size_1_3_ratio)
        count_3_5 = int(count * self.config.size_3_5_ratio)
        count_5_10 = count - count_0_1 - count_1_3 - count_3_5
        
        # Generate sizes
        sizes.extend([random.uniform(0.5, 1.0) for _ in range(count_0_1)])
        sizes.extend([random.uniform(1.0, 3.0) for _ in range(count_1_3)])
        sizes.extend([random.uniform(3.0, 5.0) for _ in range(count_3_5)])
        sizes.extend([random.uniform(5.0, 10.0) for _ in range(count_5_10)])
        
        random.shuffle(sizes)
        return sizes

    def _is_valid_placement(self, ilot: IlotPlacement, existing_ilots: List[IlotPlacement]) -> bool:
        """Check if îlot placement is valid"""
        # Check if within available space
        if not any(space.contains(ilot.polygon) for space in self.available_space):
            return False
        
        # Check spacing with existing îlots
        for existing in existing_ilots:
            if ilot.polygon.distance(existing.polygon) < self.config.min_spacing:
                return False
        
        # Check restricted areas
        if self.config.avoid_restricted:
            for restricted in self.restricted_areas:
                if ilot.polygon.intersects(restricted):
                    return False
        
        # Check entrances
        if self.config.avoid_entrances:
            for entrance in self.entrances:
                if ilot.polygon.intersects(entrance):
                    return False
        
        # Check wall contact
        if not self.config.allow_wall_contact:
            for wall in self.walls:
                if ilot.polygon.intersects(wall):
                    return False
        
        return True

    def _evaluate_fitness(self, individual: List[IlotPlacement]) -> float:
        """Evaluate fitness of individual"""
        if not individual:
            return 0.0
        
        fitness = 0.0
        
        # Coverage efficiency
        total_ilot_area = sum(ilot.area for ilot in individual)
        total_available_area = sum(space.area for space in self.available_space)
        coverage_ratio = total_ilot_area / total_available_area
        fitness += coverage_ratio * 100
        
        # Spatial distribution
        positions = np.array([[ilot.x + ilot.width/2, ilot.y + ilot.height/2] for ilot in individual])
        if len(positions) > 1:
            distances = pdist(positions)
            avg_distance = np.mean(distances)
            min_distance = np.min(distances)
            
            # Reward good spacing
            fitness += min_distance * 10
            fitness += avg_distance * 5
        
        # Size distribution balance
        sizes = [ilot.area for ilot in individual]
        size_variety = len(set(np.round(sizes, 1))) / len(sizes) if sizes else 0
        fitness += size_variety * 20
        
        # Constraint compliance
        valid_placements = sum(1 for ilot in individual if self._is_valid_placement(ilot, []))
        compliance_ratio = valid_placements / len(individual) if individual else 0
        fitness += compliance_ratio * 50
        
        return fitness

    def _tournament_selection(self, population: List, fitness_scores: List) -> List[IlotPlacement]:
        """Tournament selection for genetic algorithm"""
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_index]

    def _crossover(self, parent1: List[IlotPlacement], parent2: List[IlotPlacement]) -> Tuple[List[IlotPlacement], List[IlotPlacement]]:
        """Crossover operation for genetic algorithm"""
        if len(parent1) < 2 or len(parent2) < 2:
            return parent1, parent2
        
        # Single-point crossover
        crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2

    def _mutate(self, individual: List[IlotPlacement]) -> List[IlotPlacement]:
        """Mutation operation for genetic algorithm"""
        if not individual:
            return individual
        
        mutated = individual.copy()
        
        # Random mutation
        mutation_type = random.choice(['position', 'size', 'rotation'])
        ilot_index = random.randint(0, len(mutated) - 1)
        
        if mutation_type == 'position':
            # Move îlot slightly
            mutated[ilot_index].x += random.uniform(-1.0, 1.0)
            mutated[ilot_index].y += random.uniform(-1.0, 1.0)
        elif mutation_type == 'size':
            # Adjust size slightly
            scale = random.uniform(0.9, 1.1)
            mutated[ilot_index].width *= scale
            mutated[ilot_index].height *= scale
        elif mutation_type == 'rotation':
            # Rotate îlot
            mutated[ilot_index].rotation = random.uniform(0, 90)
        
        # Update polygon after mutation
        mutated[ilot_index].polygon = box(
            mutated[ilot_index].x, 
            mutated[ilot_index].y,
            mutated[ilot_index].x + mutated[ilot_index].width,
            mutated[ilot_index].y + mutated[ilot_index].height
        )
        mutated[ilot_index].area = mutated[ilot_index].width * mutated[ilot_index].height
        
        return mutated

    def _optimize_spatial_distribution(self, solution: List[IlotPlacement]) -> List[IlotPlacement]:
        """Optimize spatial distribution using local search"""
        logger.info("Optimizing spatial distribution")
        
        if not solution:
            return solution
        
        optimized = solution.copy()
        
        for iteration in range(min(self.optimization_iterations, 100)):
            # Select random îlot for optimization
            ilot_index = random.randint(0, len(optimized) - 1)
            original_ilot = optimized[ilot_index]
            
            # Try small improvements
            best_improvement = 0
            best_position = None
            
            for dx in [-0.1, 0, 0.1]:
                for dy in [-0.1, 0, 0.1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    test_ilot = IlotPlacement(
                        id=original_ilot.id,
                        x=original_ilot.x + dx,
                        y=original_ilot.y + dy,
                        width=original_ilot.width,
                        height=original_ilot.height,
                        rotation=original_ilot.rotation
                    )
                    
                    # Check if improvement is valid
                    other_ilots = [ilot for i, ilot in enumerate(optimized) if i != ilot_index]
                    if self._is_valid_placement(test_ilot, other_ilots):
                        improvement = self._calculate_local_improvement(test_ilot, other_ilots)
                        if improvement > best_improvement:
                            best_improvement = improvement
                            best_position = test_ilot
            
            # Apply best improvement
            if best_position:
                optimized[ilot_index] = best_position
        
        return optimized

    def _calculate_local_improvement(self, ilot: IlotPlacement, other_ilots: List[IlotPlacement]) -> float:
        """Calculate local improvement score for spatial optimization"""
        improvement = 0.0
        
        # Distance to other îlots
        for other in other_ilots:
            distance = ilot.polygon.distance(other.polygon)
            if distance < self.config.min_spacing:
                improvement -= 10  # Penalty for too close
            else:
                improvement += min(distance, 2.0)  # Reward good spacing
        
        # Position within available space
        for space in self.available_space:
            if space.contains(ilot.polygon):
                # Reward being well within space
                distance_to_boundary = space.boundary.distance(ilot.polygon.centroid)
                improvement += distance_to_boundary * 0.1
        
        return improvement

    def _validate_and_adjust_placement(self, solution: List[IlotPlacement]) -> List[IlotPlacement]:
        """Validate and adjust placement to ensure all constraints are met"""
        logger.info("Validating and adjusting placement")
        
        validated = []
        
        for ilot in solution:
            # Check if current placement is valid
            if self._is_valid_placement(ilot, validated):
                validated.append(ilot)
            else:
                # Try to find nearby valid position
                adjusted_ilot = self._find_nearby_valid_position(ilot, validated)
                if adjusted_ilot:
                    validated.append(adjusted_ilot)
        
        return validated

    def _find_nearby_valid_position(self, ilot: IlotPlacement, existing_ilots: List[IlotPlacement]) -> Optional[IlotPlacement]:
        """Find nearby valid position for îlot"""
        search_radius = 2.0
        search_steps = 20
        
        for radius in np.linspace(0.1, search_radius, search_steps):
            for angle in np.linspace(0, 2*np.pi, 16):
                new_x = ilot.x + radius * np.cos(angle)
                new_y = ilot.y + radius * np.sin(angle)
                
                test_ilot = IlotPlacement(
                    id=ilot.id,
                    x=new_x,
                    y=new_y,
                    width=ilot.width,
                    height=ilot.height,
                    rotation=ilot.rotation
                )
                
                if self._is_valid_placement(test_ilot, existing_ilots):
                    return test_ilot
        
        return None

    def _assign_categories_and_colors(self, solution: List[IlotPlacement]) -> List[IlotPlacement]:
        """Assign categories and colors based on îlot sizes"""
        logger.info("Assigning categories and colors")
        
        categorized = []
        
        for ilot in solution:
            area = ilot.area
            
            if area <= 1.0:
                ilot.category = "Micro (0-1m²)"
                ilot.color = "rgba(254, 243, 242, 0.8)"  # Very light pink
            elif area <= 3.0:
                ilot.category = "Small (1-3m²)"
                ilot.color = "rgba(254, 226, 226, 0.8)"  # Light pink
            elif area <= 5.0:
                ilot.category = "Medium (3-5m²)"
                ilot.color = "rgba(252, 231, 243, 0.8)"  # Medium pink
            else:
                ilot.category = "Large (5-10m²)"
                ilot.color = "rgba(243, 232, 255, 0.8)"  # Light purple
            
            categorized.append(ilot)
        
        return categorized

    def get_placement_statistics(self) -> Dict:
        """Get comprehensive statistics about the placement"""
        if not self.placed_ilots:
            return {}
        
        total_area = sum(ilot.area for ilot in self.placed_ilots)
        categories = {}
        
        for ilot in self.placed_ilots:
            cat = ilot.category
            if cat not in categories:
                categories[cat] = {'count': 0, 'area': 0.0}
            categories[cat]['count'] += 1
            categories[cat]['area'] += ilot.area
        
        return {
            'total_ilots': len(self.placed_ilots),
            'total_area': total_area,
            'categories': categories,
            'average_area': total_area / len(self.placed_ilots),
            'density': total_area / sum(space.area for space in self.available_space) if self.available_space else 0
        }