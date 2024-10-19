import threading
from gui import TranscriptionApp
from transcription import run_transcription
from utils import select_language, select_input_device

def main():
    # Select source language for transcription
    src_lang_code = select_language("Select the source language for transcription:")
    # Select destination language for translation
    dest_lang_code = select_language("Select the destination language for translation:")
    # Select input device
    device_index = select_input_device()

    # Create the GUI app
    app = TranscriptionApp()

    # Start the transcription in a separate thread
    transcription_thread = threading.Thread(
        target=run_transcription,
        args=(app, src_lang_code, dest_lang_code, device_index)
    )
    transcription_thread.daemon = True  # Daemonize thread
    transcription_thread.start()

    # Run the GUI main loop
    app.run()

if __name__ == '__main__':
    main()

