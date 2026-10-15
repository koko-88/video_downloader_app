# Engineering verification — Video Downloader

Single project-level owner for native Python, PySide6, yt-dlp, queue, packaging, operational safety, regression and independent code review. The per-feature acceptance inventory lives in `docs/verification/acceptance.md`.

## Existing, sourced commands

From repository root on Windows, using the already-existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

If `.venv` or a declared dependency is missing, record BLOCKED and request installation permission instead of creating a new environment or silently installing. The known `tests/test_youtube_smoke.py` normally skips live-network testing unless `RUN_YOUTUBE_SMOKE` is explicitly enabled: report SKIPPED/NOT_RUN, not PASS.

For each VD-02 task, run targeted deterministic tests plus the existing suite after changes; add real validation for channel pagination/termination, subtitles, formats, cancellation/resume, queue/UI state and corrupted/missing media. Verify fixture assertions against required behavior, not only pass counts.

## Packaging

Existing build entrypoints are `build_exe.py` and `build_installer.py`. Build scripts can delete/recreate `build/` and `dist/`; first inspect local outputs and obtain permission if they could contain user-owned artifacts. Run package checks on actual Windows installation and smoke-test the installed EXE/optional ASR model. Missing Inno Setup/FFmpeg is a separately documented blocker, never silently installed. PyInstaller success alone does not prove feature runtime behavior.

## Review and result policy

Review the whole changed diff for bugs, wrong URL/metadata assumptions, credential leaks, path traversal, hostile captions/filenames, data loss, thread safety, cancellation, unexpected resources, provider limitations, licensing and package impact. Use Qodo only if operational and authorized for the intended project/review action; a separate competent reviewer is an alternative if available. Do not create/push PRs for review without user approval.

Preserve logs/native test results; concise disposition in existing feature plan/tasks with command, exit status, revision/state and PASS/FAIL/BLOCKED/NOT_RUN. Do not weaken a gate or delete a failing test to pass. An unreached review/installer/e2e smoke is explicitly pending; do not call it release-ready.
