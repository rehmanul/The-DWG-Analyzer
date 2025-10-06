# Production Îlot Placement System

## Overview

This is a **production-grade** system for automatic îlot (storage unit) placement in architectural floor plans. The system processes CAD files (DXF/DWG), automatically places îlots according to user-defined size distributions, and generates corridors between îlot rows.

**NO SIMULATIONS OR FALLBACKS** - This system uses real CAD data processing and production algorithms only.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. CAD PARSER (core/production_cad_parser.py)              │
│     ├─ Parse DXF/DWG files                                  │
│     ├─ Extract entities (LWPOLYLINE, LINE, ARC, etc.)       │
│     ├─ Color-based classification                           │
│     │  ├─ Black → Walls (îlots can touch)                   │
│     │  ├─ Blue → Restricted (NO ENTREE)                     │
│     │  └─ Red → Entrances (ENTREE/SORTIE)                   │
│     └─ Calculate open spaces                                │
│                                                               │
│  2. ÎLOT ENGINE (core/production_ilot_engine.py)            │
│     ├─ User-defined size distribution                       │
│     │  ├─ 10% between 0-1 m²                                │
│     │  ├─ 25% between 1-3 m²                                │
│     │  ├─ 30% between 3-5 m²                                │
│     │  └─ 35% between 5-10 m²                               │
│     ├─ Genetic algorithm optimization                       │
│     │  ├─ Population: 50 chromosomes                        │
│     │  ├─ Generations: up to 100                            │
│     │  ├─ Elite selection                                   │
│     │  ├─ Tournament selection                              │
│     │  ├─ Crossover & Mutation                              │
│     │  └─ Early stopping                                    │
│     └─ Constraint validation                                │
│        ├─ Must be in open spaces                            │
│        ├─ No intersection with restricted areas             │
│        ├─ No contact with entrances                         │
│        ├─ Can touch walls (allowed)                         │
│        └─ Minimum spacing between îlots                     │
│                                                               │
│  3. CORRIDOR GENERATOR (core/production_corridor_generator.py)│
│     ├─ Group îlots into rows (clustering)                   │
│     ├─ Generate corridors between rows                      │
│     ├─ Configurable width                                   │
│     ├─ Never cuts through îlots                             │
│     └─ Connects facing rows                                 │
│                                                               │
│  4. ORCHESTRATOR (core/production_orchestrator.py)          │
│     └─ Coordinates entire pipeline                          │
│                                                               │
│  5. STREAMLIT UI (streamlit_production_app.py)              │
│     ├─ File upload                                          │
│     ├─ Configuration interface                              │
│     ├─ Real-time processing                                 │
│     └─ Interactive visualizations                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Input Processing
- **DXF/DWG File Support**: Parses all CAD entity types
  - LWPOLYLINE
  - POLYLINE
  - LINE
  - ARC
  - CIRCLE
  - SPLINE
  - ELLIPSE
  - HATCH/SOLID

- **Color-Based Classification**:
  - **Black (ACI 7, 8, 0)**: Walls - îlots CAN touch
  - **Blue (ACI 5)**: Restricted areas - NO ENTREE (stairs, elevators)
  - **Red (ACI 1)**: Entrances/Exits - ENTREE/SORTIE (no îlot contact)

### 2. Îlot Placement
- **User-Defined Distribution**:
  - Configure percentage for each size category
  - Automatic validation (must sum to 100%)
  
- **Genetic Algorithm**:
  - Population-based optimization
  - Elite selection for best solutions
  - Tournament selection for diversity
  - Adaptive mutation rates
  - Early stopping when optimal

- **Constraints**:
  - ✅ Can touch walls
  - ❌ Cannot intersect restricted areas
  - ❌ Cannot touch entrances
  - ✅ Must maintain minimum spacing
  - ✅ Must be within open spaces

### 3. Corridor Generation
- **Automatic Row Detection**:
  - Hierarchical clustering algorithm
  - Robust to irregular layouts
  
- **Intelligent Placement**:
  - Between facing rows of îlots
  - Configurable width (1.0m - 3.0m)
  - Never cuts through îlots
  - Touches both connected rows

### 4. Output
- **2D Visualization**:
  - Color-coded elements
  - Interactive Plotly charts
  - Multiple view modes:
    - Floor plan only
    - Îlot placement
    - Complete with corridors
  
- **Metrics & Analytics**:
  - Coverage percentages
  - Îlot distribution by category
  - Corridor statistics
  - Processing time

## Usage

### Running the Application

```bash
# Start the production application
streamlit run streamlit_production_app.py
```

### Configuration Parameters

#### Îlot Size Distribution
- **Micro (0-1 m²)**: Default 10%
- **Small (1-3 m²)**: Default 25%
- **Medium (3-5 m²)**: Default 30%
- **Large (5-10 m²)**: Default 35%

#### Placement Parameters
- **Total Îlots**: 10-500 (default: 100)
- **Minimum Spacing**: 0.1-2.0m (default: 0.3m)
- **Corridor Width**: 1.0-3.0m (default: 1.5m)

### Input File Requirements

Your DXF file must contain:

1. **Walls (Black Lines)**
   - Layer: Any
   - Color: ACI 7, 8, or 0
   - These define the floor plan boundaries
   - Îlots are allowed to touch walls

2. **Forbidden Zones (Blue)**
   - Color: ACI 5 (Blue)
   - Examples: Stairs, elevators, equipment
   - Îlots cannot be placed here

3. **Entrances/Exits (Red)**
   - Color: ACI 1 (Red)
   - Door locations
   - Îlots cannot touch these areas

## Algorithm Details

### Genetic Algorithm for Îlot Placement

```python
# Chromosome representation
chromosome = [(x1, y1, rot1), (x2, y2, rot2), ..., (xN, yN, rotN)]

# Fitness function
fitness = (
    num_valid_ilots * 10 +        # Primary objective
    total_area_coverage * 0.1 +    # Secondary objective
    distribution_balance * 5 +      # Tertiary objective
    spacing_efficiency * 2          # Quaternary objective
)

# Evolution process
1. Initialize random population
2. Evaluate fitness for all chromosomes
3. Select elite solutions
4. Tournament selection for parents
5. Crossover (single-point)
6. Mutation (10-20% of genes)
7. Replace population
8. Repeat until convergence or max generations
```

### Corridor Generation Algorithm

```python
# Row detection (hierarchical clustering)
1. Extract Y-coordinates of îlot centers
2. Apply Ward linkage clustering
3. Group îlots with distance < row_tolerance
4. Filter rows with < 2 îlots

# Corridor creation
For each pair of adjacent rows:
    1. Calculate row bounds
    2. Find X-overlap between rows
    3. Position corridor at Y-midpoint
    4. Create corridor polygon
    5. Validate:
       - Doesn't intersect îlots
       - Within open spaces
       - Minimum length requirement
    6. Add to corridor network
```

## Performance

- **Processing Time**: Typically 5-30 seconds depending on complexity
- **Optimization**: 
  - Early stopping when solution converges
  - Timeout protection (60s max)
  - Adaptive population size
  
- **Scalability**:
  - Handles 10-500 îlots
  - Supports complex floor plans
  - Memory efficient

## Error Handling

The system includes comprehensive error handling:

1. **File Validation**: Checks DXF file integrity
2. **Geometry Validation**: Fixes invalid polygons
3. **Constraint Validation**: Ensures all rules are followed
4. **Timeout Protection**: Prevents infinite loops
5. **Graceful Degradation**: Returns best solution found

## Testing

To verify the system works correctly:

1. Prepare a test DXF file with:
   - Black walls defining floor area
   - Blue zones for restricted areas
   - Red zones for entrances

2. Run the application:
   ```bash
   streamlit run streamlit_production_app.py
   ```

3. Upload file and process

4. Verify:
   - ✅ Îlots placed only in open spaces
   - ✅ No îlots in blue zones
   - ✅ No îlots touching red zones
   - ✅ Corridors between rows
   - ✅ No corridor-îlot intersections

## Production Deployment

### Requirements
- Python 3.8+
- 2GB RAM minimum
- Modern web browser

### Environment Variables
```bash
export LOG_LEVEL=INFO
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Docker Deployment
```bash
docker build -t ilot-placement-system .
docker run -p 8501:8501 ilot-placement-system
```

## Architecture Decisions

### Why Genetic Algorithm?
- Handles complex constraint optimization
- Naturally balances multiple objectives
- Robust to different floor plan layouts
- Produces diverse solutions
- Can escape local optima

### Why Color-Based Classification?
- Industry standard in CAD
- Easy for architects to mark zones
- Clear visual distinction
- No ambiguity in intent

### Why Production-Only Code?
- Ensures real-world reliability
- No fallback to fake data
- Forces proper CAD file preparation
- Maintains system integrity
- Professional quality output

## Limitations

1. **DXF Files Only**: Currently supports DXF format (DWG requires conversion)
2. **2D Only**: Does not handle multi-floor plans (process each floor separately)
3. **Rectangular Îlots**: Currently generates rectangular shapes only
4. **Horizontal Rows**: Corridor algorithm optimized for horizontal îlot rows

## Future Enhancements

- [ ] DWG direct support
- [ ] Multi-floor processing
- [ ] Curved corridor support
- [ ] Custom îlot shapes
- [ ] PDF export with measurements
- [ ] AutoCAD script export
- [ ] 3D visualization

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify DXF file follows color coding rules
3. Ensure entities are valid polygons
4. Review constraint violations in output

## License

Production System - All Rights Reserved
