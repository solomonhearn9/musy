from flask import Flask, render_template, jsonify
from talk import get_bot_response

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
  response_text = get_bot_response()
  return jsonify({'response': response_text})


if __name__ == '__main__':
  app.run(debug=True)
