FROM python:3.8-alpine

WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt

EXPOSE 8000

# Run with Flask
# ENV FLASK_APP=app.py
# ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=8000"]

# Run with gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0", "--access-logfile", "-", "--access-logformat", "{\"request\": \"%(r)s\", \"http_status_code\": \"%(s)s\", \"http_request_url\": \"%(U)s\", \"http_query_string\": \"%(q)s\", \"http_verb\": \"%(m)s\", \"http_version\": \"%(H)s\"}", "wsgi:app"]
