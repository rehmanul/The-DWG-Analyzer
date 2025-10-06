"""
Advanced SDK Viewer API
Flask backend for Three.js viewer integration
Production-grade CAD processing with accurate geometric handling
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import tempfile
import os
import json
import logging
from pathlib import Path

from core.production_orchestrator import ProductionOrchestrator
from core.production_ilot_engine import IlotSizeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='.')
CORS(app)

# Global state
current_session = {
    'floor_plan_data': None,
    'dxf_path': None
}


def polygon_to_geojson(polygon):
    """Convert Shapely Polygon to GeoJSON-like format"""
    if polygon is None:
        return None
    
    try:
        coords = list(polygon.exterior.coords)
        return {
            'type': 'Polygon',
            'coordinates': [[list(coord) for coord in coords]]
        }
    except Exception as e:
        logger.error(f"Failed to convert polygon: {e}")
        return None


@app.route('/')
def index():
    """Serve the main viewer HTML"""
    return send_file('advanced_sdk_viewer.html')


@app.route('/advanced_sdk_viewer.js')
def viewer_js():
    """Serve the viewer JavaScript"""
    return send_file('advanced_sdk_viewer.js', mimetype='application/javascript')


@app.route('/api/parse-dxf', methods=['POST'])
def parse_dxf():
    """
    Parse uploaded DXF file and extract zones
    Returns: walls, restricted areas, entrances, open spaces
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if not file.filename.endswith('.dxf'):
            return jsonify({'error': 'Only DXF files are supported'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        logger.info(f"Processing DXF file: {file.filename}")
        
        # Parse DXF
        orchestrator = ProductionOrchestrator()
        from core.production_cad_parser import ProductionCADParser
        
        parser = ProductionCADParser()
        
        # Update wall thickness from request if provided
        wall_thickness = request.form.get('wall_thickness', 0.20)
        parser.wall_buffer = float(wall_thickness)
        
        walls, restricted_areas, entrances, open_spaces = parser.parse_dxf(tmp_path)
        
        # Convert to GeoJSON format
        result = {
            'success': True,
            'filename': file.filename,
            'walls': [polygon_to_geojson(w) for w in walls if w],
            'restricted_areas': [polygon_to_geojson(r) for r in restricted_areas if r],
            'entrances': [polygon_to_geojson(e) for e in entrances if e],
            'open_spaces': [polygon_to_geojson(s) for s in open_spaces if s],
            'total_area': sum(s.area for s in open_spaces if s),
            'stats': {
                'walls': len(walls),
                'restricted': len(restricted_areas),
                'entrances': len(entrances),
                'open_spaces': len(open_spaces)
            }
        }
        
        # Store for later processing
        current_session['floor_plan_data'] = {
            'walls': walls,
            'restricted_areas': restricted_areas,
            'entrances': entrances,
            'open_spaces': open_spaces
        }
        current_session['dxf_path'] = tmp_path
        
        logger.info(f"Successfully parsed DXF: {result['stats']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error parsing DXF: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-floor-plan', methods=['POST'])
def process_floor_plan():
    """
    Process floor plan with îlot placement and corridor generation
    Requires: parsed DXF data in session
    """
    try:
        if not current_session['dxf_path']:
            return jsonify({'error': 'No DXF file loaded'}), 400
        
        # Get configuration from request
        config_data = request.json
        
        # Validate distribution
        dist = config_data['distribution']
        total_dist = dist['size_0_1'] + dist['size_1_3'] + dist['size_3_5'] + dist['size_5_10']
        
        if not (0.99 <= total_dist <= 1.01):
            return jsonify({'error': f'Distribution must sum to 100%, got {total_dist*100}%'}), 400
        
        # Create size configuration
        size_config = IlotSizeConfig(
            size_0_1_pct=dist['size_0_1'],
            size_1_3_pct=dist['size_1_3'],
            size_3_5_pct=dist['size_3_5'],
            size_5_10_pct=dist['size_5_10']
        )
        
        logger.info(f"Processing floor plan with {config_data['total_ilots']} îlots")
        
        # Process
        orchestrator = ProductionOrchestrator()
        result = orchestrator.process_floor_plan(
            dxf_file_path=current_session['dxf_path'],
            size_config=size_config,
            total_ilots=config_data['total_ilots'],
            corridor_width=config_data['corridor_width'],
            min_spacing=0.3
        )
        
        if not result.success:
            return jsonify({'error': result.error_message}), 500
        
        # Convert result to JSON format
        response = {
            'success': True,
            'processing_time': result.processing_time,
            'ilots': [
                {
                    'id': ilot.id,
                    'polygon': polygon_to_geojson(ilot.polygon),
                    'area': ilot.area,
                    'category': ilot.category,
                    'position': list(ilot.position),
                    'width': ilot.width,
                    'height': ilot.height,
                    'rotation': ilot.rotation
                }
                for ilot in result.ilots
            ],
            'corridors': [
                {
                    'id': corridor.id,
                    'polygon': polygon_to_geojson(corridor.polygon),
                    'width': corridor.width,
                    'length': corridor.length,
                    'connects_rows': list(corridor.connects_rows)
                }
                for corridor in result.corridors
            ],
            'walls': [polygon_to_geojson(w) for w in result.walls if w],
            'restricted_areas': [polygon_to_geojson(r) for r in result.restricted_areas if r],
            'entrances': [polygon_to_geojson(e) for e in result.entrances if e],
            'open_spaces': [polygon_to_geojson(s) for s in result.open_spaces if s],
            'total_area': result.total_area,
            'ilot_coverage_pct': result.ilot_coverage_pct,
            'corridor_coverage_pct': result.corridor_coverage_pct,
            'total_coverage_pct': result.total_coverage_pct,
            'placement_score': result.placement_score
        }
        
        logger.info(f"Successfully processed: {len(result.ilots)} îlots, {len(result.corridors)} corridors")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing floor plan: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/demo-data', methods=['GET'])
def get_demo_data():
    """
    Return demo data for testing
    """
    try:
        demo_file = Path('demo_floor_plan.dxf')
        
        if not demo_file.exists():
            return jsonify({'error': 'No demo data available'}), 404
        
        # Parse demo file
        orchestrator = ProductionOrchestrator()
        from core.production_cad_parser import ProductionCADParser
        
        parser = ProductionCADParser()
        walls, restricted_areas, entrances, open_spaces = parser.parse_dxf(str(demo_file))
        
        result = {
            'success': True,
            'walls': [polygon_to_geojson(w) for w in walls if w],
            'restricted_areas': [polygon_to_geojson(r) for r in restricted_areas if r],
            'entrances': [polygon_to_geojson(e) for e in entrances if e],
            'open_spaces': [polygon_to_geojson(s) for s in open_spaces if s],
            'total_area': sum(s.area for s in open_spaces if s),
            'ilots': [],
            'corridors': []
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error loading demo data: {e}")
        return jsonify({'error': 'Demo data not available'}), 404


@app.route('/api/export', methods=['POST'])
def export_result():
    """
    Export current result to various formats
    Supports: PDF, DXF, PNG, JSON
    """
    try:
        export_format = request.json.get('format', 'pdf')
        
        if not current_session['floor_plan_data']:
            return jsonify({'error': 'No data to export'}), 400
        
        # TODO: Implement export functionality
        # For now, return JSON
        
        return jsonify({
            'success': True,
            'format': export_format,
            'message': 'Export functionality coming soon'
        })
        
    except Exception as e:
        logger.error(f"Error exporting: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Advanced SDK Viewer API',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    import sys
    
    # Check if port is specified
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    logger.info(f"Starting Advanced SDK Viewer API on port {port}")
    logger.info("Access viewer at: http://localhost:{}/".format(port))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )
