
# 🩺 AI Medical Assistant Web App

This project is a multimodal AI-powered diagnostic tool that accepts **voice**, **image**, and **text** inputs to provide preliminary medical assessments. Built using **Flask**, **JavaScript**, **Whisper (Groq)**, **gTTS**, **ElevenLabs**, and a custom `doctor_brain` module.

---

## 📑 Table of Contents

- [Installing FFmpeg and PortAudio](#installing-ffmpeg-and-portaudio)  
  - [macOS](#macos)  
  - [Linux](#linux)  
  - [Windows](#windows)  
- [Setting Up a Python Virtual Environment](#setting-up-a-python-virtual-environment)  
  - [Using Pipenv](#using-pipenv)  
  - [Using pip and venv](#using-pip-and-venv)  
  - [Using Conda](#using-conda)  
- [Running the Application](#running-the-application)  
- [Project Phases and Python Commands](#project-phases-and-python-commands)

---

## 🛠 Installing FFmpeg and PortAudio

### macOS
1. **Install Homebrew** (if not already installed):  
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install FFmpeg and PortAudio**:  
   ```bash
   brew install ffmpeg portaudio
   ```

### Linux (Ubuntu/Debian-based)
1. **Update and install**:  
   ```bash
   sudo apt update
   sudo apt install ffmpeg portaudio19-dev
   ```

### Windows
1. **Download FFmpeg**:  
   Visit: [FFmpeg Downloads](https://ffmpeg.org/download.html)  
   Download the static Windows build.

2. **Extract and set path**:
   - Extract to: `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to system PATH (via Environment Variables)

3. **Download and install PortAudio**:  
   Visit: [PortAudio Downloads](http://www.portaudio.com/download.html)  
   Follow installation instructions for Windows.

---

## 🐍 Setting Up a Python Virtual Environment

### Using Pipenv
```bash
pip install pipenv
pipenv install
pipenv shell
```

### Using pip and venv
```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

### Using Conda
```bash
conda create --name ai-doc-assistant python=3.11
conda activate ai-doc-assistant
pip install -r requirements.txt
```

---

## 🚀 Running the Application

1. Make sure audio/image/text input devices work in your browser.
2. Run the Flask server:
   ```bash
   python app.py
   ```
3. Open your browser at:  
   ```
   http://127.0.0.1:5000/
   ```

---

## 🔄 Project Phases and Python Commands

| Phase                     | Description                          | Command                            |
|--------------------------|--------------------------------------|-------------------------------------|
| Phase 1: Brain of Doctor | Handles diagnosis logic               | `python doctor_brain.py`            |
| Phase 2: Voice of Patient| Handles audio input + transcription   | `python voice_of_patient.py`        |
| Phase 3: Voice of Doctor | Generates speech output               | `python voice_of_doctor.py`         |
| Phase 4: Flask Web UI    | Web interface with image/audio input | `python app.py`                     |
