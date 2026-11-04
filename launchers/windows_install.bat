@echo off
REM One-time setup: creates venv, installs deps, adds a "Traffic meter" Start menu shortcut.
cd /d "%~dp0\.."
if not exist .venv ( py -3 -m venv .venv || python -m venv .venv )
call .venv\Scripts\python.exe -m pip install -q -r requirements.txt
set "TARGET=%CD%\.venv\Scripts\pythonw.exe"
set "ARGS=%CD%\traffic_meter.py"
set "LNK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Traffic meter.lnk"
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LNK%');$s.TargetPath='%TARGET%';$s.Arguments='\"%ARGS%\"';$s.WorkingDirectory='%CD%';$s.Save()"
echo Done. Search "Traffic meter" in Start; right-click to pin to taskbar.
pause
