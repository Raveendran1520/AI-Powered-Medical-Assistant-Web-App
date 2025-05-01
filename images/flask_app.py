from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import csv
from datetime import datetime
import uuid

from patient_voice_log import transcribe_with_groq
from doctor_voice_log import text_to_speech_with_elevenlabs, text_to_speech_with_gtts
from doctor_brain import analyze_patient_case

# --- Setup ---
UPLOAD_FOLDER = 'uploads'
VOICE_FOLDER = 'voices'
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'm4a'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VOICE_FOLDER'] = VOICE_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VOICE_FOLDER, exist_ok=True)

# --- Helper Functions ---
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_result_to_csv(audio_transcript, audio_diagnosis, image_diagnosis):
    csv_file = "results.csv"
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Audio Transcript", "Audio Diagnosis", "Image Diagnosis"])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            audio_transcript or "(No transcript)",
            audio_diagnosis or "(No audio diagnosis)",
            image_diagnosis or "(No image diagnosis)"
        ])

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/voice/<path:filename>')
def voice_file(filename):
    return send_from_directory(app.config['VOICE_FOLDER'], filename)

@app.route('/process', methods=['POST'])
def process():
    audio_file = request.files.get('audio_input')
    image_file = request.files.get('image_input')
    text_input = request.form.get('text_input')

    transcript = ""
    diagnosis_audio = ""
    diagnosis_image = ""
    audio_response_path = ""
    image_filename = None

    try:
        # --- Handle Audio Upload and Transcription ---
        if audio_file and allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
            audio_filename = secure_filename(f"{uuid.uuid4().hex}_{audio_file.filename}")
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            audio_file.save(audio_path)
            print(f"✅ Audio uploaded: {audio_path}")

            transcript = transcribe_with_groq(audio_path)
            if transcript and transcript != "(No transcription available)":
                diagnosis_audio = analyze_patient_case(text=transcript)
            else:
                diagnosis_audio = "(No diagnosis generated from audio)"

        # --- Handle Image Upload and Analysis ---
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            image_filename = secure_filename(f"{uuid.uuid4().hex}_{image_file.filename}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            print(f"✅ Image uploaded: {image_path}")

            diagnosis_image = analyze_patient_case(image_path=image_path)
        else:
            image_path = None

        # --- Handle enhancement via text input ---
        if text_input:
            if not diagnosis_audio and image_file:
                # text + image together for image diagnosis
                diagnosis_image = analyze_patient_case(text=text_input, image_path=image_path)
            elif not diagnosis_image and audio_file:
                # text + audio transcript together for audio diagnosis
                combined_text = f"{transcript}\n{text_input}" if transcript else text_input
                diagnosis_audio = analyze_patient_case(text=combined_text)
            elif not audio_file and not image_file:
                # Only text is provided, fallback to basic audio diagnosis slot
                diagnosis_audio = analyze_patient_case(text=text_input)

        # --- No valid input ---
        if not (diagnosis_audio or diagnosis_image):
            return jsonify({"error": "❌ No valid input provided!"}), 400

        # --- Determine if both inputs relate to same condition ---
        same_case = False
        if diagnosis_audio and diagnosis_image:
            keywords_audio = set(diagnosis_audio.lower().split())
            keywords_image = set(diagnosis_image.lower().split())
            common_keywords = keywords_audio.intersection(keywords_image)
            same_case = len(common_keywords) > 3

        final_voice_text = ""
        if same_case:
            combined_text = transcript or text_input or "Patient report."
            final_diagnosis = analyze_patient_case(text=combined_text, image_path=image_path)
            final_voice_text = final_diagnosis
        else:
            final_voice_text = f"Audio diagnosis: {diagnosis_audio}. Image diagnosis: {diagnosis_image}."

        # --- Save to CSV ---
        save_result_to_csv(transcript, diagnosis_audio, diagnosis_image)

        # --- Generate AI Voice ---
        audio_response_filename = f"{uuid.uuid4().hex}_ai_response.mp3"
        audio_response_path = os.path.join(app.config['VOICE_FOLDER'], audio_response_filename)

        try:
            text_to_speech_with_elevenlabs(final_voice_text, audio_response_path)
        except Exception as e:
            print(f"⚠️ ElevenLabs failed, falling back to gTTS: {e}")
            text_to_speech_with_gtts(final_voice_text, audio_response_path)

        # --- Send Response ---
        return jsonify({
            "image": image_filename,
            "transcript": transcript,
            "diagnosis_audio": diagnosis_audio,
            "diagnosis_image": diagnosis_image,
            "combined": same_case,
            "voice": audio_response_filename
        })

    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return jsonify({"error": "⚠️ Error processing your request."}), 500


# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)