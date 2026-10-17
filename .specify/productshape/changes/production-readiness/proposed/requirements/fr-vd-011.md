---
id: FR-VD-011
type: functional-requirement
title: "Protect output files, credentials and provider access boundaries"
status: draft
derived-from: [UC-TRANSCRIPT-BATCH, BR-EXPORT-INTEGRITY]
verification:
  - scenario: "Traversal and hostile filenames cannot escape the batch root, differing products survive retries, malicious content is safely rendered and credentials or signed URLs do not reach logs."
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented (FR-011): Avoid path traversal, dangerous filenames, malicious subtitle payloads, leaked auth cookies or signed media URLs in logs; respect accessible-site limits and rights. (US-09/10)

## Rationale

Preserve the repository product promise with observable obligations. This draft does not certify implementation or release readiness.

