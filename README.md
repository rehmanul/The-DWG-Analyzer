# 🏗️ AI Architectural Space Analyzer PRO

Professional architectural drawing analysis with AI-powered insights.

## 📁 Project Structure

```
├── src/                    # Core source modules
├── apps/                   # Desktop & web applications  
├── installers/            # Installation packages
├── dist/                  # Built executables
├── docs/                  # Documentation
├── assets/                # Icons, images, samples
├── config/               # Configuration files
├── tests/                # Test files
└── scripts/              # Utility scripts
```

## 🚀 Quick Start

### Desktop Application
```bash
# Run from dist/
./AI_Architectural_Analyzer_WebFeatures.exe
```

### Web Application  
```bash
# Run from apps/
streamlit run streamlit_app.py
```

### Installation
```bash
# Run installer from installers/
./AI_Architectural_Analyzer_Setup.exe
```

## 🌟 Features

- ✅ AI-powered room detection
- ✅ Advanced furniture placement
- ✅ **Professional Îlot Placement** (NEW)
- ✅ Interactive visualizations
- ✅ Professional export options
- ✅ BIM integration
- ✅ Multi-format support (DWG/DXF)
- ✅ Corridor generation
- ✅ Constraint compliance

## 📊 Database

- **PostgreSQL**: `postgresql://de_de:PUPB8V0s2b3bvNZUblolz7d6UM9bcBzb@dpg-d1h53rffte5s739b1i40-a.oregon-postgres.render.com/dwg_analyzer_pro`
- **Gemini AI**: Configured and ready

## 🏗️ Îlot Placement PRO (NEW)

**Professional îlot placement with constraint compliance:**

- **Zone Detection**: Automatic detection by color coding
  - Black lines: Walls (îlots can touch)
  - Light blue: Restricted areas (avoided)
  - Red areas: Entrances/exits (buffer zones)

- **Proportional Placement**: User-defined size distribution
  - 0-1m²: Small utilities, storage
  - 1-3m²: Bathrooms, closets
  - 3-5m²: Standard rooms
  - 5-10m²: Suites, common areas

- **Corridor Generation**: Automatic corridor placement
  - Between facing îlot rows
  - Configurable width (80-200cm)
  - No overlap with îlots

- **Professional Export**: CAD-compatible output
  - DXF format with layers
  - JSON reports with metrics
  - Color-coded visualization

### Quick Start - Îlot Placement
```bash
# Launch dedicated îlot app
python run_ilot_placement.py

# Or use integrated version
streamlit run apps/streamlit_app.py
```

## 🛠️ Development

See individual directories for specific documentation and setup instructions.

---
**Professional CAD Analysis Solution** 🎯
