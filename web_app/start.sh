#!/bin/bash

pip install --no-cache-dir --use-pep517 --progress-bar off -r runtime-requirements.txt

./wait-for-it.sh mongodb:27017 --timeout=300 --strict -- \
    gunicorn -c gunicorn_config.py wsgi:application
