import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def respond(text):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a music teacher with many years of experience. I will ask you questions and you will respond in a warm and friendly way."},
            {"role": "user", "content": text}
        ]
    )

    assistant_message = response['choices'][0]['message']['content']
    return assistant_message
