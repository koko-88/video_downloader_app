@echo off
set "APP=%ProgramFiles%\Video Downloader\VideoDownloader.exe"
if exist "%APP%" (
    start "" "%APP%"
    exit /b 0
)
echo App is not installed yet. Run installer_output\VideoDownloader_Setup_1.0.0.exe first.
echo.
pause
exit /b 1
