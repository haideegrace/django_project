# 🚀 Deployment Guide - Farm Inventory System

Your app is configured to deploy on **Render.com** and will be accessible from anywhere on any device!

---

## 📋 Pre-Deployment Checklist

### 1. **Commit All Changes**
```bash
git add .
git commit -m "Prepare for production deployment"
git push
```

### 2. **Verify Requirements**
```bash
# All Python dependencies are in requirements.txt
# Frontend dependencies will be installed during build
```

### 3. **Environment Variables Setup**
No action needed - Render.yaml handles most variables automatically.

---

## 🌐 Deploy to Render

### Step 1: Connect GitHub to Render
1. Go to [https://render.com](https://render.com)
2. Sign up or log in with GitHub
3. Create new "Blueprint" from your GitHub repo
4. Select the branch (usually `main`)
5. Click "Create Blueprint"

### Step 2: Configure Services
Render will automatically read `render.yaml` and configure:
- **Backend API**: Python/Django with PostgreSQL
- **Frontend**: Built from React and served statically
- **Database**: PostgreSQL (free tier)

### Step 3: Deploy
1. Click "Deploy"
2. Wait for build to complete (~5-10 minutes)
3. Your app will be available at: `https://farm-inventory-api.onrender.com`

---

## 🔗 Access Your App

### After Deployment:
- **Full App**: `https://farm-inventory-api.onrender.com`
- **API Endpoint**: `https://farm-inventory-api.onrender.com/api/`
- **Admin Panel**: `https://farm-inventory-api.onrender.com/admin/`
- **WebSocket**: `wss://farm-inventory-api.onrender.com/ws/` (for real-time updates)

---

## 📱 Share With Others

Your deployed app can be accessed from:
- ✅ Any browser (desktop, mobile, tablet)
- ✅ Any WiFi network
- ✅ Any device worldwide
- ✅ Mobile hotspot / 4G / 5G

**Share the URL**: Simply give others the link: `https://farm-inventory-api.onrender.com`

---

## 🔧 Build Process

The `build.sh` script automatically:
1. Installs Python dependencies
2. Installs Node.js dependencies for React
3. Builds the React app (production optimized)
4. Copies built files to Django static folder
5. Collects Django static files
6. Runs database migrations

---

## 🛡️ Security Features Enabled

✅ **SSL/TLS**: HTTPS enabled automatically  
✅ **HSTS**: HTTP Strict Transport Security (1 year)  
✅ **CSRF Protection**: Enabled for form submissions  
✅ **CORS**: Configured for your domain  
✅ **Debug Mode**: Disabled in production  
✅ **Secret Key**: Auto-generated on Render  

---

## 📊 Database

- **Type**: PostgreSQL (free tier)
- **Auto-backups**: Enabled
- **Connection**: Managed by Render
- **Migrations**: Run automatically during build

### First-Time Setup:
Admin account setup instructions will be in Render logs:
```
Check Render deploy logs for admin credentials
Or run: python manage.py createsuperuser
```

---

## 🔄 Updating Your App

To update after changes:

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push  # Pushes to GitHub

# Render automatically redeploys!
# Check your deployment in Render dashboard
```

---

## 🐛 Troubleshooting

### App Won't Deploy?
- Check Render deploy logs for errors
- Ensure `render.yaml` is at project root
- Verify `build.sh` exists and is executable

### Database Connection Issues?
- Render automatically configures DATABASE_URL
- Migrations run during build
- Check Render logs for connection errors

### Static Files Not Loading?
- Clear browser cache (Ctrl+Shift+Del or Cmd+Shift+Del)
- Rebuild: Delete old deploy in Render and redeploy

### WebSocket Errors?
- Ensure production URL uses `wss://` not `ws://`
- Check CORS and CSRF settings in logs

---

## 📞 Local Development Still Works

Nothing changes locally - continue using:
```bash
# Terminal 1: Backend
cd "c:\Users\Haids\OneDrive\farm inventories"
.venv\Scripts\activate
daphne -b 127.0.0.1 -p 8000 myproject.asgi:application

# Terminal 2: Frontend
cd frontend
npm start
# Opens at http://localhost:3000
```

---

## 📈 Monitoring

After deployment, monitor from Render dashboard:
- Logs (real-time activity)
- Metrics (CPU, memory)
- Events (deployments, errors)
- Health checks

---

## 💡 Pro Tips

1. **Custom Domain**: Add your own domain in Render settings
2. **Email Notifications**: Enable to get alerts on deployment
3. **Automatic Redeploy**: Enable to rebuild when you push to GitHub
4. **Keep-Alive**: Free tier apps sleep after 15 min inactivity (auto-wake on request)

---

## 🎯 Next Steps

1. ✅ Push code to GitHub: `git push`
2. ✅ Go to render.com and connect repository
3. ✅ Select "Blueprint" and deploy
4. ✅ Wait for completion
5. ✅ Share your URL with team members!

---

## 📚 Helpful Links

- [Render Documentation](https://render.com/docs)
- [Django Deployment Guide](https://docs.djangoproject.com/en/6.0/howto/deployment/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)

---

**Your farm inventory system is now ready for the world! 🌍🚀**
