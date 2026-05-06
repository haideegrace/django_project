#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create superuser with password (free tier has no shell access)
python manage.py shell -c "
import os
from django.contrib.auth.models import User
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
if username and password:
    user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_superuser': True, 'is_staff': True})
    user.set_password(password)
    user.save()
    print(f'Superuser {username} {\"created\" if created else \"updated\"}')
"
