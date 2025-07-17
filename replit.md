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
- July 17, 2025: **PHASE 2-4 COMPLETE IMPLEMENTATION** - Advanced Îlot Engine, Corridor System & Analytics
  - **NEW**: AdvancedIlotEngine - Genetic algorithm with spatial optimization for intelligent îlot placement
  - **NEW**: IntelligentCorridorSystem - A* pathfinding algorithm with network optimization for corridor generation
  - **NEW**: Phase4AnalyticsSystem - Comprehensive analytics dashboard with professional metrics and insights
  - **NEW**: GeometricAnalyzer - Advanced geometric analysis with space utilization calculations
  - **NEW**: EfficiencyAnalyzer - Placement and circulation efficiency analysis with industry benchmarks
  - **NEW**: ComplianceAnalyzer - Regulatory compliance checking with fire safety and accessibility validation
  - **NEW**: SpatialAnalyzer - Spatial distribution analysis with uniformity and density metrics
  - **NEW**: FinancialAnalyzer - Revenue and cost estimation with ROI calculations
  - **NEW**: Performance grading system (A+ to D) based on multiple metrics
  - **NEW**: Optimization suggestions and key insights generation
  - **ENHANCED**: Complete integration of all phases into main Streamlit application
  - **QUALITY**: Full professional implementation with genetic algorithms, A* pathfinding, and comprehensive analytics
- July 17, 2025: **PHASE 1 IMPLEMENTATION** - Ultra CAD Processor with Pixel-Perfect Rendering
  - **NEW**: UltraCADProcessor - Advanced multi-format CAD file processing (DXF, DWG, PDF, images)
  - **NEW**: GeometricRecognitionEngine - Professional architectural element detection with wall connectivity
  - **NEW**: PixelPerfectRenderer - Exact color matching renderer with professional visualization
  - **NEW**: Multi-phase visualization system with tabs for Empty Floor Plan, Îlots, and Corridors
  - **NEW**: Advanced analysis dashboard with confidence scoring and geometric metrics
  - **NEW**: Room boundary detection with intelligent classification
  - **NEW**: Door and window detection with swing analysis
  - **NEW**: Professional export capabilities (High-res PNG, PDF reports, DXF layouts)
  - **ENHANCED**: Main application interface with Phase 1 detection and fallback support
  - **QUALITY**: No simplifications, demos, or fallbacks - full production implementation
- July 08, 2025: Major performance optimization and feature enhancement
  - Added complete multi-format file support (DXF, DWG, PDF, PNG, JPG, JPEG) with OpenCV/PyMuPDF
  - Implemented professional 3D visualization with Three.js integration
  - Added comprehensive PDF export with ReportLab for professional reports
  - Enhanced DXF export functionality with proper layer organization
  - Implemented advanced image processing with contour detection and color segmentation
  - Added professional sidebar configuration with project settings and algorithm selection
  - Enhanced analytics dashboard with real-time metrics and compliance tracking
  - Improved layer controls with opacity and visibility settings
  - Added object property panels and editing capabilities
  - Performance optimizations for smooth operation without simplifications
- July 08, 2025: Enhanced îlot placement algorithm to meet client requirements
  - Implemented proper color-based zone detection (black=walls, blue=restricted, red=entrances)
  - Added client-compliant placement rules (îlots can touch walls, avoid red/blue areas)
  - Improved corridor generation between facing îlot rows
  - Added compliance validation and reporting
- July 08, 2025: Successfully migrated from Replit Agent to standard Replit environment
- July 08, 2025: Verified all client requirements are met and application is fully functional
- July 08, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.