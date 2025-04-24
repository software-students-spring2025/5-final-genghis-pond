FROM python:3.11-slim

WORKDIR /web_app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY . .

CMD ["/wait-for-it.sh", "mongodb:27017", "--", "gunicorn", "-c", "gunicorn_config.py", "wsgi:application"]
