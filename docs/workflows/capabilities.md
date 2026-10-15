# VD-02 — Explicit capability routing and preflight

**Purpose:** eliminate tool-name guessing and make all workflow stages resolve actual inputs/outputs. This catalog is a map of known repo paths and external entrypoints, NOT a claim that every external agent/tool is connected locally. Keep relevant source docs authoritative. Do not install/update anything during preflight without user authorization.

## Stage-to-capability contract

| Stage | Required capability | Exact available entry point | Activation/condition | Evidence and exit gate |
|---|---|---|---|---|
| 0 — inspect | Git/current worktree + Python package structure | `git status --short`; `git branch --show-current`; `app/main_window.py`, `app/download_queue.py`, `app/downloader_worker.py`, `app/ydl_options.py`, `app/formats.py`, `tests/` | Always | Snapshot actual present code and baseline regression; protect local modifications |
| 0 — integrations | Spec Kit native integration and skills | `specify integration status --json`; `.specify/integration.json`; `.agents/skills/speckit-*/SKILL.md`; `.specify/feature.json` | Always; preserve 32 previously reported modified managed files until reviewed | Missing=0 and exact feature target resolved; modified is not automatically broken |
| 1 — source | yt-dlp, PySide6 and Python installed code and official documentation | `.\.venv\Scripts\python.exe -m yt_dlp --version`; `.\.venv\Scripts\python.exe -m pip show yt-dlp PySide6 yt-dlp-ejs`; official yt-dlp/PySide6 docs | Always for relevant decisions | Versioned evidence about supported extractor/track/pagination and event threading |
| 1/3 — conditional REA | REA reverse engineering of permitted external app behavior | Reported user skill: `$HOME\.agents\skills\reverse-engineer-anything\SKILL.md`; `npx rea-agents capabilities`; `codex mcp list` | ONLY when selected external closed-source target requires it and official source/docs insufficient. User's setup selected **none** for agent integrations. CLI skill presence != MCP registration | Evidence-backed observation with permissions/limitations; if no target, skip by design |
| 2/4 — product | Source of intent | `PRODUCT.md`, `ROADMAP.md`, `specs/transcript-extraction/spec.md`, `.specify/memory/constitution.md` | Always | Stable FR-/SC- IDs, no product contradictions or holes |
| 4 — feature | Spec Kit planning / tasks / analysis | `.agents/skills/speckit-plan/SKILL.md`, `speckit-tasks`, `speckit-analyze`, `speckit-checklist`, `speckit-clarify` if needed, `speckit-implement`, `speckit-converge` | Call installed Codex skills by actual name in session; never assume invoking a CLI subcommand named `specify plan` has same behavior | `plan.md`, `tasks.md`, analysis report and requirements↔tests mapping; gate before implementation |
| 5 — implement | Existing PySide6/yt-dlp queue and worker | `app/main_window.py`, `app/download_queue.py`, `app/downloader_worker.py`, `app/ydl_options.py`, `app/formats.py`, `app/config.py`, `app/cookie_fallback.py` | Always. Agent chooses smallest sound architecture after source/plan | Requirement/fixture-targeted code and verified application integration |
| 5 — loop | Native Codex session + deterministic Python test runner | The current Codex coding session; `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`, compileall; `docs/verification/acceptance.md` | Loop within the active, authorized session. No separate Ralph required by default; separate unattended process is NOT configured | Bounded task PASS/FAIL/BLOCKED with original failure root-cause and checkpoint |
| 6 — review | Spec Kit convergence / independent reviewer | `.agents/skills/speckit-converge/SKILL.md` and `IMPLEMENTATION_VERIFICATION.md`; optional Qodo installed tool if available | Qodo availability/permissions/plan **unverified** for this session. Do not assume free remediation/PR access | Independent review outcome or PENDING; do not call unreviewed release complete |
| 6 — Windows deliver | PyInstaller / Inno Setup / installed EXE | `build_exe.py`, `build_installer.py`, `installer/VideoDownloader.iss`, `video_downloader.spec` | Windows, verified dependencies, inspect `build/` and `dist/` before tools which remove them | Build and installed binary/feature smoke, or exact BLOCKED/NOT_RUN |
| 0–7 — tracking | Linear | Project: https://linear.app/koko-88/project/video-downloader-transcript-extraction-and-export-cba592feaaa3 ; tasks `KOK-5`/`KOK-6`/`KOK-7`/`KOK-8` | Connected in ChatGPT; NOT verified inside local Codex. Verify `codex mcp list` and a real read before using. Official Codex endpoint `https://mcp.linear.app/mcp`; setup requires explicit user action/login if absent | Mirror verified progress and blockers; never invent updates or duplicate task ledger |
| reproducibility | mise | `mise --version`, `mise tasks ls`; source project has separate web-specific mise.toml | User reports mise installed; target has no verified pinned toolchain yet. Do NOT copy web project's Node/graphics pins | Select target-specific versions only after inspecting existing Python/runtime/installer constraints |

## Safe, no-install Windows preflight

Run in PowerShell from repository root, capture exact stdout/stderr and exit codes:

```powershell
git status --short
git branch --show-current
specify integration status --json
.\.specify\scripts\powershell\check-prerequisites.ps1 -Json -PathsOnly
Test-Path "$HOME\.agents\skills\reverse-engineer-anything\SKILL.md"
codex mcp list
mise --version
.\.venv\Scripts\python.exe -m yt_dlp --version
.\.venv\Scripts\python.exe -m pip show yt-dlp PySide6 yt-dlp-ejs
```

If unavailable, mark the individual capability ABSENT/BLOCKED and continue independent tasks; never automatically invoke a package installer. On Windows PowerShell 5.1 prefer executing `.\.specify\scripts\powershell\check-prerequisites.ps1` directly only when local execution policy permits it. Its `-PathsOnly` mode is read-only. Expect resolved FEATURE_DIR to end in `specs\transcript-extraction`. If it doesn't, stop write-oriented Spec Kit skills and reconcile feature context first.

### Spec Kit detail

The checked-in `.specify/feature.json` explicitly selects `specs/transcript-extraction` without requiring a new Git feature branch. A pre-existing `.specify/workflows/speckit/workflow.yml` has human approval gates; its presence does not automatically schedule an unattended loop. Avoid rerunning `speckit-specify` in a mode that creates a new feature directory/branch when the existing VD-02 spec already exists. Follow the installed skill semantics and resolve selections before writing. Original managed files were reported modified in 32 locations in both copied and source workspaces; do not run `specify integration upgrade --force` reflexively.

### REA setup distinction

User's last REA setup installed the global skill and explicitly selected `none` in "Which agents should use REA?". That is success for instructions, not verified MCP integration in Codex. If an authorized RE target actually requires REA, check connected MCP tool schema or CLI capability list (e.g. `npx rea-agents capabilities`) and collect attributable evidence. Do not rerun setup, install Java/Ghidra/Hopper or elevate privilege automatically. Windows native reverse engineering may have narrower support than JavaScript/Electron inspection; defer to installed version/provider support.

### Linear and Qodo distinction

Linear tracking was created from ChatGPT, but local Codex authentication is independent. Do not claim a Linear issue was updated without a successful tool result. If an explicit user connection is needed, record as permission blocker and continue coding/repo work. Qodo is independent code review if actually callable, not an engine to implement or remediate, and its absence cannot be "fixed" with fabricated review evidence. If available via a real Codex MCP or CLI, inspect the actual tool schema and permitted scope; never invent tool names or use authenticated actions without authorization.

### Decision rule

No unverified tool is mandatory merely because it is installed or popular. A capability is mandatory only when the accepted requirement depends on its unique proven output. Official library APIs and existing app code beat speculative REA probing. The smallest evidence-backed stack wins; a separate Ralph runner is considered only if the current Codex session cannot safely provide required bounded continuations with durable progress.

### Sources (starting points; verify installed-version compatibility)

- yt-dlp: https://github.com/yt-dlp/yt-dlp
- PySide6 Qt threads/signals: https://doc.qt.io/qtforpython-6/
- Spec Kit: https://github.com/github/spec-kit
- REA: https://github.com/morluto/rea
- Linear MCP for Codex: https://linear.app/docs/mcp
- Existing project tests, scripts and package metadata are the local authority for the installed application.
