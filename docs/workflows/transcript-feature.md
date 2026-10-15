# VD-02 — Codex End-to-End Workflow (8-stage runbook)

**Read first:** `AGENTS.md` → `PRODUCT.md` → `ROADMAP.md` → `specs/transcript-extraction/spec.md` → `docs/workflows/capabilities.md` → `docs/verification/acceptance.md`. This Markdown is the authoritative **agent procedure**, not a daemon, scheduled runner or substitute for MCP authentication. Run in the user's active Codex session; user controls its duration and permissions.

## Operating contract
- Implement authorized changes in existing Windows PySide6/yt-dlp app and run local checks. Preserve uncommitted data; no git commit/push, force, cloud publish, package install, payment, credential/tool-account changes, or destructive cleanup without separate user approval.
- Stage has an entry precondition, named capabilities in `docs/workflows/capabilities.md`, tangible outputs and exit gate. A missing *optional* service must not prevent independent work; a missing essential feature/permission must stop dependent work.
- Existing `.specify/workflows/speckit/workflow.yml` contains explicit human gates. **Do not represent this runbook as executing that YAML or silently auto-approve gates.** The main session can continue independently authorized changes; report user-only decisions pending.

## Stage 0 — Worktree and tool discovery (KOK-5)
**Use:** Git, local Python source/tests, Spec Kit integration status, paths-only script; exact probes in capabilities catalog.
**Entry:** repository open; do not assume remote equals worktree.
**Actions:** review git diff/status and relevant code; verify `.specify/feature.json` resolves to `specs/transcript-extraction`; check copied Spec Kit managed-file modifications rather than overwriting them; record installed/callable/authenticated/operational/verified for each intended tool. Capture existing feature regression command results before edits.
**Gate:** actual architecture, active spec path, modifications, testing baseline and any blockers are known.

## Stage 1 — Evidence and bounded reverse engineering (KOK-5 / KOK-6)
**Use:** authoritative yt-dlp/PySide6 docs/source and installed version; REA skill/CLI only if an authorized external app target needs reverse engineering. `REA setup selected none`, so MCP is not assumed integrated. Check REA capability/version and actual command schema before use; never install analysis engines or inspect targets without permission. Inspect local Codex MCP list for Linear/Qodo; verify any intended operation. Record platform URL coverage/continuation behavior, subtitle track behavior, FFmpeg/storage and Windows packaging constraints.
**Gate:** source-backed findings distinguish observed, inferred and unknown. No unsupported technical assumptions are treated as facts.

## Stage 2 — Product scenarios and acceptance contracts (KOK-5)
**Use:** `PRODUCT.md`, `ROADMAP.md`, VD-02 spec, project constitution, `LOGIC_VERIFICATION.md`.
**Actions:** reconcile FR-001..012 and SC-001..007 with actual feature decisions, supported URL classes, auth/access limitation, language/caption/ASR default behavior and resumption boundary. Expand explicit scenarios when supported evidence finds omissions; reconcile rather than inventing new scope. Critical unanswerable user choices are explicit blockers.
**Gate:** no critical unresolved contradiction for dependent work; each requirement has an observable acceptance claim.

## Stage 3 — Risk-specific technical spike, only where justified (KOK-6)
**Use:** official source, relevant REA evidence only if needed, no alternative tooling ceremony. Identify an actual design-blocking unknown that cannot be resolved from reliable docs/source. If such a risk exists, record hypothesis, bounded reversible evidence, result and final decision; do not run random tests to choose technologies. If none exists, mark SKIPPED WITH REASON.
**Gate:** every architecture-critical unknown is resolved or dependent tasks blocked.

## Stage 4 — Spec Kit plan/tasks/consistency (KOK-6)
**Use:** installed repo Codex skill `speckit-plan` → `speckit-tasks` → `speckit-analyze` + `speckit-checklist` as appropriate; `speckit-clarify` only for genuinely unresolved details. **The existing VD-02 spec exists; do not blindly rerun `speckit-specify` to create a second spec/branch.** Read actual skill instructions. Before any write-oriented skill, verify FEATURE_DIR with paths-only script and `specify integration status --json`. Original skill adapters expect root `LOGIC_VERIFICATION.md` and `IMPLEMENTATION_VERIFICATION.md`, both supplied here.
**Actions:** generate `specs/transcript-extraction/plan.md` and `tasks.md` with sources, design tradeoffs, dependency order, acceptance traceability and implementation ownership; run read-only analyze and reconcile problems before coding. Any skill that asks for human signoff gets a recorded PENDING_USER gate; don't claim it was approved.
**Gate:** complete reviewed design, tasks and FR/SC↔task↔test mapping for authorized work; no contradiction silently bypassed.

## Stage 5 — Verified implementation loop (KOK-7)
**Use:** existing app worker/queue/settings/config and yt-dlp options; Python unittest, golden data/fixture tests, UI-thread tests; `IMPLEMENTATION_VERIFICATION.md`.
For each independent accepted task: (1) load spec/task/affected source (2) edit only relevant files (3) run targeted deterministic gate (4) classify failed evidence (5) repair underlying cause (6) re-run affected and baseline regression (7) checkpoint exact status and remaining tasks. Maximum three unsuccessful repairs in same category without new evidence; then BLOCKED. No disabled tests, threshold reductions, fake status or indefinite automatic retries. Tests alone aren't substitute for exact observable product acceptance.
**Gate:** feature tasks implemented and tested; failures remain explicit and continue only independent work.

## Stage 6 — Convergence, review, desktop packaging (KOK-8)
**Use:** `speckit-converge` for spec↔code gaps, `speckit-analyze` for doc consistency, separate code reviewer/Qodo if operational, existing `build_exe.py` and `build_installer.py` with destructive build-dir check first. Verify cancel/resume, full pagination, status/manifest, caption representation and export formats, original downloads, UI responsiveness, Windows packaged app. No unattended PR creation/push for Qodo review. Review result must be independent or PENDING; missing optional provider not faked.
**Gate:** recorded PASS or precise FAIL/BLOCKED/NOT_RUN by check; no "release complete" if crucial smoke/review missing.

## Stage 7 — Delivery and Linear reconciliation (KOK-8)
**Use:** actual test results, git diff/status, Linear project and existing KOK-5..8 issues if authenticated in the Codex runtime. ChatGPT Linear connector availability does not prove Codex availability. Update issues ONLY upon successful real tool call; otherwise provide issue-ready text in the final disposition. No commit or push.
**Gate:** per-criterion results, changed files, architectural decisions, coverage numbers with source boundaries, user-only decisions and pending reviews clearly described.

## Progress / loop resume
Keep durable checkpoints in existing `specs/transcript-extraction/tasks.md` or `plan.md` and native test logs, not a second orchestration ledger. A Codex session may execute successive tasks/repairs; an external Ralph/background runner has **not** been configured, so don't assert future repeated operation or guaranteed overnight success. The user may configure a runner separately after explicit permission and verified compatibility. Respect quotas and interruption; resume from worktree/tasks evidence, not remembered narrative.

## Failure routing
- Feature context points elsewhere → stop Spec Kit writes, fix context first.
- Critical product ambiguity, unsafe operation, credentials or missing approval → block dependent task only.
- External provider absent (REA/Qodo/Linear) → use documented equivalent **only** where it truly satisfies acceptance, otherwise mark NOT_RUN.
- Pagination/API restrictions → keep partial manifest and causal error; don't label archive complete.
- Windows packaging cannot run → NOT_RUN/BLOCKED, don't claim release.
