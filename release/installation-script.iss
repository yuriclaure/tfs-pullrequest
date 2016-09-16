#define MyAppName "Codereview"
#define MyAppVersion "1.0"
#define MyAppPublisher "Yuri Claure"
#define MyAppExeName "Codereview Installer"
#define MyDefaultDirName "{pf}\Codereview"

[Files]
Source: cr\*; DestDir: {app}; Flags: overwritereadonly recursesubdirs createallsubdirs

[Setup]
AppId={{444B4311-848B-4EA8-B743-51DE98FF6700}
OutputDir=.
AppName={#MyAppName}
AppPublisher={#MyAppPublisher}
DefaultDirName={#MyDefaultDirName}
AppVersion={#MyAppVersion}
OutputBaseFilename={#MyAppExeName}

[Registry]
Root: HKLM; Subkey: SYSTEM\CurrentControlSet\Control\Session Manager\Environment; \
    ; ValueType: expandsz; ValueName: Path; ValueData: "{olddata};{#MyDefaultDirName}"; \
    ; Check: NeedsAddPath('{#MyDefaultDirName}')

[Code]

function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  // look for the path with leading and trailing semicolon
  // Pos() returns 0 if not found
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;
