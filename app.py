from flask import Flask, render_template, request, jsonify, Response
import openai
import os
import requests
from werkzeug.utils import secure_filename
from translations.transcription import translate
from translations.dictation import text_to_speech
from flask_socketio import SocketIO, emit
from translations.gpt import respond

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")  # Enable Socket.IO and allow cross-origin requests

# Load API keys from environment variables for security
openai.api_key = os.getenv("OPENAI_API_KEY")
elapikey = os.getenv("EL_API_KEY")

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
        
        #transcribe_audio(transcription)
        # Get a response from GPT-3.5
        #response = chatgpt(transcription)
        
        # Convert response to speech using ElevenLabs API
        # audio_url = synthesize_speech(transcription)
        
        
        # Send the audio URL back to the client
        return filepath
    

def transcribe_audio(file_path):
    with open(file_path, "rb") as file:
        # Your OpenAI transcription logic here...
        result = openai.Audio.transcribe("whisper-1", file)
    transcription = result['text']
    return transcription

@app.route("/synthesize_speech", methods=["POST"])
def synthesize_speech():
    data = request.get_json()  # Ensure you're getting JSON data correctly
    
    # Assuming data contains a filepath
    filepath = data.get("filepath")
    
    if filepath:
        text = transcribe_audio(filepath)

        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional music teacher who will answer my questions with short and friendly responses of no longer than 3 sentences."},
                {"role": "user", "content": text}
            ]
        )
        reply = response['choices'][0]['message']['content']
        
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        audio_data = text_to_speech(reply, voice_id, elapikey)
        os.remove(filepath)
        
        return Response(audio_data, mimetype="audio/mpeg")
    else:
        print("Filepath not received")
        return jsonify(error="Filepath not provided"), 400

if __name__ == "__main__":
    app.run(debug=True)
