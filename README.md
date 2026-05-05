# Farm Management System - Full Stack Application

A modern farm management system with Django REST API backend and React real-time frontend.

## 📋 Project Overview

This is a comprehensive farm management solution that helps track:
- 🐔 Animal inventory and statistics
- 🥚 Egg production records and trends
- 🌾 Feed stock levels and alerts
- ⚠️ Mortality records and trends
- 👥 Employee activities and tracking
- 📋 Activity logs with photo documentation
- 📊 Real-time dashboards with WebSocket updates

## 🏗️ Project Structure

```
farm-management/
├── myproject/                      # Django Project Root
│   ├── farm/                       # Main App
│   │   ├── models.py              # Database models
│   │   ├── views.py               # Original Django views (preserved)
│   │   ├── api_views.py           # REST API viewsets
│   │   ├── serializers.py         # DRF serializers
│   │   ├── consumers.py           # WebSocket consumers
│   │   ├── routing.py             # WebSocket routing
│   │   ├── api_urls.py            # API URL routes
│   │   ├── urls.py                # Original URL routes (preserved)
│   │   └── templates/             # Original templates (preserved)
│   │
│   ├── myproject/                 # Django Settings
│   │   ├── settings.py            # Updated with DRF, CORS, Channels
│   │   ├── asgi.py                # Updated for WebSocket support
│   │   ├── wsgi.py                # WSGI (unchanged)
│   │   └── urls.py                # Main URL router
│   │
│   ├── manage.py                  # Django management script
│   └── db.sqlite3                 # Database (git-ignored)
│
├── frontend/                       # React Frontend
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Animals.jsx
│   │   │   ├── EggProduction.jsx
│   │   │   ├── ErrorBoundary.jsx
│   │   │   └── [Component].css
│   │   │
│   │   ├── services/              # API & WebSocket clients
│   │   │   ├── apiService.js      # HTTP client
│   │   │   └── webSocketService.js # WebSocket manager
│   │   │
│   │   ├── hooks/                 # Custom React hooks
│   │   │   └── index.js
│   │   │
│   │   ├── App.jsx                # Main app component
│   │   ├── App.css                # Global styles
│   │   └── index.js               # React entry point
│   │
│   ├── public/
│   │   └── index.html             # HTML template
│   │
│   ├── package.json               # npm dependencies
│   ├── .env.example               # Environment variables template
│   └── SETUP.md                   # React setup guide
│
├── MIGRATION_GUIDE.md             # Full migration documentation
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Clone or navigate to project**
   ```bash
   cd "c:\Users\Haids\OneDrive\farm inventories"
   ```

2. **Activate virtual environment**
   ```bash
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** (if not already done)
   ```bash
   python myproject/manage.py migrate
   ```

5. **Start Django with WebSocket support**
   ```bash
   daphne -b 127.0.0.1 -p 8000 myproject.asgi:application
   ```
   
   Or use Django dev server (HTTP only):
   ```bash
   python myproject/manage.py runserver 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file**
   ```bash
   copy .env.example .env
   # Or on Linux/Mac: cp .env.example .env
   ```

4. **Start development server**
   ```bash
   npm start
   ```
   
   The app opens at `http://localhost:3000`

## 🔌 API Documentation

### Authentication
- **Method**: Session-based (Django sessions)
- **Login**: POST `/login/` (existing Django endpoint)
- **Logout**: GET `/logout/` (existing Django endpoint)
- **Status**: GET `/api/profile/me/` (get current user)

### Core Endpoints

#### Animals
```
GET    /api/animals/
POST   /api/animals/
GET    /api/animals/{id}/
PUT    /api/animals/{id}/
DELETE /api/animals/{id}/
GET    /api/animals/by_category/?category=chicken
GET    /api/animals/{id}/statistics/
```

#### Egg Production
```
GET    /api/egg-production/
POST   /api/egg-production/
GET    /api/egg-production/today_total/
GET    /api/egg-production/weekly_summary/
GET    /api/egg-production/by_date_range/?start_date=2024-01-01&end_date=2024-01-31
```

#### Feed
```
GET    /api/feeds/
POST   /api/feeds/
GET    /api/feeds/low_stock/
GET    /api/feeds/stock_summary/
```

#### Mortality
```
GET    /api/mortality/
POST   /api/mortality/
GET    /api/mortality/weekly_summary/
GET    /api/mortality/by_date_range/?start_date=2024-01-01&end_date=2024-01-31
```

#### Activities
```
GET    /api/activities/
GET    /api/activities/today/
GET    /api/activities/by_date_range/?start_date=2024-01-01&end_date=2024-01-31&activity_type=egg_collection
```

#### Notifications
```
GET    /api/notifications/
POST   /api/notifications/{id}/mark_as_read/
POST   /api/notifications/mark_all_as_read/
GET    /api/notifications/unread_count/
```

#### Dashboard
```
GET    /api/dashboard/summary/
GET    /api/dashboard/recent_activity/
```

### WebSocket Endpoints
```
WS     ws://localhost:8000/ws/dashboard/    # Real-time dashboard updates
WS     ws://localhost:8000/ws/notifications/ # Real-time notifications
```

## 🪝 React Hooks Reference

### useFetch - Fetch data from API
```javascript
const { data, loading, error, refetch } = useFetch('/animals/');
```

### useDashboardRealtime - Real-time dashboard
```javascript
const { dashboardData, alerts, activities, isConnected, requestUpdate } = useDashboardRealtime();
```

### usePost - POST data to API
```javascript
const { post, loading, error } = usePost();
await post('/egg-production/', formData);
```

### usePoll - Poll API at intervals
```javascript
const { data } = usePoll(() => eggProductionAPI.getWeeklySummary(), 5000);
```

### useForm - Handle forms
```javascript
const { values, handleChange, handleSubmit, isSubmitting } = useForm(
  initialValues,
  onSubmit
);
```

## 🔐 Security Features

- ✅ Session-based authentication (preserved from original)
- ✅ CORS protection (configured for localhost)
- ✅ CSRF protection (Django built-in)
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection (React escaping)
- ✅ WebSocket authentication (requires session)

## 📊 Features

### Current Features
- ✅ Animal inventory management
- ✅ Real-time dashboard
- ✅ Egg production tracking
- ✅ Feed inventory management
- ✅ Mortality records
- ✅ Activity logging
- ✅ WebSocket real-time updates
- ✅ Responsive design

### Planned Features
- 🚧 Employee management UI
- 🚧 Advanced reporting
- 🚧 Export to PDF/Excel
- 🚧 Mobile app support
- 🚧 Multi-language support

## 🐛 Troubleshooting

### WebSocket Connection Failed
```
Solution: Ensure Daphne is running instead of Django dev server
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application
```

### CORS Errors
```
Check that CORS_ALLOWED_ORIGINS includes http://localhost:3000
in myproject/settings.py
```

### API Returns 401 Unauthorized
```
- Make sure you're logged in through Django first (/login/)
- Check that session cookie is being sent
- Verify withCredentials: true in apiService.js
```

### React Components Not Updating
```
- Check browser DevTools Network tab
- Verify API responses are correct
- Check that hooks are being called properly
- Ensure WebSocket is connected (if using real-time)
```

## 📝 Development Guide

### Adding a New Component

1. **Create component file** in `frontend/src/components/`
   ```javascript
   export function MyComponent() {
     const { data, loading } = useFetch('/endpoint/');
     return <div>{/* content */}</div>;
   }
   ```

2. **Create CSS file** with same name
   ```css
   /* MyComponent.css */
   .my-component { /* styles */ }
   ```

3. **Add to App.jsx** navigation
   ```javascript
   <button onClick={() => setCurrentPage('my-component')}>
     My Component
   </button>
   ```

### Adding a New API Endpoint

1. **Create serializer** in `farm/serializers.py`
2. **Create viewset** in `farm/api_views.py`
3. **Register in router** in `farm/api_urls.py`
4. **Use in React** with `apiService.js`

## 🧪 Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Build React for Production
```bash
cd frontend
npm run build
```

### Deploy Django
```bash
# Collect static files
python myproject/manage.py collectstatic

# Use production ASGI server (Daphne)
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application

# Or use Gunicorn + Daphne
gunicorn myproject.wsgi:application
```

## 📚 Documentation

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Detailed migration strategy
- [frontend/SETUP.md](frontend/SETUP.md) - React setup and usage
- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Django Channels Docs](https://channels.readthedocs.io/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit for review
5. Deploy to production

## 📄 License

Proprietary - BATAC Farm Management System

## ✅ Backward Compatibility

This project maintains **100% backward compatibility** with the original Django application:

- ✅ All original views still work
- ✅ All original templates preserved
- ✅ Original URL patterns functional
- ✅ Database schema unchanged
- ✅ Authentication system intact
- ✅ Session management preserved

The React frontend coexists with Django templates. You can migrate components gradually without affecting existing functionality.

## 🎯 Next Steps

1. **Test the setup**:
   - Start both Django and React servers
   - Test API endpoints in browser
   - Check WebSocket connection in console

2. **Migrate components**:
   - Convert one component at a time
   - Test thoroughly before removing old template
   - Keep both versions running during transition

3. **Monitor and optimize**:
   - Check performance metrics
   - Monitor WebSocket connections
   - Track API response times

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the migration guide
3. Check Django and React documentation
4. Review component examples

---

**Status**: ✅ Backend API fully set up | ✅ React frontend ready | 🚀 Ready for component migration

**Last Updated**: May 5, 2026
