
from flask import Flask, request, jsonify

app = Flask(__name__)

import re
import torch
from model import ChatModel

with open('data.txt', 'r') as file:
    data = file.read()

data = re.sub('\n+', '\n', data)
# Parse the text into a list of question-answer pairs
qa_pairs = data.strip().split('\n')

# Split each pair into a question and an answer
qa_pairs = [pair.split(': ')[1] for pair in qa_pairs]
q = []
ans = []
aq = True
for pair in range(len(qa_pairs)):
  #pair -= 1A
  if pair % 2 == 0:
    q.append(qa_pairs[pair])#.split(";;"))
  else:
    ans.append(qa_pairs[pair])

model = ChatModel(q,ans,device="cpu")


@app.route('/predict', methods=['GET'])
def predict():
    # Get the 'message' parameter from the query string
    message = request.args.get('message')
    print(message)
    return jsonify(answer=model.chat(str(message)))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
