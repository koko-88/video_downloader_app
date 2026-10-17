---
id: QR-DESKTOP-RELIABILITY
type: quality-requirement
title: Responsive and recoverable Windows desktop operation
quality-attribute: reliability
applies-to: [UC-TRANSCRIPT-BATCH, UC-MEDIA-DOWNLOAD]
verification:
  - scenario: Cancellation and resume preserve completed products and the native UI remains responsive; packaged Windows acceptance runs against the delivered artifact.
  - scenario: Malformed saved download preferences do not prevent native window startup; valid independent transcript choices and supported legacy preferences survive loading.
  - scenario: Every supported MP3 bitrate choice survives saved-settings loading and busy-to-idle UI transitions.
  - scenario: A failed history update preserves existing history, reports the limitation and lets completed media and subsequent queued jobs finish correctly.
status: draft
provenance:
  source: specs/transcript-extraction/spec.md
  confidence: high
  recovered-from: documentation
---

## Requirement

Documented: preserve existing downloads, keep UI responsive, maintain resumable manifests and validate the real packaged Windows runtime.

## Measurement

SC-003/004 require zero duplicate completed outputs, no data loss, original download regression and actual installed Windows behavior. Compilation and unit tests cannot certify live provider or installer acceptance.

