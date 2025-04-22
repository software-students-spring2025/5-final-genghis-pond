FROM python:3.11-slim

WORKDIR /web_app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY . .

CMD ["/wait-for-it.sh", "mongodb:27017", "--", "python", "run.py"]
