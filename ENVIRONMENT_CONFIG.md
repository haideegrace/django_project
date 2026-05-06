# Environment Configuration Guide

This document outlines how to configure the application for different environments.

## Development Environment Setup

### Backend Configuration

1. **Create .env file** in project root:
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-development-secret-key-here-not-for-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Frontend CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email (Development)
EMAIL_BACKEND=console  # Prints emails to console
```

2. **Update settings.py** to load environment variables:
```python
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

3. **Install python-decouple**:
```bash
pip install python-decouple
```

4. **Activate development server**:
```bash
# Option 1: Daphne with WebSocket support (recommended)
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application

# Option 2: Django dev server (HTTP only)
python manage.py runserver 8000
```

### Frontend Configuration

1. **Create .env file** in `frontend/`:
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_ENV=development
```

2. **Start React dev server**:
```bash
cd frontend
npm install
npm start
```

## Staging Environment Setup

### Backend Configuration

1. **Create .env.staging** file:
```env
# Django Settings
DEBUG=False
SECRET_KEY=generate-a-new-secret-key-for-staging
ALLOWED_HOSTS=staging.yourdomain.com,www.staging.yourdomain.com

# Database (PostgreSQL recommended for staging)
DATABASE_URL=postgresql://user:password@db-staging-server/farm_db

# Frontend CORS
CORS_ALLOWED_ORIGINS=https://staging.yourdomain.com,https://www.staging.yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Email
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
```

2. **Update settings.py** for staging:
```python
import logging
from decouple import config

# Load environment
DEBUG = config('DEBUG', default=False, cast=bool)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/farm/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

3. **Build and Deploy**:
```bash
# Backend
python manage.py collectstatic --noinput
python manage.py migrate

# Frontend
cd frontend
npm run build
# Copy build/ to static files directory
```

4. **Run with production server**:
```bash
# Daphne with concurrency
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application \
  --workers 4 \
  --ws-per-message-deflate 0
```

### Frontend Configuration

1. **Create .env.staging** file in `frontend/`:
```env
REACT_APP_API_URL=https://staging.yourdomain.com/api
REACT_APP_WS_URL=wss://staging.yourdomain.com/ws
REACT_APP_ENV=staging
```

2. **Build for staging**:
```bash
npm run build  # Creates optimized production build
```

## Production Environment Setup

### Backend Configuration

1. **Create .env.production** file** (keep secure, use secrets management):
```env
# Django Settings
DEBUG=False
SECRET_KEY=GENERATE-RANDOM-SECRET-KEY-64-CHARACTERS
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@prod-db-server:5432/farm_production

# Frontend CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Channels - Use Redis
CHANNEL_LAYERS_URL=redis://cache-server:6379/0

# Email
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=app-password

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/farm/django.log

# Cache
CACHE_URL=redis://cache-server:6379/1
```

2. **Generate secure SECRET_KEY**:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

3. **Update production settings**:
```python
# myproject/settings_production.py
from .settings import *
import os

DEBUG = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'farm_production',
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
    }
}

# Redis Cache & Channels
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://cache-server:6379/1',
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('cache-server', 6379)],
        },
    },
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/farm/static/'
MEDIA_ROOT = '/var/www/farm/media/'
MEDIA_URL = '/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/farm/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Frontend Configuration

1. **Create .env.production** file in `frontend/`:
```env
REACT_APP_API_URL=https://yourdomain.com/api
REACT_APP_WS_URL=wss://yourdomain.com/ws
REACT_APP_ENV=production
```

2. **Build for production**:
```bash
npm run build
# Creates optimized bundle in build/ directory
```

### Docker Setup (Optional but Recommended)

**Dockerfile**:
```dockerfile
# Backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=myproject.settings_production

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "myproject.asgi:application"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: farm_production
      POSTGRES_USER: farm_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql://farm_user:secure_password@db:5432/farm_production
      REDIS_URL: redis://redis:6379
    volumes:
      - ./media:/app/media
      - ./static:/app/static

  frontend:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    command: npm run build

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./media:/usr/share/nginx/html/media
      - ./static:/usr/share/nginx/html/static
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Nginx Configuration

**nginx.conf**:
```nginx
upstream django {
    server backend:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # API and WebSocket Proxy
    location /api {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Static Files
    location /static {
        alias /usr/share/nginx/html/static;
        expires 30d;
    }
    
    location /media {
        alias /usr/share/nginx/html/media;
        expires 7d;
    }
    
    # React Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }
}
```

## Environment-Specific Commands

### Development
```bash
# Backend
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application

# Frontend
npm start
```

### Staging
```bash
# Backend
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application --workers 2

# Frontend
npm run build
# Served by Nginx
```

### Production
```bash
# Using Docker
docker-compose up -d

# Or using systemd service
systemctl start farm-backend
systemctl start farm-frontend
```

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Unique SECRET_KEY generated
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SSL/TLS certificates installed
- [ ] SECURE_SSL_REDIRECT=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] Database credentials in secrets management
- [ ] Email backend configured
- [ ] Firewall rules set up
- [ ] Regular backups configured
- [ ] Log monitoring set up
- [ ] Security headers configured (HSTS, CSP)

## Monitoring & Maintenance

### Health Checks
```bash
# Health endpoint
curl https://yourdomain.com/api/health/

# Database connection
python manage.py dbshell

# Redis connection
redis-cli ping
```

### Logs
```bash
# Django logs
tail -f /var/log/farm/django.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
systemctl restart farm-backend
systemctl restart farm-frontend
```

---

**Created**: May 5, 2026
**Status**: Production-ready
