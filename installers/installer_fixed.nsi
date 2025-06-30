; AI Architectural Space Analyzer PRO Installer
!define APPNAME "AI Architectural Space Analyzer PRO"
!define COMPANYNAME "Professional CAD Solutions"
!define DESCRIPTION "Professional architectural analysis software"
!define VERSIONMAJOR 2
!define VERSIONMINOR 0
!define VERSIONBUILD 1

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES64\${APPNAME}"
LicenseData "LICENSE.txt"
Name "${APPNAME}"
outFile "AI_Architectural_Analyzer_Setup.exe"

!include LogicLib.nsh
!include MUI2.nsh

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Core Application" SecCore
    SectionIn RO
    
    SetOutPath $INSTDIR
    
    File "dist\AI_Architectural_Analyzer_WebFeatures.exe"
    File /r "src"
    File "README.md"
    File "requirements.txt"
    
    CreateDirectory "$APPDATA\${APPNAME}"
    CreateDirectory "$APPDATA\${APPNAME}\Projects"
    CreateDirectory "$APPDATA\${APPNAME}\Exports"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    
    WriteRegStr HKCR ".dwg" "" "AI_Architectural_Analyzer.dwg"
    WriteRegStr HKCR ".dxf" "" "AI_Architectural_Analyzer.dxf"
    WriteRegStr HKCR "AI_Architectural_Analyzer.dwg\shell\open\command" "" "$INSTDIR\AI_Architectural_Analyzer_WebFeatures.exe $\"%1$\""
    WriteRegStr HKCR "AI_Architectural_Analyzer.dxf\shell\open\command" "" "$INSTDIR\AI_Architectural_Analyzer_WebFeatures.exe $\"%1$\""
    
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\AI_Architectural_Analyzer_WebFeatures.exe"
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\AI_Architectural_Analyzer_WebFeatures.exe"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

LangString DESC_SecCore ${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create Start Menu shortcuts"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCR ".dwg"
    DeleteRegKey HKCR ".dxf"
    DeleteRegKey HKCR "AI_Architectural_Analyzer.dwg"
    DeleteRegKey HKCR "AI_Architectural_Analyzer.dxf"
    
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\*.*"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    Delete "$INSTDIR\AI_Architectural_Analyzer_WebFeatures.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR\src"
    RMDir "$INSTDIR"
SectionEnd