# VD-02 — Transcript Extraction & Export

**State:** product requirements captured; technical decisions pending repo-grounded planning. **Scope:** Windows PySide6 existing application.

## User scenarios / pass criteria

1. **Single-video URL:** recognized accessible video has captions; user can select languages/manual vs auto and formats, export content matching selected source and video ID.
2. **Playlist:** discover all available entries across pagination, record unavailable/deleted/private entries where discoverable, avoid duplicate downloads on repeat runs and produce coverage manifest.
3. **Channel /videos:** collect all accessible videos across pagination (not an RSS first page), preserve IDs, report discovered/attempted/completed/unavailable/failed/not-run counts and collection cutoff if any.
4. **Mixed URLs:** arbitrary number of supported links, deduplicate by site/video ID + chosen track, handle invalid/unsupported inputs individually rather than losing whole batch.
5. **Track selection:** manual and automatic captions considered independently; selected language prioritized predictably; availability and fallback reason shown.
6. **No caption:** clearly record missing captions and explain optional local ASR. Local ASR is automatic only if explicitly enabled and verified available; distinguish ASR text from native caption text.
7. **Export:** valid Unicode MD/TXT/JSON/SRT/VTT with timestamps where applicable, proper cue sequence and timing; select one or multiple types, deterministic naming and collision handling.
8. **Large archive:** progress per-video and batch, cancellation, failure isolation, checkpoints/resume and no duplicate completed output. Interrupted scans must not be labeled complete.
9. **Failures:** permissions, private/deleted videos, network throttling, geoblocking, timeout, unsupported extractor and partial results are distinct machine-readable states; human-readable report and retry failed only.
10. **Existing capability regression:** video/audio download, file format/quality, cookies fallback, queue and installer still function.
11. **Packaging:** installed Windows application performs the feature with declared dependencies. Missing optional ASR produces meaningful guidance, not crash.
12. **Security and privacy:** URL handling, filenames, subtitles, logs and local paths withstand malicious metadata; no unrequested uploads or credential leaks.

## Required technical questions (resolve with cited evidence in planning)

- Supported sites and exact behavior of each extractor, including YouTube playlists/channels/shorts/live; distinguish optional sites from claims of universal support.
- Which caption representation is canonical for deterministic conversion? How to avoid loss of timing/track metadata?
- UI model for transcript mode vs existing downloads, queue semantics, cancel/retry/progress and mixed sources.
- What available local ASR backend/models exist, whether redistributable, and how to bundle or configure without large unwanted C: writes.
- What does a complete discovery scan mean on dynamic/inaccessible channels? Define observable completion/pagination termination and partial-state classification.
- Runtime compatibility with packaged PyInstaller/Inno Setup and legal/usage obligations.

## Feature completion

Requirements have traceability to executable tests and verified evidence, including full paginated discovery fixture, track edge cases, serialization and conversion golden fixtures, partial/failure/cancel/resume, UI state controls, regression tests and Windows installer smoke. Independent review findings resolved; unresolved blocking dependencies remain BLOCKED, never assumed PASS.
