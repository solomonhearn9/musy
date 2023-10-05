import requests
import os


elapi_key = os.getenv("EL_API_KEY")

def text_to_speech(text, voice_id, api_key):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.85
        }
    }
    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    
    return response.content  # Return the audio data directly