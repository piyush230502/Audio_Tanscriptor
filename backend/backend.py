import os
import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from groq import Groq
load_dotenv()


# Setup logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Groq client
client = Groq()

# Save transcription to a file
def save_transcription(text, output_path):
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception as e:
        logging.error(f"Error saving transcription: {e}")

# Transcribe a single file
def transcribe_file(filepath):
    try:
        with open(filepath, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(filepath), file.read()),
                model="whisper-large-v3-turbo",
                prompt="Specify context or spelling",
                response_format="json",
                language="en",
                temperature=0.0
            )
            output_path = os.path.join(os.path.dirname(filepath), "transcript.txt")
            save_transcription(transcription.text, output_path)
            return transcription.text
    except Exception as e:
        logging.error(f"Error processing file {filepath}: {e}")
        return f"Error processing file {filepath}: {e}"

# Watchdog classes for real-time monitoring
class Watcher:
    DIRECTORY_TO_WATCH = "uploads"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except Exception as e:
            logging.error(f"Observer stopped due to error: {e}")
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if not event.is_directory and event.src_path.endswith((".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a")):
            logging.info(f"New file detected: {event.src_path}")
            transcribe_file(event.src_path)