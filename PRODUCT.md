# Video Downloader — Product Authority

## Existing product (observed in published main, 2026-10-15)
Windows PySide6 app, yt-dlp downloader, MP4/WEBM video and MP3/M4A audio, multi-URL input, sequential queue, cancellation and retry, output folder selection, quality options, browser-cookie fallback, history/logging, PyInstaller and Inno Setup installers. Local worktree can differ; verify before changes.

## Product goal
Users can enter any **supported** media/video/playlist/channel URL or combination, discover all accessible matching videos (including pagination where available), collect provided human/automatic captions, optionally derive transcripts from accessible audio using a verified local speech-to-text backend when no captions are available, and export in user-selected formats without downloading finished media unnecessarily.

## User outcomes
- Single video; full playlist; complete accessible channel Videos archive; mixed/bulk URLs.
- Accurate count and provenance of discovered, processed, failed, unavailable and not-attempted videos. Never claim a whole channel was processed if only first feed page was returned.
- Choice of language and manual/automatic track precedence, with transparent unsupported languages and duplicates.
- SRT, VTT, TXT, Markdown, JSON as selectable exports **when semantically applicable**, with timestamp/cue preservation and correct Unicode. No promises of identical semantics across plain-text and timed subtitle formats.
- Progress, cancellation, resume, idempotent retries, per-video results, durable manifest, appropriate filenames and organized outputs.
- Existing video/audio download flows continue working as before.

## Explicit requirements boundaries
- 'Any URL' means URLs supported by identified and verified extractors, with clear unsupported errors; not arbitrary webpages.
- A video may have unavailable captions; that state is distinct from extractor errors, network errors, blocked content and missing language tracks.
- Speech-to-text is a distinct optional processing mode and requires a verified installed backend, model and local resources. Don't silently invoke cloud transcription or billable services.
- Respect site access limits, copyright and user permissions; don't bypass DRM or access controls.
- No remote upload, user account login, new spending or automated publishing without user authorization.
- Avoid duplicate transcripts on retries; retain source video ID/URL/track and acquisition method.
- Windows 10 desktop runtime and distributable installer are acceptance targets; large speech models need a deliberate packaging/storage policy.

## Release success
Product scenarios in `specs/transcript-extraction/spec.md` and `docs/verification/acceptance.md` pass against the actual installed runtime, with a verified inventory-vs-results crosswalk, unchanged original download behavior, and successful Windows packaging verification. Partial or offline results must be explicitly stated.