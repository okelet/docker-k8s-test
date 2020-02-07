FROM python:3.8-alpine

WORKDIR /app
COPY . /app/
RUN pip3 install -r requirements.txt

EXPOSE 5000
ENV FLASK_APP=app.py
ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
