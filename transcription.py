import os
import sys
import time
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from deep_translator import GoogleTranslator
from nltk.tokenize import sent_tokenize
from vosk_model import download_and_extract_model
import nltk

nltk.download('punkt')

MODEL_DIR = "models"
TRANSLATION_INTERVAL = 0.5
DISPLAY_TIMEOUT = 1

def add_basic_punctuation(text, lang_code):
    try:
        sentences = sent_tokenize(text, language=lang_code.split('-')[0])
        punctuated_text = ' '.join([sentence.strip() + '.' for sentence in sentences])
        return punctuated_text
    except LookupError:
        return text

def run_transcription(app, src_lang_code, dest_lang_code, device_index):
    # Initialize Vosk model
    model_path = os.path.join(MODEL_DIR, f"vosk-model-{src_lang_code.lower()}")
    if not os.path.exists(model_path):
        os.makedirs(MODEL_DIR, exist_ok=True)
        download_and_extract_model(src_lang_code.lower(), model_path)
    model = Model(model_path)
    device_info = sd.query_devices(device_index)
    samplerate = int(device_info['default_samplerate'])

    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)
    rec.SetPartialWords(True)

    q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"Audio Callback Status: {status}", file=sys.stderr)
        q.put(bytes(indata))

    # Initialize variables for timing
    last_activity_time = time.time()
    translation = ""
    transcription = ""
    last_translation_time = 0

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device_index, dtype='int16',
                           channels=1, callback=audio_callback):
        print("Listening... Press Ctrl+C to stop.")
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    res = json.loads(result)
                    transcription = res.get('text', '')
                    if transcription:
                        # Update last activity time
                        last_activity_time = time.time()
                        # Apply basic punctuation to the finalized transcription
                        punctuated_transcription = add_basic_punctuation(transcription, src_lang_code)
                        if dest_lang_code != src_lang_code:
                            translation = GoogleTranslator(
                                source=src_lang_code.split('-')[0],
                                target=dest_lang_code.split('-')[0]
                            ).translate(punctuated_transcription)
                        else:
                            translation = punctuated_transcription
                        app.update_text(punctuated_transcription, translation)
                else:
                    partial_result = rec.PartialResult()
                    res = json.loads(partial_result)
                    partial_transcription = res.get('partial', '')
                    if partial_transcription:
                        # Update last activity time
                        last_activity_time = time.time()
                        # Apply basic punctuation to the partial transcription
                        punctuated_partial = add_basic_punctuation(partial_transcription, src_lang_code)
                        current_time = time.time()
                        # Throttle translation calls to avoid excessive API requests
                        if current_time - last_translation_time > TRANSLATION_INTERVAL:
                            if dest_lang_code != src_lang_code:
                                translation = GoogleTranslator(
                                    source=src_lang_code.split('-')[0],
                                    target=dest_lang_code.split('-')[0]
                                ).translate(punctuated_partial)
                            else:
                                translation = punctuated_partial
                            last_translation_time = current_time
                        app.update_text(punctuated_partial, translation)
                    else:
                        # Check if the display timeout has been reached
                        current_time = time.time()
                        if current_time - last_activity_time > DISPLAY_TIMEOUT:
                            # Optionally, clear the subtitles after the timeout
                            # app.clear_text()
                            pass  # Keep the subtitles displayed
                        else:
                            # Keep displaying the last transcription and translation
                            app.update_text(transcription, translation)
        except KeyboardInterrupt:
            print("Real-time transcription stopped.")
        except Exception as e:
            print(f"An error occurred: {e}")

