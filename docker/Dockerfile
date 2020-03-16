FROM python:3.6-alpine

USER 0

RUN apk add bash curl gcc musl-dev libffi-dev openssl-dev postgresql-dev && \
    addgroup webapp -g 1000 && \
    adduser webapp -G webapp -u 1000 -g webapp -D

USER 1000

WORKDIR /app
ENV PATH=$PATH:/home/webapp/.local/bin

COPY --chown=webapp:webapp . /app
RUN pip3 install pipenv --user && \
    pipenv install

EXPOSE 8000

# Run with Flask
# ENV FLASK_APP=app.py
# ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=8000"]

# Run with gunicorn
ENTRYPOINT ["gunicorn", "--workers=5", "--bind", "0.0.0.0", "--access-logfile", "-", "--access-logformat", "{\"request\": \"%(r)s\", \"http_status_code\": \"%(s)s\", \"http_request_url\": \"%(U)s\", \"http_query_string\": \"%(q)s\", \"http_verb\": \"%(m)s\", \"http_version\": \"%(H)s\"}", "wsgi:app"]
