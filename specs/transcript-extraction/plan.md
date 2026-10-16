# Implementation Plan: VD-02 Transcript Extraction & Export

**Branch**: actual main unchanged; Spec Kit context transcript-extraction. **Date**: 2026-10-16.
**Input**: spec.md. Verification owners: ../../LOGIC_VERIFICATION.md and ../../IMPLEMENTATION_VERIFICATION.md.

## Summary
Extend the existing app with a Transcripts tab, cancellable Qt worker, metadata-only yt-dlp discovery/acquisition, canonical cues, five exporters and atomic resumable manifest. Preserve Downloads. No new dependencies, cloud calls or models.

## Technical Context
Existing Python 3.14.3 x64 .venv; PySide6 6.11.1; yt-dlp 2026.8.27.231323.dev0; yt-dlp-ejs 0.8.0; PyInstaller 6.20.0. Windows desktop; unittest and real Qt event-loop integration tests.
Storage: transcripts/<batch fingerprint>/manifest.json under chosen folder. Fingerprint includes inputs and choices. Atomic manifest, exclusive lock, relative confined output paths and SHA256 prevent destructive retries. One QThread; queued UI signals; retain thread until native finished. Cancel between entries/request boundaries/chunks/exports; 20 second socket timeout, bounded retries. Limits: 16 MiB caption response, 100,000 cues, nesting depth 20; no archive-size cap. No media downloaded.
Named yt-dlp extractors; GenericIE-only arbitrary pages excluded. Bare YouTube channels normalize to /videos; explicit tabs retain scope. No live wait loop. Discovery complete means raw iterator exhausted without warning/loop diagnostics or known-count mismatch, scoped to accessible provider entries, never hidden archive certification. Exact language and four precedence choices; canonical VTT/SRT/JSON3 sources. Optional ASR selected returns unavailable: no verified backend/model.

## Constitution Check
Pre/post design: I truthful scan/result coverage; II existing queue retained; III escaped captions, safe hashed paths, no secret URLs logged; IV FR/SC matrix; V existing owners; VI no Git publication/installs. No relaxation.
Gated workflow YAML is NOT executed: spec/plan/analysis approvals remain PENDING_USER. Runbook permits independent session-authorized work, explicitly requested by user. No gate recorded approved. Human release acceptance pending.

## Upfront gap audit
Initial git status clean on main. Per-command safe.directory override needed under CodexSandboxOffline, no global Git changes. Spec Kit paths-only resolves specs/transcript-extraction. Integration status: 0 missing, 0 invalid, 32 modified managed files, all preserved. Adapter customizations add project verification/controlled execution; setup-plan preserves existing plans. extensions.yml hooks empty.
Baseline: 31 tests, 30 PASS, one live smoke SKIPPED. Initial compileall FAIL was WinError 5 replacing two existing bytecode files; fresh PYTHONPYCACHEPREFIX under build_logs gives syntax PASS without deleting files. pip check PASS. Logs: build_logs/vd02-baseline.json and vd02-preflight.json. Controller PLAN_OR_RECONCILE; no transcript implementation initially.
Python/Qt/yt-dlp/unittest/Spec Kit VERIFIED. PyInstaller PRESENT/importable; build pending. Inno find_iscc returned None; FFmpeg missing. Old build/dist preserved using isolated destinations. Linear KOK-5 connector read AUTHENTICATED/OPERATIONAL; no mutation requested. Qodo not exposed, independent review pending. REA unnecessary with full source. HumanLayer/Pstack principles applied from repo/local skill, no extra runner. Desktop shortcut found C:/Users/Public/Desktop/Video Downloader.lnk; overwrite explicitly requested, dependent on verified executable and filesystem access.

## Project Structure
Feature docs research.md, data-model.md, quickstart.md, contracts/transcripts.md, tasks.md.
Source app/captions.py, app/transcript_source.py, app/transcript_batch.py, app/transcript_ui.py; app/main_window.py tab/lifecycle integration. tests/test_transcript_*.py. Build scripts gain isolated output/work destinations; no destructive default invocation.

## Phases
Plan/tasks/analyze -> cues/source -> discovery/recovery -> desktop -> security/regression/packaging/convergence. FR/SC mapping and measured checkpoints in tasks.md. Stage 3 spike SKIPPED WITH REASON: installed source resolves architecture risks. Live platform, installed Windows 10, Inno/FFmpeg and independent/human review need separate evidence.

## Complexity Tracking
No new framework, database, dependency or orchestration stack.

## Final disposition
Implementation delivered in the uncommitted worktree; release acceptance remains PARTIAL.

### Exact verification inventory (2026-10-16)

- `PYTHONPYCACHEPREFIX=K:/video_downloader_app/build_logs/vd02-pycache` followed by
  `.venv/Scripts/python.exe scripts/feature_loop.py next --run-checks`: syntax PASS;
  regression PASS_WITH_SKIPS, 71 tests, 70 passed, one default live download test skipped.
  Exact output: build_logs/vd02-final-checks.json. No failing assertions weakened.
- `.venv/Scripts/python.exe -m pip check`: exit 0, no broken requirements.
- `.venv/Scripts/python.exe scripts/smoke_check.py`: exit 0, original format/options smoke
  PASS; FFmpeg not found is explicitly reported, not actual media download success.
- Native source `main.py --smoke-report build_logs/vd02-source-final-smoke.json`: exit 0,
  Windows 10 build 19045, Qt windows platform, actual tab/worker and all five exports PASS.
  Screenshot at matching .png; it uses an isolated config and caption fixture.
- Live public `jNQXAC9IVRw` metadata/caption fetch: six manual English VTT cues PASS.
  Full five-format TranscriptBatch run and repeat: one exported, complete single-input
  scan, attempts unchanged, idempotent true. build_logs/vd02-live-provider.json and
  vd02-live-export.json. Host network permission used for public metadata/captions only.
- Earlier BaW_jenozKc sample: input inaccessible, zero transcript successes; retained
  as negative evidence. Sandbox socket probe independently returned WinError 10013;
  source now distinguishes network_access_denied from site inaccessibility.
- Explicit `RUN_YOUTUBE_SMOKE=1 ... -m unittest tests.test_youtube_smoke -v`: FAIL,
  FFmpeg missing before media download. build_logs/vd02-live-download.log. This is a
  remaining environment blocker; default suite skip does not override it.
- ASR inventory: whisper/faster_whisper/vosk import specs all absent in existing .venv.
  Explicit opt-in produces caption_absent plus backend/model unavailable, never success.
- Independent external review NOT_RUN: mcp__claw__codex_review was rejected by automatic
  approval review because it would transmit the full uncommitted diff to an external
  service without source-disclosure authorization. No alternative route bypassed that
  rejection. Local self-review completed; it is NOT an independent review.
- Inno Setup compiler search returned None. Actual build_installer invocation exited 1
  with the missing compiler, without opening install UI or installing anything.
  Installer command/path/overwrite protection tested deterministically with a stub
  compiler, which is explicitly NOT evidence of an installer build.
- `.venv/Scripts/python.exe build_exe.py --output-root build_logs/vd02-delivery-final`:
  exit 0. Final EXE build_logs/vd02-delivery-final/dist/VideoDownloader/VideoDownloader.exe.
  Native `--smoke-report .../vd02-frozen-smoke.json`: exit 0, frozen true, Windows 10
  19045, Qt windows, both tabs and all five exports PASS. Screenshot vd02-frozen-smoke.png.
  build_logs/vd02-build-source-hashes.json verifies every production input unchanged
  since final build started; earlier build retained separately, not falsely final-certified.
- Desktop shortcut replacement PASS: C:/Users/kerol/Desktop/Video Downloader.lnk points
  to the verified final EXE with its working directory; target read back successfully.
  Public Desktop denied FileWriteData even outside sandbox. Instead, original shortcut
  backed up as build_logs/vd02-original-desktop-shortcut.lnk, replacement saved/verified
  on the writable user Desktop, then only the original backed-up public link removed
  using existing Delete rights. No ACL or privilege integration changes. Exact evidence
  build_logs/vd02-shortcut.json. Original installed application files left untouched.

### Requirement-to-check reconciliation

| Contract | Result and exact evidence boundary |
|---|---|
| FR-001 | PASS named-extractor/credential validation in SourceTests; positive live public video and negative inaccessible sample. Generic-only pages rejected. |
| FR-002 | PASS deterministic BatchTests multipage/nested/interrupt/count cases; InstalledYoutubeContinuationTests executes installed three-page extractor and checks both continuation calls. Live complete playlist/channel archive NOT_RUN; no archive completeness claim. |
| FR-003 | PASS BatchTests mixed associations, repeat, cancel/export restart and live idempotence; identity/choices determine non-overwriting products. |
| FR-004 | PASS SourceTests four preferences, exact non-English language and absent-vs-missing language; live manual en track provenance. Translation only if source offers it. |
| FR-005 | PASS source raw metadata options and actual local HTTP track headers; live captions without rendered media. |
| FR-006 | PASS CaptionTests exact TXT/JSON/SRT/VTT semantics, escaped MD, Unicode, overlaps/repeated cues, invalid timing/UTF-8 rejection and timed roundtrip; live five-format export. |
| FR-007 | PASS BatchTests cancellation/resume/selective retry and QtTests native event-loop responsiveness, signals, close/cancel worker retention. Network cancellation bounded by request timeout; no forced thread termination. |
| FR-008 | PASS atomic manifest/OS lock, disjoint reconciled counts, sources/tracks/output hashes, corrupt manifest preservation, restart idempotence. |
| FR-009 | PASS optional unavailable path and installed-backend probe; no admitted ASR implementation/model/cloud usage. Actual speech transcription NOT_RUN/unavailable. |
| FR-010 | PASS original deterministic download/format/queue/history tests and native source UI; final frozen Windows 10 smoke PASS, original live media regression blocked by FFmpeg, installer NOT_RUN. |
| FR-011 | PASS malicious cue/title/credential/path tests, actual Windows junction escape refusal, integrity conflict preservation, static log reasons; independent review NOT_RUN (approval rejection). |
| FR-012 | PASS multipage/count/uncertainty fixtures and disjoint totals incl. attempted/exported/not_attempted, per-input scans distinct from per-video results. Hidden provider IDs never inferred. |
| SC-001 | PASS deterministic three-page playlist/channel iterator and installed extractor continuation tests; interrupted/warning/count mismatch incomplete. |
| SC-002 | PASS CaptionTests + SourceTests and live UTF-8 timed/text outputs; malformed inputs fail instead of partial success. |
| SC-003 | PASS cancel/resume/repeat/partial-export/corrupt-hash/lock cases and live idempotence; zero duplicate completed files. |
| SC-004 | PARTIAL: 70 deterministic tests pass and source Windows 10 native smoke passes; frozen Windows 10 native smoke passes; FFmpeg live media and actual installer/installed acceptance blocked. |
| SC-005 | PASS explicit unavailable ASR branch with provenance; no claim of produced speech transcript. |
| SC-006 | PARTIAL: local security checks/self-review pass; independent review blocked by external-source disclosure approval. Release remains pending. |
| SC-007 | PASS 19 identifiers -> unique canonical tasks -> concrete test classes and measured logs. No hidden critical design ambiguity; external release gates explicit. |

### Analysis/convergence disposition
Spec Kit analyze read-only context: all 12 FR and seven SC have mapped tasks/checks,
all ten P1 stories covered, no missing feature artifacts, duplicate IDs or constitution
relaxation. Requirement-quality checklist remains unchecked for a separate reviewer;
user explicitly authorized continuing independently executable work. Empty extension
hooks verified again. No gated YAML execution or human approval impersonation.
Code convergence: no identified missing mandatory local behavior after root-cause
repairs; partial release evidence remains SC-004/SC-006 and live collection coverage.
Three findings C1/C2/C3 appended as T019/T020/T021 under Phase 14; all are release
evidence gaps, not falsely certified by source tests. Existing T016/T017 remain pending.
Source/UI/parser changes are self-reviewed, not independently certified.

### Required user actions / issue-ready handoff
Provide an already installed approved FFmpeg and Inno compiler (or authorize installation
in a later session); rerun live download and actual installer/installed app checks. Choose
an accessible playlist/channel for live archive acceptance if that release evidence is
required. Arrange independent local review or explicitly authorize disclosure of the
uncommitted diff to the review service. Review requirement checklist and reserved
spec/plan/analysis/release gates. No Git publication occurred. Linear KOK-5 read verified;
no issue/comment/status mutations performed. KOK-5/6 planning and local implementation
are ready to mirror; KOK-8 must remain partial pending the above evidence.



### Delivery state
All safely executable local implementation, regression, native/frozen runtime and desktop
shortcut work is complete. Uncommitted source and canonical artifacts remain on main.
Release NOT certified: FFmpeg-dependent live downloads, Inno installer/actual installed
runtime, independent review and selected live playlist/channel archive acceptance remain
BLOCKED/NOT_RUN as described. Final user actions are limited to those exact gates.
