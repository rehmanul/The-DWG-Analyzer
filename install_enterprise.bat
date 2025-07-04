@echo off
echo ========================================
echo AI Architectural Space Analyzer PRO
echo Enterprise Edition Installation
echo ========================================
echo.

echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Installing additional enterprise libraries...
python -m pip install PyOpenGL PyOpenGL_accelerate
python -m pip install GDAL
python -m pip install rasterio[s3]
python -m pip install geopandas[all]

echo.
echo Setting up enterprise environment...
if not exist "temp" mkdir temp
if not exist "exports" mkdir exports
if not exist "projects" mkdir projects
if not exist "logs" mkdir logs

echo.
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\AI Architectural Analyzer PRO.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "%CD%\run.py" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> create_shortcut.vbs
echo oLink.Description = "AI Architectural Space Analyzer PRO - Enterprise Edition" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript create_shortcut.vbs
del create_shortcut.vbs

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo 1. Double-click the desktop shortcut, or
echo 2. Run: python run.py
echo.
echo Enterprise features enabled:
echo - Full DWG/DXF support
echo - Advanced AI algorithms
echo - Professional export options
echo - Database integration
echo - Multi-format support
echo.
pause