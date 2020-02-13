from datetime import datetime
import os
import socket

from flask import Flask, Response, send_from_directory

from prefix_middleware import PrefixMiddleware

app = Flask(__name__)

app_prefix = os.environ.get("APP_PREFIX")
if app_prefix:
    if not app_prefix.startswith("/"):
        app_prefix = f"/{app_prefix}"
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app_prefix)

index_info = """Hello, World!
Hostname is {hostname}
Date/Time is {dt}
"""

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return Response(
        index_info.format(
            hostname=socket.gethostname(),
            dt=datetime.now()
        ),
        mimetype='text/plain'
    )

@app.route('/hello')
def hello():
    return "Hello!"

@app.route('/hello/<name>')
def hello_name(name):
    return f"Hello {name}!"
