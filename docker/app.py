import json
from datetime import datetime
import os
import socket
from traceback import format_exc

import boto3 as boto3
from aws_xray_sdk.core import xray_recorder, patch
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from dotenv import load_dotenv
from flask import Flask, Response, send_from_directory, request, jsonify
import requests
from mysql import connector as mysql_connector

from prefix_middleware import PrefixMiddleware

libs_to_patch = ('boto3', 'requests')
patch(libs_to_patch)

load_dotenv()

app = Flask(__name__)

app_prefix = os.environ.get("APP_PREFIX")
if app_prefix:
    if not app_prefix.startswith("/"):
        app_prefix = f"/{app_prefix}"
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app_prefix)

xray_recorder.configure(service=os.environ.get("DEPLOYMENT") or "NO_SERVICE_NAME")
XRayMiddleware(app, xray_recorder)

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


@app.route('/headers')
def headers():
    text = ""
    for key, val in dict(request.headers).items():
        text += f"{key} = {val}\n"
    return Response(
        text,
        mimetype='text/plain'
    )


@app.route('/hello')
def hello():
    return "Hello!\n"


@app.route('/hello/<name>')
def hello_name(name):
    return f"Hello {name}!\n"


@app.route('/backend', defaults={'custom_route': None})
@app.route('/backend/', defaults={'custom_route': None})
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
            f"Response from {backend_url}:\n{response}",
            mimetype='text/plain'
        )
    except Exception as ex:
        trace = format_exc()
        return Response(
            f"ERROR in request to {backend_url}:\n{str(ex)}\n{trace}\n",
            mimetype='text/plain'
        )


@app.route('/metadata', defaults={'custom_route': None})
@app.route('/metadata/', defaults={'custom_route': None})
@app.route('/metadata/<path:custom_route>')
def metadata(custom_route):

    backend_url = os.environ.get("ECS_CONTAINER_METADATA_URI")
    if not backend_url:
        return "ECS_CONTAINER_METADATA_URI not set\n"

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
            f"Response from {backend_url}:\n{response}",
            mimetype='text/plain'
        )
    except Exception as ex:
        trace = format_exc()
        return Response(
            f"ERROR in request to {backend_url}:\n{str(ex)}\n{trace}\n",
            mimetype='text/plain'
        )


@app.route('/proxy/<string:protocol>/<string:domain>/<path:custom_route>')
def proxy(protocol, domain, custom_route):

    backend_url = f"{protocol}://{domain}/{custom_route}"
    try:
        response = requests.get(backend_url, timeout=5).text
        if not response.endswith("\n"):
            response = f"{response}\n"
        return Response(
            f"Response from {backend_url}:\n{response}",
            mimetype='text/plain'
        )
    except Exception as ex:
        trace = format_exc()
        return Response(
            f"ERROR in request to {backend_url}:\n{str(ex)}\n{trace}\n",
            mimetype='text/plain'
        )


@app.route('/dynamo')
def dynamodb():

    if not os.getenv("DYNAMODB_TABLE_NAME"):
        return "DYNAMODB_TABLE_NAME not set\n"

    db_conn = boto3.resource('dynamodb')
    data = ""
    for item in db_conn.Table(os.getenv("DYNAMODB_TABLE_NAME")).scan().get("Items"):
        data += json.dumps(item) + "\n"

    return Response(
        data,
        mimetype='text/plain'
    )


@app.route('/db')
def db():

    if not os.getenv("RDS_HOST"):
        return "RDS_HOST not set\n"
    host = os.getenv("RDS_HOST")

    if not os.getenv("RDS_USER"):
        return "RDS_USER not set\n"

    if not os.getenv("RDS_PASS"):
        return "RDS_PASS not set\n"

    port = 3306
    parts = os.getenv("RDS_HOST").split(":")
    if len(parts) == 2:
        host = parts[0]
        port = int(parts[1])

    if os.getenv("RDS_PORT"):
        port = int(os.getenv("RDS_PORT"))

    db_conn = mysql_connector.connect(
        host=host,
        port=port,
        user=os.getenv("RDS_USER"),
        passwd=os.getenv("RDS_PASS")
    )

    cursor = db_conn.cursor()
    cursor.execute("show databases")
    dbs = []
    for (databases) in cursor:
        dbs.append(databases[0])
    cursor.close()
    db_conn.close()

    return jsonify(dbs)
