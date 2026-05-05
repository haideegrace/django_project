# ✅ PRODUCTION DEPLOYMENT CHECKLIST

## Before Deploying

### Code Quality
- [ ] All tests pass: `python myproject/manage.py test`
- [ ] No hardcoded secrets in code
- [ ] DEBUG=False in production settings
- [ ] All print statements removed or converted to logging
- [ ] No TODO or FIXME comments that block deployment

### Backend Configuration
- [ ] `render.yaml` is updated and at project root
- [ ] `build.sh` is executable and contains frontend build steps
- [ ] `requirements.txt` includes all dependencies
- [ ] `settings.py` has SECURE_SSL_REDIRECT=True
- [ ] ALLOWED_HOSTS includes production domain
- [ ] CORS_ALLOWED_ORIGINS configured correctly
- [ ] DATABASE_URL environment variable configured
- [ ] WhiteNoise middleware enabled (for static files)

### Frontend Configuration  
- [ ] React build succeeds: `npm run build` in frontend/
- [ ] `.env.production` file exists
- [ ] REACT_APP_API_URL points to /api (relative path)
- [ ] WebSocket service handles production wss://
- [ ] All console errors fixed
- [ ] Responsive design tested on mobile
- [ ] No sensitive data in React code

### Database
- [ ] Migrations created for all models
- [ ] Run migrations locally: `python myproject/manage.py migrate`
- [ ] Admin user can be created
- [ ] Database backups configured (auto on Render)

### Git Repository
- [ ] All changes committed: `git status` shows clean
- [ ] Code pushed to GitHub: `git push`
- [ ] No merge conflicts
- [ ] Main/master branch is deployment branch

### Security
- [ ] SECRET_KEY is not in .env file (auto-generated)
- [ ] No credentials in code
- [ ] `.env` files in .gitignore
- [ ] HTTPS enforced
- [ ] HSTS enabled
- [ ] CSRF protection enabled

---

## Deployment Steps on Render

### Step 1: Connect Repository
```bash
# On your machine:
git push  # Push latest changes

# On Render website:
# 1. Go to https://render.com
# 2. Click "New +"
# 3. Select "Blueprint" 
# 4. Select your GitHub repository
# 5. Click "Create Blueprint"
```

### Step 2: Review Configuration
- Render will read `render.yaml`
- Services will be created: farm-inventory-api (Python web service)
- Database will be created: farm-inventory-db (PostgreSQL)
- Environment variables will be set automatically

### Step 3: Deploy
- Click "Deploy"
- Wait for build to complete (5-10 minutes)
- Monitor logs in Render dashboard

### Step 4: Post-Deployment
```bash
# Verify deployment
# 1. Check logs: should see "Build completed successfully!"
# 2. Access app: https://farm-inventory-api.onrender.com
# 3. Create admin user in Render shell:
#    python myproject/manage.py createsuperuser
# 4. Access admin: https://farm-inventory-api.onrender.com/admin/
```

---

## After Deployment

### Verification
- [ ] Frontend loads at https://farm-inventory-api.onrender.com
- [ ] API responds at https://farm-inventory-api.onrender.com/api/
- [ ] Admin panel accessible at https://farm-inventory-api.onrender.com/admin/
- [ ] WebSocket connects for real-time updates
- [ ] Forms submit successfully
- [ ] Data persists after page refresh
- [ ] No CORS errors in browser console
- [ ] HTTPS certificate is valid (green lock)

### Monitoring
- [ ] Check Render dashboard daily for errors
- [ ] Monitor CPU/Memory usage
- [ ] Check app logs for exceptions
- [ ] Test critical user flows regularly

### Updates
- [ ] Make code changes locally
- [ ] Commit and push to GitHub
- [ ] Render automatically redeploys within 2 minutes
- [ ] Verify new version deployed successfully

---

## Troubleshooting

### Build Fails
1. Check render logs for error message
2. Ensure build.sh exists and is not empty
3. Verify requirements.txt has all dependencies
4. Check that frontend/package.json is valid JSON

### App Won't Start  
1. Check DATABASE_URL environment variable
2. Verify Python version compatibility
3. Look for PermissionError or ImportError in logs
4. Ensure migrations ran successfully

### Static Files Missing
1. Check if build.sh runs collectstatic
2. Verify WhiteNoise middleware in settings
3. Clear browser cache
4. Rebuild deployment

### WebSocket Not Working
1. Verify production uses wss:// not ws://
2. Check CORS settings
3. Verify Django Channels is configured
4. Check Render logs for connection errors

### Database Connection Issues
1. Wait 2-3 minutes after deploy (DB initializing)
2. Check DATABASE_URL in Render environment
3. Verify migrations ran in logs
4. Check PostgreSQL free tier limits (100MB)

---

## Performance Optimization

### For Free Tier Deployment
- App may sleep after 15 minutes of inactivity (auto-wakes)
- Use Render cron jobs for scheduled tasks
- Monitor database size (100MB limit)
- Consider upgrading if growth exceeds limits

### Recommended Upgrades (Optional)
- Standard tier: $7/month (no sleep, better performance)
- Pro tier: $27/month (priority support, auto-scaling)
- Database: $15/month (unlimited storage)

---

## Long-Term Maintenance

- [ ] Daily: Check app is responding
- [ ] Weekly: Review error logs
- [ ] Monthly: Check database usage
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Annually: Review scaling needs

---

## Support Resources

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com/
- React Docs: https://react.dev/
- Troubleshooting: Check render logs first

---

**STATUS**: Ready to deploy! 🚀

**Next Step**: Push to GitHub and create Render Blueprint
