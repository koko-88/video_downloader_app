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

## Release gate

Feature and regression tests verified; local runtime and Windows installer smoke verified; independent review disposition; no unresolved critical defects; actionable limitations and missing real-network evidence reported. If a review/service/tool is unavailable, report NOT_RUN and do not claim complete release.
