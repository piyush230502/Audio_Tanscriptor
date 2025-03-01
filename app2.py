from dotenv import load_dotenv
import os
import streamlit as st
from groq import Groq
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

#load groq api key
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")
groq_api_key=os.getenv("GROQ_API_KEY")

# Initialize the Groq client
client = Groq()

st.title("Audio Transcription App 🎤")

        
# Function to save transcription to a file
def save_transcription(text, output_path):
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Function to transcribe a single file
def transcribe_file(filepath):
    try:
        with open(filepath, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(filepath), file.read()),  # Required audio file
                model="whisper-large-v3-turbo",  # Required model to use for transcription
                prompt="Specify context or spelling",  # Optional
                response_format="json",  # Optional
                language="en",  # Optional
                temperature=0.0  # Optional
            )
            output_path = os.path.join(os.path.dirname(filepath), "transcript.txt")
            save_transcription(transcription.text, output_path)
    except PermissionError:
        print(f"Permission denied: {filepath}")
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

# Function to scan directory recursively and transcribe files
def scan_and_transcribe(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a")):
                transcribe_file(os.path.join(root, file))

# File uploader
uploaded_file = st.file_uploader("Choose an audio file...", type=["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"])

if uploaded_file is not None:
    # Create a transcription of the audio file
    transcription = client.audio.transcriptions.create(
        file=(uploaded_file.name, uploaded_file.read()),  # Required audio file
        model="whisper-large-v3-turbo",  # Required model to use for transcription
        prompt="Specify context or spelling",  # Optional
        response_format="json",  # Optional
        language="en",  # Optional
        temperature=0.0  # Optional
    )
    # Display the transcription text
    st.subheader("Transcription")
    st.write(transcription.text)
    
    # Save the transcription to a file
    save_transcription(transcription.text, "transcript.txt")

# Real-time file monitoring
class Watcher:
    DIRECTORY_TO_WATCH = "File_Directory"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if not event.is_directory and event.src_path.endswith((".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a")):
            transcribe_file(event.src_path)

# Start the watcher
if __name__ == "__main__":
    scan_and_transcribe("File_Directory")
    w = Watcher()
    w.run()