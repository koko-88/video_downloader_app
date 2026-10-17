# Tasks: VD-02 Transcript Extraction & Export
Input: spec.md, plan.md, research.md, data-model.md, contracts/transcripts.md.
Sequential single-agent execution. All stories P1. No commit/push/install. Checkpoints below.

## Phase 1: Setup
- [x] T001 Reconcile worktree, dependencies, source, Spec Kit context and baseline in specs/transcript-extraction/plan.md (SC-007).
- [x] T002 Generate design/tasks through existing Spec Kit adapters and analyze FR/SC coverage in specs/transcript-extraction/tasks.md (SC-007).

## Phase 2: Foundation
- [x] T003 Implement strict canonical cues and bounded input parsing in app/captions.py; tests/test_transcript_captions.py proves non-negative integer times, end > start, maximum 100,000 cues (FR-006, FR-011, SC-002).

## Phase 3: US1 Single video
Independent check: injected metadata and HTTP caption fixture yield transcript without media download.
- [x] T004 [US1] Implement metadata-only source adapter/acquisition and HTTP fixture in app/transcript_source.py and tests/test_transcript_source.py (FR-001, FR-005).

## Phase 4: US2 Complete playlist
Independent check: three-page/nested iterator exhausts, visible unavailable entries accounted, interruption incomplete.
- [x] T005 [US2] Implement recursive discovery/input states and pagination fixtures in app/transcript_batch.py and tests/test_transcript_batch.py (FR-002, FR-008, FR-012, SC-001).

## Phase 5: US3 Complete channel Videos
Independent check: channel /videos normalization and continuation terminal/loop diagnostics.
- [x] T006 [US3] Verify channel boundaries and incomplete scans in app/transcript_source.py and tests/test_transcript_source.py (FR-002, FR-012, SC-001).

## Phase 6: US4 Mixed batch
Independent check: mixed repeated IDs retain all original source associations, per-input errors.
- [x] T007 [US4] Implement extractor+ID dedup and URL validation in app/transcript_batch.py and tests/test_transcript_batch.py (FR-001, FR-003).

## Phase 7: US5 Track selection
Independent check: exact Unicode/non-English language, four preferences, unavailable vs absent.
- [x] T008 [US5] Implement selection/provenance in app/transcript_source.py and tests/test_transcript_source.py (FR-004, FR-005, SC-002).

## Phase 8: US6 Exports
Independent check: exact UTF-8 golden MD/TXT/JSON/SRT/VTT semantic assertions and timed round trips.
- [x] T009 [US6] Implement five exporters in app/captions.py and tests/test_transcript_captions.py (FR-006, SC-002).

## Phase 9: US7 Recovery
Independent check: cancellation/resume, failed-only retry, changed-file refusal, hashes, lock and totals.
- [x] T010 [US7] Implement atomic manifest, lock and non-overwriting exports in app/transcript_batch.py and tests/test_transcript_batch.py (FR-003, FR-007, FR-008, SC-003).

## Phase 10: US8 No captions
Independent check: optional local ASR reports backend/model unavailable, never succeeded.
- [x] T011 [US8] Implement absent/language-unavailable/ASR disposition in app/transcript_batch.py and tests/test_transcript_batch.py (FR-009, SC-005).

## Phase 11: US9 Errors/security
Independent check: hostile metadata, malformed cues, credentials, traversal, symlink/output tampering.
- [x] T012 [US9] Classify errors, confine paths, limit payloads, omit raw secrets in app/transcript_source.py, app/transcript_batch.py and tests/test_transcript_source.py (FR-011, FR-012, SC-006).

## Phase 12: US10 Desktop regression
Independent check: real QApplication worker signals, responsive event loop, cancellation/lifetime, old formats.
- [x] T013 [US10] Integrate transcript tab/worker and safe close in app/transcript_ui.py, app/main_window.py and tests/test_transcript_ui.py (FR-007, FR-010, SC-004).

## Phase 13: Cross-cutting release checks
- [x] T014 Add isolated packaging destinations and packaged runtime smoke in build_exe.py, build_installer.py, installer/VideoDownloader.iss, video_downloader.spec, app/packaged_smoke.py and main.py (FR-010, SC-004).
- [x] T015 Run full deterministic/syntax/dependency/security/convergence checks, reconcile every acceptance in specs/transcript-extraction/plan.md (FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, SC-001, SC-002, SC-003, SC-004, SC-005, SC-006, SC-007).
- [ ] T016 Verify actual live provider discovery/caption/download paths and record precise restrictions in specs/transcript-extraction/plan.md (SC-001, SC-004).
- [ ] T017 Complete independent diff review and human installed Windows 10/installer acceptance, disposition in specs/transcript-extraction/plan.md (SC-004, SC-006).
- [x] T018 Replace explicitly requested C:/Users/Public/Desktop/Video Downloader.lnk with verified build; record target/readback in specs/transcript-extraction/plan.md (FR-010).

## Dependencies and execution strategy
T001->T002->T003->T004->T005->T006->T007->T008->T009->T010->T011->T012->T013->T014->T015.
T016/T017/T018 depend on appropriate runtime, provider and filesystem capabilities; blocked ones do not stop independent work. MVP US1/5/6 followed by complete batch/recovery/UI. No parallel execution; caption/source test files could be independently assessed after foundations, but one owner performs all mutations.

## Acceptance traceability
FR-001 T004/T007; FR-002 T005/T006; FR-003 T007/T010; FR-004 T008;
FR-005 T004/T008; FR-006 T003/T009; FR-007 T010/T013; FR-008 T005/T010;
FR-009 T011; FR-010 T013/T014/T018; FR-011 T003/T012; FR-012 T005/T006/T012.
SC-001 T005/T006/T016; SC-002 T003/T008/T009; SC-003 T010; SC-004 T013/T014/T016/T017;
SC-005 T011; SC-006 T012/T017; SC-007 T001/T002/T015.

## Checkpoints
Initial: fresh-cache syntax PASS, 30 unit PASS, one live smoke SKIPPED; pip check PASS.
Plan/tasks structural coverage: all 19 FR/SC IDs mapped, ten stories, unique task IDs.
Analysis: no unhandled critical design contradiction; external evidence gates stay pending.
Spec Kit YAML approvals PENDING_USER, workflow not executed. Direct implementation explicitly authorized.

T003 checkpoint: seven caption tests PASS (Unicode, overlap, malformed rejection, payload limit, exact timed goldens/roundtrips); T009 exporter validation available, integration still pending.

Source/export checkpoint: 15 targeted tests PASS, including actual local HTTP headers and payload, raw metadata-only options, channel normalization, exact language/precedence, signed-URL redaction and golden exports. Full discovery/task T005 pending.

Batch checkpoint: 12 targeted cases PASS; complete three-page fixture, 0/1/N/nested, interruption/cancel recovery, dedup associations, five-format idempotence, absent ASR, malicious title/traversal, corrupt manifest/lock and user-edited file preservation. Scan persistence throttled to 5 Hz; final transitions always durable.

T013 checkpoint: five Qt integration cases PASS, genuine queued signals/event-loop timers, cancel/resume, native thread lifetime, settings and original sequential download retry/history. Download queue lifetime race repaired with regression coverage.

Final regression detected two real integration concerns: settings normalization reordered selected formats; preserve order while filtering invalid values. Build guards ran after dependency import, letting mocked subprocess affect PyInstaller platform probing; guard destinations before imports. Both repaired at cause, no expectations/test thresholds changed. Installed-extractor fixture initially used the wrong first-page renderer; corrected it to the actual richItemRenderer shape from installed source, proving all three IDs and both continuation requests.


## Phase 14: Convergence
No additional mandatory local code gap identified. Three partial release-evidence findings:
C1 HIGH SC-004 installed installer; C2 HIGH SC-006 independent review; C3 MEDIUM FR-002/012
live archive boundary. These refine remaining T016/T017; they do not claim new approvals.
- [x] T019 Verify an actual installer and installed VD-02 app after an approved Inno compiler is available; use build_installer.py with the final source and record evidence in specs/transcript-extraction/plan.md per SC-004, FR-010. Final production installer/native installed runtime/uninstall PASS with original files/registrations/links and user sentinel preserved; production-installer-acceptance.json.
- [x] T020 Obtain independent local review or explicit authorization for external source disclosure; record review and remediation disposition in specs/transcript-extraction/plan.md per SC-006, FR-011. Qodo final fresh full/deep issue review reports no new findings; four service-retained entries have concrete source/RED-GREEN dispositions in production-qodo-disposition.json. No clean-tracker or skipped-dimension claim.
- [x] T021 Verify a user-selected accessible playlist/channel Videos archive against live continuation exhaustion and manifest inventory in specs/transcript-extraction/plan.md per FR-002, FR-012. EricWTech Videos: two independent exhausted inventories agree on 338 IDs; whole-caption completion remains rate-limited under T016.

## Historical measured checkpoint (before this production audit)
71 tests: 70 PASS, one default live smoke SKIPPED; syntax and dependency checks PASS.
Explicit live media smoke FAIL due to missing FFmpeg, not a code regression PASS.
Actual live single-video caption export five formats PASS; repeat idempotent PASS.
Installed yt-dlp extractor three-page continuation fixture PASS; Windows junction protection PASS.
Final isolated PyInstaller build exit 0; Windows 10 19045 windows-platform frozen tab/worker/export
smoke exit 0. Production hashes unchanged since final build began. Evidence paths and every
FR/SC disposition are in plan.md. Independent review auto-rejected for source disclosure;
Inno absent. No new tools installed, no Git commit/push/publication.
Desktop replacement PASS: C:/Users/kerol/Desktop/Video Downloader.lnk points to verified
build_logs/vd02-delivery-final/dist/VideoDownloader/VideoDownloader.exe; original Public
Desktop link backed up, then replaced through writable user Desktop because Public Desktop
write ACL denied direct save. No ACL changes. Exact readback build_logs/vd02-shortcut.json.
Remaining T016/T017/T019/T020/T021 are evidence/user-action gates, not silently completed.
Controller can only propose first unchecked task; it cannot resolve missing tools/approval.


## Phase 15: Production audit and remediation (2026-10-16)
Human confirmed recovery brief, repository-local ProductShape install, medium pstack budget with all roles inherit-parent, and proceeding with seven unchecked reviewer markers. Single-agent execution; no commit/push/apply/archive. Initial worktree clean on actual main, revision 1bacfa3. Baseline 71 tests: 70 pass, one live test skipped; fresh-cache compilation and pip check pass.
- [x] T022 Run one bounded ProductShape recovery batch, refine the same CHG-INITIAL draft graph, validate all 18 artifacts and configure confirmed pstack roles. Evidence: .specify/productshape/recoveries/production-readiness/report.md, .specify/productshape/changes/production-readiness; zero validation diagnostics, recovery insufficient-evidence (10/60 current sources processed), no accepted model writes (SC-007).
- [x] T023 Reject malformed manifest state/associations before mutation and retain exact non-YouTube request identities across cancel/resume while keeping secrets out of persisted provenance. Add behavioral recovery regressions in tests/test_production_regressions.py (FR-001, FR-003, FR-008, FR-011, SC-003).
- [x] T024 Redact URL credentials, cookies, authorization and signed media query values from every download logging/error path, including exception tracebacks and UI text; validate hostile download input. Add privacy regressions (FR-010, FR-011, SC-006).
- [x] T025 Preserve valid caption export semantics for blank JSON3 paragraphs and reject pathological timestamp/payload cases deterministically. Add timed/text fidelity regressions (FR-006, FR-011, SC-002).
- [x] T026 Keep large batches responsive using incremental model-backed transcript tables and bounded worker progress snapshots; deliver download progress on GUI thread and report queued cancellation accurately. Add real Qt regressions (FR-007, FR-010, SC-004).
- [x] T027 Publish transcript outputs exclusively on Windows filesystems without requiring hard-link support and require actual media output before declaring a download successful. Add non-overwrite and missing-output regressions (FR-003, FR-010, FR-011, SC-003, SC-004).
- [ ] T028 Reconcile runtime dependencies, build a fresh distributable, run native/frozen/live archive/download/installer checks where authorized, complete Qodo review and disposition every finding (FR-002, FR-010, FR-011, FR-012, SC-001, SC-004, SC-006).
- [x] T029 Reconcile stale documentation and requirement/task/test evidence, record exact remaining release gates, preserve user checklist markers and run final controller/regression checks (SC-007). Current reconciliation is in plan.md; fresh-cache controller reports no structural findings, syntax PASS and regression PASS_WITH_SKIPS.
- [x] T030 Stop new discovery/video requests after provider rate limiting, preserve pending inventory and completed products, display the pause, and resume only on explicit action. RED then GREEN regressions: production-throttle-red.log / production-throttle-green.log (FR-007, FR-008, FR-012, SC-003, SC-006).
- [x] T031 Continue repository-wide ProductShape recovery in deterministic bounded rounds, classify every authorized source, probe remaining families, resolve leads and validate/refine the same draft graph without accepted-model writes (SC-007). Final round 6: all 60 sources classified, zero pending, 24 valid drafts, all families probed and lead resolved; CLI reports ready-for-review with every completion criterion met. Human product approval remains separate. Provider restrictions do not block this independent recovery work; Qodo upload is now explicitly authorized for final review.
- [x] T032 Normalize malformed download preferences before Qt construction, preserving valid transcript settings and legacy resolution migration; demonstrate loader/native-window regressions RED then GREEN and refresh the production artifact evidence (FR-010, SC-004). Code/native regressions and fresh frozen/installed artifact checks PASS; production-complete-build-verification.json.
- [x] T033 Give surfaced provider rate limits priority over cookie/auth/database and format fallbacks in both paths, stop subsequent queued downloads with explicit unattempted reasons and retain explicit retry. RED/GREEN tests prove no extra app session/fallback/queued job after the surfaced exception while ordinary fallbacks still work (FR-007, FR-010, FR-011, SC-006).
- [x] T034 Preserve selected MP3 quality through saved settings, repeated format setup and busy/idle transitions; verify all supported audio quality choices with native Qt regression (FR-010, SC-004).
- [x] T035 Preserve malformed/unreadable history and failed-publication contents, retain valid legacy entries and prevent history I/O failures from stalling successful media queues; show the history limitation without changing download success (FR-010, FR-011, SC-003, SC-004).
- [x] T036 Keep diagnostic/test cleanup inside temporary settings ownership and prove ordinary preferences survive native smoke; disclose the earlier unsafe cleanup boundary without fabricating restoration evidence; current suite preserves ordinary preferences bytes and mtime (FR-010, FR-011, SC-003, SC-004).

- [x] T037 Narrow surfaced rate-limit classification to structured HTTP 429 or explicit redacted HTTP/status/rate-limit messages; numeric media identities, URL paths and ordinary throttle titles must retain normal failure/fallback behavior. Qodo finding 5cbf4de1 reproduced RED and repaired GREEN; 106-test source suite passes, fresh packaged revalidation remains under T028 (FR-007, FR-010, FR-011, SC-006).

- [x] T038 Resolve independent Qodo playlist-output, mixed blank-line subtitle and windowed exception-handler findings; preserve output confinement/container checks, TXT/JSON paragraphs and primary privacy-filtered crash logs. Targeted RED/GREEN plus full source regression; fresh package and final review remain under T028 (FR-006, FR-010, FR-011, SC-002, SC-004, SC-006).

- [x] T039 Restore explicit request-throttling and bare throttled error recognition while avoiding incidental numbers/URL paths and ordinary Throttle/Throttled titles. Demonstrate a throttled discovery stops later inputs; targeted RED/GREEN and full source regression (FR-007, FR-010, FR-011, SC-006).

Audit scope includes every production app module, current tests, controller, build scripts/spec/installer and canonical docs. Confirmed risks: request URL query loss, under-validated manifests, raw download logs/errors, timed paragraph export, full-table/copy churn, cross-thread queue progress, pending cancellation display, hard-link-only output publication and false media success. Optional local ASR remains explicitly unavailable; no backend/model was admitted or installed. Native ProductShape brief-aware start was relocated before Spec Kit resume because adapter start has no brief option; this is one session and one CHG-INITIAL lifecycle. Draft schema heading/order issues were repaired from installed templates before implementation admission.

2026-10-17 resume checkpoint: all admitted local implementation tasks remain complete; recover-next has no remaining batch and the same 24-artifact overlay validates without diagnostics. Fresh-cache syntax PASS, 111 tests (110 PASS, one explicit live SKIP), dependency check PASS and all 19 FR/SC identifiers mapped. Application/build/runtime inputs and final EXE/installer hashes match the independently reviewed handoff snapshot. Reused its completed full/deep Qodo review with explicit skipped dimensions and four locally repaired service-retained records; no unchanged-code review resubmission. One approved ordinary caption probe again returned rate_limited and preserved the original 338-video manifest. T016/T028 remain blocked by live captions; T017 awaits actual human Windows/installer/current-preferences acceptance. Exact receipts and boundaries are in plan.md's resume audit. No new application defect or unimplemented admitted behavior was established; no extra task or approval was invented.

Production checkpoint: T023/T024/T025/T026/T027/T030 verified by tests/test_production_regressions.py, tests/test_media_integration.py, QtTests and original format/source/batch suites. New real HTTP/FFmpeg fixture proved progressive WebM could be falsely reported as MP4; added maintained FFmpeg remux postprocessing and strict final-container checks. Native Windows 10 GUI fixture/export plus real download queue acceptance PASS: build_logs/production-source-live-smoke.json, isolated config/history; all five caption exports and actual 7,986,729-byte MP4 completed. Four real provider download formats passed FFprobe container/codec inspection: build_logs/production-live-formats-20261016/report.json. Explicit existing live download unittest PASS. Local FFmpeg/FFprobe 9.0.2 and Node 24.19.0 copied from existing host installations, licenses included; Node matched official release SHA256. No runtime-tool download/global install was necessary. Preliminary build retained at build_logs/production-delivery-20261016; final build includes subsequent container/harness/throttle corrections. Human supplied EricWTech Videos: discovery/inventory PASS (338 identical IDs across production and independent enumerations); caption batch paused on provider limit with 333 pending, one failed and four inaccessible, zero exports. Qodo host login verified; final review not yet run. Installer tests await final binary.
