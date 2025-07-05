# 🏗️ AI Îlot Placement PRO - User Guide

## Client Requirements Implementation

### ✅ Features Implemented

1. **Zone Detection by Color**
   - Black lines (color 7/0): Walls - îlots can touch these
   - Light blue areas (color 5): Restricted zones (stairs, elevators) - avoided
   - Red areas (color 1): Entrances/exits - buffer zones applied

2. **Proportional Îlot Placement**
   - 0-1m² îlots: Small utilities, storage
   - 1-3m² îlots: Bathrooms, closets
   - 3-5m² îlots: Standard rooms
   - 5-10m² îlots: Suites, common areas

3. **Automatic Corridor Generation**
   - Corridors placed between facing îlot rows
   - Configurable width (80-200cm)
   - No overlap with îlots
   - Connects all îlot groups

4. **Constraint Compliance**
   - Avoids red and blue zones
   - Allows îlots to touch walls
   - Maintains minimum clearances
   - Optimizes space utilization

## How to Use

### 1. Launch Application
```bash
# Run main application
streamlit run apps/streamlit_app.py

# Or run dedicated îlot app
python run_ilot_placement.py
```

### 2. Upload DXF File
- Upload your architectural plan in DXF format
- Ensure color coding: Black=walls, Blue=restricted, Red=entrances

### 3. Configure Îlot Distribution
- Set percentages for each size category
- Total must equal 100%
- Adjust total number of îlots
- Set corridor width

### 4. Generate Layout
- Click "Generate Îlot Layout"
- View results with color-coded îlots
- Check placement metrics

### 5. Export Results
- Download DXF file with îlots and corridors
- Export JSON report with metrics
- Professional CAD-compatible output

## Expected Output

The system generates:
- **Colored îlots** by size category
- **Orange corridors** between rows
- **Placement metrics** (success rate, utilization)
- **Professional exports** (DXF, reports)

## Example Hotel Configuration

```
10% of îlots between 0 and 1 m²   (utilities)
25% of îlots between 1 and 3 m²   (bathrooms)  
30% of îlots between 3 and 5 m²   (standard rooms)
35% of îlots between 5 and 10 m²  (suites)
```

## Technical Notes

- Uses advanced geometric algorithms
- Shapely library for spatial operations
- Genetic optimization for placement
- Real-time constraint checking
- Professional visualization with Plotly

## Troubleshooting

**No îlots placed?**
- Check DXF color coding
- Ensure sufficient space
- Reduce îlot count or size

**Missing corridors?**
- Need multiple îlot rows
- Check corridor width setting
- Verify îlot spacing

**Export issues?**
- Ensure ezdxf library installed
- Check file permissions
- Try different export format

## Integration

The îlot placement is fully integrated into the main AI Architectural Analyzer:
- Available in both Standard and Advanced modes
- Works with existing DWG/DXF parsing
- Compatible with all export functions
- Includes professional reporting