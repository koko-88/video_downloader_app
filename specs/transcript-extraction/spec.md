# VD-02 — Transcript Extraction & Export

**Status:** Product requirement contract; implementation plan and tasks to be written after live-repo and tool evaluation. **Target:** existing Windows 10 PySide6 + yt-dlp app. **Product authority:** `PRODUCT.md`. **Release checks:** `docs/verification/acceptance.md`. This is NOT proof of an implemented feature.

## User scenarios (acceptance dimensions)

| Story | Priority | Required outcome |
|---|---|---|
| US-01 — Single video | P1 | Source caption track found and export correct with language/format provenance |
| US-02 — Complete playlist | P1 | Enumerate supported accessible entries through observed continuation exhaustion; manifest includes unavailable/error entries when visible |
| US-03 — Complete channel Videos | P1 | Enumerate accessible Videos tab across pagination; no first-page-only fake success |
| US-04 — Mixed URL batch | P1 | Video/playlist/channel links can be processed together with deduplication and per-input error state |
| US-05 — Track selection | P1 | Manual/automatic track precedence and language choice are explainable; missing requested tracks reported |
| US-06 — Export | P1 | MD/TXT/JSON/SRT/VTT outputs parse and retain their respective semantic information |
| US-07 — Recovery | P1 | Resume, cancel, retry failed, no overwrites or duplicate completed products, honest progress |
| US-08 — No captions | P1 | Missing captions distinctly reported; optional explicitly enabled local ASR with verified backend if required to deliver speech transcripts |
| US-09 — Error cases | P1 | Private, deleted, region-limited, unsupported, network/throttle, malformed metadata do not silently fail |
| US-10 — Desktop regression | P1 | Existing video/audio UI and download paths remain intact; installed app works where dependencies exist |

## Functional requirements

- **FR-001:** Validate and classify each user-provided URL via supported extractor behavior; preserve original URL and normalized target identity; unsupported inputs receive explicit failure, not arbitrary-webpage promises. (US-01/04/09)
- **FR-002:** Discover all accessible matching videos for each supported playlist/channel Videos tab with actual continuation/pagination termination; report partial scans distinctly when interrupted/blocked. (US-02/03)
- **FR-003:** Deduplicate by extractor + canonical video identifier + source track and user choices; keep source URL associations for mixed inputs. (US-04/07)
- **FR-004:** Select available manual/automatic subtitle tracks by explicit language and preference; preserve track source and provenance. Do not mark language-unavailable as caption-absent. (US-05)
- **FR-005:** Acquire selected captions without downloading rendered video when media download is not requested; classify caption-absent, extraction failure and permission failure separately. (US-01/08)
- **FR-006:** Convert valid cues into each user-selected MD/TXT/JSON/SRT/VTT with Unicode safety and meaningful timestamp/cue fidelity when timed format is chosen; expose selected format(s) in UI. (US-06)
- **FR-007:** Provide interactive UI progress for scan vs per-video extraction vs conversion; cancel and resume an interrupted batch and selectively retry failed items. Keep UI thread responsive. (US-07/10)
- **FR-008:** Persist a resumable per-video result manifest with input/source/track/output provenance and disjoint status for succeeded, caption_absent, inaccessible, failed, pending; record discovery completion state independently. (US-02/03/07/09)
- **FR-009:** Optional local ASR for truly missing tracks only under an explicit user-selected mode with installed backend/model verification and storage/performance/package constraints. Never silently run paid/cloud transcription, and never call missing captions a completed transcript. (US-08)
- **FR-010:** Preserve existing PySide6 queues, worker cancellation, formats, browser-cookie fallback, history/logging and installed Windows behavior. (US-10)
- **FR-011:** Avoid path traversal, dangerous filenames, malicious subtitle payloads, leaked auth cookies or signed media URLs in logs; respect accessible-site limits and rights. (US-09/10)
- **FR-012:** Report video discovery/attempt/process/export counts correctly and include reasons for failures or not-run cases, never equating RSS feed results or yt-dlp enumeration attempts with full verified archive. (US-02/03/08)

## Success criteria

- **SC-001:** A deterministic multi-page playlist and channel fixture is fully enumerated to a verified last page; a partial scan is correctly labeled incomplete. (FR-002/012)
- **SC-002:** Golden MD/TXT/JSON/SRT/VTT fixtures pass exact expected semantic assertions for manual, auto, non-English, Unicode, overlapping/malformed and timestamp cases. (FR-004/005/006)
- **SC-003:** Cancellation/resume and repeat-execution fixtures prove zero duplicate completed outputs and no data loss, with manifest totals reconciling statuses. (FR-003/007/008)
- **SC-004:** Existing download/unit regression suite passes with zero new failures; UI remains responsive and actual installed app verified on Windows. (FR-007/010)
- **SC-005:** Optional local ASR selected by user either produces accurately attributed local transcript with verified backend or a clear blocked/unavailable status; never a silent success. (FR-009)
- **SC-006:** Security/privacy checks on malicious metadata paths and logs pass; independent diff review completed or release remains pending. (FR-011)
- **SC-007:** Requirement-to-task-to-test matrix covers every FR and SC; no critical ambiguity remains hidden in plan/tasks. (all)

## Essential planning decisions and risks

Determine using repo + official source facts: supported extractors/sites, playlist/channel boundaries, live/Shorts behavior, caption canonical source vs conversion, backend/model for local ASR, UI mode and queue semantics, per-video status semantics, performance/storage, legal/platform constraints, Windows packaged runtime. Do not choose architecture/tools from guesses; record evidence, alternatives, selected decision and verification.

**Feature implementation admission:** `ROADMAP.md` admits VD-02 once material product/technical ambiguity and approval gates are resolved. Unavailable authenticated services/installer/ASR are explicit external blockers, not permission to claim full PASS.
