---
id: SB-LANGUAGE-UNAVAILABLE
type: structured-behaviour
title: Distinguish a missing requested language
status: draft
illustrates: [UC-TRANSCRIPT-BATCH]
given:
  - "The source offers captions in another language"
  - "The exact requested language has no selected track"
when: "The user extracts captions in the requested language"
then:
  - "The result reports language unavailable"
  - "No successful transcript product is claimed"
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Intent

Preserve the difference between absent captions and an unavailable requested language.

## Boundaries

No implicit alternate language or speech-recognition fallback is asserted.
