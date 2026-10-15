FFmpeg (required for MP3 extraction and MP4 stream merging)
================================================================

Place these files in this folder:

  tools/ffmpeg/ffmpeg.exe
  tools/ffmpeg/ffprobe.exe   (recommended)

Where to get FFmpeg (Windows):
  - https://www.gyan.dev/ffmpeg/builds/  (release essentials)
  - https://github.com/BtbN/FFmpeg-Builds/releases

Extract the zip and copy ffmpeg.exe (and ffprobe.exe) into tools/ffmpeg/.

Alternative: install FFmpeg and add it to your system PATH.

The app also searches PATH if tools/ffmpeg is empty.

For EXE builds, run build_exe.py after placing FFmpeg here if you want
FFmpeg bundled inside dist/VideoDownloader/.
