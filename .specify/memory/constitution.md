# Video Downloader Constitution

Version: 1.0.0
Ratified: 2026-10-16
Last amended: 2026-10-16

## I. User-visible correctness and truthful coverage
Every promised link class and export option requires an observable result with status and provenance. Full channel/playlist means iteration until verified pagination termination for accessible entries, not feed size or guessed total. Represent undiscoverable/unavailable and incomplete scans honestly. Requirements have stable IDs and verification evidence.

## II. Preserve the existing production application
Extend the existing Windows 10 PySide6 + yt-dlp application. Keep existing video/audio formats, queue, progress, cancellation, browser-cookie fallback, local storage, history/logging and distributable installer functioning. Reuse maintained libraries and actual code before introducing layers. Do not copy HBC-only governance/requirements.

## III. Safety and privacy
Operate within user permissions and source-site access controls. Don't circumvent DRM, access checks or rate limits. No hidden uploads, payment, credential transfer, or external application mutation. Sanitize hostile video metadata, timestamps, caption text and filesystem paths. Keep raw credentials and signed URLs out of logs. Opt-in ASR is local-only unless the user explicitly authorizes another processor.

## IV. Evidence-led design and verification
Requirements → plan → task → test traceability is mandatory. Use official API/source evidence when available. Resolve critical product/technical gaps before dependent implementation. Verify relevant behavior with deterministic tests and host integrations; missing/blocked/skipped tests are NOT_RUN or BLOCKED, never PASS. Repair diagnosed causes in bounded loops, not random experiments.

## V. One owner per decision; minimal ceremony
`PRODUCT.md` owns product promise, `ROADMAP.md` admission, feature `spec.md`/`plan.md`/`tasks.md` own feature design/execution, `LOGIC_VERIFICATION.md` and `IMPLEMENTATION_VERIFICATION.md` own verification policy, and `docs/workflows/transcript-feature.md` owns end-to-end execution sequencing. Skills and connected tools are capabilities, not a second policy. Prefer existing implementation and test tooling to bespoke abstractions.

## VI. Controlled autonomous work
Codex may implement and run local verification for authorized scope. No commit, push, release, payment, new credentials, destructive operation or new tool installation unless separately authorized by the user. Existing approval gates remain gates; unattended mode cannot silently impersonate user approval. Report unresolved blockers with independently completed work. User owns Git publishing and final release sign-off.

## Governance
Changes to this constitution require explicit rationale, impact on ongoing acceptance, and user approval for any relaxation of non-negotiable principles. Validate all new specs and code against it.
