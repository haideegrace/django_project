#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create superuser with password (free tier has no shell access)
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.contrib.auth.models import User
u = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
print(f'Creating user: [{u}] with password length: {len(p)}')
if u and p:
    if User.objects.filter(username=u).exists():
        user = User.objects.get(username=u)
        user.set_password(p)
        user.save()
        print(f'Password reset for {u}')
    else:
        user = User.objects.create_superuser(u, e, p)
        print(f'Superuser {u} created')
"

