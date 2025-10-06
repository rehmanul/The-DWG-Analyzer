# Running the Production System

## Quick Start

```bash
# Install dependencies
pip install -r requirements_production.txt

# Run the production application
streamlit run streamlit_production_app.py
```

## Accessing the Application

Once running, open your browser to:
```
http://localhost:8501
```

## Step-by-Step Usage

### 1. Prepare Your DXF File

Ensure your DXF file follows these rules:

#### Color Coding (CRITICAL):
- **Black lines (ACI 0, 7, 8)** = Walls (MUR)
  - Define the floor plan boundaries
  - Îlots are ALLOWED to touch walls
  
- **Blue zones (ACI 5)** = NO ENTREE (Restricted Areas)
  - Stairs, elevators, equipment rooms
  - Îlots CANNOT be placed here
  
- **Red zones (ACI 1)** = ENTREE/SORTIE (Entrances/Exits)
  - Door locations
  - Îlots CANNOT touch these areas

#### Supported Entity Types:
- LWPOLYLINE
- POLYLINE
- LINE
- ARC
- CIRCLE
- SPLINE
- ELLIPSE
- HATCH
- SOLID

### 2. Upload File

1. Click "Choose a DXF file" button
2. Select your prepared DXF file
3. Wait for upload confirmation

### 3. Configure Parameters

In the left sidebar:

#### Îlot Size Distribution:
- Adjust sliders for each category
- Ensure total equals 100%
- Default distribution:
  - Micro (0-1m²): 10%
  - Small (1-3m²): 25%
  - Medium (3-5m²): 30%
  - Large (5-10m²): 35%

#### Placement Parameters:
- **Target îlots**: Number of îlots to place (10-500)
- **Minimum spacing**: Distance between îlots (0.1-2.0m)
- **Corridor width**: Width of corridors (1.0-3.0m)

### 4. Process

1. Click "🚀 Process Floor Plan" button
2. Wait for processing (typically 5-30 seconds)
3. View results

### 5. View Results

The application shows:

#### Metrics Dashboard:
- Number of îlots placed
- Coverage percentages
- Corridor statistics
- Processing time

#### Visualization Tabs:
1. **Floor Plan Only**: Original CAD layout
2. **Îlot Placement**: Floor plan + placed îlots
3. **Complete with Corridors**: Full layout with corridors
4. **Analytics**: Detailed metrics and distribution

## Expected Output

### Visual Elements:

```
🔲 Light Gray = Open spaces (available for îlots)
⬛ Dark Gray/Black = Walls (MUR)
🔵 Blue = Restricted areas (NO ENTREE)
🔴 Red = Entrances/Exits (ENTREE/SORTIE)
🟢 Green = Placed îlots
🟣 Purple = Generated corridors
```

### Metrics:

The system calculates:
- **Îlot Coverage**: % of open space occupied by îlots
- **Corridor Coverage**: % of open space used for corridors
- **Total Coverage**: Combined îlot + corridor coverage
- **Placement Score**: Optimization quality metric

## Troubleshooting

### Problem: No open spaces found

**Solution**: 
- Check that your DXF has proper wall entities
- Ensure walls are colored black (ACI 0, 7, or 8)
- Verify file is not corrupted

### Problem: Few îlots placed

**Solution**:
- Increase minimum spacing value
- Check for too many restricted areas
- Verify entrance buffers not too large
- Try reducing target number of îlots

### Problem: No corridors generated

**Solution**:
- Need at least 4 îlots for corridors
- Îlots must form distinct rows
- Check corridor width isn't too large
- Ensure îlots aren't clustered irregularly

### Problem: Processing timeout

**Solution**:
- Reduce target number of îlots
- Simplify floor plan
- Check for extremely complex geometry
- System auto-stops at 60 seconds

## Advanced Configuration

### Genetic Algorithm Tuning

For developers, these parameters can be adjusted in `core/production_ilot_engine.py`:

```python
self.population_size = 50      # Larger = more diverse but slower
self.max_generations = 100     # More generations = better optimization
self.mutation_rate = 0.1       # Higher = more exploration
self.elite_size = 10           # Number of best solutions to keep
self.timeout_seconds = 60      # Maximum processing time
```

### Corridor Generation Tuning

In `core/production_corridor_generator.py`:

```python
self.row_tolerance = 3.0           # Distance for grouping into rows
self.min_corridor_length = 2.0     # Minimum corridor length
```

## Performance Tips

### For Large Floor Plans:
1. Start with fewer îlots (50-100)
2. Use larger minimum spacing (0.5m+)
3. Process in sections if possible

### For Best Results:
1. Clean CAD file (remove unnecessary entities)
2. Proper color coding (critical)
3. Simple, clear floor plan layout
4. Reasonable parameter values

## Example Workflow

```
1. Architect creates floor plan in CAD
   ↓
2. Color code: Black walls, Blue restricted, Red entrances
   ↓
3. Export as DXF file
   ↓
4. Upload to system
   ↓
5. Configure: 100 îlots, 0.3m spacing, 1.5m corridors
   ↓
6. Process (15 seconds)
   ↓
7. Review results: 87 îlots placed, 12 corridors, 65% coverage
   ↓
8. Adjust parameters if needed and reprocess
   ↓
9. Export final visualization (screenshot/PDF)
```

## System Requirements

### Minimum:
- Python 3.8+
- 2GB RAM
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Recommended:
- Python 3.10+
- 4GB RAM
- Chrome browser for best Plotly performance

## Getting Help

### Check Logs:
The system logs detailed information. Look for:
```
[INFO] Processing steps
[WARNING] Potential issues
[ERROR] Critical problems
```

### Common Issues:
1. **"No valid zones found"** → Check color coding
2. **"Percentages don't sum to 100%"** → Adjust sliders
3. **"Processing failed"** → Check DXF file integrity
4. **"Timeout exceeded"** → Reduce complexity

## Next Steps

After successful processing:

1. **Review Layout**: Check if îlot distribution meets requirements
2. **Adjust Parameters**: Fine-tune for better results
3. **Export Results**: Screenshot visualizations
4. **Iterate**: Reprocess with different configurations
5. **Validate**: Ensure all constraints are met

## Production Deployment

For deploying to a server:

```bash
# Set environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export LOG_LEVEL=INFO

# Run with nohup for background process
nohup streamlit run streamlit_production_app.py &
```

Or use Docker (see Dockerfile in repository).

## Support

For technical support:
1. Check PRODUCTION_SYSTEM.md for architecture details
2. Review logs for error messages
3. Verify input file meets requirements
4. Ensure latest dependencies installed

---

**Remember**: This is a production system with NO SIMULATIONS. All results are based on real CAD data processing and optimization algorithms.
