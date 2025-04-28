#!/bin/bash

./wait-for-it.sh mongodb:27017 --timeout=90 --strict -- \
    gunicorn -c gunicorn_config.py wsgi:application