from flask import Flask, render_template, request, jsonify, Response
import openai
import os
import requests
from werkzeug.utils import secure_filename
from translations.dictation import text_to_speech
from translations.gpt import respond
import pyaudio
import aubio
import numpy as np

app = Flask(__name__)


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

        return filepath
    

def transcribe_audio(file_path):
    with open(file_path, "rb") as file:
        # Your OpenAI transcription logic here...
        result = openai.Audio.transcribe("whisper-1", file)
    transcription = result['text']
    return transcription


# @app.route("/detect_pitch", methods=["POST"])
# def detect_pitch():
#     audiobuffer = stream.read(buffer_size)
#     signal = np.fromstring(audiobuffer, dtype=np.float32)
#     pitch = pitch_o(signal)[0]
#     confidence = pitch_o.get_confidence()
#     return jsonify({"pitch": pitch, "confidence": confidence})

# def detect_pitch_aubio(audio_data):
#     win_s = 4096
#     hop_s = 512 
#     tolerance = 0.8

#     pitch_o = aubio.pitch("yin", win_s, hop_s, 44100)
#     pitch_o.set_tolerance(tolerance)

#     # Convert raw audio data to numpy array
#     samples = np.frombuffer(audio_data, dtype=aubio.float_type)

#     # Detect pitch
#     pitch = pitch_o(samples)[0]

#     return pitch

# @app.route("/ask", methods=["POST"])
# def ask():
#     data = request.get_json()
#     user_input = data.get("user_input")
    
#     if user_input:
#         model_response = respond(user_input)
#         return jsonify(response=model_response)
#     else:
#         return jsonify(error="User input not provided"), 400
    
@app.route("/synthesize_speech", methods=["POST"])
def synthesize_speech():
    data = request.get_json()
    
    filepath = data.get("filepath")
    
    if filepath:
        text = transcribe_audio(filepath)
        model_response = respond(text)
        
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        audio_data = text_to_speech(model_response, voice_id, elapikey)
        
        return Response(audio_data, mimetype="audio/mpeg")
    else:
        print("Filepath not received")
        return jsonify(error="Filepath not provided"), 400
    # data = request.get_json()  # Ensure you're getting JSON data correctly
    
    # # Assuming data contains a filepath
    # filepath = data.get("filepath")
    
    # if filepath:
    #     text = transcribe_audio(filepath)

    #     openai.api_key = os.getenv("OPENAI_API_KEY")
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": "You are a professional music teacher who will answer my questions with short and friendly responses of no longer than 3 sentences."},
    #             {"role": "user", "content": text}
    #         ]
    #     )
    #     reply = response['choices'][0]['message']['content']
        
    #     voice_id = "21m00Tcm4TlvDq8ikWAM"
    #     audio_data = text_to_speech(reply, voice_id, elapikey)
    #     # os.remove(filepath)
        
    #     return Response(audio_data, mimetype="audio/mpeg")
    # else:
    #     print("Filepath not received")
    #     return jsonify(error="Filepath not provided"), 400

    
if __name__ == "__main__":
    app.run(debug=True)
