from datetime import datetime
import os
import socket
from traceback import format_exc

from flask import Flask, Response, send_from_directory
import requests

from prefix_middleware import PrefixMiddleware

app = Flask(__name__)

app_prefix = os.environ.get("APP_PREFIX")
if app_prefix:
    if not app_prefix.startswith("/"):
        app_prefix = f"/{app_prefix}"
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app_prefix)

index_info = """Hello, World!
Hostname is {host_name}
IP is {host_ip}
Date/Time is {dt}
"""

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return Response(
        index_info.format(
            host_name=host_name,
            host_ip=host_ip,
            dt=datetime.now()
        ),
        mimetype='text/plain'
    )

@app.route('/env')
def env():
    data = "Environment:\n"
    for item, value in os.environ.items():
        data += f"{item} => {value}\n"
    return Response(
        data,
        mimetype='text/plain'
    )

@app.route('/healthcheck')
def healthcheck():
    return "OK\n"

@app.route('/hello')
def hello():
    return "Hello!\n"

@app.route('/hello/<name>')
def hello_name(name):
    return f"Hello {name}!\n"

@app.route('/backend', defaults={'custom_route': None})
@app.route('/backend/<path:custom_route>')
def backend(custom_route):

    backend_url = os.environ.get("BACKEND_URL")
    if not backend_url:
        return "BACKEND_URL not set\n"

    if not backend_url.endswith("/"):
        backend_url += "/"

    if custom_route:
        # Remove the / from the start (we have already added to the backend URL)
        if custom_route.startswith("/"):
            custom_route = custom_route[1:]
        backend_url += custom_route

    try:
        response = requests.get(backend_url, timeout=5).text
        if not response.endswith("\n"):
            response = f"{response}\n"
        return Response(
            f"Response from backend:\n{response}",
            mimetype='text/plain'
        )
    except Exception as ex:
        trace = format_exc(ex)
        return Response(
            f"ERROR in request to {backend_url}:\n{str(ex)}\n{trace}\n",
            mimetype='text/plain'
        )
