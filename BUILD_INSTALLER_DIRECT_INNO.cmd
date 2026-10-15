@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Video Downloader - Direct Inno Build

set "ROOT=%~dp0"
set "LOGDIR=%ROOT%build_logs"
set "LOG=%LOGDIR%\direct_installer_build.log"
set "ISCC_EXE=C:\Users\kerol\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
set "INNO_DIR=C:\Users\kerol\AppData\Local\Programs\Inno Setup 6"
set "DIST_EXE=%ROOT%dist\VideoDownloader\VideoDownloader.exe"
set "INSTALLER=%ROOT%installer_output\VideoDownloader_Setup_1.0.0.exe"
set "ISS=%ROOT%installer\VideoDownloader.iss"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo ============================================================ > "%LOG%"
echo Direct Inno build started: %DATE% %TIME% >> "%LOG%"
echo Project: %ROOT% >> "%LOG%"
echo ISCC: %ISCC_EXE% >> "%LOG%"
echo ============================================================ >> "%LOG%"

echo.
echo ============================================================
echo   Video Downloader - Direct Inno Build
echo ============================================================
echo Log: %LOG%
echo.

REM --- Inno Setup (fixed path) ---
if not exist "%ISCC_EXE%" (
    echo ISCC.exe was not found at the expected path
    echo   %ISCC_EXE%
    echo ISCC.exe was not found at the expected path>> "%LOG%"
    echo Path checked: %ISCC_EXE%>> "%LOG%"
    if exist "%INNO_DIR%" start "" explorer "%INNO_DIR%"
    goto :failed
)
echo Inno Setup OK: %ISCC_EXE%
echo Inno Setup OK: %ISCC_EXE%>> "%LOG%"
echo.

REM --- Python ---
set "PYEXE="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3"
if not defined PYEXE (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PYEXE=python"
)
if not defined PYEXE (
    echo Python was not found. Install Python and enable Add Python to PATH.
    echo Python was not found.>> "%LOG%"
    goto :failed
)
echo Python OK: %PYEXE%
echo Python OK: %PYEXE%>> "%LOG%"
echo.

REM --- Virtual environment ---
if not exist "%ROOT%.venv\Scripts\python.exe" (
    echo Creating .venv ...
    echo Creating .venv ...>> "%LOG%"
    %PYEXE% -m venv "%ROOT%.venv" >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo Failed to create .venv
        echo Failed to create .venv>> "%LOG%"
        goto :failed
    )
)

call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate .venv
    echo Failed to activate .venv>> "%LOG%"
    goto :failed
)

set "PY=%ROOT%.venv\Scripts\python.exe"
echo Using: %PY%
echo Using: %PY%>> "%LOG%"
echo.

echo Upgrading pip...
echo Upgrading pip...>> "%LOG%"
"%PY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 echo pip upgrade warning - continuing...

echo Installing requirements...
echo Installing requirements...>> "%LOG%"
"%PY%" -m pip install -r "%ROOT%requirements.txt" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo requirements.txt install failed.
    echo requirements.txt install failed.>> "%LOG%"
    goto :failed
)

echo Updating yt-dlp to the latest nightly...
echo pip install --upgrade --pre yt-dlp>> "%LOG%"
"%PY%" -m pip install --upgrade --pre yt-dlp >> "%LOG%" 2>&1
if errorlevel 1 (
    echo yt-dlp nightly update failed.
    echo yt-dlp nightly update failed.>> "%LOG%"
    goto :failed
)
echo.

echo [1/2] Building application (PyInstaller)...
echo [1/2] build_exe.py>> "%LOG%"
"%PY%" "%ROOT%build_exe.py" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo build_exe.py failed.
    echo build_exe.py failed.>> "%LOG%"
    goto :failed
)

if not exist "%DIST_EXE%" (
    echo PyInstaller EXE was not created
    echo   %DIST_EXE%
    echo PyInstaller EXE was not created: %DIST_EXE%>> "%LOG%"
    goto :failed
)
echo Application EXE OK: %DIST_EXE%
echo Application EXE OK>> "%LOG%"
echo.

echo [2/2] Building installer (Inno Setup)...
echo [2/2] ISCC compile>> "%LOG%"
echo Command: cd installer ^& "%ISCC_EXE%" VideoDownloader.iss>> "%LOG%"
pushd "%ROOT%installer"
"%ISCC_EXE%" "VideoDownloader.iss" >> "%LOG%" 2>&1
set "ISCC_ERR=%ERRORLEVEL%"
popd
if not "%ISCC_ERR%"=="0" (
    echo ISCC failed.
    echo ISCC failed.>> "%LOG%"
    goto :failed
)

if not exist "%INSTALLER%" (
    echo Installer was not created:
    echo   %INSTALLER%
    echo Installer missing: %INSTALLER%>> "%LOG%"
    goto :failed
)

echo.
echo ============================================================
echo   SUCCESS: Installer created. Double click VideoDownloader_Setup_1.0.0.exe
echo ============================================================
echo.
echo %INSTALLER%
echo SUCCESS>> "%LOG%"
echo %INSTALLER%>> "%LOG%"

if not exist "%ROOT%installer_output" mkdir "%ROOT%installer_output"
start "" explorer "%ROOT%installer_output"

echo Build finished OK. Press any key to close...
pause >nul
exit /b 0

:failed
echo.
echo ============================================================
echo   BUILD FAILED - see log
echo ============================================================
echo %LOG%
echo.
start notepad "%LOG%"
echo Press any key to close...
pause >nul
exit /b 1
