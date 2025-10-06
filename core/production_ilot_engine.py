"""
Production Îlot Placement Engine
Automatically places îlots based on user-defined size distribution
NO SIMULATIONS - Real optimization algorithms only
"""

import logging
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from scipy.spatial import distance_matrix
import time

logger = logging.getLogger(__name__)


@dataclass
class IlotSizeConfig:
    """User-defined îlot size distribution"""
    size_0_1_pct: float  # 10% between 0-1 m²
    size_1_3_pct: float  # 25% between 1-3 m²
    size_3_5_pct: float  # 30% between 3-5 m²
    size_5_10_pct: float  # 35% between 5-10 m²
    
    def validate(self):
        """Ensure percentages sum to 100%"""
        total = self.size_0_1_pct + self.size_1_3_pct + self.size_3_5_pct + self.size_5_10_pct
        if not (0.99 <= total <= 1.01):  # Allow 1% tolerance
            raise ValueError(f"Percentages must sum to 100%, got {total*100}%")


@dataclass
class PlacedIlot:
    """Represents a placed îlot"""
    id: int
    polygon: Polygon
    area: float
    category: str  # Size category
    position: Tuple[float, float]  # Center position
    width: float
    height: float
    rotation: int  # 0 or 90 degrees
    
    @property
    def bounds(self):
        return self.polygon.bounds


class ProductionIlotEngine:
    """
    Production-grade îlot placement engine using genetic algorithm
    Respects all constraints: walls OK, entrances NO, restricted areas NO
    """
    
    def __init__(self, config: IlotSizeConfig, total_ilots: int = 100,
                 min_spacing: float = 0.3, corridor_width: float = 1.5):
        """
        Initialize engine
        
        Args:
            config: Size distribution configuration
            total_ilots: Target number of îlots to place
            min_spacing: Minimum spacing between îlots (meters)
            corridor_width: Width of corridors (meters)
        """
        config.validate()
        self.config = config
        self.total_ilots = total_ilots
        self.min_spacing = min_spacing
        self.corridor_width = corridor_width
        
        # Genetic algorithm parameters
        self.population_size = 50
        self.max_generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = 10
        self.timeout_seconds = 60
        
    def place_ilots(self, open_spaces: List[Polygon], walls: List[Polygon],
                   restricted_areas: List[Polygon], entrances: List[Polygon]) -> Dict:
        """
        Main method to place îlots
        
        Returns:
            {
                'ilots': List[PlacedIlot],
                'coverage_pct': float,
                'placement_score': float
            }
        """
        start_time = time.time()
        logger.info(f"Starting îlot placement with {self.total_ilots} target îlots")
        
        # Validate input
        if not open_spaces:
            logger.error("No open spaces available for îlot placement")
            return {'ilots': [], 'coverage_pct': 0, 'placement_score': 0}
        
        # Calculate total available area
        total_area = sum(space.area for space in open_spaces)
        logger.info(f"Total available area: {total_area:.2f} m²")
        
        # Create forbidden zone union (restricted + entrance buffers)
        forbidden_zones = self._create_forbidden_zones(restricted_areas, entrances)
        
        # Generate îlot specifications based on distribution
        ilot_specs = self._generate_ilot_specs()
        logger.info(f"Generated {len(ilot_specs)} îlot specifications")
        
        # Run genetic algorithm
        best_solution = self._run_genetic_algorithm(
            ilot_specs, open_spaces, forbidden_zones, walls, start_time
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Îlot placement completed in {elapsed:.2f}s - Placed {len(best_solution['ilots'])} îlots")
        
        # Calculate metrics
        placed_area = sum(ilot.area for ilot in best_solution['ilots'])
        coverage_pct = (placed_area / total_area) * 100 if total_area > 0 else 0
        
        return {
            'ilots': best_solution['ilots'],
            'coverage_pct': coverage_pct,
            'placement_score': best_solution['fitness'],
            'elapsed_time': elapsed
        }
    
    def _create_forbidden_zones(self, restricted_areas: List[Polygon], 
                               entrances: List[Polygon]) -> Optional[Polygon]:
        """Create union of all forbidden zones"""
        forbidden = []
        
        # Add restricted areas (stairs, elevators, etc.)
        forbidden.extend(restricted_areas)
        
        # Add entrance buffers - îlots cannot touch entrances
        for entrance in entrances:
            forbidden.append(entrance.buffer(0.3))  # 30cm buffer
        
        if forbidden:
            return unary_union(forbidden)
        return None
    
    def _generate_ilot_specs(self) -> List[Dict]:
        """Generate îlot specifications based on size distribution"""
        specs = []
        
        # Define size ranges and their counts
        size_ranges = [
            ('0-1m²', 0.5, 1.0, self.config.size_0_1_pct),
            ('1-3m²', 1.0, 3.0, self.config.size_1_3_pct),
            ('3-5m²', 3.0, 5.0, self.config.size_3_5_pct),
            ('5-10m²', 5.0, 10.0, self.config.size_5_10_pct),
        ]
        
        for category, min_area, max_area, percentage in size_ranges:
            count = int(self.total_ilots * percentage)
            
            for _ in range(count):
                # Random area within range
                area = np.random.uniform(min_area, max_area)
                
                # Calculate dimensions (rectangular with slight variation)
                aspect_ratio = np.random.uniform(1.2, 1.8)  # Prefer elongated shapes
                width = np.sqrt(area * aspect_ratio)
                height = area / width
                
                specs.append({
                    'area': area,
                    'width': width,
                    'height': height,
                    'category': category
                })
        
        return specs
    
    def _run_genetic_algorithm(self, ilot_specs: List[Dict], open_spaces: List[Polygon],
                               forbidden_zones: Optional[Polygon], walls: List[Polygon],
                               start_time: float) -> Dict:
        """Run genetic algorithm to find optimal placement"""
        
        # Get bounds for placement
        all_bounds = [space.bounds for space in open_spaces]
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        # Initialize population
        population = [
            self._create_random_chromosome(ilot_specs, min_x, min_y, max_x, max_y)
            for _ in range(self.population_size)
        ]
        
        best_fitness = -1
        best_solution = None
        generations_without_improvement = 0
        
        for generation in range(self.max_generations):
            # Check timeout
            if time.time() - start_time > self.timeout_seconds:
                logger.warning(f"Genetic algorithm timeout at generation {generation}")
                break
            
            # Evaluate fitness for all chromosomes
            evaluated = []
            for chromosome in population:
                fitness, ilots = self._evaluate_fitness(
                    chromosome, ilot_specs, open_spaces, forbidden_zones, walls
                )
                evaluated.append((fitness, chromosome, ilots))
            
            # Sort by fitness
            evaluated.sort(key=lambda x: x[0], reverse=True)
            
            # Check for improvement
            if evaluated[0][0] > best_fitness:
                best_fitness = evaluated[0][0]
                best_solution = {
                    'fitness': best_fitness,
                    'ilots': evaluated[0][2],
                    'chromosome': evaluated[0][1]
                }
                generations_without_improvement = 0
                logger.info(f"Gen {generation}: New best fitness {best_fitness:.2f} - {len(evaluated[0][2])} îlots")
            else:
                generations_without_improvement += 1
            
            # Early stopping if no improvement
            if generations_without_improvement >= 20:
                logger.info(f"Early stopping at generation {generation} - no improvement for 20 generations")
                break
            
            # Selection: keep elite + select parents
            elite = [chrom for _, chrom, _ in evaluated[:self.elite_size]]
            
            # Create next generation
            next_gen = elite.copy()
            
            while len(next_gen) < self.population_size:
                # Tournament selection
                parent1 = self._tournament_selection(evaluated)
                parent2 = self._tournament_selection(evaluated)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1.copy()
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child = self._mutate(child, ilot_specs, min_x, min_y, max_x, max_y)
                
                next_gen.append(child)
            
            population = next_gen
        
        if best_solution is None:
            logger.warning("No valid solution found")
            return {'fitness': 0, 'ilots': []}
        
        return best_solution
    
    def _create_random_chromosome(self, ilot_specs: List[Dict], 
                                 min_x: float, min_y: float, 
                                 max_x: float, max_y: float) -> List[Tuple]:
        """Create random chromosome (placement genes)"""
        chromosome = []
        for spec in ilot_specs:
            x = random.uniform(min_x, max_x - spec['width'])
            y = random.uniform(min_y, max_y - spec['height'])
            rotation = random.choice([0, 90])  # 0 or 90 degrees
            chromosome.append((x, y, rotation))
        return chromosome
    
    def _evaluate_fitness(self, chromosome: List[Tuple], ilot_specs: List[Dict],
                         open_spaces: List[Polygon], forbidden_zones: Optional[Polygon],
                         walls: List[Polygon]) -> Tuple[float, List[PlacedIlot]]:
        """Evaluate fitness of a chromosome"""
        
        valid_ilots = []
        
        for idx, (x, y, rotation) in enumerate(chromosome):
            spec = ilot_specs[idx]
            
            # Apply rotation
            if rotation == 90:
                width, height = spec['height'], spec['width']
            else:
                width, height = spec['width'], spec['height']
            
            # Create îlot polygon
            ilot_poly = box(x, y, x + width, y + height)
            
            # Validate placement
            if not self._is_valid_placement(ilot_poly, open_spaces, forbidden_zones, valid_ilots):
                continue
            
            # Create placed îlot
            placed = PlacedIlot(
                id=len(valid_ilots),
                polygon=ilot_poly,
                area=spec['area'],
                category=spec['category'],
                position=(x + width/2, y + height/2),
                width=width,
                height=height,
                rotation=rotation
            )
            valid_ilots.append(placed)
        
        # Calculate fitness score
        if not valid_ilots:
            return 0, []
        
        # Fitness components:
        # 1. Number of placed îlots (most important)
        # 2. Total area coverage
        # 3. Distribution balance
        # 4. Spacing efficiency
        
        num_ilots = len(valid_ilots)
        total_area = sum(ilot.area for ilot in valid_ilots)
        
        # Check category distribution
        categories = {}
        for ilot in valid_ilots:
            categories[ilot.category] = categories.get(ilot.category, 0) + 1
        distribution_score = len(categories) / 4  # We have 4 categories
        
        # Calculate spacing efficiency (avoid clustering)
        spacing_score = 1.0
        if num_ilots > 1:
            positions = np.array([ilot.position for ilot in valid_ilots])
            distances = distance_matrix(positions, positions)
            np.fill_diagonal(distances, np.inf)
            min_distances = distances.min(axis=1)
            avg_spacing = min_distances.mean()
            # Prefer spacing between 0.5m and 2m
            spacing_score = 1.0 if 0.5 <= avg_spacing <= 2.0 else 0.5
        
        # Combined fitness
        fitness = (
            num_ilots * 10 +  # Primary: maximize number of îlots
            total_area * 0.1 +  # Secondary: maximize coverage
            distribution_score * 5 +  # Tertiary: balanced distribution
            spacing_score * 2  # Quaternary: good spacing
        )
        
        return fitness, valid_ilots
    
    def _is_valid_placement(self, ilot_poly: Polygon, open_spaces: List[Polygon],
                           forbidden_zones: Optional[Polygon], 
                           existing_ilots: List[PlacedIlot]) -> bool:
        """Check if îlot placement is valid"""
        
        # Must be within open spaces
        in_open_space = False
        for space in open_spaces:
            if space.contains(ilot_poly):
                in_open_space = True
                break
        
        if not in_open_space:
            return False
        
        # Must NOT intersect forbidden zones (restricted areas + entrances)
        if forbidden_zones and ilot_poly.intersects(forbidden_zones):
            return False
        
        # Must NOT overlap with existing îlots (with spacing)
        for existing in existing_ilots:
            if ilot_poly.distance(existing.polygon) < self.min_spacing:
                return False
        
        return True
    
    def _tournament_selection(self, evaluated: List[Tuple], tournament_size: int = 3) -> List[Tuple]:
        """Tournament selection for genetic algorithm"""
        tournament = random.sample(evaluated, min(tournament_size, len(evaluated)))
        winner = max(tournament, key=lambda x: x[0])
        return winner[1]  # Return chromosome
    
    def _crossover(self, parent1: List[Tuple], parent2: List[Tuple]) -> List[Tuple]:
        """Single-point crossover"""
        point = random.randint(1, len(parent1) - 1)
        child = parent1[:point] + parent2[point:]
        return child
    
    def _mutate(self, chromosome: List[Tuple], ilot_specs: List[Dict],
               min_x: float, min_y: float, max_x: float, max_y: float) -> List[Tuple]:
        """Mutate chromosome by randomly changing some genes"""
        mutated = list(chromosome)
        
        # Mutate 10-20% of genes
        num_mutations = max(1, int(len(mutated) * random.uniform(0.1, 0.2)))
        
        for _ in range(num_mutations):
            idx = random.randint(0, len(mutated) - 1)
            spec = ilot_specs[idx]
            
            x = random.uniform(min_x, max_x - spec['width'])
            y = random.uniform(min_y, max_y - spec['height'])
            rotation = random.choice([0, 90])
            
            mutated[idx] = (x, y, rotation)
        
        return mutated
