LOCAL RUNTIMES FOR WINDOWS DELIVERY
==================================

Downloads need FFmpeg/FFprobe. YouTube also needs a supported JavaScript runtime and the matching installed yt-dlp-ejs package. Caption-only export requires neither rendered media nor FFmpeg.

Stage authorized existing runtime files before a production build:
  tools/ffmpeg/ffmpeg.exe
  tools/ffmpeg/ffprobe.exe
  tools/ffmpeg/LICENSE.txt
  tools/ffmpeg/README-distribution.txt
  tools/javascript/node.exe
  tools/javascript/LICENSE.txt

The current local copies are FFmpeg/FFprobe 9.0.2 (Gyan full build) and Node 24.19.0. tools/runtime-provenance.json records exact hashes, vendor sources and the successful official Node checksum comparison. Binaries are ignored by Git; vendor notices are retained and bundled. These are copied local runtime files, not a global installation.

FFmpeg links from its upstream download page:
  https://ffmpeg.org/download.html
  https://www.gyan.dev/ffmpeg/builds/
Node release and license:
  https://nodejs.org/dist/v24.19.0/
  https://raw.githubusercontent.com/nodejs/node/v24.19.0/LICENSE

The app prefers bundled runtimes, otherwise existing supported PATH runtimes. It explicitly enables the selected Deno/Node path and disables remote EJS-component downloads. There are no automatic dependency installs, browser account changes or speech-model downloads.

ProductShape is a separate development-only local CLI at tools/productshape/node_modules/.bin/prodshape.cmd, pinned to 0.22.0 by its package-lock.json. It is not bundled with the desktop application. A fresh tool installation requires operator authorization; npm install scripts were disabled in this task.
