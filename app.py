from flask import Flask, render_template, request, jsonify
import openai
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load API keys from environment variables for security
openai.api_key = os.getenv("OPENAI_API_KEY")
elapikey = os.getenv("ELAPI_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify(error="No audio file part"), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join("uploads", filename)
        file.save(filepath)
        
        # Transcribe audio using OpenAI
        transcription = transcribe_audio(filepath)
        print(transcription)
        # Get a response from GPT-3.5
        #response = chatgpt(transcription)
        
        # Convert response to speech using ElevenLabs API
       # audio_url = text_to_speech(response)
        
        # Cleanup: Remove the file after processing
        os.remove(filepath)
        
        # Send the audio URL back to the client
        return jsonify(transcription)

def transcribe_audio(file_path):
    with open(file_path, "rb") as file:
        # Your OpenAI transcription logic here...
        result = openai.Audio.transcribe("whisper-1", file)
    transcription = result['text']
    return transcription

def chatgpt(user_input):
    return ""

def text_to_speech(text):
    return ""

if __name__ == "__main__":
    app.run(debug=True)
