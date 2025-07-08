# AI Architectural Space Analyzer PRO - Enterprise Edition

## Overview

The AI Architectural Space Analyzer PRO is a comprehensive enterprise-grade application for architectural drawing analysis and space planning. The system combines advanced AI algorithms with building information modeling (BIM) to provide intelligent room detection, îlot placement optimization, and professional visualization capabilities. The application supports multiple deployment modes including desktop GUI, web interface, and API services.

## System Architecture

### Frontend Architecture
- **Desktop Application**: PyQt5-based professional interface with advanced parameter panels and real-time visualization
- **Web Interface**: Streamlit-based responsive web application with progressive enhancement
- **API Service**: Flask-based RESTful API with tiered access (free, pro, enterprise)

### Backend Architecture
- **CAD Processing Engine**: Multi-format parser supporting DWG, DXF, PNG, JPG, TIFF with ezdxf and OpenCV
- **AI Analysis Engine**: Multi-service AI integration (Google Gemini, OpenAI, Anthropic) for room classification
- **Optimization Engine**: Genetic algorithm, constraint solver, and space-filling optimizer for îlot placement
- **Database Layer**: PostgreSQL with SQLAlchemy ORM for project management and collaboration

### Data Storage Solutions
- **Primary Database**: PostgreSQL hosted on Render (dpg-d1h53rffte5s739b1i40-a.oregon-postgres.render.com)
- **Session Storage**: Streamlit session state for web interface
- **File Storage**: Temporary file handling with secure cleanup
- **Export Storage**: Multiple formats (PDF, DXF, JSON, CSV, SVG)

## Key Components

### Core Processing Modules
1. **Enhanced DWG Parser** (`src/enhanced_dwg_parser.py`): Multi-strategy parsing with fallback mechanisms
2. **Enhanced Îlot Engine** (`src/enhanced_ilot_engine.py`): Client-compliant îlot placement with color-based zone detection
3. **Advanced AI Models** (`src/advanced_ai_models.py`): Ensemble learning for room classification
4. **Enterprise Visualization** (`src/enterprise_visualization.py`): Professional 2D/3D rendering

### Îlot Placement System
- **Zone Detection**: Color-coded area identification (Black=walls, Blue=restricted, Red=entrances)
- **Proportional Placement**: Configurable size distributions (0-1m², 1-3m², 3-5m², 5-10m²)
- **Corridor Generation**: Automatic corridor placement between îlot rows with configurable width
- **Constraint Compliance**: Avoids restricted areas while allowing wall contact

### AI Integration
- **Multi-AI Support**: Google Gemini, OpenAI GPT, Anthropic Claude with priority ordering
- **Room Recognition**: Advanced pattern matching with confidence scoring
- **Optimization Algorithms**: Genetic algorithm, space-filling optimizer, constraint solver

### Professional Export System
- **PDF Reports**: Comprehensive analysis reports with statistics and visualizations
- **CAD Export**: DXF format with proper layers and scaling
- **Data Export**: JSON, CSV formats for further analysis
- **Vector Graphics**: SVG export for presentations

## Data Flow

1. **File Upload**: User uploads DWG/DXF files through web or desktop interface
2. **Parsing**: Enhanced parser extracts entities with multiple fallback strategies
3. **Zone Detection**: Color-based classification identifies walls, restricted areas, and entrances
4. **AI Analysis**: Multi-service AI performs room type classification with confidence scoring
5. **Îlot Placement**: Genetic algorithm optimizes placement based on proportional configuration
6. **Corridor Generation**: Automatic corridor placement between facing îlot rows
7. **Visualization**: Professional rendering with interactive 2D/3D views
8. **Export**: Multiple format generation (PDF, DXF, JSON) with professional styling

## External Dependencies

### Required Libraries
- **CAD Processing**: ezdxf (DXF parsing), opencv-python (image processing)
- **AI/ML**: google-generativeai, openai, anthropic, scikit-learn, scipy
- **Visualization**: plotly, matplotlib, streamlit
- **Database**: psycopg2-binary, sqlalchemy
- **Geometry**: shapely (spatial operations)
- **Export**: reportlab (PDF), pandas (data export)

### Optional Dependencies
- **GUI**: PyQt5 (desktop interface)
- **3D Visualization**: OpenGL, PyOpenGL
- **Advanced Optimization**: tensorflow, pytorch

### External Services
- **Database**: PostgreSQL on Render cloud platform
- **AI Services**: Google Gemini API, OpenAI API, Anthropic API
- **Deployment**: Streamlit Cloud for web hosting

## Deployment Strategy

### Web Deployment
- **Platform**: Streamlit Cloud
- **URL**: https://the-dwg-analyzer.streamlit.app/
- **Features**: Full îlot placement, AI analysis, professional visualization
- **Limitations**: File size limited to 10MB due to tunnel/proxy restrictions

### Desktop Deployment
- **Installer**: NSIS-based Windows installer (`installers/`)
- **Executable**: PyInstaller-built standalone application
- **Features**: Full functionality including large file support (up to 190MB)

### API Deployment
- **Service**: Flask-based RESTful API
- **Tiers**: Free (10 requests), Pro (1000 requests), Enterprise (unlimited)
- **Authentication**: API key-based with usage tracking

### Development Environment
- **Container**: DevContainer configuration for Codespaces
- **Requirements**: Multiple requirement files for different deployment scenarios
- **Testing**: Automated testing scripts and validation

## Changelog
- July 08, 2025: Successfully migrated from Replit Agent to standard Replit environment
- July 08, 2025: Verified all client requirements are met and application is fully functional
- July 08, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.