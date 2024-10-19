import sounddevice as sd

SUPPORTED_LANGUAGES = {
    "English": "en-us",
    "Italian": "it",
    "Spanish": "es",
    "German": "de",
    "French": "fr",
    "Japanese": "ja"
}

def select_input_device():
    print("Select an input device for recording:")
    devices = sd.query_devices()
    input_devices = [device for device in devices if device['max_input_channels'] > 0]
    for idx, device in enumerate(input_devices):
        print(f"{idx + 1}. {device['name']}")
    while True:
        try:
            choice = int(input("Enter the number corresponding to your input device: "))
            if 1 <= choice <= len(input_devices):
                selected_device = input_devices[choice - 1]
                device_index = devices.index(selected_device)
                print(f"Selected device: {selected_device['name']} (Index: {device_index})")
                return device_index
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def select_language(prompt):
    print(prompt)
    for idx, (lang_name, lang_code) in enumerate(SUPPORTED_LANGUAGES.items()):
        print(f"{idx + 1}. {lang_name}")
    while True:
        try:
            choice = int(input("Enter the number corresponding to your language: "))
            if 1 <= choice <= len(SUPPORTED_LANGUAGES):
                selected_lang_code = list(SUPPORTED_LANGUAGES.values())[choice - 1]
                selected_lang_name = list(SUPPORTED_LANGUAGES.keys())[choice - 1]
                print(f"Selected language: {selected_lang_name} ({selected_lang_code})")
                return selected_lang_code
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

