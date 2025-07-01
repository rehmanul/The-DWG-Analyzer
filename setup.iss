[Setup]
AppName=AI Architectural Space Analyzer PRO
AppVersion=2.0.0
AppPublisher=AI Architecture Solutions
AppPublisherURL=https://the-dwg-analyzer.streamlit.app
DefaultDirName={autopf}\AI Architectural Analyzer PRO
DefaultGroupName=AI Architectural Analyzer PRO
OutputDir=installer_output
OutputBaseFilename=AI_Architectural_Analyzer_PRO_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\app_icon.ico
WizardImageFile=assets\wizard.bmp
WizardSmallImageFile=assets\wizard_small.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "dist\AI_Architectural_Analyzer_FINAL.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "sample_files\*"; DestDir: "{app}\samples"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AI Architectural Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_FINAL.exe"
Name: "{group}\{cm:UninstallProgram,AI Architectural Analyzer PRO}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AI Architectural Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_FINAL.exe"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".dwg"; ValueType: string; ValueName: ""; ValueData: "AI.ArchitecturalFile"
Root: HKCR; Subkey: ".dxf"; ValueType: string; ValueName: ""; ValueData: "AI.ArchitecturalFile"
Root: HKCR; Subkey: "AI.ArchitecturalFile"; ValueType: string; ValueName: ""; ValueData: "Architectural Drawing File"
Root: HKCR; Subkey: "AI.ArchitecturalFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\AI_Architectural_Analyzer_FINAL.exe"" ""%1"""

[Run]
Filename: "{app}\AI_Architectural_Analyzer_FINAL.exe"; Description: "{cm:LaunchProgram,AI Architectural Analyzer PRO}"; Flags: nowait postinstall skipifsilent