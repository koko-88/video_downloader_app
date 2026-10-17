---
id: UC-MEDIA-DOWNLOAD
type: use-case
title: Download existing video and audio formats
primary-actor: ACT-DESKTOP-USER
status: draft
provenance:
  source: PRODUCT.md
  confidence: high
  recovered-from: documentation
---

## Goal

Documented: retain the existing sequential multi-URL download workflow for MP4/WEBM video and MP3/M4A audio.

## Trigger

The user starts the existing download queue.

## Preconditions

A supported accessible media link, writable folder and required local conversion dependencies are available.

## Main Flow

Choose URLs, format, quality and output directory, start the queue, inspect progress and history, cancel or retry as required.

## Alternative Flows

Cancel an active batch or retry failed jobs with selected format and quality. Browser-cookie fallback follows existing authorized access.

## Failure Conditions

Missing FFmpeg, inaccessible media and extraction failures are visible and do not become completed jobs.

## Postconditions

Successful local media files exist in the requested container with completed queue records. History is recorded when available; a history I/O failure preserves existing history and reports the limitation without invalidating completed media. Where source codecs cannot be remuxed to the selected video container, conversion fails visibly. Failures and cancellations remain distinct.

