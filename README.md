# Video Downloader

Windows desktop application built with PySide6 and yt-dlp for video/audio downloads and transcript extraction.

## Use the application

The Downloads tab supports MP4/WEBM video and MP3/M4A audio, quality selection, a sequential URL queue, cancellation, failed-job retry and history. A source rate limit stops further downloads; remaining jobs show a not-attempted reason and wait for explicit Retry failed. Video outputs are remuxed to the selected container where the source codecs permit; an incompatible conversion fails visibly rather than reporting another container as success.

The Transcripts tab accepts supported single videos, playlists, channel Videos archives and mixed URLs. Choose an export folder, exact language, manual/automatic track preference and any combination of TXT, Markdown, JSON, SRT and VTT. Extract / Resume reuses the same inputs and choices; Retry failed selectively retries failed records. Per-input discovery completeness is separate from per-video results. Provider restrictions and partial scans remain visible. Track inputs currently support VTT/SRT/JSON3.

A durable manifest records statuses, source identity, track provenance, output hashes and counts. Existing differing files are preserved. Keep the original inputs/choices to resume; public provenance removes sensitive or unknown query fields. Local speech recognition is optional and currently reports backend/model unavailable; there are no cloud calls or model downloads.

Use the latest verified installer and evidence paths in `specs/transcript-extraction/plan.md`. The installer supports its normal all-user mode and explicit `/CURRENTUSER` installation. Existing installed applications and older build outputs are not replaced by verification.

## Development

Windows 10+ is the verified target. The captured development environment is Python 3.14.3, PySide6 6.11.1 and the yt-dlp/EJS versions in `requirements.lock.txt`. That lock records the tested installed environment; a clean reinstall has not been claimed. `requirements.txt` remains the dependency declaration. Dependency installation or upgrades are separate operator actions.

```powershell
.venv/Scripts/python.exe main.py
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe scripts/feature_loop.py next --run-checks
```

If existing bytecode has different ownership, set `PYTHONPYCACHEPREFIX` to a fresh directory under `build_logs` rather than deleting user files. The default suite skips the external YouTube smoke; enable `RUN_YOUTUBE_SMOKE=1` explicitly for that network check.

## Build and verify

Stage FFmpeg, FFprobe and a supported JavaScript runtime with their vendor licenses as described in `tools/README.txt`. Local runtime versions/hashes are recorded in `tools/runtime-provenance.json`. Node must be explicitly enabled for yt-dlp; the application resolves its bundled runtime and keeps remote component downloads disabled.

Choose fresh destinations; build scripts refuse collisions instead of removing older outputs:

```powershell
.venv/Scripts/python.exe build_exe.py --output-root build_logs/release-example
.venv/Scripts/python.exe build_installer.py --source-dir build_logs/release-example/dist/VideoDownloader --output-dir build_logs/installer-example
```

The second command needs an existing Inno Setup compiler. The output is `VideoDownloader_Setup_1.0.0.exe` in the selected installer folder. See the compiler vendor's current licensing terms; the build scripts do not install tools or open download pages.

Run the actual source or frozen application diagnostic with isolated settings/history and temporary fixture outputs:

```powershell
.venv/Scripts/python.exe main.py --smoke-report build_logs/source-smoke.json
build_logs/release-example/dist/VideoDownloader/VideoDownloader.exe --smoke-report build_logs/frozen-smoke.json
```

Adding `--download-url <authorized public video URL>` exercises a real download through the UI/queue. Each report declares the actual runtime paths, frozen state, GUI platform and results. Offline fixture success cannot certify live archive coverage, installer behavior or human acceptance.

## Data and verification ownership

Development settings/history use `data/`, logs use `logs/`. Installed builds use `%LOCALAPPDATA%/VideoDownloader`. The uninstaller removes its installed files without recursively deleting user-added tools/files.

`PRODUCT.md` and `ROADMAP.md` own scope; `specs/transcript-extraction/` owns the feature contract/design/tasks. `LOGIC_VERIFICATION.md`, `IMPLEMENTATION_VERIFICATION.md` and `docs/verification/acceptance.md` own validation. Current exact results and remaining release gates are in the feature plan. The ProductShape recovery/refinement container is a draft proposal and does not replace the accepted product authorities.
