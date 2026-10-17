---
id: CHG-INITIAL
type: product-change
title: Recover existing Video Downloader product contract
status: draft
base-revision: '1bacfa3e9821e1fdc27c24ece9bf00210360899a'
operations:
  add:
    - ACT-DESKTOP-USER
    - CON-LOCAL-AUTHORITY
    - QR-DESKTOP-RELIABILITY
    - QR-SECURITY
    - FR-VD-001
    - FR-VD-002
    - FR-VD-003
    - FR-VD-004
    - FR-VD-005
    - FR-VD-006
    - FR-VD-007
    - FR-VD-008
    - FR-VD-009
    - FR-VD-010
    - FR-VD-011
    - FR-VD-012
    - UC-MEDIA-DOWNLOAD
    - UC-TRANSCRIPT-BATCH
    - BR-EXPORT-INTEGRITY
    - BR-ARCHIVE-COVERAGE
    - SB-RESUME-VERIFIED
    - SB-DISCOVERY-INTERRUPTED
    - SB-LANGUAGE-UNAVAILABLE
    - SB-CAPTIONS-ABSENT
  modify: []
  remove: []
---

## Problem

The existing product/specifications describe production obligations, while workflow status and runtime evidence differ. There is no accepted ProductShape baseline.

## Intended Product Outcome

A single draft graph expresses existing downloads, complete accessible transcript discovery, format/language selection, resumable results, privacy and truthful Windows delivery gates.

## Rationale

The human requested a full production gap review, confirmed repository-first recovery boundaries, authorized repository-local CLI installation, and authorized implementation with reviewer checklist items still unchecked. This graph recovers existing intent; existing PRODUCT/ROADMAP scope separately authorizes engineering corrections.

## Affected Product Areas

Desktop downloads, captions, archive coverage, exports, recovery, local processing, privacy and release verification.

## Open Questions

None for the recovered product meaning. Engineering evidence and remaining delivery gates are owned by the canonical feature plan; this draft does not authorize or certify release.

## Product Acceptance

The draft graph validates and traces back to repository sources with high documentation confidence. Human product approval remains pending. No accepted model is changed.

## Out of Scope

New ASR backend/model, cloud processing, arbitrary-webpage guarantees, account changes, publication, deployment and accepted-model apply/archive. This change does not grant release acceptance.
