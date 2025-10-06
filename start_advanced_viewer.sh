#!/bin/bash

# Advanced SDK Viewer Startup Script
# Starts the Flask API server for the Three.js viewer

echo "=================================================="
echo "Advanced CAD SDK Viewer"
echo "Production-grade floor plan processing"
echo "=================================================="
echo ""

# Check Python version
python3 --version

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask, ezdxf, shapely, scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    pip3 install -r requirements_production.txt
fi

# Set default port
PORT="${1:-5000}"

echo ""
echo "Starting Advanced SDK Viewer API on port $PORT..."
echo "Access the viewer at: http://localhost:$PORT/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask server
python3 advanced_viewer_api.py $PORT
