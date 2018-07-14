from blt import loadlang
from flask import Flask, request, send_from_directory
app = Flask(__name__)

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()
    
@app.route("/index.js")
def indexscript():
    return open("index.js", encoding="utf-8").read()
    
@app.route("/web/<path:path>")
def assets(path):
    return send_from_directory('web', path)
    
@app.route("/translate", methods=["POST"])
def translate():
    return loadlang("Latko").translate(request.json['data'])[0]

@app.route("/addradical", methods=["POST"])
def add_radical():
    l = loadlang("Latko")
    l.add_radical(request.json['key'], request.json['value'])
    open("lang_Latko.bat", "w").write(l.dumps())
    return "SUCCESS"

@app.route("/addcomposite", methods=["POST"])
def add_composite():
    l = loadlang("Latko")
    l.add_composite(request.json['key'], *request.json['radicals'])
    open("lang_Latko.bat", "w").write(l.dumps())
    return "SUCCESS"
