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
from django.contrib.auth import authenticate
u = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
print(f'Creating user: [{u}] with password length: {len(p)}')
if u and p:
    if User.objects.filter(username=u).exists():
        user = User.objects.get(username=u)
    else:
        user = User.objects.create_superuser(u, e, p)
        print(f'Superuser {u} created')
    user.set_password(p)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'Password set for {u}, is_active={user.is_active}')
    # Verify auth works
    test = authenticate(username=u, password=p)
    print(f'Auth test: {\"SUCCESS\" if test else \"FAILED\"}')
    print(f'All users: {list(User.objects.values_list(\"username\", \"is_active\"))}')
"

# Seed default animals
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from farm.models import Animal

animals = [
    ('chicken', 'Broiler Chicken'),
    ('chicken', 'Layer Chicken'),
    ('duck',    'Mallard Duck'),
    ('duck',    'Muscovy Duck'),
    ('goose',   'Embden Goose'),
    ('turkey',  'Bronze Turkey'),
    ('quail',   'Japanese Quail'),
    ('pigs',    'Yorkshire Pig'),
    ('pigs',    'Duroc Pig'),
    ('goat',    'Boer Goat'),
    ('fish',    'Tilapia'),
    ('fish',    'Catfish'),
]

created = 0
for category, name in animals:
    obj, was_created = Animal.objects.get_or_create(
        name=name,
        defaults={'category': category, 'total_count': 0}
    )
    if was_created:
        created += 1
        print(f'  Created: {name} ({category})')
    else:
        print(f'  Exists:  {name} ({category})')

print(f'Animal seeding done — {created} new, {len(animals) - created} already existed.')
"
