[Setup]
AppName=AI Architectural Space Analyzer PRO
AppVersion=2.0.0
AppPublisher=AI Architecture Solutions
DefaultDirName={autopf}\AI Architectural Analyzer PRO
DefaultGroupName=AI Architectural Analyzer PRO
OutputDir=installer_output
OutputBaseFilename=AI_Architectural_Analyzer_PRO_Setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\AI_Architectural_Analyzer_FINAL.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AI Architectural Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_FINAL.exe"
Name: "{autodesktop}\AI Architectural Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_FINAL.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AI_Architectural_Analyzer_FINAL.exe"; Description: "Launch AI Architectural Analyzer PRO"; Flags: nowait postinstall skipifsilent