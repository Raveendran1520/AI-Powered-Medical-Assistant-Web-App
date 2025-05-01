import os
import platform
import subprocess
from gtts import gTTS
from pydub import AudioSegment
import elevenlabs
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# -------- gTTS fallback method --------
def text_to_speech_with_gtts(input_text, output_filepath):
    language = "en"
    try:
        tts = gTTS(text=input_text, lang=language, slow=False)
        tts.save(output_filepath)

        # Convert to WAV for better playback
        wav_path = output_filepath.replace(".mp3", ".wav")
        sound = AudioSegment.from_mp3(output_filepath)
        sound.export(wav_path, format="wav")

        play_audio(wav_path)
    except Exception as e:
        print(f"⚠️ Error with gTTS: {e}")

# -------- ElevenLabs TTS method --------
def text_to_speech_with_elevenlabs(input_text, output_filepath):
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found. Falling back to gTTS.")
        text_to_speech_with_gtts(input_text, output_filepath)
        return

    try:
        client = elevenlabs.Client(api_key=ELEVENLABS_API_KEY)

        audio = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )

        with open(output_filepath, 'wb') as f:
            f.write(audio)

        # Convert to WAV
        wav_path = output_filepath.replace(".mp3", ".wav")
        sound = AudioSegment.from_mp3(output_filepath)
        sound.export(wav_path, format="wav")

        play_audio(wav_path)

    except Exception as e:
        print(f"⚠️ ElevenLabs failed: {e}")
        text_to_speech_with_gtts(input_text, output_filepath)

# -------- Audio player function --------
def play_audio(audio_path):
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(["afplay", audio_path])
        elif os_name == "Windows":  # Windows
            subprocess.run(["powershell", "-c", f'(New-Object Media.SoundPlayer "{audio_path}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(["aplay", audio_path])
        else:
            raise Exception("Unsupported OS for audio playback.")
    except Exception as e:
        print(f"⚠️ Audio play error: {e}")

# -------- Test run --------
if __name__ == "__main__":
    input_text = "Hello, this is Doctor AI checking in."

    print("\n🟢 Playing with gTTS:")
    text_to_speech_with_gtts(input_text, "gtts_output.mp3")

    print("\n🟢 Playing with ElevenLabs:")
    text_to_speech_with_elevenlabs(input_text, "elevenlabs_output.mp3")
