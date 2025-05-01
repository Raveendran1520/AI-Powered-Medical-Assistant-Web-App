import os
import csv
from datetime import datetime
import gradio as gr

from patient_voice_log import transcribe_with_groq
from doctor_brain import analyze_patient_case
from doctor_voice_log import text_to_speech_with_elevenlabs

# Load API keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables.")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables.")

CSV_FILE = "results.csv"

# Ensure CSV file exists with headers
if not os.path.exists(CSV_FILE):
    print("Writing to:", os.path.abspath(CSV_FILE))
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Transcription", "Diagnosis", "AI Voice File"])

# Append one row per call
def log_to_csv(transcription, diagnosis, ai_voice_file):
    try:
        path = os.path.abspath(CSV_FILE)
        print("🔍 Writing to CSV at:", path)

        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                transcription.strip(),
                diagnosis.strip(),
                ai_voice_file if ai_voice_file else "No voice"
            ])
        print("✅ CSV entry added.")
    except Exception as e:
        print("❌ CSV logging error:", e)


# Main AI consultation logic
def agentic_consult(audio_file, image_file):
    transcript = ""
    if audio_file:
        transcript = transcribe_with_groq("whisper-large-v3", audio_file, GROQ_API_KEY)

    if not transcript and not image_file:
        return "❌ Please provide either audio or image.", "", None

    if not transcript:
        transcript = "No audio symptoms provided. Image-only analysis."

    diagnosis = analyze_patient_case(transcript, image_file or "")
    output_audio_path = "doctor_voice_response.mp3"
    text_to_speech_with_elevenlabs(diagnosis, output_audio_path)

    # Log to CSV with newline-safe logic
    log_to_csv(transcript, diagnosis, output_audio_path)

    return transcript, diagnosis, output_audio_path

# Gradio UI
with gr.Blocks(css=""" 
    #title {font-size: 32px; font-weight: bold; color: #3B82F6; margin-bottom: 10px;}
    .gr-box {border-radius: 20px; padding: 20px; background-color: #f9f9f9;}
    .gr-button {background-color: #3B82F6 !important; color: white !important;}
    .gr-button:hover {background-color: #2563EB !important;}
    .output-box {border: 1px solid #e5e7eb; padding: 10px; border-radius: 12px;}
""") as demo:

    gr.Markdown("# 🧠 AI Health Buddy")

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="🎤 Patient Voice")
        image_input = gr.Image(type="filepath", label="📸 Upload Medical Image")

    with gr.Row():
        transcript_output = gr.Textbox(label="📝 Transcribed Text")
        diagnosis_output = gr.Textbox(label="🩺 AI Diagnosis")
        voice_output = gr.Audio(label="🔊 AI Doctor Voice", interactive=False)

    submit_btn = gr.Button("🚀 Submit for Diagnosis", elem_classes="gr-button")
    submit_btn.click(
        fn=agentic_consult,
        inputs=[audio_input, image_input],
        outputs=[transcript_output, diagnosis_output, voice_output]
    )

demo.launch()
