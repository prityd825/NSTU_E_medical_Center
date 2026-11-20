#!/usr/bin/env bash
# Render build script: install packages, collect CSS/images, update the database, create demo logins.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py create_demo_users
