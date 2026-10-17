---
id: FR-VD-006
type: functional-requirement
title: "Export Unicode cues into all selected transcript formats"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH]
verification:
  - scenario: "Ordered Unicode cues round-trip through selected SRT and VTT timestamps and produce the specified TXT, Markdown and JSON semantics without silent partial parsing."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-006): Convert valid cues into each user-selected MD/TXT/JSON/SRT/VTT with Unicode safety and meaningful timestamp/cue fidelity when timed format is chosen; expose selected format(s) in UI. (US-06)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

