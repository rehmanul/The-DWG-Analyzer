"""
Advanced AI Algorithms for Enterprise Îlot Placement
Genetic Algorithm, Constraint Solving, and Space Optimization
"""

import numpy as np
import random
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import logging

logger = logging.getLogger(__name__)

@dataclass
class Individual:
    """Genetic algorithm individual representing an îlot layout"""
    ilots: List[Tuple[float, float, float, float]]  # x, y, width, height
    fitness: float = 0.0
    constraint_violations: int = 0

class GeneticAlgorithmOptimizer:
    """Advanced genetic algorithm for optimal îlot placement"""
    
    def __init__(self, 
                 population_size: int = 100,
                 generations: int = 200,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elite_size: int = 10):
        
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
    def optimize_placement(self, 
                          ilot_specs: List[Dict],
                          forbidden_areas: List[Polygon],
                          bounds: Tuple[float, float, float, float]) -> List[Individual]:
        """Run genetic algorithm optimization"""
        
        logger.info(f"Starting genetic algorithm optimization with {len(ilot_specs)} îlots")
        
        # Initialize population
        population = self._initialize_population(ilot_specs, bounds, forbidden_areas)
        
        best_fitness_history = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            for individual in population:
                individual.fitness = self._evaluate_fitness(individual, forbidden_areas, bounds)
            
            # Sort by fitness (higher is better)
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            best_fitness = population[0].fitness
            best_fitness_history.append(best_fitness)
            
            if generation % 20 == 0:
                logger.info(f"Generation {generation}: Best fitness = {best_fitness:.3f}")
            
            # Create next generation
            new_population = []
            
            # Keep elite individuals
            new_population.extend(population[:self.elite_size])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1, bounds)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2, bounds)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
        
        # Final evaluation
        for individual in population:
            individual.fitness = self._evaluate_fitness(individual, forbidden_areas, bounds)
        
        population.sort(key=lambda x: x.fitness, reverse=True)
        
        logger.info(f"Optimization complete. Best fitness: {population[0].fitness:.3f}")
        
        return population[:10]  # Return top 10 solutions
    
    def _initialize_population(self, 
                              ilot_specs: List[Dict],
                              bounds: Tuple[float, float, float, float],
                              forbidden_areas: List[Polygon]) -> List[Individual]:
        """Initialize random population"""
        
        population = []
        min_x, min_y, max_x, max_y = bounds
        
        for _ in range(self.population_size):
            individual_ilots = []
            
            for spec in ilot_specs:
                width, height = spec['dimensions']
                
                # Random placement with bounds checking
                max_attempts = 50
                placed = False
                
                for _ in range(max_attempts):
                    x = random.uniform(min_x, max_x - width)
                    y = random.uniform(min_y, max_y - height)
                    
                    # Quick check for major overlaps
                    candidate = (x, y, width, height)
                    if self._is_roughly_valid(candidate, individual_ilots, forbidden_areas):
                        individual_ilots.append(candidate)
                        placed = True
                        break
                
                if not placed:
                    # Force placement if can't find good spot
                    x = random.uniform(min_x, max_x - width)
                    y = random.uniform(min_y, max_y - height)
                    individual_ilots.append((x, y, width, height))
            
            population.append(Individual(ilots=individual_ilots))
        
        return population
    
    def _is_roughly_valid(self, 
                         candidate: Tuple[float, float, float, float],
                         existing_ilots: List[Tuple[float, float, float, float]],
                         forbidden_areas: List[Polygon]) -> bool:
        """Quick validity check for initialization"""
        
        x, y, w, h = candidate
        candidate_poly = Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)])
        
        # Check forbidden areas
        for forbidden in forbidden_areas:
            if candidate_poly.intersects(forbidden):
                return False
        
        # Check existing îlots (simple overlap)
        for ex_x, ex_y, ex_w, ex_h in existing_ilots:
            if (x < ex_x + ex_w and x + w > ex_x and 
                y < ex_y + ex_h and y + h > ex_y):
                return False
        
        return True
    
    def _evaluate_fitness(self, 
                         individual: Individual,
                         forbidden_areas: List[Polygon],
                         bounds: Tuple[float, float, float, float]) -> float:
        """Evaluate fitness of an individual"""
        
        fitness = 0.0
        violations = 0
        
        ilot_polygons = []
        
        # Convert îlots to polygons
        for x, y, w, h in individual.ilots:
            poly = Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)])
            ilot_polygons.append(poly)
        
        # 1. Constraint violations (heavy penalty)
        for i, poly in enumerate(ilot_polygons):
            # Check forbidden areas
            for forbidden in forbidden_areas:
                if poly.intersects(forbidden):
                    violations += 1
                    fitness -= 1000
            
            # Check overlaps with other îlots
            for j, other_poly in enumerate(ilot_polygons):
                if i != j and poly.intersects(other_poly):
                    violations += 1
                    fitness -= 500
        
        # 2. Space utilization (positive reward)
        total_ilot_area = sum(poly.area for poly in ilot_polygons)
        min_x, min_y, max_x, max_y = bounds
        total_available_area = (max_x - min_x) * (max_y - min_y)
        
        # Subtract forbidden area
        forbidden_area = 0
        if forbidden_areas:
            forbidden_union = unary_union(forbidden_areas)
            forbidden_area = forbidden_union.area
        
        available_area = max(1, total_available_area - forbidden_area)
        utilization = total_ilot_area / available_area
        fitness += utilization * 1000
        
        # 3. Compactness bonus (îlots close together)
        if len(ilot_polygons) > 1:
            total_distance = 0
            count = 0
            
            for i, poly1 in enumerate(ilot_polygons):
                for j, poly2 in enumerate(ilot_polygons[i+1:], i+1):
                    distance = poly1.distance(poly2)
                    total_distance += distance
                    count += 1
            
            if count > 0:
                avg_distance = total_distance / count
                compactness_bonus = max(0, 100 - avg_distance * 10)
                fitness += compactness_bonus
        
        # 4. Alignment bonus (îlots in rows/columns)
        alignment_bonus = self._calculate_alignment_bonus(individual.ilots)
        fitness += alignment_bonus
        
        individual.constraint_violations = violations
        
        return fitness
    
    def _calculate_alignment_bonus(self, ilots: List[Tuple[float, float, float, float]]) -> float:
        """Calculate bonus for aligned îlots"""
        
        if len(ilots) < 2:
            return 0
        
        bonus = 0
        tolerance = 0.5  # meters
        
        # Check horizontal alignment
        y_positions = [y for x, y, w, h in ilots]
        for i, y1 in enumerate(y_positions):
            aligned_count = sum(1 for y2 in y_positions if abs(y1 - y2) < tolerance)
            if aligned_count >= 3:  # At least 3 îlots in a row
                bonus += aligned_count * 10
        
        # Check vertical alignment
        x_positions = [x for x, y, w, h in ilots]
        for i, x1 in enumerate(x_positions):
            aligned_count = sum(1 for x2 in x_positions if abs(x1 - x2) < tolerance)
            if aligned_count >= 3:  # At least 3 îlots in a column
                bonus += aligned_count * 10
        
        return bonus
    
    def _tournament_selection(self, population: List[Individual], tournament_size: int = 5) -> Individual:
        """Tournament selection for parent selection"""
        
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Crossover operation to create offspring"""
        
        if len(parent1.ilots) != len(parent2.ilots):
            return parent1, parent2
        
        # Single-point crossover
        crossover_point = random.randint(1, len(parent1.ilots) - 1)
        
        child1_ilots = parent1.ilots[:crossover_point] + parent2.ilots[crossover_point:]
        child2_ilots = parent2.ilots[:crossover_point] + parent1.ilots[crossover_point:]
        
        return Individual(ilots=child1_ilots), Individual(ilots=child2_ilots)
    
    def _mutate(self, individual: Individual, bounds: Tuple[float, float, float, float]) -> Individual:
        """Mutation operation"""
        
        min_x, min_y, max_x, max_y = bounds
        mutated_ilots = []
        
        for x, y, w, h in individual.ilots:
            if random.random() < 0.3:  # 30% chance to mutate each îlot
                # Small random displacement
                dx = random.uniform(-2, 2)
                dy = random.uniform(-2, 2)
                
                new_x = max(min_x, min(max_x - w, x + dx))
                new_y = max(min_y, min(max_y - h, y + dy))
                
                mutated_ilots.append((new_x, new_y, w, h))
            else:
                mutated_ilots.append((x, y, w, h))
        
        return Individual(ilots=mutated_ilots)

class ConstraintSolver:
    """Advanced constraint satisfaction solver for îlot placement"""
    
    def __init__(self):
        self.constraints = []
        
    def add_constraint(self, constraint_func, weight: float = 1.0):
        """Add a constraint function"""
        self.constraints.append((constraint_func, weight))
    
    def solve_constraints(self, 
                         initial_solution: List[Tuple[float, float, float, float]],
                         bounds: Tuple[float, float, float, float],
                         max_iterations: int = 1000) -> List[Tuple[float, float, float, float]]:
        """Solve constraints using iterative improvement"""
        
        current_solution = initial_solution.copy()
        best_solution = current_solution.copy()
        best_score = self._evaluate_constraints(current_solution)
        
        min_x, min_y, max_x, max_y = bounds
        
        for iteration in range(max_iterations):
            # Try small modifications
            modified_solution = current_solution.copy()
            
            # Randomly select an îlot to modify
            if modified_solution:
                idx = random.randint(0, len(modified_solution) - 1)
                x, y, w, h = modified_solution[idx]
                
                # Small random movement
                dx = random.uniform(-1, 1)
                dy = random.uniform(-1, 1)
                
                new_x = max(min_x, min(max_x - w, x + dx))
                new_y = max(min_y, min(max_y - h, y + dy))
                
                modified_solution[idx] = (new_x, new_y, w, h)
                
                # Evaluate new solution
                score = self._evaluate_constraints(modified_solution)
                
                # Accept if better or with probability (simulated annealing)
                temperature = 1.0 - (iteration / max_iterations)
                if score > best_score or random.random() < temperature * 0.1:
                    current_solution = modified_solution
                    
                    if score > best_score:
                        best_solution = modified_solution.copy()
                        best_score = score
        
        return best_solution
    
    def _evaluate_constraints(self, solution: List[Tuple[float, float, float, float]]) -> float:
        """Evaluate constraint satisfaction score"""
        
        total_score = 0
        
        for constraint_func, weight in self.constraints:
            score = constraint_func(solution)
            total_score += score * weight
        
        return total_score

class SpaceFillingOptimizer:
    """Advanced space-filling algorithm for maximum area utilization"""
    
    def __init__(self, grid_resolution: float = 0.25):
        self.grid_resolution = grid_resolution
        
    def optimize_space_filling(self,
                              ilot_specs: List[Dict],
                              forbidden_areas: List[Polygon],
                              bounds: Tuple[float, float, float, float]) -> List[Tuple[float, float, float, float]]:
        """Optimize îlot placement for maximum space filling"""
        
        min_x, min_y, max_x, max_y = bounds
        
        # Create occupancy grid
        grid_width = int((max_x - min_x) / self.grid_resolution) + 1
        grid_height = int((max_y - min_y) / self.grid_resolution) + 1
        occupancy_grid = np.zeros((grid_height, grid_width), dtype=bool)
        
        # Mark forbidden areas in grid
        for forbidden in forbidden_areas:
            self._mark_polygon_in_grid(forbidden, occupancy_grid, bounds)
        
        placed_ilots = []
        
        # Sort îlots by area (largest first)
        sorted_specs = sorted(ilot_specs, key=lambda x: x['area'], reverse=True)
        
        for spec in sorted_specs:
            width, height = spec['dimensions']
            
            best_position = self._find_best_position(
                width, height, occupancy_grid, bounds
            )
            
            if best_position:
                x, y = best_position
                placed_ilots.append((x, y, width, height))
                
                # Mark this îlot in the grid
                ilot_poly = Polygon([
                    (x, y), (x + width, y), (x + width, y + height), (x, y + height)
                ])
                self._mark_polygon_in_grid(ilot_poly, occupancy_grid, bounds)
        
        return placed_ilots
    
    def _mark_polygon_in_grid(self, 
                             polygon: Polygon,
                             grid: np.ndarray,
                             bounds: Tuple[float, float, float, float]):
        """Mark polygon area as occupied in grid"""
        
        min_x, min_y, max_x, max_y = bounds
        
        # Get polygon bounds
        poly_bounds = polygon.bounds
        
        # Convert to grid coordinates
        start_col = max(0, int((poly_bounds[0] - min_x) / self.grid_resolution))
        end_col = min(grid.shape[1], int((poly_bounds[2] - min_x) / self.grid_resolution) + 1)
        start_row = max(0, int((poly_bounds[1] - min_y) / self.grid_resolution))
        end_row = min(grid.shape[0], int((poly_bounds[3] - min_y) / self.grid_resolution) + 1)
        
        # Mark grid cells that intersect with polygon
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                # Convert grid cell to world coordinates
                cell_x = min_x + col * self.grid_resolution
                cell_y = min_y + row * self.grid_resolution
                
                cell_point = Point(cell_x, cell_y)
                
                if polygon.contains(cell_point) or polygon.intersects(cell_point.buffer(self.grid_resolution/2)):
                    grid[row, col] = True
    
    def _find_best_position(self,
                           width: float,
                           height: float,
                           occupancy_grid: np.ndarray,
                           bounds: Tuple[float, float, float, float]) -> Optional[Tuple[float, float]]:
        """Find best position for îlot placement"""
        
        min_x, min_y, max_x, max_y = bounds
        
        # Convert dimensions to grid units
        width_cells = int(width / self.grid_resolution) + 1
        height_cells = int(height / self.grid_resolution) + 1
        
        best_score = -1
        best_position = None
        
        # Search grid for best position
        for row in range(occupancy_grid.shape[0] - height_cells):
            for col in range(occupancy_grid.shape[1] - width_cells):
                
                # Check if area is free
                area = occupancy_grid[row:row+height_cells, col:col+width_cells]
                
                if not np.any(area):  # Area is free
                    # Calculate position score (prefer corners and edges)
                    score = self._calculate_position_score(row, col, occupancy_grid.shape)
                    
                    if score > best_score:
                        best_score = score
                        # Convert back to world coordinates
                        world_x = min_x + col * self.grid_resolution
                        world_y = min_y + row * self.grid_resolution
                        best_position = (world_x, world_y)
        
        return best_position
    
    def _calculate_position_score(self, 
                                 row: int, 
                                 col: int, 
                                 grid_shape: Tuple[int, int]) -> float:
        """Calculate position score for space-filling optimization"""
        
        height, width = grid_shape
        
        # Prefer positions closer to edges and corners
        edge_distance = min(row, col, height - row, width - col)
        corner_distance = min(
            np.sqrt(row**2 + col**2),
            np.sqrt(row**2 + (width - col)**2),
            np.sqrt((height - row)**2 + col**2),
            np.sqrt((height - row)**2 + (width - col)**2)
        )
        
        # Combine scores (lower distance = higher score)
        score = 1000 - edge_distance - corner_distance * 0.5
        
        return score