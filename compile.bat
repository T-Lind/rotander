@echo off
REM Navigate to the directory containing the script
cd /d "%~dp0"

REM load the .venv python environment
call .venv\Scripts\activate

REM Run the PyInstaller command
pyinstaller --onefile --noconsole --hidden-import scipy.special._cdflib main.py

REM Notify user when done
echo Build process complete. Press any key to exit.
pause
