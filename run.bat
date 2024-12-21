@echo off
REM Get the current directory of the batch script
set GAME_ROOT=%~dp0

REM Run the executable
start "" "%~dp0main.exe"
