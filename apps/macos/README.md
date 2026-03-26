# macOS App Scaffold

This directory contains the native macOS shell for Voice-to-Screen.

## Current Scope

The scaffold is intentionally narrow:

- SwiftUI app entry point
- floating overlay shell
- session configuration controls
- mock transcript rendering
- pipeline client boundary for a future local backend process

## Next Steps

1. Replace the mock pipeline client with a real process bridge.
2. Add always-on-top and click-through window controls.
3. Add audio-device and model selection UI.
4. Add first-run `BlackHole` guidance.
