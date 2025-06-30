
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
InstallDir "$PROGRAMFILES64\${APPNAME}"
LicenseData "LICENSE.txt"
Name "${APPNAME}"
outFile "AI_Architectural_Analyzer_Setup.exe"

!include LogicLib.nsh
!include MUI2.nsh

; Modern UI Configuration
!define MUI_ABORTWARNING

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
    File "dist\AI_Architectural_Analyzer_Functional.exe"
    File /r "src"
    File "README.md"
    File "requirements.txt"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\${APPNAME}"
    CreateDirectory "$APPDATA\${APPNAME}\Projects"
    CreateDirectory "$APPDATA\${APPNAME}\Exports"
    CreateDirectory "$APPDATA\${APPNAME}\Templates"
    
    ; Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; File associations for DWG/DXF files
    WriteRegStr HKCR ".dwg" "" "AI_Architectural_Analyzer.dwg"
    WriteRegStr HKCR ".dxf" "" "AI_Architectural_Analyzer.dxf"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dwg" "" "AutoCAD Drawing"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dxf" "" "AutoCAD Exchange Format"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dwg\shell\open\command" "" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe \"%1\""
    WriteRegStr HKCR "AI_Architectural_Analyzer.dxf\shell\open\command" "" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe \"%1\""
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Desktop shortcut section
Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe" "" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe" 0
SectionEnd

; Start Menu shortcuts section
Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe" "" "$INSTDIR\AI_Architectural_Analyzer_Functional.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\User Manual.lnk" "$INSTDIR\README.md" "" "" 0
SectionEnd

; Sample files section
Section "Sample DWG Files" SecSamples
    SetOutPath "$INSTDIR\Samples"
    File /r "sample_files\*.*"
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
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCR ".dwg"
    DeleteRegKey HKCR ".dxf"
    DeleteRegKey HKCR "AI_Architectural_Analyzer.dwg"
    DeleteRegKey HKCR "AI_Architectural_Analyzer.dxf"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\*.*"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Remove files
    Delete "$INSTDIR\AI_Architectural_Analyzer_Functional.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR\src"
    RMDir /r "$INSTDIR\Samples"
    RMDir "$INSTDIR"
    
    ; Remove application data (ask user)
    MessageBox MB_YESNO "Do you want to remove user data and settings?" IDNO +3
    RMDir /r "$APPDATA\${APPNAME}"
    
SectionEnd
