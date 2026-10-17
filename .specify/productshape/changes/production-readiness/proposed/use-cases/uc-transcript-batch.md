---
id: UC-TRANSCRIPT-BATCH
type: use-case
title: Collect and export accessible video transcripts
primary-actor: ACT-DESKTOP-USER
governed-by: [BR-EXPORT-INTEGRITY, BR-ARCHIVE-COVERAGE]
status: draft
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Goal

Documented: collect captions from supported single videos, complete accessible playlists, channel Videos archives and mixed inputs.

## Trigger

The user starts or resumes transcript extraction.

## Preconditions

The user supplies supported URLs, writable storage, exact language and at least one export format.

## Main Flow

1. Supply URLs, output folder, exact language, track preference and selected export formats.
2. Discover accessible entries through observed continuation exhaustion, retaining per-input coverage and failures.
3. Acquire captions without downloading rendered media, then export Unicode MD/TXT/JSON/SRT/VTT with provenance.
4. Inspect disjoint results and durable counts; cancel, resume or retry failures without duplicate or overwritten products.

## Alternative Flows

Documented: distinguish absent captions, missing requested language, unsupported representations and provider failures. Optional local ASR requires explicit selection and verified backend/model; unavailable capability is reported honestly.

## Failure Conditions

Missing language, absent captions, denied content, interrupted discovery, malformed captions and output conflicts retain explicit non-success reasons and preserve existing files.

## Postconditions

Outputs and manifest reconcile; partial discovery never claims complete archive coverage.

