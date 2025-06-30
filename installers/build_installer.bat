@echo off
echo Building AI Architectural Space Analyzer PRO Installer...
echo.

if not exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo ERROR: NSIS not found!
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo.
    pause
    exit /b 1
)

echo Compiling installer...
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ SUCCESS! Installer created: AI_Architectural_Analyzer_Setup.exe
    echo.
    echo The installer includes:
    echo - Professional installation wizard
    echo - Start Menu shortcuts
    echo - Desktop shortcut
    echo - File associations for DWG/DXF
    echo - Add/Remove Programs entry
    echo - Complete uninstaller
    echo.
) else (
    echo.
    echo ❌ ERROR: Failed to create installer
    echo.
)

pause
