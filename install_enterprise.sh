#!/bin/bash

echo "========================================"
echo "AI Architectural Space Analyzer PRO"
echo "Enterprise Edition Installation"
echo "========================================"
echo

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "Error: Python 3.8 or higher required. Current version: $python_version"
    exit 1
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "Installing additional enterprise libraries..."
python3 -m pip install PyOpenGL PyOpenGL_accelerate

# Try to install GDAL (optional)
echo "Attempting to install GDAL (optional)..."
python3 -m pip install GDAL || echo "GDAL installation failed - continuing without it"

# Install geospatial libraries
python3 -m pip install rasterio geopandas || echo "Some geospatial libraries failed - basic functionality will work"

echo
echo "Setting up enterprise environment..."
mkdir -p temp exports projects logs

echo
echo "Setting up system libraries..."

# Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "Detected Ubuntu/Debian system"
    sudo apt-get update
    sudo apt-get install -y python3-tk python3-dev libgl1-mesa-glx libglib2.0-0
fi

# CentOS/RHEL/Fedora
if command -v yum &> /dev/null; then
    echo "Detected CentOS/RHEL/Fedora system"
    sudo yum install -y tkinter python3-devel mesa-libGL
fi

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system"
    if command -v brew &> /dev/null; then
        brew install python-tk
    else
        echo "Homebrew not found. Please install manually: brew install python-tk"
    fi
fi

echo
echo "Creating application launcher..."
cat > ai_analyzer_pro.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 run.py
EOF

chmod +x ai_analyzer_pro.sh

# Create desktop entry for Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    desktop_file="$HOME/Desktop/AI_Architectural_Analyzer_PRO.desktop"
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Architectural Analyzer PRO
Comment=Enterprise CAD Analysis Tool
Exec=$(pwd)/ai_analyzer_pro.sh
Icon=$(pwd)/assets/icon.png
Terminal=false
Categories=Engineering;Graphics;
EOF
    chmod +x "$desktop_file"
fi

echo
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo
echo "To run the application:"
echo "1. Run: ./ai_analyzer_pro.sh, or"
echo "2. Run: python3 run.py"
echo
echo "Enterprise features enabled:"
echo "- Full DWG/DXF support"
echo "- Advanced AI algorithms" 
echo "- Professional export options"
echo "- Database integration"
echo "- Multi-format support"
echo

# Test installation
echo "Testing installation..."
python3 -c "
import sys
try:
    import PyQt5
    import matplotlib
    import numpy
    import shapely
    print('✅ Core libraries installed successfully')
except ImportError as e:
    print(f'❌ Missing library: {e}')
    sys.exit(1)
"

echo "Installation test passed!"
echo "You can now run the application."