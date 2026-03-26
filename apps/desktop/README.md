# Python Desktop App

This is the primary app shell for local development.

It replaces the Swift scaffold with a Python-first desktop app built on `PySide6`, so the UI and pipeline can be developed without Xcode.

## Current Scope

- frameless floating overlay window
- always-on-top desktop shell
- opacity control
- compact or dual caption view
- speaker label toggle
- pipeline subprocess bridge
- live rendering of mock pipeline events

## Run

```bash
cd apps/desktop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m voice_to_screen_app.main
```

## Next Steps

1. Replace the stub pipeline with real audio ingestion.
2. Add real click-through behavior on macOS.
3. Add system-audio device selection and `BlackHole` guidance.
4. Add live rolling correction rather than append-only updates.
