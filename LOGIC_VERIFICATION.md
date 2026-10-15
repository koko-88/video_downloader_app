# Logic verification — Video Downloader

Single project-level owner for checking product, roadmap, constitution, specifications, plans, tasks and contracts for contradictions, gaps and unrequested scope. Feature-specific pass cases belong in `specs/transcript-extraction/spec.md` and `docs/verification/acceptance.md`.

1. Reconcile FR/SC ↔ user scenario ↔ design decision ↔ task ID ↔ executable check. Requirements with no mapped test/task or contradictory claims (e.g., first-page feed == whole-channel coverage) are material findings.
2. Use the existing `speckit-checklist` to assess requirement quality and `speckit-analyze` *after* `plan.md` and `tasks.md` exist and are selected by the feature context. The latter is read-only; separately authorize any remediation it proposes under the implementation scope.
3. Validate the actual feature resolution with `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly`. The intended directory is `specs/transcript-extraction`; verify returned FEATURE_DIR matches before running write-oriented skills. The checked-in `.specify/feature.json` establishes this repo's current feature, unless an explicit user-owned override is present.
4. Use `specify integration status --json` for manifest diagnostics. Existing files may intentionally differ from generated templates; never blindly run `upgrade --force` or erase modifications.
5. Record results as PASS / FAIL / BLOCKED / NOT_RUN. Evidence has exact artifact names, source revision/state and unresolved requirements. No new duplicate policy or status files.

Stop dependent execution on an unresolved CRITICAL/HIGH ambiguity, but continue independent authorized work. Do not quietly convert a pending user approval into an agent-approved decision.
