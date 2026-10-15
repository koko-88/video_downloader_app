# Agent entry point — Video Downloader

## Canonical reading order
1. `PRODUCT.md` — product promise, supported scenarios, boundaries.
2. `ROADMAP.md` — status, feature scope and dependencies.
3. `.specify/memory/constitution.md` — existing project constitution; complete and reconcile before specification.
4. `specs/transcript-extraction/spec.md` — feature requirements and acceptance.
5. `docs/workflows/transcript-feature.md` — end-to-end runbook.
6. `docs/verification/acceptance.md` — gates, evidence and failure policy.
7. Relevant source files under `app/`, tests, packaging, and installed skills, progressively as required.

## Authority and safety
- Treat repository and live worktree as truth; GitHub inspection is only a snapshot. Check `git status`, local differences and existing work first.
- User owns commits, pushes, releases and destructive operations. Do not commit, push, force push, delete user data or run unrelated package updates.
- Never silently install packages, pay for services or modify external accounts. Ask only for a truly blocking authorization; continue independent steps.
- Use installed tools/skills when available and operational. Distinguish installed, exposed, authenticated, operational and verified. No assumed REA/Qodo/Linear integration.
- Follow mature official packages/APIs where possible. Don't add separate governance, orchestration, result tracking or skill layers when existing ones suffice.
- Implement functionality in the current PySide6/yt-dlp app; preserve the behavior and packaging of existing downloads.
- No guesswork: sources, tests and material technical claims need evidence; unknowns remain explicit and block dependent implementation. Assertions are not evidence.
- Use limited bounded retries and exact acceptance checks. No silent acceptance of partial channel results. Never mark skipped or unrun verification as passed.
- User-approved unattended execution is limited to repo code changes, local deterministic tests, and checkpointed progress. External publishing, secrets, unsafe permissions and architectural requirement contradictions require stopping.
- Linear is a mirror of milestone/issue status and blockers; repository documents own specs and detailed tests.