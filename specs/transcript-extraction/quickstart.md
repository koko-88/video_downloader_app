# VD-02 validation
Use existing .venv/Scripts/python.exe; install nothing. Set PYTHONPYCACHEPREFIX to K:/video_downloader_app/build_logs/vd02-pycache for protected old bytecode. Run scripts/feature_loop.py next --run-checks and -m pip check.
Run main.py, Transcripts tab: URLs, writable folder, exact language e.g. en, precedence and formats, Extract / Resume. Observe scan and result states. Cancel/run same choices; verified successes reused. Retry failed only affects failed videos. Reconcile manifest totals and JSON/SRT/VTT with contracts/transcripts.md. Downloads retains original formats/queue/quality/cookies.
Deterministic tests cover multipage/interrupted iterators, local HTTP captions, Unicode/overlap exports, recovery and actual Qt event-loop signals. These cannot prove live provider archives, installed Windows 10 or installer acceptance. Record those and independent/human review separately in plan/tasks.


## Build and delivery without replacing older artifacts
Run `.venv/Scripts/python.exe build_exe.py --output-root build_logs/vd02-delivery-final`
only when that destination has no build/dist. Existing outputs are refused, not removed.
Frozen native diagnostic:
`build_logs/vd02-delivery-final/dist/VideoDownloader/VideoDownloader.exe --smoke-report K:/video_downloader_app/build_logs/vd02-frozen-smoke.json`.
Use a different fresh output root for future builds. When Inno is installed, run
`.venv/Scripts/python.exe build_installer.py --source-dir build_logs/vd02-delivery-final/dist/VideoDownloader --output-dir build_logs/vd02-installer-final`.
The installer must be built from the selected new feature source, not older dist contents.
Missing compiler exits without installing/opening a download page. All remaining acceptance
and exact evidence are in plan.md. Do not equate stub-compiler tests with an installer.
