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

## Historical delivery checkpoint (before production hardening)
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


## Production hardening — current checkpoint (2026-10-16)

Current source implementation and deterministic checks pass; release acceptance remains partial. The handoff distribution is `build_logs/production-delivery-handoff/dist/VideoDownloader/VideoDownloader.exe`. Its matching installer is `build_logs/production-installer-handoff/VideoDownloader_Setup_1.0.0.exe`; compiler, isolated installed native runtime and uninstall verification PASS for this exact snapshot. Older complete/reviewed/candidate artifacts are retained historical snapshots and do not certify changed source. Current status owner: `build_logs/production-current-delivery.json`.

### Exact current evidence

- `production-handoff-source-hashes.json`: 35 application, entry/build, resource and staged runtime inputs. All match the source tested and frozen. `production-handoff-controller.json`: syntax PASS, regression 111 total / 110 PASS / one explicit opt-in live SKIP, zero structural findings. `production-preservation/after-handoff-checks.json` proves current ordinary settings/history unchanged. No default live skip is converted into live PASS.
- `production-handoff-build.log`: PyInstaller exit 0. `production-handoff-frozen-smoke.json`: actual Windows 10 19045, windows Qt platform, both tabs, five transcript exports and actual local HTTP VP9 WebM downloaded/remuxed to MP4 through the real UI/queue. Bundled FFmpeg/FFprobe/Node paths are reported. `production-preservation/after-handoff-native.json`: source and installed settings/history bytes and mtime unchanged.
- `production-handoff-installer-acceptance.json` and `production-handoff-installed-smoke.json`: compiler/install/native/uninstall PASS. Installed EXE matches distribution, user sentinel survives, temporary EXE/registration removed and original installation/links unchanged. Source/installed settings/history stay byte/mtime-identical. `production-handoff-build-verification.json` confirms all 35 source/runtime inputs still match, and each bundled runtime executes and matches staging. Installer SHA256 927f7d089ebe6e307b7565d0da0575ad0dc4a60bb5375fd3afdd345d72a620a7; EXE SHA256 5017f6870cb3dfd5cb122a97d0b748b1e25877f5e683dbbc25f0657a7623d9ee. Earlier complete/reviewed/candidate receipts remain historical snapshots.
- Public MP4/WEBM/MP3/M4A downloads passed FFprobe before the provider restriction (`production-live-formats-20261016/report.json`); explicit live media unittest also passed (`production-live-download.log`). The current package's real media fixture is local HTTP, not a fresh provider-wide live acceptance claim.

Evidence files above are under `build_logs/` and are operational verification, excluded from ProductShape product evidence and Qodo payloads except the explicitly authorized context JSON.

### Independent review and dispositions

Human explicitly authorized current source/context disclosure after the earlier automatic rejection. Existing host Qodo CLI 1.6.0/authentication was reused; no account/credential changes. Exact published comparison base: `1bacfa3e9821e1fdc27c24ece9bf00210360899a`. Final fresh full/deep operation `c08fbbd2-6565-405c-8720-88d4d2d960c9` completed: no new findings, complete reported issue coverage, two issue reviewers completed, no skipped files. Compliance/skills/spec/UI/persona/cross-repo dimensions were skipped; the supplied pinned spec reference remained unresolved despite also supplying the full contract narrative. No independent requirements/compliance/UI review or clean tracker verdict is claimed.

`production-qodo-disposition.json` retains every finding, source repair and RED/GREEN receipt. The original numeric-429 finding was recognized resolved by the service. Four later records remain in service `still_open`, although the following source behavior is verified locally; no stored dismissal was authorized or made. The unchanged-source automatic loop stopped after the fresh full review, not after falsely interpreting an empty findings array as clean.

| Qodo finding | Current repair and behavioral evidence |
|---|---|
| 5cbf4de1 — incidental 429 metadata | Typed HTTP/status context and redacted messages; numeric IDs/URLs/titles retain normal format/auth fallback. ProviderRateLimitTests; production-qodo-fix-red/green.log. Service resolved. |
| 9003bab5 — later playlist output ignored | Inspect entries until a nonempty selected-container file inside output_dir qualifies; reject foreign/wrong/missing outputs. DownloadProductionTests playlist case; production-qodo-finalfix-red/green.log. Locally fixed, service retains. |
| fa1ae5bd — mixed blank timed cues | Remove empty/whitespace-only body lines for SRT/VTT; mixed separators round-trip while TXT/JSON retain paragraphs. CaptionProductionTests; production-qodo-finalfix-red/green.log. Locally fixed, service retains. |
| e49caa1e — absent windowed stderr | Log primary exception first, guard None/unwritable console, retain traceback redaction. CrashHandlerProductionTests; production-qodo-finalfix-red/green.log. Locally fixed, service retains. |
| 9d9a1c73 — request throttling ignored | Recognize explicit request/provider-throttling and whole-message throttled without matching ordinary titles; later inputs stay pending. ProviderRateLimitTests and ProductionBatchTests; production-qodo-throttle-red/green.log. Locally fixed, service retains. |

### Live archive boundary

User selected `https://www.youtube.com/@EricWTech/videos`. Production discovery and an independent flat extraction exhausted the returned Videos feed, matching 338 identities with no warnings. First caption attempt reported rate_limited: four inaccessible, one failed, 333 pending, zero exports. One bounded normal availability check after 4,467 seconds of cooldown again reported rate_limited; the original manifest remained unchanged. No further provider request followed. Exact inventories/report/manifest are in `production-live-archive-20261016/`; recheck is `production-live-caption-availability.json`.

Discovery/inventory passes only for returned accessible entries. Complete caption export and idempotent repeat remain BLOCKED/NOT_RUN. No hidden/private archive or successful-caption claim. Empty output hash/equality flags were clarified to null/NOT_APPLICABLE/NOT_RUN, preserving the earlier report copy, rather than treating an empty all()/equality as proof.

### Recovery, scope and preservation

Six deterministic ProductShape rounds classified all sixty authorized repository sources into the same CHG-INITIAL overlay. Twenty-four documentation-grounded drafts validate without diagnostics; all families are probed, remaining-source lead resolved and every recovery completion criterion met. No journey/domain ownership was invented to fill optional families. Later changed-source digests were refreshed only for already classified evidence. External Qodo receipts remain verification, not new product authority. Human product approval/apply/archive is separate; accepted model untouched.

Human confirmed repository-first brief, medium pstack budget/all inherit-parent roles, local ProductShape/build tools and proceeding despite seven unchecked reviewer markers. ProductShape 0.22.0 is pinned locally. Existing FFmpeg/FFprobe 9.0.2 and Node 24.19.0 were staged with notices/provenance; Node matched official release checksums. No global install, duplicate runner, agent delegation, Git mutation or publishing. Starting worktree was clean on actual main at the exact base above. Optional ASR remains explicitly unavailable without an admitted backend/model.

A round-three new Qt test closed a window after its temporary Settings.config_path patch ended, writing through ordinary repository settings. Earlier values were not captured and cannot be claimed preserved/restored. This was disclosed; no guessed restoration was applied. Close now occurs inside the patch, and diagnostic cleanup stays inside temporary config/history ownership. Success/early/late-failure sentinel checks and current suite/native byte+mtime receipts prove the corrected boundary. An opaque post-discovery operational copy is excluded from product recovery and external review. Initial smoke probes named red actually passed and are not RED defect evidence.

### Current requirement crosswalk

| Requirement | Evidence and remaining boundary |
|---|---|
| FR-001 | SourceTests and ProductionBatchTests validate named inputs, public identities, unsupported/credential errors; no arbitrary-page guarantee. |
| FR-002 | BatchTests + installed three-page extractor continuation fixture; live 338-ID inventory matches, whole-caption completion pending. |
| FR-003 | Mixed dedup associations, restart identity, hash-verified resume and exclusive conflict preservation tests. |
| FR-004 | SourceTests all four preferences, exact language/manual/automatic provenance and language-unavailable distinction. |
| FR-005 | Metadata-only adapter, actual local HTTP caption headers and earlier public caption acquisition; no rendered media retrieval. |
| FR-006 | CaptionTests + CaptionProductionTests exact Unicode/timed goldens, paragraphs, mixed blank lines and round trips; current frozen five-format smoke. |
| FR-007 | Batch/Qt cancellation/resume, GUI affinity/lifetime, model/delta-volume tests and surfaced limit/throttle stop with explicit retry. |
| FR-008 | Strict manifests, associations, atomic persistence/locks, disjoint totals, confined paths and output integrity/preservation regressions. |
| FR-009 | Explicit optional unavailable behavior; no verified/admitted ASR backend/model or speech transcript claim. |
| FR-010 | Original formats/queue/cookies/retry/history plus malformed preferences, MP3 quality, playlist output and windowed error regressions; handoff frozen and matching installed/uninstall checks PASS; reserved human acceptance pending. |
| FR-011 | Hostile cue/path/junction/credential/logging/traceback/preservation tests; Qodo dispositions explicit, four retained service records. |
| FR-012 | Separate input discovery/video outcomes, interrupted/warning/count fixtures, reconciled live inventory and visible pending restrictions. |
| SC-001 | Deterministic last-page continuation and complete live returned inventory; blocked caption requests do not become archive success. |
| SC-002 | Golden exports and source selection plus mixed-separator timed round trips. |
| SC-003 | Cancel/restart/repeat, edited/corrupt product and lock preservation checks; current ordinary state unchanged, earlier unknown settings values disclosed. |
| SC-004 | 110 source tests pass; handoff native frozen and matching installed/uninstall checks PASS; reserved human acceptance pending. |
| SC-005 | Verified unavailable optional branch; actual ASR NOT_RUN/unavailable. |
| SC-006 | Privacy/security regressions and independent issue review completed with concrete dispositions; skipped dimensions/service-retained records/human gate explicit, no overall release PASS. |
| SC-007 | All 19 FR/SC and ten stories map to unique canonical tasks/checks; no structural finding or hidden critical ambiguity. |

Remaining tasks: T016 live caption acceptance, T017 reserved human Windows/installer acceptance and T028 composite production delivery. T020 records completed independent review/disposition without claiming a clean service tracker. Seven reviewer-owned checklist markers and Spec Kit YAML human gates remain unchanged; independently authorized implementation does not impersonate those approvals. No commit, push, publication or deployment.


Recovery continuation round 2: processed only deterministic E-0011..E-0020 (plan, quickstart, research, tasks, AGENTS, README, both build scripts, entry prompt and capabilities). Documentation corroborated existing scope; build code was secondary observed evidence, not a new product mandate. Recovered BR-EXPORT-INTEGRITY and BR-ARCHIVE-COVERAGE, linked their use case/requirements, replaced truncated FR titles and generic checks with concrete verification scenarios, and clarified selected media-container outcomes. Repaired stale operational instructions that said current plan/tasks were absent; clarified historical Inno research and explicit user authorization for external tracker writes. No application/runtime/build-script byte changed, so the tested distributable remains current. Full recovery remains tracked by T031; source/Qodo/provider/human gates are not silently completed.


Recovery continuation round 3: only E-0021..E-0030 processed; 30/60 sources, 30 pending, twenty draft artifacts. Dependency/version markers are technical metadata; source observations corroborate documented FR/SC without creating new product scope. Reconciled stale workflow assumptions and explicit authorization for tracker writes. Discovered malformed saved download preferences reaching Qt and mixed explicit rate-limit errors triggering browser/database/format retries or subsequent queued jobs. Each failing boundary was demonstrated RED before repair. Settings now normalize each invalid download field independently while preserving valid transcript choices and legacy resolution migration. A shared surfaced-rate-limit classifier now dominates app fallback policies; transcript fallback stops even when an authenticated attempt encounters the limit. The download queue retains unattempted jobs with explicit reasons for user-controlled Retry failed. Maintained transport retry settings remain bounded and unchanged; tests prove no additional application-level fallback/session/queued job after the exception surfaces. Evidence: production-settings-red.log, production-settings-green.log, production-fallback-limit-red.log, production-authenticated-limit-red.log, production-queue-limit-red.log, production-round3-targeted.log, production-round3-final-unit.log. Full regression: 96 total, 95 pass, one default live skip. No external provider retry or Qodo upload occurred. Source fixes require a fresh final build after remaining audit; prior artifact files are preserved.


Recovery continuation round 4: only E-0031..E-0040 processed, now 40/60 and twenty pending. Worker/error/runtime/path/logging code corroborates documented obligations. RED tests reproduced MP3 quality resetting to Best on ordinary startup/busy transitions and history corruption being overwritten, failed publication leaving a temp file, and history read failure stalling the successful queue. Repairs preserve every supported MP3 quality, valid legacy history, corrupt/unreadable history bytes, atomic publication and completed-media status; a visible history warning permits subsequent jobs to finish. Evidence: production-round4-red.log, production-history-preservation-red.log, production-round4-green.log and production-round4-final-unit.log (103 total, 102 pass, one live skip).

Verification correction: a round-3 native-window test registered its close cleanup outside the temporary Settings.config_path patch. Its cleanup wrote through the ordinary repository settings path; original prior preference values were not captured, so preservation or restoration of those prior values cannot be claimed. The test now closes inside the patch. The diagnostic window lifetime was also moved inside temporary settings/history ownership. Sentinel tests cover successful diagnostics, failure before thread creation and validation failure; the initial probes named production-smoke-isolation-red.log and production-smoke-failure-isolation-red.log actually PASSED and are not RED evidence. An opaque post-discovery copy was retained under ignored build_logs/production-preservation solely for operational preservation, never product recovery or external review evidence. The full current suite left current ordinary preferences bytes and mtime unchanged (after-round4-tests.json). This issue and the uncertainty about earlier values were disclosed to the user; no guessed restoration was applied. Source runtime receipts still require rebuild under T028/T032.


Recovery continuation round 5: only E-0041..E-0050 classified, now 50/60 with ten sources pending. Transcript batch/source/UI, download options, entry point and validation scripts/tests corroborate existing requirements; controller plumbing and the empty tests package add no product intent. No additional runtime defect established. Refined the draft media success/history-failure postcondition, linked FR-VD-010 to both use cases and corrected stale Qodo-authorization and current-artifact wording. Previous source suite remains 103 total, 102 pass, one opt-in live skip; the refreshed controller confirms syntax PASS, regression PASS_WITH_SKIPS and zero structural findings, preserving ordinary settings/history. No source/runtime change, provider retry, review upload, accepted-model or Git mutation in this round. T028/T032 still require fresh packaged acceptance after the last evidence batch.


Recovery continuation round 6: E-0051..E-0060 only, all sixty sources now classified. No additional runtime defect established by reviewing remaining tests and runtime/privacy modules. Four structured behavior examples recover documented observable scenarios; three remaining families have explicit no-candidate reasoning. The adapter exposes no lead-resolution command, so its existing generated lead record was resolved in place with an evidence note and verified by recover-round. Recovery ready-for-review, zero diagnostics/stale evidence, all completion criteria true, twenty-four drafts; T031 complete. Human product acceptance is not inferred. Fresh packaged acceptance and independent final review proceed under T028.


Pre-Qodo artifact refresh after all sixty sources (now superseded by the classifier fix): PyInstaller exit 0, all 35 source/resource/runtime inputs unchanged, matching Inno compiler exit 0. Installer SHA256 9902f4afb98d1b1029fde81d69c7db0a6e93280d934a1a3241e99102791ba7ba; EXE SHA256 8291d539caab7639a88bcb7de3d65891a286cccb1cf58e88f389fcfb04a48794. All three bundled runtime executables run successfully and match staged hashes; native frozen/installed acceptance executes the real media UI/queue and five-format transcript worker. Installed EXE matches distribution; install and uninstall exit 0. User sentinel survives; temporary EXE and per-user registration are removed; existing machine registration, inspected installed executable and links stay unchanged. Opaque source/installed config and history state stays unchanged across both checks. T032 artifact refresh is complete; T028 remains pending Qodo/live gates. No installed production app was replaced.


Qodo final deep review e4b29ca1-294c-44f4-b776-429d791e4364 completed: meta.coverage.complete and finding_state.complete true; no skipped files. Two issue reviewers ran, while compliance/skills/spec/UI/persona/cross-repo dimensions were skipped; spec lacked a supplied spec reference. One valid finding 5cbf4de1-13d3-40bc-8dcb-68b5e4c98bfc: raw bare 429 or throttling text inside media metadata could falsely halt queues and disable fallbacks. Accepted and reproduced with seven failing assertions/subtests; narrowed to typed yt-dlp/urllib HTTP status or explicit HTTP/status/rate-limit messages after URL redaction. Walk typed nested exceptions instead of tuple repr. Numeric URLs/IDs/titles and unrelated Throttle titles retain normal error/fallback behavior; real limits still stop work. production-qodo-fix-red.log then production-qodo-fix-green.log; production-reviewed-controller.json: 106 total, 105 pass, one opt-in skip, zero structural findings, exact reviewed source snapshot unchanged and ordinary settings/history unchanged. T037 complete for source behavior. Fresh reviewed artifacts and same-depth Qodo fix review follow; the next context supplies the pinned published spec (FR/SC unchanged locally) for the previously skipped requirements dimension. No provider retry beyond the single cooldown probe.


Second Qodo review f83d60bb-2e43-4d63-bebf-3f568d287a83 completed with issue coverage complete, previous rate-limit finding resolved, three introduced findings and no still-open prior items. Explicit pinned spec reference was received but unresolved; spec reviewer still skipped (no_spec_content), so no independent requirements-review claim. Accepted all three: 9003bab5 later playlist outputs were ignored; fa1ae5bd mixed empty/whitespace subtitle lines produced invalid cue blocks; e49caa1e windowed builds have stderr=None and the crash hook raised a secondary error. Targeted RED: one failed playlist assertion plus ten caption/crash errors; GREEN all nine targeted cases. Replaced first-entry-only normalization with per-entry validated output lookup; timed body excludes blank/whitespace-only lines while TXT/JSON retain paragraphs; console writing is guarded and primary logging remains first. The source suite has 110 tests (109 pass, one opt-in skip), exact candidate source hashes and ordinary config/history preservation are measured by production-candidate-controller.json and production-preservation/after-candidate-checks.json. T038 source repair complete; final candidate artifact/review remains pending.


Third Qodo operation 74413b77-9120-4f4d-834d-6d413abacf04 completed with one new supported finding 9d9a1c73: removing broad throttling matches also missed explicit request-throttled errors, allowing later requests. Restored narrow request/provider-throttling grammar and an entire-message throttled case, while ordinary Throttle/Throttled titles and numeric URL/ID regressions stay negative. A real RuntimeError fixture now proves subsequent discovery inputs remain pending. RED/GREEN: production-qodo-throttle-red.log / production-qodo-throttle-green.log. Full handoff controller: 111 total, 110 pass, one opt-in live skip; exact 35-input source snapshot and ordinary config/history unchanged. Service finding_state still retains the three earlier findings; current source has per-entry lookup, nonblank timed bodies and guarded stderr, each with prior RED/GREEN evidence. No stored dismissal was authorized or made. The service spec dimension is disabled/unresolved despite supplied ref and full contract narrative; no independent spec-review claim. A fresh full-scope, same-depth current-source review follows the supported correction; repeated stale records will be reported with concrete local disposition rather than chased indefinitely. Prior candidate frozen smoke and installer compile are retained snapshots, not certification of this changed source.


Final handoff metadata: all application/build/resource/runtime inputs match the tested source snapshot and final independent review source. Later edits only record delivery/review/recovery evidence in documentation/bookkeeping; the final review is not represented as reviewing those later receipt bytes. No source fix followed the fresh full review. Unknown exec handle on continuation was resolved by the terminal PASS installer receipt and a new preservation-only check; installation was not restarted. Exact machine verification is complete. Human Windows/current-preferences acceptance and live caption-archive completion remain pending, so release_certified stays false.

### Resume audit — 2026-10-17

Inspected the live modified worktree and continued the existing production-readiness recovery/change, retaining the confirmed brief, medium/inherit-parent pstack configuration, single-agent execution and permission to proceed with seven unchanged reviewer checklist markers. Spec Kit resolves to this feature; extension hooks are empty, integration has zero missing/invalid paths and the same 32 intentional managed-file modifications. ProductShape recover-next returned an empty batch: all sixty sources were already classified. The same twenty-four proposed artifacts were reread and overlay validation returned no diagnostics. No new product scope, accepted-model write or application defect was established by this continuation.

Fresh deterministic verification: `build_logs/resume-20261017-controller.json` records syntax PASS, 111 tests (110 PASS, one opt-in live SKIP), zero structural findings and all nineteen FR/SC identifiers mapped. `python -m pip check` exits 0. Initial compileall without the documented cache prefix hit WinError 5 replacing existing bytecode; rerunning with `PYTHONPYCACHEPREFIX=K:/video_downloader_app/build_logs/resume-20261017-pycache` resolves that environmental failure. No source patch or weakened check was needed. All thirty-five application/build/resource/runtime inputs and both final EXE/installer SHA256 values still match the handoff snapshot and delivery receipt; existing frozen/installed/uninstall acceptance remains applicable to those identical artifacts.

At 2026-10-17 06:35:57 UTC (09:35:57 Cairo), one ordinary caption availability probe for the previously limited public video again returned `rate_limited`; the original archive manifest remained byte-identical. The first sandbox attempt was network_access_denied, followed by one approved ordinary network check; no additional provider retry or archive processing followed the limit. Receipt: `build_logs/resume-20261017-caption-availability.json`. The accessible discovery inventory remains 338; zero transcript exports, four inaccessible, one failed and 333 pending. Whole-caption completion and repeated-output acceptance remain BLOCKED under T016/T028.

Final Qodo verification reuses the completed full/deep handoff review for the unchanged application snapshot, following qodo-review's same-snapshot lifecycle rule. Its issue coverage is complete with zero skipped files and no new findings; four service-retained records have explicit local fixes and passing regressions in production-qodo-disposition.json. Compliance, skills, spec, UI, persona and cross-repo dimensions remain skipped; no clean tracker or independent requirements-review claim. This avoids resubmitting unchanged code and does not claim the prior review covers these new receipt paragraphs. CLI version 1.6.0 is present/callable. No new upload, stored dismissal or review spending occurred.

T017 still requires the human's actual Windows/installer acceptance, including current preferences; a request supplies the exact verified EXE and installer paths. Machine evidence does not impersonate that response. T016/T017/T028 stay unchecked, release_certified remains false, and no commit/push/deployment or data deletion occurred. The next useful actions require provider availability and the human acceptance result; further automatic provider retries are not authorized by this checkpoint.
