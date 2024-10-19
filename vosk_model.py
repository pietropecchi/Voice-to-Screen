import os
import sys
import requests
import zipfile
import shutil
from tqdm import tqdm

MODEL_DIR = "models"

def download_and_extract_model(lang_code, model_path):
    MODEL_URLS = {
        "en-us": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "es": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
        "de": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
        "fr": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
        "it": "https://alphacephei.com/vosk/models/vosk-model-small-it-0.4.zip",
        "ja": "https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip",
    }

    if lang_code not in MODEL_URLS:
        print(f"No model URL found for language code '{lang_code}'. Please download the model manually.")
        sys.exit(1)
    model_url = MODEL_URLS[lang_code]
    print(f"Downloading model for '{lang_code}' from {model_url}...")
    # Download the file
    local_filename = model_url.split('/')[-1]
    response = requests.get(model_url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024 * 8  # 8KB
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(local_filename, 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR: Something went wrong during the download")
        sys.exit(1)
    print("Download complete.")
    # Extract the zip file
    print("Extracting model...")
    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall(MODEL_DIR)
    # Rename the extracted directory to the model_path
    extracted_dir = os.path.join(MODEL_DIR, zip_ref.namelist()[0].split('/')[0])
    if os.path.exists(model_path):
        shutil.rmtree(model_path)
    os.rename(extracted_dir, model_path)
    # Remove the zip file
    os.remove(local_filename)
    print("Model ready.")

