; Inno Setup — packages PyInstaller onedir output (build-time only).
; Run: BUILD_INSTALLER_DOUBLE_CLICK.bat

#define MyAppName "Video Downloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Video Downloader"
#define MyAppExeName "VideoDownloader.exe"

; Paths relative to this .iss file (installer\)
#ifndef BuildSource
#define BuildSource "..\dist\VideoDownloader"
#endif
#ifndef BuildOutput
#define BuildOutput "..\installer_output"
#endif

[Setup]
AppId={{A7B3C9E1-4F2D-4A8B-9C0E-1D5E6F7A8B9C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir={#BuildOutput}
OutputBaseFilename=VideoDownloader_Setup_{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

#ifexist "..\resources\icon.ico"
SetupIconFile=..\resources\icon.ico
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; All PyInstaller onedir files (build machine must have dist\VideoDownloader before compiling)
Source: "{#BuildSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"
