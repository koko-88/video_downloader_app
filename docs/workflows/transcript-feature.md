# Codex End-to-End Runbook — VD-02 Transcript Feature

## Goal and operating bounds

Extend existing Windows PySide6/yt-dlp application with comprehensive transcript discovery/extraction, multi-format export and properly scoped optional local ASR. Work independently on the current worktree, with bounded verification-driven iterations. Do not commit/push/force/deploy/delete user data or install tools/spend credits without explicit authorization. This Markdown is a runbook, **not** a self-executing orchestrator or a permission bypass.

## Stage 0 — Discover live repo, preserve work

Check pwd, git status --short, current branch, app modules/tests/config, existing product/spec files, installed agents/skills/MCP and command help. Respect any newer local edits not reflected in GitHub. Read AGENTS.md, PRODUCT.md, ROADMAP.md, specs/transcript-extraction/spec.md, docs/verification/acceptance.md. Record observed/inferred/unknown separately. Do not duplicate working architecture or existing tasks.

## Stage 1 — Capability & technical evidence

Read yt-dlp official extractor/subtitle/options documentation and locally installed package version and code, PySide6 threads/queues, conversion libraries, packaged-runtime constraints. Inspect REA if present: name/version, registration, source, operations, privileges. User has reported REA skill installation; do not assume agent integration or an operational REA provider. Use REA only where reverse engineering an external app is genuinely required and permitted, not to replace available source/docs. Inventory Qodo/Linear and tool permissions. For absent/untested integrations, record it; avoid installing without permission. Research best native runner for bounded Codex execution rather than assuming Spec Kit YAML or a Markdown file executes itself.

## Stage 2 — Scope and requirements alignment

Verify canonical product scope; reconcile contradictions, enumerate URL cases, discoverability/continuations, subtitle source hierarchy, formats and ASR operational expectations. Update feature spec acceptance cases; draft/review proposed product changes before accepting ambiguous requirements. A critical unresolved scope or rights question blocks dependent tasks; continue safe evidence/planning.

## Stage 3 — Technical risk disposition

Identify only material unknowns remaining after official docs/source inspection; if a technical spike is indispensable, define falsifiable hypothesis, bounded evidence needed, minimal reversible implementation and disposition before production design. Do not run arbitrary experiments for tool selection. Never turn a disposable prototype into committed implementation architecture.

## Stage 4 — Spec Kit plan + tasks

Use existing installed Spec Kit skills (specify, clarify, plan, tasks, analyze, checklist as relevant). Record selected architecture and alternatives in specs/transcript-extraction/plan.md and tasks in tasks.md once research resolves design. Avoid reusing HBC project docs. Require explicit task→requirement→test mapping and incremental checkpoint identifiers. Existing .specify/workflows/speckit/workflow.yml has user review gates; do **not** claim that its YAML executes unattended or disable explicit user approvals silently. Use this runbook as authorized execution scope for independently resolvable items; stop at decisions reserved for user.

## Stage 5 — Implementation loop

Implement in current app architecture; add smallest justified modules (e.g., discovery, track acquisition, converter, manifest) as determined by plan; reuse actual queue/worker/logging/settings where compatible. Per task: inspect source → implement → run checks → classify errors → root-cause repair → re-run affected regression → checkpoint. Hard cap 3 unsuccessful same-cause repair attempts; no shifting acceptance criteria, unbounded tool restarts, or silent fallbacks. Run headless/CLI test commands with explicit timeouts if automation runner supports it. Do not block on optional tool absent if equivalent verification can be done with local tests; mark optional review pending.

## Stage 6 — Review, convergence, packaging

Run Spec Kit analyze/checklist/converge if operational; review entire diff and security/quality regressions. Qodo is advisory independent reviewer only when credentials/plan/integration actually usable; otherwise record unmet independent-review requirement. Run Windows installer build and launch/smoke only on compatible local environment, record NOT_RUN on non-Windows. User owns committing/pushing and releasing.

## Stage 7 — Report

Report changed files, design, coverage matrix, exact executed checks and statuses, all unresolved blockers, whether original download behavior still passes, and manual approval needed. Update Linear issues by existing IDs KOK-5, KOK-6, KOK-7 and KOK-8 only if tool is available/authorized; never let Linear claims override actual worktree/test results. Leave changes uncommitted.

## Bounded autonomy

Work across approved repo changes without asking about reversible implementation details. Stop when an essential architectural/product/security/payments/credentials/user approval is unresolved, on unexpected destructive action, runaway API/retry behavior, or explicit agent quotas. Preserve recoverable current state. **No promise of completed unattended execution unless a real runner has been configured and demonstrated.**
