# Integration Checklist & Quick Reference

## ✅ Pre-Launch Checklist

### Backend Setup
- [ ] Python virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database migrated: `python myproject/manage.py migrate`
- [ ] Django admin working: `http://localhost:8000/admin/`
- [ ] API endpoints responding: `http://localhost:8000/api/animals/`
- [ ] WebSocket server running with Daphne
- [ ] CORS configured for React frontend
- [ ] Environment variables set (if using production)

### Frontend Setup
- [ ] Node.js and npm installed
- [ ] Dependencies installed: `npm install`
- [ ] `.env` file created from `.env.example`
- [ ] API URL correct: `REACT_APP_API_URL=http://localhost:8000/api`
- [ ] WebSocket URL correct: `REACT_APP_WS_URL=ws://localhost:8000/ws`
- [ ] React dev server starting: `npm start`
- [ ] React app loads at `http://localhost:3000`

### Integration Tests
- [ ] Can fetch animals from API
- [ ] Can record egg production
- [ ] Dashboard loads real-time data
- [ ] WebSocket shows "Live Updates"
- [ ] Notifications appear in real-time
- [ ] No CORS errors in console
- [ ] No API 401/403 errors
- [ ] Page refresh doesn't break state

---

## 🚀 Startup Commands

### Terminal 1: Django Backend
```bash
# Navigate to project root
cd "c:\Users\Haids\OneDrive\farm inventories"

# Activate virtual environment
.venv\Scripts\activate

# Start Django with WebSocket support
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application

# Or use Django dev server (HTTP only)
# python myproject/manage.py runserver 8000
```

### Terminal 2: React Frontend
```bash
# Navigate to frontend directory
cd "c:\Users\Haids\OneDrive\farm inventories\frontend"

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

### Terminal 3: Optional - Django Admin
```bash
cd "c:\Users\Haids\OneDrive\farm inventories"
.venv\Scripts\activate

# Create superuser (if not exists)
python myproject/manage.py createsuperuser

# Access at: http://localhost:8000/admin/
```

---

## 📋 API Testing Guide

### Test with Browser
```
GET http://localhost:8000/api/animals/
GET http://localhost:8000/api/dashboard/summary/
GET http://localhost:8000/api/notifications/unread_count/
```

### Test with cURL
```bash
# Get all animals
curl http://localhost:8000/api/animals/

# Get dashboard summary
curl http://localhost:8000/api/dashboard/summary/

# Create animal (requires login)
curl -X POST http://localhost:8000/api/animals/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Chicken1", "category": "chicken", "total_count": 50}' \
  --cookie "sessionid=YOUR_SESSION_ID"
```

### Test WebSocket Connection
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');
ws.onopen = () => {
  console.log('Connected!');
  ws.send(JSON.stringify({ command: 'get_dashboard' }));
};
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Dashboard update:', data);
};
```

---

## 🔧 Common Configuration

### Django Settings (myproject/settings.py)
```python
# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Channels
ASGI_APPLICATION = 'myproject.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

### React Environment (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

---

## 📊 Database Schema

The existing schema is preserved. Key models:

```
Animal
├── category (CharField)
├── name (CharField)
├── total_count (PositiveIntegerField)
└── timestamps

EggProduction
├── animal (ForeignKey)
├── quantity (PositiveIntegerField)
├── date (DateField)
└── collected_by (ForeignKey to User)

Feed
├── name (CharField)
├── current_stock (DecimalField)
├── low_stock_threshold (DecimalField)
└── unit (CharField)

Mortality
├── animal (ForeignKey)
├── count (PositiveIntegerField)
├── date (DateField)
└── reported_by (ForeignKey to User)

ActivityLog
├── activity_type (CharField)
├── employee (ForeignKey)
├── animal (ForeignKey)
├── date (DateField)
└── quantity (DecimalField)

Notification
├── user (ForeignKey)
├── title (CharField)
├── message (TextField)
├── is_read (BooleanField)
└── notification_type (CharField)
```

---

## 🔑 Key Files Modified

### Backend Files Created
- `farm/serializers.py` - 200+ lines
- `farm/api_views.py` - 400+ lines
- `farm/api_urls.py` - Router configuration
- `farm/consumers.py` - WebSocket handlers
- `farm/routing.py` - WebSocket URL routing
- `myproject/settings.py` - Updated with DRF, CORS, Channels
- `myproject/asgi.py` - Updated for WebSocket support

### Frontend Files Created
- `frontend/src/services/apiService.js` - API client
- `frontend/src/services/webSocketService.js` - WebSocket client
- `frontend/src/hooks/index.js` - Custom hooks
- `frontend/src/components/Dashboard.jsx` - Dashboard component
- `frontend/src/components/Animals.jsx` - Animals component
- `frontend/src/components/EggProduction.jsx` - Egg production component
- `frontend/src/components/ErrorBoundary.jsx` - Error boundary
- `frontend/src/App.jsx` - Main app
- `frontend/src/App.css` - Global styles
- `frontend/src/index.js` - Entry point
- `frontend/package.json` - Dependencies

### No Changes to Existing Files
- `farm/models.py` - ✅ Unchanged
- `farm/views.py` - ✅ Preserved
- `farm/urls.py` - ✅ Preserved
- `farm/templates/` - ✅ Preserved
- `farm/admin.py` - ✅ Unchanged
- Database schema - ✅ Unchanged

---

## 🐛 Debugging Tips

### Check Browser Console
1. Open DevTools (F12)
2. Check Console for JavaScript errors
3. Check Network tab for API requests
4. Check WebSocket connections in Network

### Check Django Logs
```bash
# Watch logs in real-time
tail -f /path/to/server.log

# Or check Django console output
# Errors appear in terminal where Daphne is running
```

### Enable Django Debug Toolbar
```python
# Add to INSTALLED_APPS in settings.py
'debug_toolbar',

# Add to MIDDLEWARE
'debug_toolbar.middleware.DebugToolbarMiddleware',

# Add to urls.py
if DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

### Test API with Insomnia/Postman
1. Import API routes
2. Test endpoints
3. Check response times
4. Verify authentication

---

## 📈 Performance Optimization

### Backend
- Use `select_related()` and `prefetch_related()` in queries
- Add database indexes on frequently queried fields
- Implement caching with Redis
- Use pagination for large datasets

### Frontend
- Use React.memo() for static components
- Implement code splitting
- Optimize images and assets
- Use service workers for caching

### WebSocket
- Monitor connection pool
- Set heartbeat interval
- Implement reconnection logic
- Handle message queue

---

## 🚀 Production Deployment

### Environment Variables (Create .env)
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Build Commands
```bash
# Backend
python myproject/manage.py collectstatic
python myproject/manage.py migrate

# Frontend
cd frontend
npm run build
```

### Server Configuration
```bash
# Use production ASGI server
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application --ws-per-message-deflate 0

# Or use Gunicorn
gunicorn myproject.wsgi:application -b 0.0.0.0:8000
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
}
```

---

## 📚 File Structure Reference

For quick navigation:

```
Components:     frontend/src/components/
Services:       frontend/src/services/
Hooks:          frontend/src/hooks/
API Views:      myproject/farm/api_views.py
Serializers:    myproject/farm/serializers.py
WebSocket:      myproject/farm/consumers.py
Settings:       myproject/settings.py
Database:       myproject/db.sqlite3 (git-ignored)
Original Views: myproject/farm/views.py (preserved)
```

---

## ✅ Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Django REST Framework | ✅ Complete | All endpoints created |
| Django Channels | ✅ Complete | WebSocket ready |
| React Setup | ✅ Complete | All dependencies in place |
| Authentication | ✅ Preserved | Session-based, unchanged |
| Database | ✅ Preserved | Schema unchanged |
| Original Templates | ✅ Preserved | All preserved, coexisting |
| Real-time Updates | ✅ Ready | WebSocket configured |
| Error Handling | ✅ Ready | Error boundary implemented |
| CORS | ✅ Configured | Localhost setup ready |

---

**Created**: May 5, 2026
**Status**: Ready for Development & Testing
