# Enterprise Îlot Placement System

A sophisticated CAD analysis application for architectural drawing analysis and intelligent space optimization.

## Features

- **CAD File Processing**: Supports DXF, DWG, PDF, PNG, JPG, JPEG files
- **AI Analysis**: Multi-service integration (Google Gemini, OpenAI, Anthropic)
- **Genetic Algorithm**: Optimized îlot placement with corridor generation
- **Professional Visualization**: 2D/3D rendering with interactive controls
- **Export Options**: PDF reports, DXF layouts, JSON/CSV data

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `streamlit run streamlit_app.py`
3. Upload your CAD files and configure placement parameters
4. Generate optimized îlot placements with corridors

## Deployment

### Render Deployment (Recommended)
1. Go to https://render.com
2. Create a new Web Service
3. Connect your repository
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `./start.sh`

See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions.

### Docker Deployment
```bash
docker build -t enterprise-ilot-system .
docker run -p 8501:8501 enterprise-ilot-system
```

## Architecture

- **Core Processing**: `core/` - CAD parsing and optimization algorithms
- **Advanced Features**: `src/` - AI models and visualization engines
- **Configuration**: `.streamlit/` - Production-ready Streamlit settings

## Performance

- Startup time: < 30 seconds
- File processing: < 5 seconds for standard files
- Memory usage: < 400MB for normal operations
- Supports large files (968 walls, 2991 entrances tested)

## License

Enterprise Edition - All rights reserved.