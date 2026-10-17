---
id: SB-RESUME-VERIFIED
type: structured-behaviour
title: Resume verified transcript products
status: draft
illustrates: [UC-TRANSCRIPT-BATCH, BR-EXPORT-INTEGRITY]
given:
  - "A batch has completed transcript products whose recorded hashes match every selected output"
  - "The user keeps identical inputs and choices"
when: "The user resumes the batch"
then:
  - "Verified completed products are reused without duplicate output"
  - "Remaining pending records may continue"
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Intent

Preserve completed work and make explicit resume idempotent.

## Boundaries

A differing existing file is preserved and reported as a conflict; this example does not authorize overwriting it.
