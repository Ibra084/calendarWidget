@echo off
REM Builds a standalone TimetableWidget.exe (no Python install needed to run it).
REM Run this on Windows, from this folder, with Python installed.

python -m pip install --upgrade pyinstaller
python -m PyInstaller --onefile --windowed --name TimetableWidget widget.py

echo.
echo Done. Find TimetableWidget.exe in the dist\ folder.
pause
