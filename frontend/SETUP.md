# React Frontend - Quick Setup Guide

## Installation & Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Create Environment File
Create `.env` file in the `frontend` directory:

```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 3. Start Development Server
```bash
npm start
```

The app will open at `http://localhost:3000`

## File Structure

```
src/
├── components/              # React components
│   ├── Dashboard.jsx       # Main dashboard with real-time updates
│   ├── Animals.jsx         # Animals list and management
│   ├── EggProduction.jsx   # Egg production recording
│   ├── Animals.css         # Component styles
│   ├── Dashboard.css
│   └── EggProduction.css
├── services/               # API integration
│   ├── apiService.js       # HTTP client with all endpoints
│   └── webSocketService.js # WebSocket connection manager
├── hooks/                  # Custom React hooks
│   └── index.js            # All custom hooks
├── App.jsx                 # Main app component
├── App.css                 # Global styles
└── index.js                # React entry point
```

## Component Checklist

- ✅ Dashboard (Real-time updates via WebSocket)
- ✅ Animals (List, filter, statistics)
- ✅ EggProduction (Record, view history, weekly summary)
- ⬜ FeedInventory (To be created)
- ⬜ MortalityRecords (To be created)
- ⬜ Employees (To be created)
- ⬜ Notifications (To be created)
- ⬜ UserProfile (To be created)

## Example Usage

### Basic Component with Data Fetching
```javascript
import { useFetch } from '../hooks';

export function MyComponent() {
  const { data, loading, error, refetch } = useFetch('/animals/');
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {data?.map(item => <div key={item.id}>{item.name}</div>)}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

### Real-time Dashboard
```javascript
import { useDashboardRealtime } from '../hooks';

export function RealtimeDashboard() {
  const { dashboardData, alerts, isConnected } = useDashboardRealtime();
  
  return (
    <div>
      <span className={isConnected ? 'connected' : 'offline'}>
        {isConnected ? '🟢 Live' : '🔴 Offline'}
      </span>
      <p>Animals: {dashboardData?.total_animals}</p>
      <p>Today's Eggs: {dashboardData?.total_eggs_today}</p>
    </div>
  );
}
```

### Form Submission
```javascript
import { useForm } from '../hooks';
import { animalAPI } from '../services/apiService';

export function AddAnimal() {
  const { values, handleChange, handleSubmit, isSubmitting } = useForm(
    { name: '', category: '', total_count: 0 },
    async (data) => {
      await animalAPI.create(data);
      alert('Animal added!');
    }
  );
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="name" value={values.name} onChange={handleChange} />
      <select name="category" value={values.category} onChange={handleChange}>
        <option>Chicken</option>
        <option>Duck</option>
      </select>
      <input name="total_count" type="number" value={values.total_count} onChange={handleChange} />
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Adding...' : 'Add Animal'}
      </button>
    </form>
  );
}
```

## Styling

All components use CSS files in the components directory. They follow a consistent design pattern:

- `.{ComponentName}.css` - Component-specific styles
- Global CSS uses CSS variables for theming
- Responsive design with flexbox/grid

## Common Issues & Solutions

### WebSocket Connection Fails
- Ensure Django is running with Daphne: `daphne -b 127.0.0.1 -p 8000 myproject.asgi:application`
- Check `.env` file WebSocket URL is correct
- Verify Django settings have Channels configured

### API Returns 404
- Make sure you're using `/api/` prefix
- Check Django API endpoints are created in `farm/api_urls.py`
- Verify main `urls.py` includes API routes

### Components Don't Update
- Check browser console for errors
- Verify data is coming through in Network tab
- Ensure component is using correct hook

### CORS Errors
- Check `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
- Verify `withCredentials: true` in apiService.js

## Building for Production

```bash
npm run build
```

This creates an optimized production build in `build/` directory.

To serve the React app:
1. Copy `build/` contents to Django static files
2. Serve from Django or configure reverse proxy (Nginx)
3. Update API/WebSocket URLs to production URLs

## Monitoring Real-time Updates

Open browser DevTools and check:

1. **Network Tab**:
   - Check API requests to `/api/` endpoints
   - Watch for WebSocket connection to `/ws/`

2. **Console**:
   - Messages like "WebSocket connected"
   - API response data
   - Any errors

3. **Redux/State Inspector** (if installed):
   - Monitor component state changes
   - Track real-time updates

## Performance Tips

- Use `usePoll` instead of `useFetch` for frequently updated data
- Memoize callbacks with `useCallback`
- Use `React.memo()` for static components
- Lazy load components with `React.lazy()`
- Debounce search inputs with `useDebounce`

---

Ready to start developing! 🚀
