---
id: SB-CAPTIONS-ABSENT
type: structured-behaviour
title: Report unavailable optional speech recognition
status: draft
illustrates: [UC-TRANSCRIPT-BATCH, CON-LOCAL-AUTHORITY]
given:
  - "No source caption tracks are available"
  - "The user explicitly selected local speech recognition"
  - "No verified local backend and model are available"
when: "The user extracts the transcript"
then:
  - "The result reports caption absence and local speech-recognition unavailability"
  - "No transcript success is recorded"
  - "No cloud transcription or model download occurs"
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Intent

Keep the optional capability boundary explicit instead of silently claiming a transcript.

## Boundaries

This example does not establish an installed ASR backend or successful speech transcription.
