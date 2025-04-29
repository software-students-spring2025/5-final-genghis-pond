FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    netcat-traditional \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt runtime-requirements.txt ./
RUN pip install --no-cache-dir --use-pep517 --progress-bar off -r requirements.txt

COPY . .

RUN chmod +x wait-for-it.sh

RUN mkdir -p static/uploads/ml_temp
RUN mkdir -p databases
RUN mkdir -p outputs

EXPOSE 5002

CMD ["./wait-for-it.sh", "mongodb:27017", "--", "gunicorn", "-c", "gunicorn_config.py", "wsgi:application"]