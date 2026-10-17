---
id: FR-VD-003
type: functional-requirement
title: "Deduplicate videos while preserving every source association"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH]
verification:
  - scenario: "Repeated canonical video identities in mixed inputs are processed once per batch while all source associations remain recorded; changed choices identify a distinct batch."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-003): Deduplicate by extractor + canonical video identifier + source track and user choices; keep source URL associations for mixed inputs. (US-04/07)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

