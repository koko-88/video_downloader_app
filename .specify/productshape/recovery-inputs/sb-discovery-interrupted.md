---
id: SB-DISCOVERY-INTERRUPTED
type: structured-behaviour
title: Keep interrupted discovery incomplete
status: draft
illustrates: [UC-TRANSCRIPT-BATCH, BR-ARCHIVE-COVERAGE]
given:
  - "An accessible collection has yielded some video entries"
  - "Its discovery iterator has not exhausted"
when: "The collection scan is interrupted"
then:
  - "The input retains an incomplete discovery state"
  - "Already discovered video results remain accounted for"
  - "The application does not report complete archive coverage"
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Intent

Separate evidence of discovered entries from proof of an exhausted accessible feed.

## Boundaries

Only entries returned by the supported provider are in scope; hidden or private identities are not invented.
