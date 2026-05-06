# Farm Management System - React Migration Guide

A comprehensive guide for migrating your Django server-rendered farm management system to a modern React frontend with real-time updates via WebSockets.

## 📋 Overview

This migration strategy allows you to gradually transition from Django templates to React while maintaining full backward compatibility. The approach uses:

- **Django REST Framework** for API endpoints
- **Django Channels** for real-time WebSocket updates
- **React Hooks** for component state management
- **Fallback polling** if WebSocket connections fail

## 🏗️ Architecture

### Backend Structure
```
myproject/
├── farm/
│   ├── serializers.py          # DRF serializers
│   ├── api_views.py            # REST API viewsets
│   ├── api_urls.py             # API URL routing
│   ├── consumers.py            # WebSocket consumers
│   ├── routing.py              # WebSocket routing
│   ├── views.py                # Original Django views (PRESERVED)
│   ├── urls.py                 # Original URL patterns (PRESERVED)
│   ├── templates/              # Original templates (PRESERVED)
│   └── models.py               # Models (UNCHANGED)
├── myproject/
│   ├── settings.py             # Updated with DRF, CORS, Channels
│   ├── asgi.py                 # Updated for Channels
│   ├── urls.py                 # Includes API routes
│   └── wsgi.py                 # UNCHANGED
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── Animals.jsx
│   │   ├── EggProduction.jsx
│   │   └── ...more components
│   ├── services/
│   │   ├── apiService.js       # HTTP client
│   │   └── webSocketService.js # WebSocket manager
│   ├── hooks/
│   │   └── index.js            # Custom React hooks
│   ├── App.jsx                 # Main app component
│   └── index.js                # React entry point
├── package.json
└── .env                        # Environment variables
```

## 🚀 Setup Instructions

### Step 1: Install Backend Dependencies

```bash
cd "c:\Users\Haids\OneDrive\farm inventories"

# Install required packages
pip install djangorestframework
pip install django-cors-headers
pip install channels
pip install channels-redis  # Optional: for production
pip install daphne            # ASGI server
```

### Step 2: Update Django Settings

The settings.py has already been updated with:
- REST_FRAMEWORK configuration
- CORS settings
- CHANNELS configuration

### Step 3: Run Migrations

```bash
python myproject/manage.py migrate
```

### Step 4: Start Django Server

Option A: Using Django Development Server (HTTP only):
```bash
python myproject/manage.py runserver 8000
```

Option B: Using Daphne (supports WebSockets):
```bash
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application
```

### Step 5: Set Up React Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
echo "REACT_APP_WS_URL=ws://localhost:8000/ws" >> .env

# Start development server
npm start
```

The React app will open at `http://localhost:3000`

## 🔌 API Endpoints Reference

### Animals
```
GET    /api/animals/                    # List all animals
POST   /api/animals/                    # Create animal
GET    /api/animals/{id}/               # Get specific animal
PUT    /api/animals/{id}/               # Update animal
DELETE /api/animals/{id}/               # Delete animal
GET    /api/animals/by_category/        # Filter by category
GET    /api/animals/{id}/statistics/    # Get animal statistics
```

### Egg Production
```
GET    /api/egg-production/             # List all productions
POST   /api/egg-production/             # Record new production
GET    /api/egg-production/today_total/ # Get today's total
GET    /api/egg-production/weekly_summary/ # Get weekly data
GET    /api/egg-production/by_date_range/ # Filter by date
```

### Feed
```
GET    /api/feeds/                      # List all feeds
GET    /api/feeds/low_stock/            # Get low stock alerts
GET    /api/feeds/stock_summary/        # Get feed summary
POST   /api/feeds/                      # Create feed
```

### Mortality
```
GET    /api/mortality/                  # List mortality records
POST   /api/mortality/                  # Record mortality
GET    /api/mortality/weekly_summary/   # Weekly summary
GET    /api/mortality/by_date_range/    # Filter by date
```

### Activities
```
GET    /api/activities/                 # List all activities
GET    /api/activities/today/           # Get today's activities
GET    /api/activities/by_date_range/   # Filter by date/type
```

### Notifications
```
GET    /api/notifications/              # List notifications
POST   /api/notifications/{id}/mark_as_read/ # Mark as read
POST   /api/notifications/mark_all_as_read/  # Mark all as read
GET    /api/notifications/unread_count/      # Get unread count
```

### Dashboard
```
GET    /api/dashboard/summary/          # Get dashboard data
GET    /api/dashboard/recent_activity/  # Get recent activities
```

## 🔄 WebSocket Connections

### Dashboard Real-time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');

// Listen for updates
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'dashboard_update') {
    console.log('Dashboard updated:', message.data);
  }
  if (message.type === 'egg_production_recorded') {
    console.log('New egg production:', message.data);
  }
  if (message.type === 'mortality_recorded') {
    console.log('Mortality recorded:', message.data);
  }
};

// Send commands
ws.send(JSON.stringify({ command: 'get_dashboard' }));
```

### Notifications Real-time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

// Listen for notifications
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'notification') {
    console.log('New notification:', message);
  }
};
```

## 🪝 React Hooks Usage

### useFetch - Fetch data from API

```javascript
import { useFetch } from './hooks';

function MyComponent() {
  const { data, loading, error, refetch } = useFetch('/animals/');
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {data?.map(animal => <div key={animal.id}>{animal.name}</div>)}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

### useDashboardRealtime - Real-time dashboard updates

```javascript
import { useDashboardRealtime } from './hooks';

function Dashboard() {
  const { dashboardData, alerts, activities, isConnected, requestUpdate } = useDashboardRealtime();
  
  return (
    <div>
      <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnected ? 'Live' : 'Offline'}
      </div>
      <div>Total Animals: {dashboardData?.total_animals}</div>
      {alerts.map(alert => <div key={alert.id}>{alert.title}</div>)}
      <button onClick={() => requestUpdate('get_dashboard')}>Refresh</button>
    </div>
  );
}
```

### usePost - Post data to API

```javascript
import { usePost } from './hooks';

function RecordEggs() {
  const { post, loading, error } = usePost();
  
  const handleSubmit = async (formData) => {
    try {
      const result = await post('/egg-production/', formData);
      console.log('Success:', result);
    } catch (err) {
      console.error('Error:', err);
    }
  };
  
  return (
    <button onClick={() => handleSubmit({...data})} disabled={loading}>
      {loading ? 'Saving...' : 'Save'}
    </button>
  );
}
```

### usePoll - Poll API at intervals

```javascript
import { usePoll } from './hooks';
import { eggProductionAPI } from './services/apiService';

function EggStats() {
  const { data: summary } = usePoll(
    () => eggProductionAPI.getWeeklySummary(),
    5000,  // Poll every 5 seconds
    true   // Enable polling
  );
  
  return <div>Weekly Total: {summary?.total}</div>;
}
```

### useForm - Handle form state

```javascript
import { useForm } from './hooks';

function AddAnimal() {
  const { values, handleChange, handleBlur, handleSubmit, touched, errors } = useForm(
    { name: '', category: '', total_count: 0 },
    async (values) => {
      await animalAPI.create(values);
      alert('Animal added!');
    }
  );
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={values.name}
        onChange={handleChange}
        onBlur={handleBlur}
      />
      {touched.name && errors.name && <span>{errors.name}</span>}
      <button type="submit">Add Animal</button>
    </form>
  );
}
```

## 🔐 Authentication

The system uses Django's session-based authentication:

1. **Login endpoint**: POST `/login/` (existing Django view preserved)
2. **Logout endpoint**: GET `/logout/` (existing Django view preserved)
3. **API authentication**: Uses session cookies (configured with `withCredentials: true`)

No changes needed to existing authentication. The React app will automatically use session cookies for API requests.

## 🐛 Fallback Mechanisms

### WebSocket Fallback to Polling

If WebSocket connection fails:
1. Dashboard component catches the error
2. Automatically falls back to `usePoll` for periodic updates
3. Shows "Offline" status but continues fetching data every 5 seconds

### API Error Handling

```javascript
import { handleAPIError } from './services/apiService';

try {
  const data = await apiClient.get('/endpoint');
} catch (error) {
  const { status, message, data } = handleAPIError(error);
  console.error(`Error ${status}: ${message}`);
}
```

## 🚀 Gradual Migration Strategy

### Phase 1: API & Infrastructure (COMPLETE)
- ✅ Set up Django REST Framework
- ✅ Create serializers for all models
- ✅ Create API viewsets and endpoints
- ✅ Set up Django Channels for WebSockets
- ✅ Configure CORS and authentication

### Phase 2: React Frontend (IN PROGRESS)
- ✅ Set up React project structure
- ✅ Create API service layer
- ✅ Create WebSocket service
- ✅ Create custom hooks
- ✅ Create example components

### Phase 3: Component Migration (NEXT)
- [ ] Convert Dashboard to React
- [ ] Convert Animals to React
- [ ] Convert Egg Production to React
- [ ] Convert Feed Inventory to React
- [ ] Convert Mortality Records to React
- [ ] Convert Reports to React

### Phase 4: Full Integration (LATER)
- [ ] Test all components with API
- [ ] Implement error boundaries
- [ ] Add loading states
- [ ] Test WebSocket connections
- [ ] Performance optimization

### Phase 5: Deployment (FINAL)
- [ ] Build React production bundle
- [ ] Deploy to production servers
- [ ] Monitor performance
- [ ] Remove old Django templates

## 📊 Testing the Integration

### Test API Endpoints

```bash
# Get animals
curl http://localhost:8000/api/animals/

# Get dashboard summary
curl http://localhost:8000/api/dashboard/summary/

# Create egg production (requires authentication)
curl -X POST http://localhost:8000/api/egg-production/ \
  -H "Content-Type: application/json" \
  -d '{"animal": 1, "quantity": 50, "date": "2024-05-05"}'
```

### Test WebSocket Connection

```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({ command: 'get_dashboard' }));
```

## 🛠️ Troubleshooting

### CORS Errors
- Make sure `CORS_ALLOWED_ORIGINS` in settings.py includes `http://localhost:3000`
- Ensure `CORS_ALLOW_CREDENTIALS = True`

### WebSocket Connection Fails
- Check that Daphne is running: `daphne -b 127.0.0.1 -p 8000 myproject.asgi:application`
- Verify WebSocket URL in `.env` file

### API Returns 401 Unauthorized
- Make sure you're logged in through the Django app first
- Check that session cookie is being sent with requests
- Verify `withCredentials: true` in apiClient configuration

### React Components Don't Update
- Check browser console for errors
- Verify API responses in Network tab
- Ensure hooks are being called correctly
- Check that WebSocket is connected (if using real-time features)

## 📝 Next Steps

1. **Start the Django backend with WebSocket support**:
   ```bash
   daphne -b 127.0.0.1 -p 8000 myproject.asgi:application
   ```

2. **Start the React development server**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test a single component**:
   - Open React app at `http://localhost:3000`
   - Check browser console for any errors
   - Verify API requests in Network tab

4. **Migrate components one at a time**:
   - Complete testing in React before removing Django template
   - Keep both versions running during transition
   - Gradually replace Django views with React routing

## 📚 Additional Resources

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Django Channels Docs](https://channels.readthedocs.io/)
- [React Hooks Documentation](https://react.dev/reference/react/hooks)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## ✅ Backward Compatibility Checklist

- ✅ All existing Django views remain functional
- ✅ All existing Django templates preserved
- ✅ All existing URL patterns work
- ✅ Session authentication preserved
- ✅ Database schema unchanged
- ✅ Original features unmodified

## 🎯 Key Principles

1. **Non-breaking**: React coexists with Django templates
2. **Gradual**: Migrate one component at a time
3. **Testable**: Each component tested before full replacement
4. **Performant**: WebSockets for real-time, fallback to polling
5. **Secure**: Session-based authentication preserved
6. **Maintainable**: Clean separation of concerns

---

**Status**: Django backend API fully configured. React frontend ready for component migration.
