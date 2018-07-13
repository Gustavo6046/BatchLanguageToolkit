from blt import loadlang
from flask import Flask, request, send_from_directory
app = Flask(__name__)

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()
    
@app.route("/web/<path:path>")
def assets(path):
    return send_from_directory('web', path)
    
@app.route("/translate", methods=["POST"])
def translate():
    return loadlang("Latko").translate(request.json['data'])[0]