
# Voice-to-Screen: Real-Time Transcription and Translation

This project provides a real-time transcription and translation tool using **Vosk** for speech recognition and **GoogleTranslator** for translation. It features a graphical user interface (GUI) that displays both the transcription and translation in real-time, supporting multiple languages.

## Features

- **Real-time transcription**: Transcribes speech in real-time using the Vosk speech recognition library.
- **Real-time translation**: Translates the transcribed text into a target language using the GoogleTranslator API.
- **Punctuation**: Automatically adds basic punctuation to the transcribed text.
- **Multi-language support**: Includes support for English, Italian, Spanish, German, French, and Japanese.
- **Custom GUI**: A simple and customizable GUI to display the transcription and translation.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/voice-to-screen.git
    cd voice-to-screen
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Download the necessary Vosk models for transcription. The models will be automatically downloaded when you first run the program, but you can manually download them from the following links if needed:
    - [English Model](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
    - [Italian Model](https://alphacephei.com/vosk/models/vosk-model-small-it-0.4.zip)
    - [Spanish Model](https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip)
    - [German Model](https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip)
    - [French Model](https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip)
    - [Japanese Model](https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip)

## Virtual Microphone Setup (Linux, Windows, macOS)

If you want to transcribe and translate system audio (instead of using a physical microphone), you can set up a virtual microphone.

### Linux (PulseAudio)

For Linux users with PulseAudio, you can set up a virtual microphone by running the following command:

```bash
pactl load-module module-remap-source source_name=VirtualMic master=VirtualSink.monitor
```

This command creates a virtual microphone that listens to system audio without the need for physical speakers or a microphone. You can then select `VirtualMic` as your input device when running the program.

### Windows

For Windows users, you can achieve a similar setup using virtual audio tools like **VB-Audio Virtual Cable**. Install the software and set it up as your input device to allow transcription of system audio.

- Download and set up: [VB-Audio Virtual Cable](https://www.vb-audio.com/Cable/)

### macOS

On macOS, you can use **Loopback** or **Soundflower** to create a virtual audio device. These tools allow you to capture system audio and feed it into the transcription program.

- [Loopback](https://rogueamoeba.com/loopback/) (paid)
- [Soundflower](https://github.com/mattingalls/Soundflower) (free)

Once set up, select the virtual audio device as your input device in the program.

## Usage

1. Run the application:
    ```bash
    python main.py
    ```

2. Select the source and target languages for transcription and translation.
3. Select the audio input device for recording (e.g., microphone or virtual microphone).
4. The application will display real-time transcription and translation in the GUI.

## File Descriptions

- **`main.py`**: Entry point of the application. Handles user input for language selection and audio device selection, and starts the GUI and transcription process.
- **`transcription.py`**: Contains the core logic for real-time transcription and translation. It uses the Vosk model for transcription and the GoogleTranslator for translation.
- **`utils.py`**: Utility functions for handling input devices and language selection.
- **`gui.py`**: Manages the graphical user interface for displaying transcription and translation.
- **`vosk_model.py`**: Downloads and extracts the appropriate Vosk model for the selected language.

## Supported Languages

- English (en-us)
- Italian (it)
- Spanish (es)
- German (de)
- French (fr)
- Japanese (ja)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Citations
This project utilizes the following open-source tools:

- **Vosk**: A toolkit for speech recognition. [Vosk GitHub](https://github.com/alphacep/vosk-api)
- **Deep Translator**: Used for translation services. [Deep Translator GitHub](https://github.com/nidhaloff/deep-translator)
