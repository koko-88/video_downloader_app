---
id: FR-VD-007
type: functional-requirement
title: "Keep transcript progress, cancellation and recovery interactive"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH, BR-EXPORT-INTEGRITY]
verification:
  - scenario: "The native event loop stays responsive during scanning, extraction and export; cancellation preserves work, explicit resume reuses verified products and failed-only retry leaves other records unchanged."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-007): Provide interactive UI progress for scan vs per-video extraction vs conversion; cancel and resume an interrupted batch and selectively retry failed items. Keep UI thread responsive. (US-07/10)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

