Windows installer (Inno Setup)
==============================

This folder contains VideoDownloader.iss — a script that builds a normal
Windows setup program (.exe) you can double-click to install the app.

Prerequisites
-------------
1. Build the app once:
     python build_exe.py

2. Use an existing Inno Setup 6/7 compiler (review current vendor licensing):
     https://jrsoftware.org/isdl.php

   Default compiler path:
     C:\Program Files (x86)\Inno Setup 6\ISCC.exe

Build the installer
-------------------
From the project root:

  python build_installer.py

Output:

  installer_output\VideoDownloader_Setup_1.0.0.exe

Install on your PC
------------------
Run the setup EXE. It will:
  - Install under Program Files\Video Downloader
  - Add Start Menu shortcut
  - Optional desktop shortcut (checkbox in wizard)
  - Register uninstaller in Windows Settings -> Apps

Optional
--------
- Add resources\icon.ico before building for setup icon
- Bundle tools\ffmpeg\ffmpeg.exe before build_exe.py to include FFmpeg

Safe verification/build destinations
-----------------------------------
Build scripts preserve existing files. Prefer a fresh build_exe.py --output-root and an explicit matching build_installer.py --source-dir / --output-dir; exact verified paths are in specs/transcript-extraction/plan.md.

The normal installer remains all-user. /CURRENTUSER selects per-user mode for an explicitly isolated acceptance run or installation. Use /DIR only with a new intended target, and verify no existing matching per-user uninstall registration will be overwritten. /NOICONS and an empty /TASKS avoid shortcut changes during isolated acceptance. The uninstaller does not recursively remove user-added files under tools/.
