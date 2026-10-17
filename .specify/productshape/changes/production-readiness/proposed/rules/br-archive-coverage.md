---
id: BR-ARCHIVE-COVERAGE
type: business-rule
title: Distinguish exhausted discovery from completed transcript processing
status: draft
applies-to: [UC-TRANSCRIPT-BATCH]
provenance:
  source: specs/transcript-extraction/research.md
  confidence: high
  recovered-from: documentation
---

## Rule

Documented: collection discovery is complete only after the accessible returned iterator terminates without interruption, warning, feed-loop diagnostic or known-count mismatch. Discovery completeness and per-video transcript outcomes remain separate. Discovered videos reconcile into mutually exclusive succeeded, caption_absent, inaccessible, failed and pending states; an enumeration attempt or exported subset does not prove a complete archive.

## Rationale

Provider feeds, access restrictions and caption availability expose different evidence boundaries. Users need to know whether missing results reflect undiscovered entries, unattempted work, inaccessible media or absent captions.

## Examples

- Exhaust three continuation pages and retain every returned identity before reporting discovery complete.
- A network interruption leaves discovery incomplete even when already discovered videos have exported successfully.
- A rate limit pauses further requests with remaining videos pending; successful discovery does not make those transcripts complete.

## Exceptions

None. The guarantee is limited to accessible returned entries; hidden or private identities are never invented to claim a larger archive.
