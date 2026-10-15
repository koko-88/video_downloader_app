# Video Downloader

Desktop app for downloading videos and audio using **PySide6** and **yt-dlp**.

**Quick start (no terminal):** read [START_HERE.txt](START_HERE.txt) and double-click `BUILD_INSTALLER_DOUBLE_CLICK.bat`.

## Features

- Paste one or more `http://` or `https://` links (any site yt-dlp supports)
- Choose output folder, MP4 or MP3, and resolution (MP4 only)
- Sequential batch downloads with per-URL status table
- Cancel, retry failed, open download folder
- Silent YouTube cookie fallback (Edge → Chrome → Firefox) when sign-in/bot errors occur
- Config, history, and log files persisted under `data/` and `logs/`

## Requirements

- Windows 10+
- Python 3.10+ (for development)
- **FFmpeg** — required when you download MP3 or MP4 (merging/audio extract).  
  Place `ffmpeg.exe` in `tools/ffmpeg/` or install FFmpeg on PATH.  
  See [tools/README.txt](tools/README.txt).

## Development setup

```powershell
cd k:\video_downloader_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install --upgrade --pre yt-dlp
python main.py
```

## Build EXE

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install --upgrade --pre yt-dlp
python build_exe.py
```

Output: `dist\VideoDownloader\VideoDownloader.exe`

## Build Windows installer (setup EXE)

Install [Inno Setup 6](https://jrsoftware.org/isdl.php) (free), then:

```powershell
python build_exe.py
python build_installer.py
```

Output: `installer_output\VideoDownloader_Setup_1.0.0.exe`

Double-click that file on any PC to install (Program Files, Start Menu, uninstall entry). See [installer/README.txt](installer/README.txt).

Optional before build:

- `resources\icon.ico` — application icon
- `resources\loader.gif` — loading animation (otherwise busy cursor)
- `tools\ffmpeg\ffmpeg.exe` — bundle FFmpeg with the EXE

## Data locations

| Dev | Frozen EXE |
|-----|------------|
| `data/config.json` | `%LOCALAPPDATA%\VideoDownloader\config.json` |
| `data/history.json` | `%LOCALAPPDATA%\VideoDownloader\history.json` |
| `logs/app.log` | `%LOCALAPPDATA%\VideoDownloader\logs\app.log` |

## Legacy

Previous UI scaffold: `_backup/Youtube_downloader_old.py`

## Notes

- Unsigned PyInstaller builds may trigger antivirus warnings.
- Keep yt-dlp on the latest nightly: `pip install --upgrade --pre yt-dlp`
- YouTube may block anonymous downloads; sign in via Edge or Chrome and retry.
