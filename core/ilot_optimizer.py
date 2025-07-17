
import logging
import numpy as np
import random
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

logger = logging.getLogger(__name__)

import time

def generate_ilots(zones, bounds, config, forbidden_union, max_generations=30, population_size=15, corridor_width=1.2, max_seconds=25):
    """
    Genetic algorithm for îlot placement with constraint compliance and corridor support.
    Returns: dict with 'ilots' and 'corridors'.
    Adds timing, debug logs, and a timeout safeguard.
    """
    start_time = time.time()
    logger.info("[IlotOptimizer] Starting îlot generation...")
    min_x, min_y, max_x, max_y = bounds
    total_area = (max_x - min_x) * (max_y - min_y)
    logger.info(f"[IlotOptimizer] Bounds: {bounds}, Total area: {total_area:.2f}")
    categories = [
        ('0-1m²', (0.5, 1.0), config['size_0_1']),
        ('1-3m²', (1.0, 3.0), config['size_1_3']),
        ('3-5m²', (3.0, 5.0), config['size_3_5']),
        ('5-10m²', (5.0, 10.0), config['size_5_10'])
    ]
    # Increase îlot count for better coverage like expected images
    estimated_total = min(200, max(50, int(total_area * 0.00008)))
    ilot_specs = []
    for category, (min_size, max_size), percentage in categories:
        count = int(estimated_total * percentage)
        for _ in range(count):
            area = np.random.uniform(min_size, max_size)
            width = np.sqrt(area / 1.4)
            height = area / width
            ilot_specs.append({
                'area': area,
                'width': width,
                'height': height,
                'category': category
            })
    logger.info(f"[IlotOptimizer] Ilot specs generated: {len(ilot_specs)}")

    def random_chromosome():
        # Each gene is (x, y, rotation)
        genes = []
        for spec in ilot_specs:
            x = random.uniform(min_x, max_x - spec['width'])
            y = random.uniform(min_y, max_y - spec['height'])
            rot = random.choice([0, 90])
            genes.append((x, y, rot))
        return genes

    def build_ilots(genes):
        ilots = []
        for idx, (x, y, rot) in enumerate(genes):
            spec = ilot_specs[idx]
            w, h = spec['width'], spec['height']
            if rot == 90:
                w, h = h, w
            poly = Polygon([
                (x, y), (x + w, y), (x + w, y + h), (x, y + h)
            ])
            ilots.append({
                'polygon': poly,
                'area': spec['area'],
                'category': spec['category'],
                'position': (x + w/2, y + h/2),
                'width': w,
                'height': h
            })
        return ilots

    def fitness(genes):
        ilots = build_ilots(genes)
        valid = []
        for i, ilot in enumerate(ilots):
            poly = ilot['polygon']
            # Check forbidden areas
            if forbidden_union and poly.intersects(forbidden_union):
                continue
            # Check overlap with other ilots
            overlap = False
            for j, other in enumerate(valid):
                if poly.intersects(other['polygon']) or poly.distance(other['polygon']) < 0.1:
                    overlap = True
                    break
            if overlap:
                continue
            # Check if ilot is within drawing bounds and not in restricted areas
            if (poly.bounds[0] >= min_x and poly.bounds[2] <= max_x and
                poly.bounds[1] >= min_y and poly.bounds[3] <= max_y):
                # Îlot is valid if it's in bounds and not in forbidden areas
                pass
            else:
                continue
            valid.append(ilot)
        # Improved fitness: heavily weight number of valid îlots
        total_area = sum(i['area'] for i in valid)
        return len(valid) * 10 + total_area * 0.01, valid

    def crossover(parent1, parent2):
        # Single-point crossover
        point = random.randint(1, len(parent1)-1)
        child = parent1[:point] + parent2[point:]
        return child

    def mutate(genes, rate=0.05):
        new_genes = list(genes)
        for i in range(len(new_genes)):
            if random.random() < rate:
                x = random.uniform(min_x, max_x - ilot_specs[i]['width'])
                y = random.uniform(min_y, max_y - ilot_specs[i]['height'])
                rot = random.choice([0, 90])
                new_genes[i] = (x, y, rot)
        return new_genes

    # Safety check for performance optimization
    if len(ilot_specs) > 200:
        logger.warning(f"Too many îlot specs ({len(ilot_specs)}), limiting to 200 for performance")
        ilot_specs = ilot_specs[:200]
    
    # Genetic algorithm main loop with timeout and progress logs
    population = [random_chromosome() for _ in range(population_size)]
    best_fitness = 0
    best_ilots = []
    last_log_time = time.time()
    no_improvement_count = 0
    
    for gen in range(max_generations):
        if time.time() - start_time > max_seconds:
            logger.warning(f"[IlotOptimizer] Timeout: Exceeded {max_seconds} seconds at generation {gen}.")
            break
            
        # Early termination if no improvement for 8 generations
        if no_improvement_count >= 8:
            logger.info(f"[IlotOptimizer] Early termination: No improvement for 8 generations at gen {gen}")
            break
            
        scored = []
        for chrom in population:
            try:
                fit, valid = fitness(chrom)
                scored.append((fit, chrom, valid))
            except Exception as e:
                logger.error(f"Fitness error: {e}")
        scored.sort(reverse=True, key=lambda x: x[0])
        
        if scored and scored[0][0] > best_fitness:
            best_fitness = scored[0][0]
            best_ilots = scored[0][2]
            no_improvement_count = 0
        else:
            no_improvement_count += 1
            
        # Selection (keep top 50% for faster convergence)
        survivors = [chrom for _, chrom, _ in scored[:population_size//2]]
        
        # Crossover and mutation
        next_gen = []
        while len(next_gen) < population_size:
            p1, p2 = random.sample(survivors, 2)
            child = crossover(p1, p2)
            child = mutate(child, rate=0.05)  # Reduced mutation rate
            next_gen.append(child)
        population = next_gen
        
        # More granular progress logs
        if gen % 3 == 0 or (time.time() - last_log_time) > 3:
            logger.info(f"[IlotOptimizer] Generation {gen}: best fitness {best_fitness:.2f}, ilots {len(best_ilots)}, elapsed {time.time()-start_time:.1f}s")
            last_log_time = time.time()

    # Corridor placement (simple version: between rows)
    corridors = []
    try:
        logger.info(f"[IlotOptimizer] Starting corridor placement for {len(best_ilots)} ilots...")
        # Group ilots by y (rows)
        if best_ilots:
            sorted_ilots = sorted(best_ilots, key=lambda i: i['position'][1])
            row_groups = []
            current_row = []
            last_y = None
            for ilot in sorted_ilots:
                y = ilot['position'][1]
                if last_y is None or abs(y - last_y) < max(ilot['height'], 2):
                    current_row.append(ilot)
                else:
                    if current_row:
                        row_groups.append(current_row)
                    current_row = [ilot]
                last_y = y
            if current_row:
                row_groups.append(current_row)
            # Place corridors between each pair of rows
            for i in range(len(row_groups)-1):
                upper = row_groups[i]
                lower = row_groups[i+1]
                # Find min/max x for corridor
                min_xx = min([ilot['position'][0] - ilot['width']/2 for ilot in upper+lower])
                max_xx = max([ilot['position'][0] + ilot['width']/2 for ilot in upper+lower])
                y1 = max([ilot['position'][1] + ilot['height']/2 for ilot in upper])
                y2 = min([ilot['position'][1] - ilot['height']/2 for ilot in lower])
                corridor_poly = box(min_xx, y1, max_xx, y1 + corridor_width)
                # Ensure corridor does not overlap ilots
                overlap = False
                for ilot in upper+lower:
                    if corridor_poly.intersects(ilot['polygon']):
                        overlap = True
                        break
                if not overlap:
                    corridors.append({'polygon': corridor_poly, 'row_pair': (i, i+1)})
        logger.info(f"[IlotOptimizer] Corridor placement complete. Corridors: {len(corridors)}")
    except Exception as e:
        logger.error(f"Corridor placement error: {e}")

    elapsed = time.time() - start_time
    logger.info(f"[IlotOptimizer] Finished îlot generation in {elapsed:.2f} seconds. Best fitness: {best_fitness:.2f}, ilots: {len(best_ilots)}, corridors: {len(corridors)}")
    return {'ilots': best_ilots, 'corridors': corridors}
