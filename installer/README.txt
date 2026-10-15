Windows installer (Inno Setup)
==============================

This folder contains VideoDownloader.iss — a script that builds a normal
Windows setup program (.exe) you can double-click to install the app.

Prerequisites
-------------
1. Build the app once:
     python build_exe.py

2. Install Inno Setup 6 (free):
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
