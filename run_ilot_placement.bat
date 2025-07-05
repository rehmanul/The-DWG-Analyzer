@echo off
echo 🏗️ AI Îlot Placement PRO - Starting...
echo.
echo 📋 Client Requirements Implementation:
echo    • Zone detection by color (walls, restricted, entrances)
echo    • Proportional îlot placement (0-1m², 1-3m², 3-5m², 5-10m²)
echo    • Automatic corridor generation between rows
echo    • Constraint compliance (avoid red/blue zones)
echo.
echo 🌐 Opening application in browser...
echo 📍 URL: http://localhost:8502
echo.
python run_ilot_placement.py
pause