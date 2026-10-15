# Start Codex for VD-02

## Goal
Deliver the complete Transcript Extraction & Export feature end-to-end in the existing K:\video_downloader_app Windows PySide6/yt-dlp application, preserving existing download behavior.

## Requirements
1. Read AGENTS.md, PRODUCT.md, ROADMAP.md, specs/transcript-extraction/spec.md, docs/workflows/transcript-feature.md, and docs/verification/acceptance.md.
2. Execute the documented stages in order. First inspect the actual local worktree and installed skills, MCP tools, Spec Kit integration and available agent runner; do not assume that installation implies operational access.
3. Use official source code/documentation for technical evidence; use REA only if authorized external reverse engineering genuinely closes a specific evidence gap.
4. Resolve material contradictions and critical scope/requirements dependencies before dependent implementation.
5. Use the existing Spec Kit integrations for consistent feature plan, tasks, traceability and gate analysis. Do not silently bypass human approval gates.
6. Deliver supported URL discovery across all pages, manual/automatic caption acquisition, configurable languages, multiple output formats, precise coverage reporting, cancellation/retry/resume, safe storage and optional locally verified ASR where permitted.
7. Use bounded task-level verification loops, diagnose root causes and preserve checkpoints; run new acceptance tests, existing regression suite, UI integration verification and packaged-app checks.
8. Track progress/blockers in the connected Linear project using existing issues KOK-5 through KOK-8 when actually available. Use Qodo for independent review when its integration and permissions are verified.

## Constraints
- No commits, pushes, force updates, releases, service installation, purchases or external account changes without user authorization.
- No overwriting unrelated working-tree edits, duplicate governance/orchestration, fabricated tests, fake complete-archive claims or unbounded autonomous retries.
- If a critical requirement, right, credential or human approval is unresolved, block only dependent work and continue independently executable authorized work.

## Expected outcome
Deliver the integrated feature with observed verification evidence if acceptance gates pass; otherwise complete safely executable independent work and report precise blockers. End with architecture decisions, changes, exact test results, coverage status, independent review state and remaining approvals. Leave changes uncommitted.
