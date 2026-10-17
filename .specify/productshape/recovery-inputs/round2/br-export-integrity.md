---
id: BR-EXPORT-INTEGRITY
type: business-rule
title: Reuse only verified transcript products and preserve differing files
status: draft
applies-to: [UC-TRANSCRIPT-BATCH]
provenance:
  source: specs/transcript-extraction/plan.md
  confidence: high
  recovered-from: documentation
---

## Rule

Documented: a previously completed transcript product may be skipped or reused only after all selected output files match their recorded hashes. Interrupted runs preserve completed products. An existing differing file is preserved and reported as a conflict; it is never overwritten merely to make a retry succeed.

## Rationale

The plan, quickstart and research require resumable, idempotent work without data loss. A completed status alone cannot prove that files still contain the verified transcript.

## Examples

- Resume with the same inputs and choices: verified successes are reused without duplicate products.
- A user edits an exported file: integrity verification fails visibly and preserves the edited file.
- Cancellation after one selected format is written: a later explicit resume may reuse byte-identical content and finish remaining formats.

## Exceptions

None. Selecting different inputs or choices identifies a different batch; it does not authorize overwriting another product.
