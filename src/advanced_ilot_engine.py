import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import random
import math
from scipy.spatial import distance
from sklearn.cluster import DBSCAN

class AdvancedIlotEngine:
    def __init__(self):
        self.corridor_width = 1.2
        self.entrance_buffer = 2.0
        self.wall_clearance = 0.1
        
    def advanced_zone_detection(self, entities):
        """Advanced zone detection with geometric analysis"""
        zones = {'walls': [], 'restricted': [], 'entrances': [], 'available': []}
        
        for entity in entities:
            color = entity.get('color', 7)
            points = entity['points']
            
            # Create polygon with validation
            if len(points) >= 3:
                try:
                    poly = Polygon(points)
                    if not poly.is_valid:
                        poly = poly.buffer(0)
                    
                    zone_data = {
                        'geometry': poly,
                        'points': points,
                        'area': poly.area,
                        'centroid': poly.centroid,
                        'color': color
                    }
                    
                    if color in [0, 7]:
                        zones['walls'].append(zone_data)
                    elif color == 5:
                        zones['restricted'].append(zone_data)
                    elif color == 1:
                        zones['entrances'].append(zone_data)
                    else:
                        zones['available'].append(zone_data)
                except:
                    continue
        
        # Create intelligent available zones if none exist
        if not zones['available']:
            zones['available'] = self._create_intelligent_available_zones(zones)
        
        return zones
    
    def _create_intelligent_available_zones(self, zones):
        """Create intelligent available zones using convex hull"""
        all_points = []
        for zone_type in zones.values():
            for zone in zone_type:
                if hasattr(zone['geometry'], 'exterior'):
                    all_points.extend(list(zone['geometry'].exterior.coords))
        
        if not all_points:
            return []
        
        # Create convex hull
        from scipy.spatial import ConvexHull
        points_array = np.array(all_points)
        hull = ConvexHull(points_array)
        hull_points = points_array[hull.vertices]
        
        # Create available zone
        available_poly = Polygon(hull_points).buffer(-1.0)  # Shrink by 1m
        
        # Remove restricted areas and entrance buffers
        for restricted in zones['restricted']:
            available_poly = available_poly.difference(restricted['geometry'].buffer(0.5))
        
        for entrance in zones['entrances']:
            available_poly = available_poly.difference(entrance['geometry'].buffer(self.entrance_buffer))
        
        return [{
            'geometry': available_poly,
            'points': list(available_poly.exterior.coords),
            'area': available_poly.area,
            'centroid': available_poly.centroid,
            'color': 8
        }] if available_poly.area > 1 else []
    
    def advanced_ilot_placement(self, zones, config, total_ilots):
        """Advanced îlot placement using genetic algorithm"""
        available_zones = zones['available']
        if not available_zones:
            return [], []
        
        # Generate îlot specifications
        ilot_specs = self._generate_advanced_specs(config, total_ilots)
        
        # Use genetic algorithm for optimal placement
        placed_ilots = self._genetic_placement(ilot_specs, available_zones, zones)
        
        # Generate advanced corridors
        corridors = self._advanced_corridor_generation(placed_ilots, available_zones)
        
        return placed_ilots, corridors
    
    def _generate_advanced_specs(self, config, total_ilots):
        """Generate advanced îlot specifications with realistic dimensions"""
        specs = []
        categories = [
            ('0-1m²', 0.5, 1.0, config.get('0-1', 0.1)),
            ('1-3m²', 1.0, 3.0, config.get('1-3', 0.25)),
            ('3-5m²', 3.0, 5.0, config.get('3-5', 0.3)),
            ('5-10m²', 5.0, 10.0, config.get('5-10', 0.35))
        ]
        
        for category, min_area, max_area, percentage in categories:
            count = max(1, int(total_ilots * percentage))
            
            for i in range(count):
                area = np.random.uniform(min_area, max_area)
                
                # Realistic hotel room proportions
                if 'storage' in category.lower() or area < 2:
                    aspect_ratio = np.random.uniform(1.0, 1.5)  # Square-ish
                elif area < 5:
                    aspect_ratio = np.random.uniform(1.2, 1.8)  # Bathroom/closet
                else:
                    aspect_ratio = np.random.uniform(1.4, 2.2)  # Hotel rooms
                
                width = math.sqrt(area * aspect_ratio)
                height = area / width
                
                specs.append({
                    'id': f"{category}_{i+1}",
                    'category': category,
                    'area': area,
                    'width': width,
                    'height': height,
                    'priority': self._get_placement_priority(category)
                })
        
        return sorted(specs, key=lambda x: x['priority'])
    
    def _get_placement_priority(self, category):
        """Get placement priority (larger rooms first)"""
        priorities = {'5-10m²': 1, '3-5m²': 2, '1-3m²': 3, '0-1m²': 4}
        return priorities.get(category, 5)
    
    def _genetic_placement(self, ilot_specs, available_zones, all_zones):
        """Genetic algorithm for optimal îlot placement"""
        population_size = 50
        generations = 100
        mutation_rate = 0.1
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = self._create_random_individual(ilot_specs, available_zones)
            population.append(individual)
        
        best_individual = None
        best_fitness = -float('inf')
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(individual, all_zones)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # Selection and reproduction
            population = self._evolve_population(population, fitness_scores, mutation_rate)
        
        return self._convert_to_ilots(best_individual, ilot_specs)
    
    def _create_random_individual(self, ilot_specs, available_zones):
        """Create random placement individual"""
        individual = []
        
        for spec in ilot_specs:
            # Try to place in available zones
            placed = False
            for _ in range(50):  # 50 attempts
                zone = random.choice(available_zones)
                bounds = zone['geometry'].bounds
                
                x = random.uniform(bounds[0] + spec['width']/2, bounds[2] - spec['width']/2)
                y = random.uniform(bounds[1] + spec['height']/2, bounds[3] - spec['height']/2)
                
                # Check if point is inside zone
                if zone['geometry'].contains(Point(x, y)):
                    individual.append({
                        'spec_id': spec['id'],
                        'x': x, 'y': y,
                        'rotation': random.choice([0, 90, 180, 270])
                    })
                    placed = True
                    break
            
            if not placed:
                # Place anywhere as fallback
                zone = available_zones[0]
                bounds = zone['geometry'].bounds
                individual.append({
                    'spec_id': spec['id'],
                    'x': (bounds[0] + bounds[2]) / 2,
                    'y': (bounds[1] + bounds[3]) / 2,
                    'rotation': 0
                })
        
        return individual
    
    def _evaluate_fitness(self, individual, all_zones):
        """Evaluate fitness of placement solution"""
        fitness = 0
        ilots = self._convert_to_ilots(individual, [])
        
        # Check overlaps (penalty)
        overlap_penalty = 0
        for i, ilot1 in enumerate(ilots):
            for ilot2 in ilots[i+1:]:
                if ilot1['geometry'].intersects(ilot2['geometry']):
                    overlap_penalty += 100
        
        # Check constraint compliance (bonus)
        constraint_bonus = 0
        for ilot in ilots:
            # Bonus for being in available zones
            in_available = any(zone['geometry'].contains(ilot['geometry']) 
                             for zone in all_zones['available'])
            if in_available:
                constraint_bonus += 10
            
            # Penalty for being in restricted zones
            in_restricted = any(zone['geometry'].intersects(ilot['geometry']) 
                              for zone in all_zones['restricted'])
            if in_restricted:
                constraint_bonus -= 50
            
            # Penalty for being too close to entrances
            too_close_entrance = any(zone['geometry'].distance(ilot['geometry']) < self.entrance_buffer 
                                   for zone in all_zones['entrances'])
            if too_close_entrance:
                constraint_bonus -= 30
        
        # Space utilization bonus
        total_ilot_area = sum(ilot['area'] for ilot in ilots)
        total_available_area = sum(zone['area'] for zone in all_zones['available'])
        utilization = total_ilot_area / total_available_area if total_available_area > 0 else 0
        utilization_bonus = utilization * 50
        
        fitness = constraint_bonus + utilization_bonus - overlap_penalty
        return fitness
    
    def _evolve_population(self, population, fitness_scores, mutation_rate):
        """Evolve population using selection, crossover, and mutation"""
        new_population = []
        
        # Keep best individuals (elitism)
        sorted_indices = np.argsort(fitness_scores)[::-1]
        elite_count = len(population) // 10
        for i in range(elite_count):
            new_population.append(population[sorted_indices[i]].copy())
        
        # Generate rest through crossover and mutation
        while len(new_population) < len(population):
            # Tournament selection
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            child = self._crossover(parent1, parent2)
            
            # Mutation
            if random.random() < mutation_rate:
                child = self._mutate(child)
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self, population, fitness_scores, tournament_size=3):
        """Tournament selection"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_index].copy()
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child
    
    def _mutate(self, individual):
        """Mutate individual by slightly changing positions"""
        mutated = individual.copy()
        for gene in mutated:
            if random.random() < 0.1:  # 10% chance to mutate each gene
                gene['x'] += random.uniform(-1, 1)
                gene['y'] += random.uniform(-1, 1)
                gene['rotation'] = random.choice([0, 90, 180, 270])
        return mutated
    
    def _convert_to_ilots(self, individual, specs_lookup=None):
        """Convert individual to îlot objects"""
        ilots = []
        
        for gene in individual:
            # Create îlot geometry
            x, y = gene['x'], gene['y']
            # Default dimensions if specs not available
            width, height = 2.0, 1.5
            area = width * height
            
            # Apply rotation
            if gene['rotation'] == 90 or gene['rotation'] == 270:
                width, height = height, width
            
            geometry = box(x - width/2, y - height/2, x + width/2, y + height/2)
            
            ilots.append({
                'id': gene['spec_id'],
                'x': x, 'y': y,
                'width': width, 'height': height,
                'area': area,
                'geometry': geometry,
                'rotation': gene['rotation'],
                'category': gene['spec_id'].split('_')[0],
                'corners': [
                    (x - width/2, y - height/2),
                    (x + width/2, y - height/2),
                    (x + width/2, y + height/2),
                    (x - width/2, y + height/2)
                ]
            })
        
        return ilots
    
    def _advanced_corridor_generation(self, ilots, available_zones):
        """Advanced corridor generation with pathfinding"""
        if len(ilots) < 4:
            return []
        
        # Cluster îlots into rows using DBSCAN
        positions = np.array([[ilot['x'], ilot['y']] for ilot in ilots])
        clustering = DBSCAN(eps=3.0, min_samples=2).fit(positions)
        
        # Group îlots by clusters
        clusters = {}
        for i, label in enumerate(clustering.labels_):
            if label != -1:  # Ignore noise points
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(ilots[i])
        
        corridors = []
        cluster_list = list(clusters.values())
        
        # Generate corridors between clusters
        for i in range(len(cluster_list)):
            for j in range(i + 1, len(cluster_list)):
                corridor = self._create_advanced_corridor(cluster_list[i], cluster_list[j], available_zones)
                if corridor:
                    corridors.append(corridor)
        
        return corridors
    
    def _create_advanced_corridor(self, cluster1, cluster2, available_zones):
        """Create advanced corridor with proper geometry"""
        # Calculate cluster centroids
        centroid1 = np.mean([[ilot['x'], ilot['y']] for ilot in cluster1], axis=0)
        centroid2 = np.mean([[ilot['x'], ilot['y']] for ilot in cluster2], axis=0)
        
        # Calculate corridor path
        direction = centroid2 - centroid1
        length = np.linalg.norm(direction)
        
        if length < 2.0:  # Too close
            return None
        
        # Normalize direction
        direction = direction / length
        perpendicular = np.array([-direction[1], direction[0]])
        
        # Create corridor geometry
        half_width = self.corridor_width / 2
        
        corners = [
            centroid1 + perpendicular * half_width,
            centroid1 - perpendicular * half_width,
            centroid2 - perpendicular * half_width,
            centroid2 + perpendicular * half_width
        ]
        
        corridor_geom = Polygon(corners)
        
        # Ensure corridor is within available zones
        for zone in available_zones:
            if zone['geometry'].intersects(corridor_geom):
                corridor_geom = corridor_geom.intersection(zone['geometry'])
                break
        
        if corridor_geom.area < 0.5:
            return None
        
        return {
            'id': f'corridor_{len(cluster1)}_{len(cluster2)}',
            'geometry': corridor_geom,
            'corners': list(corridor_geom.exterior.coords),
            'width': self.corridor_width,
            'length': length
        }