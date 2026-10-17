---
id: QR-SECURITY
type: quality-requirement
title: Protect local files and credentials
quality-attribute: security
applies-to: [UC-TRANSCRIPT-BATCH, UC-MEDIA-DOWNLOAD]
verification:
  - scenario: Hostile metadata and credentials never escape output confinement or appear in logs; existing user files survive retries.
  - scenario: A surfaced source rate limit stops further app-level browser, format and queued-job attempts; unattempted work remains visible for explicit user retry.
status: draft
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented: reject path traversal, unsafe output paths and malicious caption/metadata payloads; keep raw credentials, cookies and signed media URLs out of logs. Respect source access controls.

## Measurement

FR-011 and SC-006 require deterministic hostile-input, preservation and privacy checks plus independent review. Any unreached review remains NOT_RUN.

