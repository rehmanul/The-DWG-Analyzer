#!/usr/bin/env python3
"""
Create Professional Windows Installer
Using NSIS (Nullsoft Scriptable Install System)
"""

import os
import subprocess
import shutil
from pathlib import Path

def create_nsis_script():
    """Create NSIS installer script"""
    nsis_script = '''
; AI Architectural Space Analyzer PRO Installer
; Professional Windows Installer

!define APPNAME "AI Architectural Space Analyzer PRO"
!define COMPANYNAME "Professional CAD Solutions"
!define DESCRIPTION "Professional architectural analysis software with AI capabilities"
!define VERSIONMAJOR 2
!define VERSIONMINOR 0
!define VERSIONBUILD 1
!define HELPURL "https://github.com/rehmanul/The-DWG-Analyzer"
!define UPDATEURL "https://github.com/rehmanul/The-DWG-Analyzer"
!define ABOUTURL "https://github.com/rehmanul/The-DWG-Analyzer"
!define INSTALLSIZE 524288  ; 512MB in KB

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES64\\${APPNAME}"
LicenseData "LICENSE.txt"
Name "${APPNAME}"
Icon "app_icon.ico"
outFile "AI_Architectural_Analyzer_Setup.exe"

!include LogicLib.nsh
!include MUI2.nsh

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "app_icon.ico"
!define MUI_UNICON "app_icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer_banner.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "installer_banner.bmp"

; Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Default installation section
Section "Core Application" SecCore
    SectionIn RO  ; Read-only, always installed
    
    SetOutPath $INSTDIR
    
    ; Main application files
    File "dist\\AI_Architectural_Analyzer_Functional.exe"
    File /r "src"
    File "README.md"
    File "requirements.txt"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\\${APPNAME}"
    CreateDirectory "$APPDATA\\${APPNAME}\\Projects"
    CreateDirectory "$APPDATA\\${APPNAME}\\Exports"
    CreateDirectory "$APPDATA\\${APPNAME}\\Templates"
    
    ; Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "QuietUninstallString" "$INSTDIR\\uninstall.exe /S"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayIcon" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; File associations for DWG/DXF files
    WriteRegStr HKCR ".dwg" "" "AI_Architectural_Analyzer.dwg"
    WriteRegStr HKCR ".dxf" "" "AI_Architectural_Analyzer.dxf"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dwg" "" "AutoCAD Drawing"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dxf" "" "AutoCAD Exchange Format"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dwg\\shell\\open\\command" "" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe \\"%1\\""
    WriteRegStr HKCR "AI_Architectural_Analyzer.dxf\\shell\\open\\command" "" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe \\"%1\\""
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

; Desktop shortcut section
Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe" "" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe" 0
SectionEnd

; Start Menu shortcuts section
Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe" "" "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe" 0
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe" "" "$INSTDIR\\uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\User Manual.lnk" "$INSTDIR\\README.md" "" "" 0
SectionEnd

; Sample files section
Section "Sample DWG Files" SecSamples
    SetOutPath "$INSTDIR\\Samples"
    File /r "sample_files\\*.*"
SectionEnd

; Section descriptions
LangString DESC_SecCore ${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create Start Menu shortcuts"
LangString DESC_SecSamples ${LANG_ENGLISH} "Install sample DWG/DXF files for testing"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecSamples} $(DESC_SecSamples)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
    DeleteRegKey HKCR ".dwg"
    DeleteRegKey HKCR ".dxf"
    DeleteRegKey HKCR "AI_Architectural_Analyzer.dwg"
    DeleteRegKey HKCR "AI_Architectural_Analyzer.dxf"
    
    ; Remove shortcuts
    Delete "$DESKTOP\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${APPNAME}\\*.*"
    RMDir "$SMPROGRAMS\\${APPNAME}"
    
    ; Remove files
    Delete "$INSTDIR\\AI_Architectural_Analyzer_Functional.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\requirements.txt"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir /r "$INSTDIR\\src"
    RMDir /r "$INSTDIR\\Samples"
    RMDir "$INSTDIR"
    
    ; Remove application data (ask user)
    MessageBox MB_YESNO "Do you want to remove user data and settings?" IDNO +3
    RMDir /r "$APPDATA\\${APPNAME}"
    
SectionEnd
'''
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    print("✅ NSIS script created: installer.nsi")

def create_license_file():
    """Create license file"""
    license_text = """AI Architectural Space Analyzer PRO
Professional License Agreement

Copyright (c) 2024 Professional CAD Solutions

This software is licensed for professional use.

FEATURES:
- Professional DWG/DXF analysis
- AI-powered room detection
- Construction planning tools
- BIM integration capabilities
- Advanced export options

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 1GB available disk space
- Internet connection for AI features

SUPPORT:
For technical support and updates, visit:
https://github.com/rehmanul/The-DWG-Analyzer

By installing this software, you agree to these terms.
"""
    
    with open("LICENSE.txt", "w") as f:
        f.write(license_text)
    
    print("✅ License file created: LICENSE.txt")

def create_installer_assets():
    """Create installer assets"""
    # Create simple icon if not exists
    if not os.path.exists("app_icon.ico"):
        print("⚠️ Creating placeholder icon...")
        # Create a simple text file as placeholder
        with open("app_icon.ico", "w") as f:
            f.write("ICON_PLACEHOLDER")
    
    # Create installer banner if not exists
    if not os.path.exists("installer_banner.bmp"):
        print("⚠️ Creating placeholder banner...")
        with open("installer_banner.bmp", "w") as f:
            f.write("BANNER_PLACEHOLDER")
    
    print("✅ Installer assets prepared")

def download_nsis():
    """Instructions to download NSIS"""
    print("""
🔧 TO BUILD THE INSTALLER:

1. Download NSIS (Nullsoft Scriptable Install System):
   https://nsis.sourceforge.io/Download

2. Install NSIS on your system

3. Right-click on 'installer.nsi' and select:
   "Compile NSIS Script"

4. This will create: AI_Architectural_Analyzer_Setup.exe

ALTERNATIVE - Command Line:
makensis installer.nsi
""")

def create_batch_builder():
    """Create batch file to build installer"""
    batch_content = '''@echo off
echo Building AI Architectural Space Analyzer PRO Installer...
echo.

if not exist "C:\\Program Files (x86)\\NSIS\\makensis.exe" (
    echo ERROR: NSIS not found!
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo.
    pause
    exit /b 1
)

echo Compiling installer...
"C:\\Program Files (x86)\\NSIS\\makensis.exe" installer.nsi

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
'''
    
    with open("build_installer.bat", "w") as f:
        f.write(batch_content)
    
    print("✅ Batch builder created: build_installer.bat")

def create_inno_setup_script():
    """Create Inno Setup script as alternative"""
    inno_script = '''
[Setup]
AppName=AI Architectural Space Analyzer PRO
AppVersion=2.0.1
AppPublisher=Professional CAD Solutions
AppPublisherURL=https://github.com/rehmanul/The-DWG-Analyzer
AppSupportURL=https://github.com/rehmanul/The-DWG-Analyzer
AppUpdatesURL=https://github.com/rehmanul/The-DWG-Analyzer
DefaultDirName={autopf}\\AI Architectural Space Analyzer PRO
DefaultGroupName=AI Architectural Space Analyzer PRO
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=.
OutputBaseFilename=AI_Architectural_Analyzer_Setup_InnoSetup
SetupIconFile=app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "associate"; Description: "Associate DWG and DXF files"; GroupDescription: "File associations:"

[Files]
Source: "dist\\AI_Architectural_Analyzer_Functional.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\\*"; DestDir: "{app}\\src"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "sample_files\\*"; DestDir: "{app}\\Samples"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCR; Subkey: ".dwg"; ValueType: string; ValueName: ""; ValueData: "AI_Architectural_Analyzer.dwg"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: ".dxf"; ValueType: string; ValueName: ""; ValueData: "AI_Architectural_Analyzer.dxf"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dwg"; ValueType: string; ValueName: ""; ValueData: "AutoCAD Drawing"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dxf"; ValueType: string; ValueName: ""; ValueData: "AutoCAD Exchange Format"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dwg\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: """{app}\\AI_Architectural_Analyzer_Functional.exe"" ""%1"""; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dxf\\shell\\open\\command"; ValueType: string; ValueName: ""; ValueData: """{app}\\AI_Architectural_Analyzer_Functional.exe"" ""%1"""; Tasks: associate

[Icons]
Name: "{group}\\AI Architectural Space Analyzer PRO"; Filename: "{app}\\AI_Architectural_Analyzer_Functional.exe"
Name: "{group}\\{cm:UninstallProgram,AI Architectural Space Analyzer PRO}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\AI Architectural Space Analyzer PRO"; Filename: "{app}\\AI_Architectural_Analyzer_Functional.exe"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\AI Architectural Space Analyzer PRO"; Filename: "{app}\\AI_Architectural_Analyzer_Functional.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\AI_Architectural_Analyzer_Functional.exe"; Description: "{cm:LaunchProgram,AI Architectural Space Analyzer PRO}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{userappdata}\\AI Architectural Space Analyzer PRO"
Name: "{userappdata}\\AI Architectural Space Analyzer PRO\\Projects"
Name: "{userappdata}\\AI Architectural Space Analyzer PRO\\Exports"
'''
    
    with open("installer_inno.iss", "w") as f:
        f.write(inno_script)
    
    print("✅ Inno Setup script created: installer_inno.iss")

def main():
    """Create complete installer package"""
    print("🚀 Creating Professional Windows Installer Package")
    print("=" * 60)
    
    # Create all installer files
    create_nsis_script()
    create_license_file()
    create_installer_assets()
    create_batch_builder()
    create_inno_setup_script()
    
    print("\n✅ INSTALLER PACKAGE CREATED!")
    print("\n📦 FILES CREATED:")
    print("• installer.nsi - NSIS installer script")
    print("• installer_inno.iss - Inno Setup script")
    print("• LICENSE.txt - Software license")
    print("• build_installer.bat - Build script")
    
    print("\n🔧 TO CREATE INSTALLER:")
    print("\nOPTION 1 - NSIS (Recommended):")
    print("1. Download NSIS: https://nsis.sourceforge.io/Download")
    print("2. Install NSIS")
    print("3. Double-click: build_installer.bat")
    print("4. Result: AI_Architectural_Analyzer_Setup.exe")
    
    print("\nOPTION 2 - Inno Setup:")
    print("1. Download Inno Setup: https://jrsoftware.org/isinfo.php")
    print("2. Install Inno Setup")
    print("3. Open installer_inno.iss in Inno Setup")
    print("4. Click Build > Compile")
    print("5. Result: AI_Architectural_Analyzer_Setup_InnoSetup.exe")
    
    print("\n🎯 INSTALLER FEATURES:")
    print("✅ Professional installation wizard")
    print("✅ Program Files installation")
    print("✅ Start Menu shortcuts")
    print("✅ Desktop shortcut (optional)")
    print("✅ File associations (DWG/DXF)")
    print("✅ Add/Remove Programs entry")
    print("✅ Complete uninstaller")
    print("✅ User data directories")
    print("✅ Registry entries")
    
    print("\n💪 PROFESSIONAL SOFTWARE INSTALLER READY!")

if __name__ == "__main__":
    main()