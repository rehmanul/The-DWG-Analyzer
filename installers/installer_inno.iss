
[Setup]
AppName=AI Architectural Space Analyzer PRO
AppVersion=2.0.1
AppPublisher=Professional CAD Solutions
AppPublisherURL=https://github.com/rehmanul/The-DWG-Analyzer
AppSupportURL=https://github.com/rehmanul/The-DWG-Analyzer
AppUpdatesURL=https://github.com/rehmanul/The-DWG-Analyzer
DefaultDirName={autopf}\AI Architectural Space Analyzer PRO
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
Source: "dist\AI_Architectural_Analyzer_Functional.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "sample_files\*"; DestDir: "{app}\Samples"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCR; Subkey: ".dwg"; ValueType: string; ValueName: ""; ValueData: "AI_Architectural_Analyzer.dwg"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: ".dxf"; ValueType: string; ValueName: ""; ValueData: "AI_Architectural_Analyzer.dxf"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dwg"; ValueType: string; ValueName: ""; ValueData: "AutoCAD Drawing"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dxf"; ValueType: string; ValueName: ""; ValueData: "AutoCAD Exchange Format"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dwg\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\AI_Architectural_Analyzer_Functional.exe"" ""%1"""; Tasks: associate
Root: HKCR; Subkey: "AI_Architectural_Analyzer.dxf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\AI_Architectural_Analyzer_Functional.exe"" ""%1"""; Tasks: associate

[Icons]
Name: "{group}\AI Architectural Space Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_Functional.exe"
Name: "{group}\{cm:UninstallProgram,AI Architectural Space Analyzer PRO}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AI Architectural Space Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_Functional.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\AI Architectural Space Analyzer PRO"; Filename: "{app}\AI_Architectural_Analyzer_Functional.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\AI_Architectural_Analyzer_Functional.exe"; Description: "{cm:LaunchProgram,AI Architectural Space Analyzer PRO}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{userappdata}\AI Architectural Space Analyzer PRO"
Name: "{userappdata}\AI Architectural Space Analyzer PRO\Projects"
Name: "{userappdata}\AI Architectural Space Analyzer PRO\Exports"
