# VD-02 Verification and Evidence Contract

## Logic gate

Before coding verify PRODUCT.md ↔ ROADMAP.md ↔ Spec Kit spec.md/plan.md/tasks.md consistency, source links, coverage, permissions and dependencies. Use existing speckit-analyze/checklist if functional; don't create substitute policy layers. Reconcile contradictions before dependent code.

## Engineering gates

- Static/syntax/import checks on changed Python; existing unit tests; dependency and security review based on exact changes.
- Deterministic offline fixtures for URL classification, nested playlists/continuations, 0/1/N videos, pagination exhaustion, deduplication, private/unavailable records and interrupted enumeration.
- Caption track fixtures: manual, automatic, translated if supported, malformed VTT, missing language, HTML entities, overlapping cues, Unicode, repeated segments, very long outputs and track provenance.
- Export golden files for MD/TXT/JSON/SRT/VTT; preserve intended timestamp/cue semantics and validate round-trips where meaningful.
- Cancellation/resume/retry/idempotency and manifests recording per-video states. Re-running a completed batch must not duplicate output.
- PySide6 UI state changes and worker-thread safety, not just headless utilities; existing download regression; packaged Windows app/installer behavior.
- Real external interaction smoke only as necessary to verify live platform behavior and only with allowed network access. Report provider throttling/changes and skipped offline checks; no fabricated success.
- Independent high-risk review (Qodo if available and operational, otherwise separately scoped independent review or explicitly pending). Human acceptance and Git operations remain user-owned.

## Results convention

For each gate record PASS/FAIL/BLOCKED/NOT_RUN with input/fixture identity, exact command, exit status, revision/worktree state, failures and scope limits. Exclude skipped and blocked checks from PASS. All-captions collection is incomplete if manifest totals don't reconcile: discovered IDs = succeeded + caption_absent + inaccessible + failed + pending (with mutually exclusive states); results count alone cannot prove all channel videos were discovered.

## Bounded feedback loop

Each iteration: pick next independent approved task → implement focused change → run relevant checks → diagnose failing evidence → repair root cause → run regressions → mark checkpoint. At most 3 unsuccessful attempts on same failure category without new evidence; then mark BLOCKED and continue unrelated safe tasks. No test deletion, threshold relaxation or fabricated receipt to get green. Stop after limits selected and recorded in feature plan; no indefinite unattended retries.

## Actual sensor and feedback

`scripts/feature_loop.py` measures spec/plan/task presence, FR/SC textual traceability and (with `--run-checks`) existing fixed Python syntax/unittest checks. `PASS_WITH_SKIPS` is not a full PASS, and `VERIFY_RELEASE` only requests final acceptance, **not** approval. The sensor cannot establish semantic requirement coverage, channel completeness, GUI correctness, caption integrity or a valid Windows installer.

For each failed acceptance case, identify the measured error and select a small correction. After two unsuccessful fixes sharing one assumption, follow Pstack's **attack-the-premise**: name the common assumption and collect contrary/confirming evidence before repeating a fix. Keep the requirement→task→test links and actual output evidence current; preserve regression gates. Do not declare all requirements passed just because tests that currently exist are green.

## Release gate

Feature and regression tests verified; local runtime and Windows installer smoke verified; independent review disposition; no unresolved critical defects; actionable limitations and missing real-network evidence reported. If a review/service/tool is unavailable, report NOT_RUN and do not claim complete release.

## Production regression mapping (2026-10-16)

- `tests/test_production_regressions.py`: non-YouTube query identity after restart; corrupted manifest preservation; Windows alternate stream/device/trailing-dot path rejection; hard-link-independent publication; paragraph cue semantics; absent output refusal; credential/header/traceback redaction; local JS runtime enablement; cancellation during metadata retries; installer deletion boundaries; provider rate-limit pause during discovery/extraction with explicit resume and failed-only retry.
- `tests/test_transcript_ui.py`: GUI-thread queue progress, queued cancellation, 10,000 visible model rows without reset, and update payload volume proportional to changed rows; real native event-loop lifecycle remains covered.
- `tests/test_media_integration.py`: actual local HTTP download and FFmpeg remux of a progressive WebM input to requested MP4, checked by FFprobe. This needs the installed FFmpeg/FFprobe pair and does not contact external sites.
- `main.py --smoke-report <fresh report.json> --download-url <authorized public video>`: actual source/frozen/installed Windows tabs, transcript fixture/exports and real download UI/queue with isolated settings/history. Omit the optional URL for offline fixture-only verification. Every report declares frozen state, actual runtime paths and GUI platform.
- `build_logs/production-live-formats-20261016/report.json` records actual MP4/WEBM/MP3/M4A containers/codecs. A correct file extension alone is insufficient.

The final source snapshot, installer, installed runtime, independent Qodo review and user-provided archive URL must each have their own current evidence. Preliminary builds do not satisfy those gates. Human release acceptance is separate from machine evidence.

Live archive input provided: `https://www.youtube.com/@EricWTech/videos`. Production discovery and an independent flat extraction each exhausted the returned feed and produced the same 338 IDs. See `build_logs/production-live-archive-20261016/{discovered-inventory.json,independent-inventory.json,report.json}`. The first caption request was rate-limited: zero exported, four inaccessible, one failed, 333 pending; counts reconcile. One bounded ordinary caption availability check after 4,467 seconds of cooldown again reported rate_limited and preserved the original manifest; no further request or bypass followed. Discovery/inventory PASS within the accessible returned Videos scope; whole-archive caption completion BLOCKED, not PASS. The persistent manifest supports later explicit resume/retry.


Historical round-3 regressions: QtTests covers malformed saved download preferences, preservation of valid transcript choices and legacy resolution migration, plus stopped download queues with explicit retry after a surfaced rate limit. ProviderRateLimitTests covers mixed limit/auth/database/format errors and a limit reached during browser fallback. RED receipts precede fixes; production-round3-final-unit.log records 96 tests (95 pass, one live skip). These changes superseded the earlier distributable at that checkpoint; the latest exact artifact status is in build_logs/production-current-delivery.json.


Historical round-4 checks: all supported MP3 choices survive startup/busy transitions; corrupt history bytes and failed-publication contents are preserved, valid legacy entries retained and history I/O failures do not stall successful queued media. Native diagnostic sentinel tests cover success plus early and late failure cleanup; current ordinary preferences bytes/mtime remain unchanged across the full suite. A previous test cleanup wrote through the ordinary settings path, and earlier values are unknown; no restoration claim is made. See the current feature plan for exact scope and evidence. That checkpoint had 103 tests, 102 pass and one opt-in live skip; the current source and review evidence below supersede it.


## Current handoff evidence (2026-10-16)

- `build_logs/production-handoff-controller.json`: 111 tests, 110 PASS, one explicitly opt-in live SKIP; syntax PASS and zero structural findings. The 35-input application/build/resource/runtime snapshot matches source before/after those checks, with ordinary config/history unchanged.
- `build_logs/production-delivery-handoff/dist/VideoDownloader/VideoDownloader.exe`: fresh native frozen Windows 10 checks pass both tabs, five export formats and real local HTTP media download/remux; see production-handoff-frozen-smoke.json.
- `build_logs/production-installer-handoff/VideoDownloader_Setup_1.0.0.exe`: matching compiler and isolated install/native/uninstall PASS; production-handoff-installer-acceptance.json and production-handoff-installed-smoke.json. Installed EXE matches distribution; user sentinel survives uninstall, temporary registration removed, original installed files/links and ordinary settings/history unchanged.
- `build_logs/production-qodo-handoff-status-003.json`: final fresh full/deep issue review, no new findings, complete reported coverage, two issue reviewers completed. Four earlier service records remain open despite verified local repairs; every source fix and RED/GREEN case is in production-qodo-disposition.json. No clean-tracker claim. Requirements/compliance/UI/other skipped dimensions are explicit; supplied spec ref remained unresolved.

Provider-limited whole-archive captions and reserved human Windows/installer acceptance remain pending. Machine evidence does not authorize those human gates, a stored review dismissal, accepted ProductShape model application, Git publication or deployment.
