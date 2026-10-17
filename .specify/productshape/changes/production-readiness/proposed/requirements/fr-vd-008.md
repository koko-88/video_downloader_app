---
id: FR-VD-008
type: functional-requirement
title: "Persist verifiable transcript state and disjoint outcomes"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH, BR-EXPORT-INTEGRITY]
verification:
  - scenario: "The manifest records sources, tracks, output hashes and independent input discovery states; totals reconcile, edited outputs fail integrity checks and malformed state is preserved without mutation."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-008): Persist a resumable per-video result manifest with input/source/track/output provenance and disjoint status for succeeded, caption_absent, inaccessible, failed, pending; record discovery completion state independently. (US-02/03/07/09)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

