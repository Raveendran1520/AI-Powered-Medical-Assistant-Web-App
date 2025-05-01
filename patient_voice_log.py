import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
from groq import Groq

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY in environment variables.")

# Function to record audio and save as mp3
def record_audio(file_path, timeout=10, phrase_time_limit=None):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("🎙️ Start speaking now...")
            
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("✅ Recording complete.")
            
            # Convert to MP3
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            logging.info(f"💾 Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"⚠️ An error occurred during recording: {e}")

# Function to transcribe audio using Groq Whisper model
def transcribe_with_groq(audio_filepath, stt_model="whisper-large-v3"):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        return transcription.text
    except Exception as e:
        logging.error(f"⚠️ Error during transcription: {e}")
        return None

# Example usage (you can comment this out if importing elsewhere)

if __name__ == "__main__":
    audio_filepath = "patient_voice_test_for_patient.mp3"

    # record_audio(file_path=audio_filepath)
    # print(transcribe_with_groq(audio_filepath))
