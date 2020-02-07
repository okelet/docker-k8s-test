import os
import socket

from flask import Flask, send_from_directory


app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def hello_world():
    return "Hello, World from {hostname}!\n".format(hostname=socket.gethostname())
