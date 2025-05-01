import os
from groq import Groq

# Load Groq API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY in environment variables.")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Function to analyze patient case
def analyze_patient_case(text=None, image_path=None):
    try:
        # Build prompt depending on input
        if text:
            prompt = (
                f"You are an experienced and professional AI doctor. "
                f"Analyze the patient's statement and provide a helpful, friendly, and medically accurate diagnosis and advice.\n\n"
                f"Patient says: \"{text}\"\n\n"
                f"Give a detailed but simple reply for the patient."
            )
        elif image_path:
            prompt = (
                f"A patient image is uploaded: {image_path}. "
                f"Analyze the image (assume it's a medical image like X-ray, rash, or MRI) "
                f"and describe your diagnosis and advice for the patient."
            )
        else:
            return "No valid patient input provided."

        # Call Groq API to get Doctor's response
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # you can also use "llama3-70b-8192" if needed
            messages=[
                {"role": "system", "content": "You are a highly skilled, friendly AI doctor providing accurate diagnoses and advice to patients."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )

        doctor_response = response.choices[0].message.content
        return doctor_response

    except Exception as e:
        print(f"⚠️ Error analyzing the case: {e}")
        return "Doctor AI is currently unavailable. Please try again later."
