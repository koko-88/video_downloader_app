---
id: FR-VD-001
type: functional-requirement
title: "Validate supported URLs and preserve source identity"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH]
verification:
  - scenario: "Supported named-extractor URLs and unsupported or credential-bearing inputs receive independent explicit results without arbitrary-page support claims."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-001): Validate and classify each user-provided URL via supported extractor behavior; preserve original URL and normalized target identity; unsupported inputs receive explicit failure, not arbitrary-webpage promises. (US-01/04/09)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

