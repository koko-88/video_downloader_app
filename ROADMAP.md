# Video Downloader — Roadmap

## Source and admission
Canonical product intent: `PRODUCT.md`; feature contract: `specs/transcript-extraction/spec.md`. This roadmap admits the transcript feature for planning and implementation **only once blocking requirement ambiguities are resolved via the runbook's gate**. The published repo already has an existing downloader; the priority is extension, not reconstruction.

| ID | Feature | Current status | Dependencies / acceptance |
|---|---|---|---|
| VD-01 | Existing video/audio download behavior | EXISTING — preserve | Regression coverage for format selection, queue, cancellation, cookies, packaging |
| VD-02 | Transcript extraction + multi-format export | PLANNING REQUIRED | Product scenarios and acceptance matrix; URL discovery, track acquisition, format conversion, UI/queue integration |
| VD-03 | Optional local ASR fallback | CONDITIONAL PART OF VD-02 | Verified backend, storage, model licensing/performance, cancellation, offline and packaging behavior; must not be silently assumed |
| VD-04 | Release verification & packaged desktop delivery | REQUIRED FOR COMPLETION | VD-02/03 scope, Windows runtime, installer checks, independent review and receipt |

## Dependencies
VD-02 cannot be called complete until all accessible videos in supported target inputs are accounted for, not just returned first-page entries. VD-03, if admitted into scope, needs explicit technical acceptance and verified local resources. Features involving existing downloader changes require VD-01 regression pass. Scope changes update PRODUCT first and affected specification; no drift allowed.

## Tracked work
Use Spec Kit `spec.md`, `plan.md`, `tasks.md` as canonical technical decomposition. Linear issue references may mirror milestones but must not replace those files. Keep one authoritative result/disposition in the feature plan or test runner artifact.