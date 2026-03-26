# Module Boundaries

This document defines the intended project shape for a modular local macOS app with a native shell and a replaceable speech pipeline backend.

## Top-Level Layout

```text
Voice-to-Screen/
  apps/
    macos/
  services/
    pipeline/
  shared/
    schemas/
  docs/
```

## apps/macos

Native macOS application layer.

Responsibilities:

- floating overlay window
- session controls
- onboarding and setup UX
- model download UI
- preferences
- hotkeys
- rendering transcript and translation state
- IPC client for backend communication

Suggested internal modules:

- `OverlayWindow`
- `SessionControls`
- `PreferencesStore`
- `PipelineClient`
- `CaptionViewModel`
- `BlackHoleSetupGuide`

## services/pipeline

Local backend service coordinating capture and inference.

Responsibilities:

- audio ingestion from selected input device
- buffering and rolling chunking
- transcription
- diarization
- translation
- state reconciliation
- event streaming to the UI

Suggested internal packages:

- `audio/`
- `transcription/`
- `translation/`
- `diarization/`
- `orchestrator/`
- `models/`
- `events/`

## shared/schemas

Contracts shared between the app and the backend.

Responsibilities:

- session config schema
- pipeline event schema
- transcript and translation segment schema
- model metadata schema
- error schema

Recommended transport style:

- JSON-over-stdio for the first milestone, or
- local WebSocket if UI update complexity grows

## Core Interfaces

### AudioSource

Provides normalized audio chunks to the pipeline.

Methods:

- `start(config)`
- `stop()`
- `read_chunk()`

### TranscriptionEngine

Converts rolling audio into transcript segments.

Methods:

- `load(model_descriptor)`
- `transcribe(audio_window, context)`
- `close()`

### TranslationEngine

Translates transcript segments into English.

Methods:

- `load(model_descriptor)`
- `translate(segment, context)`
- `close()`

### DiarizationEngine

Assigns speaker labels to recent time windows.

Methods:

- `load(model_descriptor)`
- `assign_speakers(audio_window, transcript_segments)`
- `close()`

### EventPublisher

Streams pipeline state back to the UI.

Event types:

- `session_started`
- `session_stopped`
- `audio_level`
- `transcript_segment_added`
- `transcript_segment_updated`
- `translation_segment_added`
- `translation_segment_updated`
- `speaker_assignment_updated`
- `model_download_progress`
- `error`

## Parallel Work Split

This structure is designed so multiple people can work independently.

Workstream A:

- SwiftUI overlay and window behavior

Workstream B:

- audio capture and chunking

Workstream C:

- transcription engine integration

Workstream D:

- translation engine integration

Workstream E:

- diarization integration

Workstream F:

- shared schemas, IPC, and reconciliation logic

## Default v1 Decisions

- App/UI language: `Swift`
- Backend language: `Python`
- Input routing assumption: `BlackHole`
- Source language selection: manual only
- Target language: English only
- Model tier default: balanced
- Diarization persistence: session-local only
- Gender hints: optional experimental flag

## Implementation Order

1. Shared schemas and event transport
2. SwiftUI overlay shell
3. Audio ingestion and pipeline orchestrator
4. Transcription integration
5. Translation integration
6. Draft/revision/final segment stabilization
7. Diarization integration
8. Setup UX and model manager

## Rules for Future Changes

- Keep engines swappable behind interfaces
- Do not couple UI rendering to a specific model provider
- Keep segment IDs stable so the UI can patch lines in place
- Treat diarization and gender hints as enrichments, not core assumptions
- Keep local-only processing as a hard product invariant
