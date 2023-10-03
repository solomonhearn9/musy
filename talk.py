import sounddevice as sd
import soundfile as sf
import openai
import os
import requests
import re
from flask import Flask, request, jsonify
from pydub import AudioSegment
from pydub.playback import play

app = Flask(__name__)


def open_file(filepath):
  with open(filepath, 'r', encoding='utf-8') as infile:
    return infile.read()


api_key = open_file('openaiapikey2.txt')
elapikey = open_file('elabapikey.txt')

conversation1 = []
chatbot1 = open_file('chatbot1.txt')


def chatgpt(api_key,
            conversation,
            chatbot,
            user_input,
            temperature=0.9,
            frequency_penalty=0.2,
            presence_penalty=0):
  openai.api_key = api_key
  conversation.append({"role": "user", "content": user_input})
  messages_input = conversation.copy()
  prompt = [{"role": "system", "content": chatbot}]
  messages_input.insert(0, prompt[0])
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    temperature=temperature,
    frequency_penalty=frequency_penalty,
    presence_penalty=presence_penalty,
    messages=messages_input)
  chat_response = completion['choices'][0]['message']['content']
  conversation.append({"role": "assistant", "content": chat_response})
  return chat_response


def record_and_transcribe_from_file(file_path, fs=44100):
  with open(file_path, "rb") as file:
    openai.api_key = api_key
    result = openai.Audio.transcribe("whisper-1", file)
  transcription = result['text']
  return transcription


def get_bot_response(user_message):
  response = chatgpt(api_key, conversation1, chatbot1, user_message)
  user_message_without_generate_image = re.sub(
    r'(Response:|Narration:|Image: generate_image:.*|)', '', response).strip()
  return user_message_without_generate_image


@app.route('/get_response', methods=['POST'])
def get_response_endpoint():
  audio_file = request.files['audio']
  audio_file.save("received_audio.wav")
  user_message = record_and_transcribe_from_file("received_audio.wav")
  response_text = get_bot_response(user_message)
  return jsonify({'response': response_text})


if __name__ == '__main__':
  app.run(debug=True)
