import xlrd
from flask import Flask, jsonify, request
from multipleSpiders import call_floripa

app = Flask(__name__)


@app.route('/floripa', methods=['GET'])
def home():
    return jsonify(call_floripa()), 200

@app.route('/floripa', methods=['POST'])
def sendRequest():
    imoveis = {'imoveis': request.json['imoveis']}
    print(imoveis)
    return jsonify(call_floripa(imoveis)), 200


if __name__ == '__main__':
    app.run(debug=True)
