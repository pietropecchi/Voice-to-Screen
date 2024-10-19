import tkinter as tk
import tkinter.font as tkfont  # Import the font module

# GUI Configuration
APP_TITLE = "Real-Time Transcription and Translation"
WINDOW_POSITION = "+100+600"
WINDOW_TRANSPARENCY = '0.5'
BACKGROUND_COLOR = 'gray'
TRANSCRIPTION_FONT = ('Arial', 18)
TRANSCRIPTION_COLOR = 'yellow'
TRANSLATION_FONT = ('Arial', 30)
TRANSLATION_COLOR = 'white'
TEXT_WIDTH = 60  # Number of characters wide

class TranscriptionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(False)
        self.root.attributes("-topmost", True)
        self.root.configure(background=BACKGROUND_COLOR)
        self.root.attributes("-alpha", WINDOW_TRANSPARENCY)
        self.root.geometry(WINDOW_POSITION)
        self.root.title(APP_TITLE)

        # Create font objects
        self.transcription_font = tkfont.Font(font=TRANSCRIPTION_FONT)
        self.translation_font = tkfont.Font(font=TRANSLATION_FONT)

        # Compute wraplength based on TEXT_WIDTH and font metrics
        avg_char_width_transcription = self.transcription_font.measure('0')
        wraplength_transcription = avg_char_width_transcription * TEXT_WIDTH

        avg_char_width_translation = self.translation_font.measure('0')
        wraplength_translation = avg_char_width_translation * TEXT_WIDTH

        # Create labels for current transcription and translation
        self.label_transcription = tk.Label(
            self.root, text="", font=TRANSCRIPTION_FONT, width=TEXT_WIDTH,
            bg=BACKGROUND_COLOR, fg=TRANSCRIPTION_COLOR, anchor='w',
            justify='left', wraplength=wraplength_transcription)
        self.label_transcription.pack()

        self.label_translation = tk.Label(
            self.root, text="", font=TRANSLATION_FONT, width=TEXT_WIDTH,
            bg=BACKGROUND_COLOR, fg=TRANSLATION_COLOR, anchor='w',
            justify='left', wraplength=wraplength_translation)
        self.label_translation.pack()

    def update_text(self, transcription, translation):
        # Update the transcription and translation labels
        self.label_transcription.config(text=transcription)
        self.label_translation.config(text=translation)
        # Refresh the window
        self.root.update_idletasks()

    def clear_text(self):
        # Clear the transcription and translation labels
        self.label_transcription.config(text="")
        self.label_translation.config(text="")
        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()

