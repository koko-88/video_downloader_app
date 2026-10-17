# VD-02 Control Loop — executable contract and preflight gap audit

**Engineering sources:** [HumanLayer design-control-loop](https://github.com/humanlayer/skills/tree/main/plugins/design-control-loop/skills/design-control-loop), [HumanLayer build-iterated-agentic-loop](https://github.com/humanlayer/skills/tree/main/plugins/build-iterated-agentic-loop/skills/build-iterated-agentic-loop), [Pstack attack-the-premise](https://github.com/backnotprop/pstack/tree/main/skills/principle-attack-the-premise), [Pstack create-verification-skill](https://github.com/backnotprop/pstack/tree/main/skills/create-verification-skill). Apply the principles, don't assume the user installed these skills or that they are usable in Codex.

## What is actually implemented

| Control part | Existing executable / authority | Limits |
|---|---|---|
| Set point | VD-02 specification FR-001..012 and SC-001..007 | Real observable product outcomes; not green tests alone |
| Sensor | `scripts/feature_loop.py measure` | Reads current spec/plan/tasks; optional Python compileall and unittest. Reports missing artifacts, unmapped requirement IDs, duplicate task IDs and regression failures |
| Deterministic controller signal | `scripts/feature_loop.py next --run-checks` | Reports BLOCKED, PLAN_OR_RECONCILE, RUN_BASELINE, DIAGNOSE, IMPLEMENT_ONE or VERIFY_RELEASE |
| Actuator | **One Codex agent** working on a single accepted task with existing Spec Kit skills | Codex must inspect dependencies, risks and actual source; deterministic selection does not replace engineering judgment |
| Feedback | Test result + requirement gap + source diff; record task completion and evidence in canonical `tasks.md`/`plan.md` | Remeasure after every increment; distinguish genuine progress from changed test expectations |
| Disturbance/dampener | Prior regression failures preempt new work; rerun tests and review diff | Existing suite is incomplete for transcript/Windows UI; add acceptance fixtures and runtime verification |
| Execution runtime | Current interactive Codex session | External Ralph/Symphony and unattended iteration **not installed or verified** |

### Windows commands (no new tools)

Run from the repository with its **existing** Python interpreter (Python 3.10+). Example if the repo already has `.venv`:

```powershell
.\.venv\Scripts\python.exe scripts\feature_loop.py measure
.\.venv\Scripts\python.exe scripts\feature_loop.py next --run-checks
.\.venv\Scripts\python.exe -m unittest tests.test_feature_loop -v
```

If no such venv exists, Codex must identify the interpreter already used by the app; new tool installation requires separate user authorization. `--run-checks` executes only fixed syntax and unittest commands with subprocess timeouts, not external network smoke. The syntax check may generate normal ignored `__pycache__` files. A nonzero exit indicates checks failed or a blocking structural finding; parse JSON for the cause. The existing YouTube smoke is skipped by default.

**Guarantee boundary:** Explicit FR/SC mentions in tasks are structural traceability, NOT proof the right feature tests exist. `PASS_WITH_SKIPS` is not a full test pass. `VERIFY_RELEASE` means *run final acceptance* and is **not** a release certificate. Full pagination, subtitle semantics, native Windows GUI, packaging, user permissions, external reviews and optional ASR require their own actual evidence.

## End-to-end control policy for Codex

1. Inspect live worktree and existing tool registration, then read `AGENTS.md`, Product, Roadmap, Spec, the workflow and this control contract. Preserve unrelated changes; do not assume connected GitHub/Linear/Qodo from ChatGPT implies connectivity locally.
2. **Before feature implementation:** resolve feature pointer with `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` and inspect `specify integration status --json`. Measure actual current state rather than assuming a controller result. If the selected feature lacks plan/tasks, use the installed Spec Kit skills to create them from source-backed decisions and all FR/SC identifiers; otherwise continue the existing artifacts. Do not create a competing spec or silently bypass Spec Kit's human review gates.
3. Perform `next --run-checks`. Treat controller result as **proposal only**: confirm task dependencies, approved requirements, change budget and exit test. For `PLAN_OR_RECONCILE` fix missing traceability; for `DIAGNOSE` correct regressions before taking new work; for `IMPLEMENT_ONE` implement a reviewable increment with the needed real behavioral tests.
4. Measure after every change; compare before/after, preserve existing download behavior, mark a checkbox complete only after evidence. When two failed repairs share an assumption, apply **Pstack attack-the-premise**: state the premise and find an observation that distinguishes whether it is false before writing another fix. Three repeated failures is a resource ceiling, not the engineering design.
5. If controller returns `VERIFY_RELEASE`, separately execute all feature acceptance contracts, required true-user desktop/UI verification, installer, completeness manifest, security and independent review. Mark absent evidence NOT_RUN/BLOCKED; never fake success.
6. Stop on missing product decision, credentials, explicitly reserved human approval, unsafe operation, exhausted budget or irrecoverable environment; continue independent authorized work and hand off precise blockers and worktree state. No agent commits/push/releases.

## Expected outputs on every increment

**Observation** (exact check, fixture, PASS/FAIL/SKIPPED/BLOCKED, revision) → **measured gap** (specific FR/SC mismatch) → **controller decision** (one small, dependency-safe correction) → **actuation** (source diff and targeted test) → **feedback** (repeat same check and regression) → **checkpoint or documented halt**. Never conflate the changed source with the checked behavior.

## Historical pre-implementation gap register — initial assessment

| Issue | Evidence/state | Agent action |
|---|---|---|
| Spec Kit integration | Existing `workflow.yml` previously omitted Codex in advertised allowlist | Added `codex`; retain all user approval gates |
| Active feature | `.specify/feature.json` pinned to transcript directory | Verify actual Windows checkout path, don't overwrite local work |
| Product plan/tasks | `plan.md` / `tasks.md` missing on published main | Generate with Spec Kit after evidence review, map FR/SC to tests and tasks |
| Core download regression | Existing Python unittest suite present | Establish passing pre-change result; some live smoke tests skip |
| Transcript acceptance suites | Not implemented yet | Implement offline full-pagination, language, export, resume, UI and security tests |
| Library assumptions | yt-dlp and Qt runtime versions vary by host | Inspect installed versions and official source, no invented extractor promises |
| Complete archive | Discovery semantics not yet proven | Enumerate supported continuations to terminal state; label partial/inaccessible |
| ASR | Conditional capability; no approved backend/model | Do not silently install large models/cloud services; implement safe missing-caption state |
| Windows deliverable | PyInstaller/Inno scripts exist, but `build_exe.py` deletes `build/` and `dist/` | Inspect user-owned outputs before destructive build; run installed app smoke |
| HumanLayer/Pstack skill install | User reports installing a skill, precise inventory unknown | Detect local files and available Codex skills; don't install anything tonight |
| REA | Global REA skill installed; setup chose no agent integrations | Conditionally use only when authorized and operational |
| Linear/Qodo | ChatGPT Linear project exists; Codex MCP/reviewer unverified | Keep issue updates/review as explicit pending until confirmed |
| Autonomous runner | No verified Ralph TUI/Symphony service on Windows | Do not claim background/overnight loops; evaluate tomorrow separately |
| Spec Kit human gates | Original YAML has three approval gates | Do not impersonate approval or run gated YAML unattended |
| End-to-end quality | Existing tests cannot prove all FR/SC requirements | Independent criterion-to-test mapping, real user journey and release proof |
| Reproducibility | Current repo uses Python requirements; no accepted pin policy | Choose compatible pins and reusable skill references after actual evidence |

**Tomorrow's optional tool queue (not an installation task tonight):** HumanLayer/Pstack skills where missing, pytest-qt/Ruff where justified by tests, then compare Ralph TUI with Codex native headless facilities and Symphony given Windows constraints and user preference for a single agent. Exactly one runner should own task iteration. The Git repo owns canonical tasks; Linear mirrors them, not a second untrusted task source.


## Current worktree note (2026-10-16)
Historical references above to missing plan/tasks or unimplemented transcript suites describe the initial repository assessment. The current worktree contains the implementation, plan/tasks and deterministic/native acceptance suites. Use the latest production-hardening section of specs/transcript-extraction/plan.md and its task checkpoints for actual capabilities and evidence; do not recreate artifacts or interpret historical NOT_RUN/tool absence as current state. Build entrypoints now preserve existing outputs and require fresh destinations. Pstack is configured with the human-selected inherit-parent roles; no external autonomous runner is configured.
