# Voice-to-Screen v1 Specification

## Product Goal

Build a local-only macOS overlay app for Apple Silicon that captures routed system audio, transcribes speech from a user-selected source language, and displays rolling English translation over video content in near real time.

The primary use case is watching movies, podcasts, livestreams, or other spoken media in a foreign language while reading live English captions in a floating, semi-transparent window.

## Confirmed Scope

- Input source: routed system audio via a virtual audio device such as `BlackHole`
- Platform: `macOS` on `Apple Silicon`
- UX shell: floating semi-transparent window over other apps
- Flow priority: low latency and readability over perfect accuracy
- Translation mode: live rolling captions with correction
- Source language: manually selected by the user
- Output language: English only for v1
- Transcript view: dual view for testing, with future compact translation-only mode
- Speaker persistence: session-local only
- Model selection: automatic download with user-facing model size choice

## Non-Goals for v1

- Cloud APIs or remote inference
- Mixed-language input in one session
- Cross-session speaker identity persistence
- Full subtitle editor workflows
- Broad export workflows beyond basic debug needs

## UX Requirements

### Overlay Window

- Always-on-top
- Semi-transparent background
- User-adjustable opacity
- User-resizable
- User-draggable
- Optional click-through lock mode
- Fast show/hide control
- Minimal visual footprint suitable for video overlay

### Modes

#### Compact Mode

- English translation only
- Minimal controls
- Intended for normal use while watching content

#### Dual Mode

- Left pane: source transcript
- Right pane: English translation
- Speaker labels visible
- Intended for testing, tuning, and debugging

### Session Controls

- Start/stop session
- Select system audio input device
- Select source language
- Select model tier
- Toggle compact/dual mode
- Toggle click-through
- Adjust opacity
- Adjust font size
- Toggle speaker labels
- Toggle experimental speaker gender hints

## Functional Requirements

### Audio Capture

- Capture audio from a user-selected routed system input device
- Support `BlackHole`-based workflows
- Normalize incoming audio to the sample format expected by the speech pipeline
- Process audio continuously with bounded buffering
- Handle short audio interruptions gracefully

### Transcription

- Use a local speech recognition engine suitable for Apple Silicon
- Produce incremental transcript updates
- Distinguish between draft and stabilized transcript segments
- Reprocess recent context to improve wording and punctuation
- Respect the user-selected source language

### Translation

- Translate transcript output to English locally
- Emit draft translations quickly
- Update recent translations when transcript segments are corrected
- Prefer stable flow over frequent full-line rewrites

### Speaker Separation

- Perform session-local diarization
- Show speaker labels in the overlay
- Keep labels stable within the session when possible
- Do not persist identities across launches

### Speaker Gender Hints

- Optional experimental feature
- Off by default
- Display as probabilistic hints only
- Must degrade cleanly to neutral speaker labels

### Model Management

- Present user-facing size/performance options on first run
- Download selected models locally
- Store models under an app-managed directory
- Surface estimated disk usage and expected speed
- Permit future model upgrades without restructuring the app

## Quality Targets

### Latency

- Initial draft captions should appear quickly enough to feel live
- System should favor short rolling updates rather than long delayed batches
- Corrections should be limited to a recent window to reduce visible churn

### Readability

- Captions should be line-broken for reading, not raw token dumps
- Older lines should stabilize instead of constantly shifting
- Speaker changes should be visible without dominating the overlay

### Privacy

- All audio processing, transcription, diarization, and translation must stay local
- No cloud translation or telemetry required for core functionality

## Recommended Technology Direction

### App Shell

- `SwiftUI` for native macOS overlay behavior and window management

### Backend Runtime

- `Python` local service for model orchestration and pipeline iteration speed

### Transcription Engine

- Default direction: `faster-whisper`
- Alternative fallback for future evaluation: `whisper.cpp`

### Translation Engine

- Local translation engine with downloadable open-source models
- Must support incremental English translation for the selected source language

### Diarization Engine

- Local diarization pipeline with clear separation from the transcription engine
- Treated as optional but planned from the start

## Pipeline Behavior

1. Capture continuous system audio.
2. Chunk audio into short rolling windows.
3. Run low-latency transcription on fresh audio plus short retained context.
4. Emit draft transcript segments.
5. Assign diarization labels to the same time-aligned region.
6. Translate transcript segments into English.
7. Publish updates to the UI as `draft`, `revised`, or `final`.
8. Freeze older segments after a stabilization threshold.

## Data Model Concepts

### SessionConfig

- input device id
- source language
- target language
- model tier
- compact or dual mode
- overlay preferences
- diarization enabled
- gender hints enabled

### AudioChunk

- chunk id
- session id
- start timestamp
- end timestamp
- sample rate
- channels
- raw PCM payload reference

### TranscriptSegment

- segment id
- start timestamp
- end timestamp
- text
- speaker label
- status: `draft | revised | final`
- confidence if available

### TranslationSegment

- source segment id
- translated text
- status: `draft | revised | final`

## Stability Rules

- New text can revise recent lines
- Older lines should be frozen after a short window
- UI updates should patch existing segments rather than re-render everything
- Speaker labels should remain stable unless confidence is low

## Packaging Direction

Preferred packaging approach:

- Native `SwiftUI` app bundle
- Embedded or managed Python runtime for the backend
- App-managed model directory
- First-run setup flow for:
  - dependency bootstrap
  - model selection and download
  - `BlackHole` routing guide

## Accessibility and Usability

- High-contrast caption theme option
- User-adjustable text size
- Keyboard shortcuts for core actions
- Compact mode suitable for small displays
- Clear visual indication when the app is in click-through mode

## Risks and Unknowns

### System Audio Routing

macOS system audio capture is operationally dependent on virtual routing. The app should document and guide `BlackHole` setup rather than treating capture as invisible magic.

### Translation Model Tradeoffs

The final engine choice may change after benchmarking. Translation quality, cold start time, and incremental update behavior need direct testing.

### Diarization Latency

Speaker separation can add delay or instability. It should be isolated behind a clean module boundary so it can be disabled or replaced without affecting the rest of the app.

### Gender Classification

Voice-based gender inference is error-prone and should remain optional and clearly marked as experimental.

## Phased Delivery

### Phase 1

- SwiftUI floating overlay
- system audio device selection
- `BlackHole` setup guidance
- source transcript + English translation
- dual view
- rolling correction logic
- balanced model default

### Phase 2

- compact translation-only mode
- session-local speaker diarization
- overlay polish
- model manager UI
- better line segmentation and stabilization

### Phase 3

- optional experimental speaker gender hints
- performance tuning
- debug export
- longer-session reliability improvements

## Immediate Next Step

Build around a modular service boundary, not around the current prototype. The next implementation artifact should be an architecture skeleton that separates:

- macOS app shell
- audio ingestion
- transcription engine
- translation engine
- diarization engine
- shared event/state transport
