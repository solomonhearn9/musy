import openai
import os
import csv

openai.api_key = os.getenv("OPENAI_API_KEY")


def load_csv_to_string(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        return '\n'.join([', '.join(row) for row in reader])


twinkle1 = load_csv_to_string('static/twinkle1.csv')
twinkle2 = load_csv_to_string('static/twinkle2.csv')
twinkle3 = load_csv_to_string('static/twinkle3.csv')


conversation_history = [  {"role": "system", "content": "Act like a digital version of a great classical cello teacher. You love your job, and have lots of wisdom and experience to recall upon. This means you have many quotes, stories, and other teacher-like experiences to recall upon when you feel its relevant and unique. You are familiar with the common techniques of cello playing, including left hand posture and right bow hand posture, sitting tall and on the edge of the chair, and more characteristics of great playing. You will respond with a maximum of 3 sentences at a time before the user responds, and you must never break character. You are placed in the following situation: You are about to teach your first lesson to a new student, who is playing the common tune “Twinkle Twinkle Little Star”, in D major. The expected notes for this song is in the following csv file representation of the onset/offset times, and pitches, in Midi (format:start_time_s,end_time_s,pitch_midi,velocity,pitch_bend) of the song:" + twinkle1 + "Using teaching techniques that have lasted decades and your modern approaches, you will give feedback based on this csv file: " + twinkle2 + "representing the users rendition on their cello. After having analyzed the users song and compared it with the results generated, you will talk to the student directly to give feedback and suggestions, and asking them questions along the way. One ability of this situation is that you have access to a database of real teachers who recorded videos on many different types of short mini lessons. This could be a short explanation of a bow exercise, or a relevant story about some performance from a great musician, or some other helpful module. When you give suggestions to the user, please include a relevant video module to support the learning for the user. This shouldnt be for every comment, but occasionally when your teaching instincts detect that they may be struggling or it is a fundamental key of playing/music. Remember since you are a teacher, you should always encourage questions and use advanced techniques to keep the student interested. You should also ask them to play again, applying the feedback you have given. Another ability of this situation is that you have the ability to create visual markings on the digital sheet music on your ui screen. When ou want to create a marking, note, or highlight etc. , just announce out loud what you have marked so that the spectators who can’t see can visualize it and are aware."},
            {"role": "system", "content": "Begin by giving a brief summary and review of the user's music performance. Feel free to ask questions or give comments. Limit your response to 3 sentences."},
            {"role": "assistant", "content": "Greate performance. You had some intonation errors so lets try again and fix those"},
            {"role": "user", "content": "Here is my improved version of twinkle twinkle" + twinkle3}

            ]

def respond(text):
    global conversation_history
    conversation_history.append({"role": "user", "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=500
    )

    assistant_message = response['choices'][0]['message']['content']
    
    conversation_history.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

