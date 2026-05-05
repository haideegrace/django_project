# React Frontend - Setup & Development Guide

Welcome to the Farm Management System React frontend! This guide covers everything you need to get started developing and deploying the React application.

## 📋 Quick Start

### 1. Prerequisites
- Node.js 14.0.0 or higher
- npm 6.0.0 or higher
- Python/Django backend running (see main README)

### 2. Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env
# On Linux/Mac: cp .env.example .env

# Start development server
npm start
```

The app opens at `http://localhost:3000`

## 🗂️ Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML template
│
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx       # Dashboard component with real-time updates
│   │   ├── Dashboard.css       # Dashboard styles
│   │   ├── Animals.jsx         # Animals list with filtering
│   │   ├── Animals.css         # Animals styles
│   │   ├── EggProduction.jsx   # Egg production form & history
│   │   ├── EggProduction.css   # Egg production styles
│   │   ├── ErrorBoundary.jsx   # Error handling component
│   │   └── [Feature].jsx       # Additional components (coming soon)
│   │
│   ├── services/
│   │   ├── apiService.js       # HTTP client for API calls
│   │   └── webSocketService.js # WebSocket management
│   │
│   ├── hooks/
│   │   └── index.js            # Custom React hooks (8 hooks)
│   │
│   ├── App.jsx                 # Main app component
│   ├── App.css                 # Global styles & layout
│   ├── index.js                # React entry point
│   └── index.css               # Base styles (if needed)
│
├── package.json                # Dependencies & scripts
├── .env.example                # Environment template
├── .env                        # Environment variables (git-ignored)
├── SETUP.md                    # React-specific setup guide
├── README.md                   # Project overview
└── node_modules/               # Dependencies (git-ignored)
```

## ⚙️ Environment Configuration

### .env File Setup

Create a `.env` file in the `frontend/` directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws

# Environment
REACT_APP_ENV=development
```

### Environment Variable Usage

In React components:
```javascript
const apiUrl = process.env.REACT_APP_API_URL;
const wsUrl = process.env.REACT_APP_WS_URL;
```

### Environment Values

| Variable | Development | Staging | Production |
|----------|-------------|---------|-----------|
| REACT_APP_API_URL | http://localhost:8000/api | https://staging.domain.com/api | https://domain.com/api |
| REACT_APP_WS_URL | ws://localhost:8000/ws | wss://staging.domain.com/ws | wss://domain.com/ws |
| REACT_APP_ENV | development | staging | production |

## 🚀 Available Scripts

### npm start
Runs the app in development mode at `http://localhost:3000`

The page reloads when you make changes.

```bash
npm start
```

### npm test
Launches the test runner in interactive watch mode

```bash
npm test
```

### npm run build
Builds the app for production to the `build` folder

Creates an optimized production build with minification and source maps.

```bash
npm run build
```

### npm run eject
Exposes all configuration (one-way operation, not reversible)

```bash
npm run eject
```

## 🎣 Custom React Hooks

The application includes 8 custom hooks for common functionality:

### useFetch(url, options)
Fetch data from API endpoints

```javascript
const { data, loading, error, refetch } = useFetch('/animals/');

if (loading) return <div>Loading...</div>;
if (error) return <div>Error: {error}</div>;
return <div>{data.length} animals</div>;
```

**Options**:
- `method` - HTTP method (default: GET)
- `body` - Request body
- `headers` - Custom headers
- `skip` - Skip initial fetch if true

### useDashboardRealtime()
Real-time dashboard updates via WebSocket

```javascript
const { 
  dashboardData, 
  alerts, 
  activities, 
  isConnected, 
  requestUpdate 
} = useDashboardRealtime();

return (
  <div>
    {isConnected ? '✓ Live' : '○ Offline'}
    <div>Animals: {dashboardData?.animals}</div>
  </div>
);
```

### useNotificationsRealtime()
Real-time notifications via WebSocket

```javascript
const { notifications, unreadCount, isConnected } = useNotificationsRealtime();

return (
  <div>
    Notifications ({unreadCount})
    {notifications.map(n => <div key={n.id}>{n.message}</div>)}
  </div>
);
```

### usePost()
Handle POST requests

```javascript
const { post, loading, error } = usePost();

const handleSubmit = async (formData) => {
  try {
    const response = await post('/animals/', formData);
    console.log('Created:', response);
  } catch (err) {
    console.error('Error:', err.message);
  }
};
```

### usePoll(fetchFunction, interval, enabled)
Poll API at regular intervals

```javascript
const { data, loading, error } = usePoll(
  () => eggProductionAPI.getWeeklySummary(),
  5000, // 5 second interval
  true  // enabled
);
```

### useForm(initialValues, onSubmit)
Manage form state and validation

```javascript
const { 
  values, 
  touched, 
  errors, 
  handleChange, 
  handleBlur, 
  handleSubmit, 
  isSubmitting 
} = useForm(
  { animal: '', quantity: '' },
  async (values) => {
    await submitForm(values);
  }
);

return (
  <form onSubmit={handleSubmit}>
    <input 
      name="animal" 
      value={values.animal} 
      onChange={handleChange} 
    />
    {errors.animal && <span>{errors.animal}</span>}
  </form>
);
```

### useDebounce(value, delay)
Debounce value changes

```javascript
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearchTerm = useDebounce(searchTerm, 300);

useEffect(() => {
  // This runs only after searchTerm hasn't changed for 300ms
  searchAnimals(debouncedSearchTerm);
}, [debouncedSearchTerm]);
```

### useAsync(asyncFunction, immediate)
Execute async functions with caching

```javascript
const { execute, status, data, error } = useAsync(
  async () => {
    return await fetchData();
  },
  true // immediate
);
```

## 🎨 Styling System

The application uses CSS variables and custom styles for consistent theming.

### CSS Variables (in App.css)

```css
:root {
  --primary: #2e7d32;           /* Main green */
  --primary-dark: #1b5e20;      /* Dark green */
  --primary-light: #4caf50;     /* Light green */
  
  --warning: #ff9800;           /* Orange alerts */
  --danger: #d32f2f;            /* Red errors */
  --success: #4caf50;           /* Green success */
  --info: #2196f3;              /* Blue info */
  
  --bg: #ffffff;                /* Background */
  --text-primary: #212121;      /* Primary text */
  --text-secondary: #757575;    /* Secondary text */
  --border: #e0e0e0;            /* Border color */
  
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

### Color Usage

- **Primary (#2e7d32)**: Main buttons, active states, highlights
- **Warning (#ff9800)**: Caution alerts, "needs attention" items
- **Danger (#d32f2f)**: Critical alerts, deletions, errors
- **Success (#4caf50)**: Confirmations, completed actions
- **Info (#2196f3)**: Informational messages, status updates

### Responsive Design

The application is responsive with breakpoint at 768px:

```css
@media (max-width: 768px) {
  /* Mobile-specific styles */
  .layout {
    flex-direction: column;
  }
  
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
  }
}
```

## 🔌 API Service Usage

All API calls go through the centralized `apiService.js`:

```javascript
import * as apiService from '../services/apiService';

// Get all animals
const animals = await apiService.animalAPI.getAll();

// Get animal by ID
const animal = await apiService.animalAPI.getById(1);

// Create new animal
const newAnimal = await apiService.animalAPI.create({
  name: 'Chicken 1',
  category: 'chicken',
  total_count: 50
});

// Update animal
await apiService.animalAPI.update(1, {
  total_count: 60
});

// Delete animal
await apiService.animalAPI.delete(1);

// Get animals by category
const chickens = await apiService.animalAPI.getByCategory('chicken');
```

## 🔌 WebSocket Service Usage

Real-time updates via WebSocket:

```javascript
import webSocketService from '../services/webSocketService';

// Connect to WebSocket
webSocketService.connect('ws://localhost:8000/ws/dashboard/');

// Listen for events
const unsubscribe = webSocketService.on('dashboard_update', (data) => {
  console.log('Dashboard updated:', data);
});

// Send data
webSocketService.emit('get_dashboard', {});

// Cleanup
unsubscribe(); // Stop listening
webSocketService.disconnect(); // Close connection
```

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Write Tests
Create test files alongside components:

```javascript
// Dashboard.test.jsx
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  const element = screen.getByText(/dashboard/i);
  expect(element).toBeInTheDocument();
});
```

## 🐛 Common Issues

### WebSocket Connection Failed

**Problem**: WebSocket connection times out or fails

**Solution**:
1. Check Daphne is running: `daphne -b 127.0.0.1 -p 8000 myproject.asgi:application`
2. Check REACT_APP_WS_URL in .env is correct
3. Check browser console for error messages
4. Verify firewall isn't blocking WebSocket

### CORS Errors

**Problem**: API requests fail with CORS error

**Solution**:
1. Check CORS_ALLOWED_ORIGINS includes http://localhost:3000
2. Verify apiService has `withCredentials: true`
3. Restart Django server
4. Clear browser cache

### 401 Unauthorized Errors

**Problem**: API returns 401 Unauthorized

**Solution**:
1. Login at http://localhost:8000/login/ first
2. Check session cookie is being sent
3. Verify withCredentials in apiService.js
4. Check user has required permissions

### Components Not Updating

**Problem**: Component state not updating when data changes

**Solution**:
1. Check useEffect dependencies are correct
2. Verify WebSocket is connected (check logs)
3. Use React DevTools to inspect component state
4. Check Network tab for API requests

## 📦 Building for Production

### Build Steps

```bash
# Build optimized bundle
npm run build

# Result is in build/ directory
# Copy to Django static files:
cp -r build/* ../myproject/static/
```

### Build Optimization

The build includes:
- Minified JavaScript and CSS
- Source maps for debugging
- Optimized bundle splitting
- Asset optimization

### Environment Variables for Production

Update `.env` before building:

```env
REACT_APP_API_URL=https://yourdomain.com/api
REACT_APP_WS_URL=wss://yourdomain.com/ws
REACT_APP_ENV=production
```

## 🚀 Deployment

### Serve with Django

1. Build React: `npm run build`
2. Copy build to static directory
3. Configure Django to serve React
4. Update API URLs for production domain

### Serve with Nginx

```nginx
location / {
    root /var/www/farm/frontend;
    try_files $uri /index.html;
}

location /api {
    proxy_pass http://django:8000;
}

location /ws {
    proxy_pass http://django:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Docker Build

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📚 Resources

- [React Documentation](https://react.dev)
- [React Hooks](https://react.dev/reference/react/hooks)
- [Axios Documentation](https://axios-http.com/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [CSS Grid & Flexbox](https://css-tricks.com/)

## ✅ Component Checklist

Implemented Components:
- ✅ Dashboard - Real-time updates with WebSocket
- ✅ Animals - List and filter animals
- ✅ EggProduction - Record and view production history
- ✅ ErrorBoundary - Error handling

Coming Soon:
- 🚧 FeedInventory - Manage feed stock
- 🚧 MortalityRecords - Track animal mortality
- 🚧 Employees - Employee management
- 🚧 Notifications - Notification center
- 🚧 UserProfile - User settings
- 🚧 Reports - Advanced reporting

## 🆘 Getting Help

1. **Check the troubleshooting section** above
2. **Review component examples** in `src/components/`
3. **Check browser console** for error messages
4. **Review Network tab** for API responses
5. **Check MIGRATION_GUIDE.md** for detailed info

## 📊 Performance Tips

- Use React.memo() for static components
- Implement code splitting with React.lazy()
- Use useCallback for event handlers
- Optimize images and assets
- Implement pagination for large lists
- Use service workers for offline support

## 🔐 Security

- ✅ Session authentication preserved
- ✅ CSRF protection enabled
- ✅ XSS protection via React
- ✅ Secure cookie handling
- ✅ Input validation on forms
- ✅ API response validation

---

**Version**: 1.0.0
**Last Updated**: May 5, 2026
**Status**: Production Ready ✅
