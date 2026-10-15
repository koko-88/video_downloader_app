@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title Video Downloader - Build Installer

set "ROOT=%~dp0"
set "LOGDIR=%ROOT%build_logs"
set "LOG=%LOGDIR%\installer_build.log"
set "INSTALLER=%ROOT%installer_output\VideoDownloader_Setup_1.0.0.exe"
set "DIST_EXE=%ROOT%dist\VideoDownloader\VideoDownloader.exe"
set "FAILED_STEP=unknown"
set "EXITCODE=0"

set "PIP_TRUST=--trusted-host pypi.org --trusted-host files.pythonhosted.org"
set "PIP_BASE=--no-cache-dir --retries 10 %PIP_TRUST%"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo. > "%LOG%"
echo ============================================================>> "%LOG%"
echo Video Downloader - Build started: %DATE% %TIME%>> "%LOG%"
echo Project: %ROOT%>> "%LOG%"
echo ============================================================>> "%LOG%"
echo.

call :logecho "============================================================"
call :logecho "  Video Downloader - Build App + Windows Installer"
call :logecho "============================================================"
call :logecho "Log file: %LOG%"
call :logecho ""

REM ---------- Inno Setup ----------
set "FAILED_STEP=Inno Setup detection"
set "ISCC="
echo Inno Setup ISCC.exe search:>> "%LOG%"

if defined INNO_SETUP_DIR (
    echo   [check] "%INNO_SETUP_DIR%\ISCC.exe">>"%LOG%"
    if exist "%INNO_SETUP_DIR%\ISCC.exe" set "ISCC=%INNO_SETUP_DIR%\ISCC.exe"
)

if not defined ISCC (
    echo   [check] PATH ISCC>> "%LOG%"
    where ISCC >nul 2>&1
    if not errorlevel 1 for /f "delims=" %%I in ('where ISCC 2^>nul') do if not defined ISCC set "ISCC=%%I"
    if defined ISCC echo   [FOUND] PATH: !ISCC!>> "%LOG%"
)

if not defined ISCC (
    call :logecho "Checking Inno Setup per-user install path..."
    if defined LOCALAPPDATA (
        echo   [check] "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe">>"%LOG%"
        if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
    )
)
if not defined ISCC (
    if defined LOCALAPPDATA (
        echo   [check] "%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe">>"%LOG%"
        if exist "%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe"
    )
)
if not defined ISCC (
    if defined USERNAME (
        echo   [check] "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe">>"%LOG%"
        if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe" set "ISCC=C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    )
)
if not defined ISCC (
    if defined USERNAME (
        echo   [check] "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 7\ISCC.exe">>"%LOG%"
        if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 7\ISCC.exe" set "ISCC=C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 7\ISCC.exe"
    )
)
if not defined ISCC (
    echo   [check] "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe">>"%LOG%"
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC (
    echo   [check] "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe">>"%LOG%"
    if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
)
if not defined ISCC (
    echo   [check] "%ProgramFiles%\Inno Setup 6\ISCC.exe">>"%LOG%"
    if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC (
    echo   [check] "%ProgramFiles%\Inno Setup 7\ISCC.exe">>"%LOG%"
    if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
)

if not defined ISCC (
    echo.>> "%LOG%"
    echo ERROR: Inno Setup not found.>> "%LOG%"
    call :fail "Inno Setup was not found. Install Inno Setup 6, then run BUILD_INSTALLER_DOUBLE_CLICK.bat again."
    start "" "https://jrsoftware.org/isdl.php"
    goto :end
)
echo   [FOUND] %ISCC%>> "%LOG%"
for %%D in ("%ISCC%") do set "INNO_SETUP_DIR=%%~dpD"
if defined INNO_SETUP_DIR set "INNO_SETUP_DIR=%INNO_SETUP_DIR:~0,-1%"
call :logecho "Inno Setup OK: %ISCC%"
call :logecho ""

REM ---------- Python ----------
set "FAILED_STEP=Python detection"
set "PYEXE="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3"
if not defined PYEXE (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PYEXE=python"
)
if not defined PYEXE (
    call :fail "Python was not found. Install Python and enable Add Python to PATH."
    goto :end
)
call :logecho "Python OK: %PYEXE%"
call :logecho ""

REM ---------- Virtual environment ----------
set "FAILED_STEP=Create virtual environment"
if not exist "%ROOT%.venv\Scripts\python.exe" (
    call :logecho "Creating .venv ..."
    %PYEXE% -m venv "%ROOT%.venv"
    if errorlevel 1 (
        call :fail "Failed to create .venv"
        goto :end
    )
)

set "FAILED_STEP=Activate virtual environment"
call "%ROOT%.venv\Scripts\activate.bat"
if errorlevel 1 (
    call :fail "Failed to activate .venv"
    goto :end
)

set "PY=%ROOT%.venv\Scripts\python.exe"
if not exist "%PY%" (
    call :fail "Missing .venv\Scripts\python.exe"
    goto :end
)
call :logecho "Using: %PY%"
call :logecho ""

REM ---------- pip (one package at a time, retries) ----------
set "FAILED_STEP=pip cache purge"
call :logecho "Purging pip cache..."
echo pip cache purge>> "%LOG%"
"%PY%" -m pip cache purge >> "%LOG%" 2>&1

set "FAILED_STEP=pip upgrade pip setuptools wheel"
call :logecho "Upgrading pip, setuptools, wheel..."
echo pip install --upgrade pip setuptools wheel>> "%LOG%"
"%PY%" -m pip install --upgrade pip setuptools wheel %PIP_BASE% --timeout 180 >> "%LOG%" 2>&1
if errorlevel 1 (
    call :fail "pip setuptools wheel upgrade failed. See log."
    goto :end
)
call :logecho "pip / setuptools / wheel OK."
call :logecho ""

set "FAILED_STEP=pip install PySide6"
call :logecho "Installing PySide6 (up to 3 attempts)..."
set "PKG_OK=0"
set "ATTEMPT=0"
:pyside6_loop
set /a ATTEMPT+=1
if !ATTEMPT! GTR 3 goto :pyside6_fail
if !ATTEMPT! GTR 1 call :logecho "Retrying PySide6 install attempt !ATTEMPT!/3..."
echo pip install PySide6 attempt !ATTEMPT!>> "%LOG%"
"%PY%" -m pip install PySide6 --prefer-binary %PIP_BASE% --timeout 300 >> "%LOG%" 2>&1
if not errorlevel 1 set "PKG_OK=1" & goto :pyside6_ok
goto :pyside6_loop
:pyside6_fail
if not "!PKG_OK!"=="1" (
    call :fail "PySide6 install failed after 3 attempts. See log."
    goto :end
)
:pyside6_ok
call :logecho "PySide6 OK."
call :logecho ""

set "FAILED_STEP=pip install --upgrade --pre yt-dlp"
call :logecho "Installing the latest yt-dlp nightly (up to 3 attempts)..."
set "PKG_OK=0"
set "ATTEMPT=0"
:ytdlp_loop
set /a ATTEMPT+=1
if !ATTEMPT! GTR 3 goto :ytdlp_fail
if !ATTEMPT! GTR 1 call :logecho "Retrying yt-dlp install attempt !ATTEMPT!/3..."
echo pip install --upgrade --pre yt-dlp attempt !ATTEMPT!>> "%LOG%"
"%PY%" -m pip install --upgrade --pre yt-dlp --prefer-binary %PIP_BASE% --timeout 180 >> "%LOG%" 2>&1
if not errorlevel 1 set "PKG_OK=1" & goto :ytdlp_ok
goto :ytdlp_loop
:ytdlp_fail
if not "!PKG_OK!"=="1" (
    call :fail "yt-dlp install failed after 3 attempts. See log."
    goto :end
)
:ytdlp_ok
call :logecho "yt-dlp nightly OK."
call :logecho ""

set "FAILED_STEP=pip install pyinstaller"
call :logecho "Installing pyinstaller (up to 3 attempts)..."
set "PKG_OK=0"
set "ATTEMPT=0"
:pyinstaller_loop
set /a ATTEMPT+=1
if !ATTEMPT! GTR 3 goto :pyinstaller_fail
if !ATTEMPT! GTR 1 call :logecho "Retrying pyinstaller install attempt !ATTEMPT!/3..."
echo pip install pyinstaller attempt !ATTEMPT!>> "%LOG%"
"%PY%" -m pip install pyinstaller --prefer-binary %PIP_BASE% --timeout 180 >> "%LOG%" 2>&1
if not errorlevel 1 set "PKG_OK=1" & goto :pyinstaller_ok
goto :pyinstaller_loop
:pyinstaller_fail
if not "!PKG_OK!"=="1" (
    call :fail "pyinstaller install failed after 3 attempts. See log."
    goto :end
)
:pyinstaller_ok
call :logecho "pyinstaller OK."
call :logecho "All dependencies installed."
call :logecho ""

REM ---------- PyInstaller ----------
set "FAILED_STEP=build_exe.py (PyInstaller)"
call :logecho "[1/2] Building application EXE..."
"%PY%" "%ROOT%build_exe.py" >> "%LOG%" 2>&1
if errorlevel 1 (
    call :fail "build_exe.py failed. See log."
    goto :end
)
if not exist "%DIST_EXE%" (
    call :fail "dist\VideoDownloader\VideoDownloader.exe was not created."
    goto :end
)
call :logecho "Application EXE OK."
call :logecho ""

REM ---------- Inno compiler ----------
set "FAILED_STEP=build_installer.py (Inno Setup)"
call :logecho "[2/2] Building Windows installer..."
set "INNO_SETUP_DIR=%INNO_SETUP_DIR%"
set "ISCC_LOG=%LOGDIR%\iscc_step.log"
echo.>> "%ISCC_LOG%"
echo build_installer.py started: %DATE% %TIME%>> "%ISCC_LOG%"
"%PY%" "%ROOT%build_installer.py" >> "%ISCC_LOG%" 2>&1
set "ISCC_PY_ERR=%ERRORLEVEL%"
type "%ISCC_LOG%" >> "%LOG%"
if not "%ISCC_PY_ERR%"=="0" (
    call :fail "build_installer.py failed. See log."
    goto :end
)

set "FAILED_STEP=Verify installer output"
if not exist "%INSTALLER%" (
    call :fail "Installer was not created: %INSTALLER%"
    goto :end
)

call :logecho ""
call :logecho "============================================================"
call :logecho "SUCCESS: Installer created."
call :logecho "Double click VideoDownloader_Setup_1.0.0.exe to install."
call :logecho "============================================================"
call :logecho ""
call :logecho "%INSTALLER%"
call :logecho ""

if not exist "%ROOT%installer_output" mkdir "%ROOT%installer_output"
start "" explorer "%ROOT%installer_output"
set "EXITCODE=0"
goto :end

:fail
set "EXITCODE=1"
call :logecho ""
call :logecho "============================================================"
call :logecho "BUILD FAILED"
call :logecho "Step: %FAILED_STEP%"
call :logecho "%~1"
call :logecho "============================================================"
call :logecho ""
call :logecho "Full log: %LOG%"
echo FAILED STEP: %FAILED_STEP%>> "%LOG%"
echo %~1>> "%LOG%"
goto :end

:logecho
set "MSG=%~1"
if defined MSG (
    echo !MSG!
    echo !MSG!>> "%LOG%"
)
exit /b 0

:end
echo.>> "%LOG%"
echo Build ended: %DATE% %TIME% exit=%EXITCODE%>> "%LOG%"
if "%EXITCODE%"=="1" (
    echo.
    echo Opening log in Notepad...
    start notepad "%LOG%"
)
echo.
echo Press any key to close this window...
pause >nul
exit /b %EXITCODE%
