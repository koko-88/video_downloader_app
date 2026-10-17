---
id: FR-VD-009
type: functional-requirement
title: "Report unavailable optional local speech recognition honestly"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH]
verification:
  - scenario: "Selecting local ASR with absent captions and no verified backend/model produces an explicit unavailable outcome without a transcript success, cloud call or model download."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-009): Optional local ASR for truly missing tracks only under an explicit user-selected mode with installed backend/model verification and storage/performance/package constraints. Never silently run paid/cloud transcription, and never call missing captions a completed transcript. (US-08)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

