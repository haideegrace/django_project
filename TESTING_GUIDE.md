# Testing & Validation Guide

Comprehensive guide to test and validate the entire farm management system before deployment.

## 📋 Pre-Testing Checklist

Before running tests, ensure:

- [ ] Virtual environment activated
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] npm dependencies installed: `cd frontend && npm install`
- [ ] Database migrated: `python manage.py migrate`
- [ ] .env files configured correctly
- [ ] No port conflicts (8000, 3000)

## 🧪 Backend API Testing

### 1. Test API Without Authentication

Start Django server:
```bash
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application
```

Test unauthenticated access (should be rejected):
```bash
# Should return 403 Forbidden
curl http://localhost:8000/api/animals/

# Should return 403 Forbidden
curl http://localhost:8000/api/dashboard/summary/
```

### 2. Test Login Flow

```bash
# Login to get session cookie
curl -c cookies.txt -X POST http://localhost:8000/login/ \
  -d "username=admin&password=admin"

# Now test with session
curl -b cookies.txt http://localhost:8000/api/animals/
# Should return 200 OK
```

### 3. Test All Animal Endpoints

```bash
# Get all animals (paginated)
curl -b cookies.txt http://localhost:8000/api/animals/

# Create animal
curl -b cookies.txt -X POST http://localhost:8000/api/animals/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Chicken", "category": "chicken", "total_count": 100}'

# Get specific animal
curl -b cookies.txt http://localhost:8000/api/animals/1/

# Update animal
curl -b cookies.txt -X PUT http://localhost:8000/api/animals/1/ \
  -H "Content-Type: application/json" \
  -d '{"total_count": 150}'

# Delete animal
curl -b cookies.txt -X DELETE http://localhost:8000/api/animals/1/

# Get animals by category
curl -b cookies.txt http://localhost:8000/api/animals/by_category/?category=chicken

# Get animal statistics
curl -b cookies.txt http://localhost:8000/api/animals/1/statistics/
```

### 4. Test Dashboard Endpoints

```bash
# Get dashboard summary
curl -b cookies.txt http://localhost:8000/api/dashboard/summary/
# Response should include:
# - animals: count
# - today_eggs: quantity
# - feed_stock: status
# - mortality: count

# Get recent activity
curl -b cookies.txt http://localhost:8000/api/dashboard/recent_activity/
# Response should include activity logs
```

### 5. Test Egg Production Endpoints

```bash
# Get all egg productions
curl -b cookies.txt http://localhost:8000/api/egg-production/

# Get today's total
curl -b cookies.txt http://localhost:8000/api/egg-production/today_total/

# Get weekly summary
curl -b cookies.txt http://localhost:8000/api/egg-production/weekly_summary/

# Get by date range
curl -b cookies.txt "http://localhost:8000/api/egg-production/by_date_range/?start_date=2024-01-01&end_date=2024-12-31"

# Create egg production
curl -b cookies.txt -X POST http://localhost:8000/api/egg-production/ \
  -H "Content-Type: application/json" \
  -d '{"animal": 1, "quantity": 50, "date": "2024-05-05"}'
```

### 6. Test Feed Endpoints

```bash
# Get all feeds
curl -b cookies.txt http://localhost:8000/api/feeds/

# Get low stock feeds
curl -b cookies.txt http://localhost:8000/api/feeds/low_stock/

# Get stock summary
curl -b cookies.txt http://localhost:8000/api/feeds/stock_summary/
```

### 7. Test Notification Endpoints

```bash
# Get all notifications
curl -b cookies.txt http://localhost:8000/api/notifications/

# Get unread count
curl -b cookies.txt http://localhost:8000/api/notifications/unread_count/

# Mark notification as read
curl -b cookies.txt -X POST http://localhost:8000/api/notifications/1/mark_as_read/

# Mark all as read
curl -b cookies.txt -X POST http://localhost:8000/api/notifications/mark_all_as_read/
```

### 8. API Response Validation

Expected response format for animals:
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/animals/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Chicken 1",
      "category": "chicken",
      "category_display": "Chicken",
      "total_count": 100,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-05-05T15:30:00Z"
    }
  ]
}
```

## 🔌 WebSocket Testing

### 1. Test WebSocket Connection

Open browser console and run:

```javascript
// Connect to dashboard WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');

ws.onopen = () => {
  console.log('✓ WebSocket connected');
  
  // Request dashboard update
  ws.send(JSON.stringify({
    command: 'get_dashboard'
  }));
};

ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('✓ Received:', data);
};

ws.onerror = (e) => {
  console.error('✗ WebSocket error:', e);
};

ws.onclose = () => {
  console.log('✗ WebSocket disconnected');
};
```

### 2. Test WebSocket Events

```javascript
// Listen for various events
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Event type:', data.type);
  console.log('Event data:', data.data);
};

// Expected events:
// - dashboard_update
// - activity_created
// - egg_production_recorded
// - mortality_recorded
// - feed_alert
```

### 3. Test Notification WebSocket

```javascript
const wsNotif = new WebSocket('ws://localhost:8000/ws/notifications/');

wsNotif.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Notification received:', data);
};
```

### 4. Test WebSocket Reconnection

```javascript
// Manually close connection
ws.close();

// Should auto-reconnect within 5 attempts
// Watch console for reconnection logs
```

## 🎨 Frontend Testing

### 1. Start React Development Server

```bash
cd frontend
npm start
```

Access at `http://localhost:3000`

### 2. Test Page Loading

- [ ] Page loads without JavaScript errors
- [ ] No CORS errors in console
- [ ] Dashboard displays
- [ ] Header shows user info
- [ ] Sidebar navigation visible
- [ ] Footer visible

### 3. Test Dashboard Component

- [ ] Summary cards display (animals, eggs, feed, mortality)
- [ ] Real-time indicator shows "Live Updates" or "Offline"
- [ ] Alerts display with correct colors
- [ ] Activity list loads
- [ ] Refresh button works
- [ ] Data updates in real-time

### 4. Test Animals Component

- [ ] Animals list loads
- [ ] Search filters animals
- [ ] Category dropdown filters work
- [ ] Animals grouped by category
- [ ] Click "View Stats" shows animal statistics
- [ ] Pagination works (if many animals)
- [ ] Loading states display correctly

### 5. Test EggProduction Component

- [ ] Form displays all fields
- [ ] Can select animal from dropdown
- [ ] Can enter quantity
- [ ] Can select date
- [ ] Form submission works
- [ ] Success message displays
- [ ] Production history updates
- [ ] Weekly summary chart displays
- [ ] Polling updates every 5 seconds

### 6. Test Error Handling

- [ ] Disconnect network (F12 → Network → Offline)
- [ ] API calls fail gracefully
- [ ] Error messages display
- [ ] Components show fallback UI
- [ ] WebSocket shows "Offline"
- [ ] Reconnect works when network restored

### 7. Browser DevTools Checks

**Console**:
- [ ] No JavaScript errors
- [ ] No CORS warnings (in production)
- [ ] WebSocket messages logged (in development)

**Network**:
- [ ] API requests to `/api/` show 200 status
- [ ] WebSocket connection shows 101 status
- [ ] Response times reasonable (<500ms)
- [ ] No 401/403 errors
- [ ] Session cookies sent with requests

**Performance**:
- [ ] Page loads in <3 seconds
- [ ] Interactive in <5 seconds
- [ ] No memory leaks
- [ ] Bundle size reasonable

## 🔐 Security Testing

### 1. Authentication Testing

- [ ] Can't access `/api/` without login
- [ ] Session expires properly
- [ ] Logout clears session
- [ ] Can't modify others' data
- [ ] CSRF protection works

### 2. CORS Testing

- [ ] Requests from localhost:3000 work
- [ ] Requests from other origins blocked
- [ ] Credentials sent with requests
- [ ] Preflight requests successful

### 3. Input Validation

- [ ] Can't create animal with empty name
- [ ] Invalid quantities rejected
- [ ] Invalid dates handled
- [ ] XSS attempts sanitized
- [ ] SQL injection impossible (ORM)

### 4. Data Privacy

- [ ] Can't see other users' data
- [ ] Notifications user-specific
- [ ] Profile shows only own data
- [ ] No sensitive data in API responses

## 📊 Performance Testing

### 1. Load Testing

Using Apache Bench:
```bash
# Test API endpoint with 1000 requests
ab -n 1000 -c 10 http://localhost:8000/api/animals/

# Expected results:
# - Requests per second > 50
# - Average response time < 100ms
# - Failure rate 0%
```

### 2. WebSocket Load Testing

```javascript
// Open multiple WebSocket connections
const connections = [];
for (let i = 0; i < 10; i++) {
  const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');
  connections.push(ws);
}

// Monitor performance
console.log('Connections:', connections.filter(c => c.readyState === 1).length);
```

### 3. React Component Performance

Use React DevTools:
- [ ] Check render times
- [ ] Identify unnecessary re-renders
- [ ] Check hook dependencies
- [ ] Profile component hierarchy

### 4. Network Performance

- [ ] Bundle size < 500KB (compressed)
- [ ] CSS files < 100KB
- [ ] JavaScript files < 300KB
- [ ] Images optimized
- [ ] No duplicate requests

## ✅ Regression Testing

### 1. Original Django Features

Test that original Django templates still work:

- [ ] Django admin accessible
- [ ] Original login page works
- [ ] Original templates load
- [ ] Original views functional
- [ ] Database intact

### 2. Backward Compatibility

- [ ] Old URLs still work
- [ ] Old API endpoints functional
- [ ] Session authentication unchanged
- [ ] Database schema unchanged
- [ ] Migrations apply cleanly

## 📋 Test Report Template

Use this template to document test results:

```markdown
# Test Report - [Date]

## Environment
- Backend: Django 6.0.2 with Daphne
- Frontend: React 18.2.0
- Browser: [Browser/Version]
- OS: [OS/Version]

## API Testing
- [✓/✗] Animals endpoints
- [✓/✗] Egg production endpoints
- [✓/✗] Dashboard endpoints
- [✓/✗] Notification endpoints

## WebSocket Testing
- [✓/✗] Dashboard WebSocket
- [✓/✗] Notification WebSocket
- [✓/✗] Auto-reconnection
- [✓/✗] Event delivery

## Frontend Testing
- [✓/✗] Dashboard loads
- [✓/✗] Animals list works
- [✓/✗] Egg production form works
- [✓/✗] Real-time updates

## Security Testing
- [✓/✗] Authentication required
- [✓/✗] CORS configured
- [✓/✗] No XSS vulnerabilities
- [✓/✗] Data privacy maintained

## Performance
- Page load time: [ms]
- API response time: [ms]
- WebSocket latency: [ms]
- Bundle size: [KB]

## Issues Found
1. [Issue 1]
2. [Issue 2]

## Sign-off
- Date: [Date]
- Tester: [Name]
- Status: [PASS/FAIL]
```

## 🚀 Go-Live Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] No console errors
- [ ] Performance metrics acceptable
- [ ] Security review completed
- [ ] Backup created
- [ ] Database migrated to production
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team trained
- [ ] Rollback plan prepared

## 🆘 Troubleshooting Test Failures

### API Tests Fail

**Check**:
1. Django server running: `daphne -b 127.0.0.1 -p 8000 ...`
2. Migrations applied: `python manage.py migrate`
3. User logged in or session valid
4. Database connection working
5. API URLs correct in Django

### WebSocket Tests Fail

**Check**:
1. Daphne running (not Django dev server)
2. ASGI configured correctly
3. Channels installed: `pip install channels daphne`
4. Routing configured in farm/routing.py
5. WebSocket URL correct in browser

### Frontend Tests Fail

**Check**:
1. React server running: `npm start`
2. Dependencies installed: `npm install`
3. .env file configured correctly
4. API URL correct in .env
5. No CORS errors in console

### Performance Tests Fail

**Check**:
1. Server not under load from other processes
2. Network connection stable
3. Browser not running other intensive tasks
4. Cache cleared
5. DevTools not impacting performance

---

**Version**: 1.0.0
**Last Updated**: May 5, 2026
**Recommended**: Test before any production deployment
