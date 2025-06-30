@echo off
echo Building AI Architectural Space Analyzer PRO Installer...
echo.

if not exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo ERROR: NSIS not found!
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    pause
    exit /b 1
)

echo Compiling installer without icons...
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

if %ERRORLEVEL% == 0 (
    echo.
    echo SUCCESS! Installer created: AI_Architectural_Analyzer_Setup.exe
    echo.
    echo INSTALLER FEATURES:
    echo - Professional installation wizard
    echo - Program Files installation
    echo - Start Menu shortcuts
    echo - Desktop shortcut option
    echo - File associations DWG/DXF
    echo - Add/Remove Programs entry
    echo - Complete uninstaller
    echo.
    echo READY TO DISTRIBUTE!
) else (
    echo.
    echo ERROR: Failed to create installer
)

pause