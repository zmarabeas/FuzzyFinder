from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello_world():
    response = jsonify({'message': 'Hello, World!'})
    return response


if __name__ == '__main__':
    app.run()
