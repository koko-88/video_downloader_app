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
- [ ] T019 Verify an actual installer and installed VD-02 app after an approved Inno compiler is available; use build_installer.py with the final source and record evidence in specs/transcript-extraction/plan.md per SC-004, FR-010 (partial).
- [ ] T020 Obtain independent local review or explicit authorization for external source disclosure; record review and remediation disposition in specs/transcript-extraction/plan.md per SC-006, FR-011 (partial).
- [ ] T021 Verify a user-selected accessible playlist/channel Videos archive against live continuation exhaustion and manifest inventory in specs/transcript-extraction/plan.md per FR-002, FR-012 (partial).

## Final measured checkpoint
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
