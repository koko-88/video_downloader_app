---
id: FR-VD-004
type: functional-requirement
title: "Select exact-language manual or automatic caption tracks"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH]
verification:
  - scenario: "Manual-first and auto-first honor the exact requested language; a missing requested language differs from no caption tracks, and selected track provenance is retained."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-004): Select available manual/automatic subtitle tracks by explicit language and preference; preserve track source and provenance. Do not mark language-unavailable as caption-absent. (US-05)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

