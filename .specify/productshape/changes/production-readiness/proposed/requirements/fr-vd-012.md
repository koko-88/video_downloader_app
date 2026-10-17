---
id: FR-VD-012
type: functional-requirement
title: "Report discovery and processing coverage truthfully"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH, BR-ARCHIVE-COVERAGE]
verification:
  - scenario: "Discovered equals succeeded plus caption_absent plus inaccessible plus failed plus pending; attempted and exported remain distinct, and partial feeds never become complete-archive claims."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-012): Report video discovery/attempt/process/export counts correctly and include reasons for failures or not-run cases, never equating RSS feed results or yt-dlp enumeration attempts with full verified archive. (US-02/03/08)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

