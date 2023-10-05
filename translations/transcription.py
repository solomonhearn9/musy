import os
import openai
import whisper

openai.api_key = os.getenv("OPENAI_API_KEY")

def translate(audio_file):
    model = whisper.load_model("base")
    return model.transcribe(audio_file)

