# Agent entry point — Video Downloader

## Canonical read path
1. `PRODUCT.md` — authoritative product intent and feature boundaries.
2. `ROADMAP.md` — admitted feature and dependencies.
3. `.specify/memory/constitution.md` — project principles.
4. `specs/transcript-extraction/spec.md` — VD-02 user scenarios, FR/SC and acceptance.
5. `docs/workflows/transcript-feature.md` — execution order and stopping rules.
6. `docs/workflows/capabilities.md` — stage-by-stage skills, exact tool entry points and availability probes.
7. `docs/workflows/loop-engineering.md` — source-backed control loop, runnable sensor/controller, and gap audit.
8. `LOGIC_VERIFICATION.md` and `IMPLEMENTATION_VERIFICATION.md` — project-wide validation ownership; feature checks stay under `docs/verification/acceptance.md`.
9. Existing `app/`, `tests/`, scripts, packaging, relevant installed skills. Read incrementally.

## Execution authorization
The operator runs Codex to implement VD-02 within this repository. Repo source edits and bounded local verification are authorized. Codex must NOT commit, push, force-update Git, publish releases, deploy, purchase tools/services, install new dependencies globally, change account/credential integrations, silently overwrite unrelated local changes, or delete user data. Only the user authorizes those separately.

Read `git status --short` before changing files, preserve untracked/uncommitted work, and never presume the remote branch equals the live Windows worktree. Branch selection belongs to the user. Use an existing repo architecture instead of reconstructing it.

## Evidence and tools
Distinguish PRESENT / CALLABLE / AUTHENTICATED / OPERATIONAL / VERIFIED. Report absence and partial completion without guesses. Use official yt-dlp/PySide6 source/docs first; conditional REA only when examining authorized *external* applications whose behavior is not established by available source. The global REA skill is not proof that its MCP is registered in Codex. Linear was linked in ChatGPT, not proven available in local Codex. Qodo readiness is unverified. Use native verified facilities; do not install a duplicate agent orchestration stack.

Use one code-task loop: requirement → implementation → relevant deterministic verification → root-cause repair → regression → checkpoint; max three repeated attempts with no new evidence. Escalate or mark BLOCKED when an essential product/security/permissions/architecture input is missing; continue independent authorized work. Do not turn NOT_RUN or external restrictions into PASS.

## Authoritative ownership
`PRODUCT.md` scope; `ROADMAP.md` feature admission; `specs/transcript-extraction/{spec.md,plan.md,tasks.md}` feature definition/design/tasks; `LOGIC_VERIFICATION.md` consistency method; `IMPLEMENTATION_VERIFICATION.md` engineering acceptance process; `docs/verification/acceptance.md` exact VD-02 checks; `docs/workflows/transcript-feature.md` execution path; `docs/workflows/capabilities.md` tool routing. Linear mirrors progress only; Git history/results and feature artifacts are truth.
