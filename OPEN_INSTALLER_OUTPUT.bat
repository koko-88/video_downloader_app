@echo off
cd /d "%~dp0"
if not exist "installer_output" mkdir "installer_output"
start "" explorer "%~dp0installer_output"
echo Opened installer_output folder.
pause
