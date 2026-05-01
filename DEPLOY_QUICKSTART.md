# SignBridge Production Deployment - Quick Start Guide

**Status**: ✅ All code is ready for production deployment
**Date**: April 26, 2026
**Repository**: https://github.com/aadvikon/signbridge

---

## Overview

SignBridge is now ready to deploy to production. This guide provides the fastest path from development to production.

### Current Setup
- ✅ Backend: FastAPI with JWT auth, video processing, 3D avatar support
- ✅ Frontend: React + Vite with real-time 3D avatar animation
- ✅ Database: Supabase (configured, not initialized)
- ✅ Storage: Cloudflare R2 (configured)
- ✅ Payments: Stripe (configured)
- ✅ Environment variables: Properly configured for production
- ✅ API Calls: Using environment variables (no hardcoded localhost)

---

## 🚀 Deployment in 5 Minutes

### Step 1: Deploy Backend to Railway (3 minutes)

1. Go to https://railway.app and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select **aadvikon/signbridge** repository
4. Configure:
   - **Root Directory**: `backend/`
   - **Environment**: `production`
5. Add environment variables from [`.env.production.example`](.env.production.example):
   ```
   API_HOST=0.0.0.0
   API_PORT=8000
   API_RELOAD=False
   ENVIRONMENT=production
   # ... (add all other vars from .env.production.example)
   ```
6. Click Deploy
7. ⏳ Wait 2-5 minutes for deployment
8. 📝 Copy the public URL (e.g., `https://signbridge-prod-abc123.railway.app`)

**Verify**: Visit `https://your-railway-url/docs` and see Swagger API docs

### Step 2: Deploy Frontend to Vercel (2 minutes)

1. Go to https://vercel.com and sign up with GitHub
2. Click "Add New" → "Project"
3. Select **aadvikon/signbridge** repository
4. Configure:
   - **Root Directory**: `frontend/`
   - **Framework**: Vite
   - **Build Command**: `npm run build`
5. Add Environment Variables:
   ```
   VITE_API_URL=https://your-railway-backend-url
   ```
   (Replace with actual Railway URL from Step 1)
6. Click Deploy
7. ⏳ Wait 1-2 minutes for deployment
8. 📝 Copy the public URL (e.g., `https://signbridge.vercel.app`)

**Verify**: Visit `https://your-vercel-url` and see the dashboard

### Step 3: Update Backend CORS (1 minute)

1. Return to Railway dashboard
2. Select your backend service
3. Go to Settings → Environment Variables
4. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-vercel-frontend-url.vercel.app
   ```
5. Deploy/Restart the service

**Done!** Your production environment is now deployed and connected.

---

## ✅ Quick Testing

### Test 1: API Health Check
```bash
curl https://your-railway-url/health
# Should return: {"status": "healthy", "service": "SignBridge API", "version": "0.1.0"}
```

### Test 2: Frontend Loads
- Visit `https://your-vercel-url`
- Should see the SignBridge dashboard with upload area and 3D avatar

### Test 3: Full Flow Test
1. Visit production frontend URL
2. Upload a test video (drag & drop)
3. Check browser Network tab - requests should go to Railway URL (not localhost)
4. Watch processing status
5. Verify avatar displays and animates

---

## 📋 Files Changed for Production

The following files were updated to support production deployment:

- **`frontend/src/components/VideoUpload.jsx`** - Now uses `VITE_API_URL` environment variable
- **`backend/main.py`** - Updated trusted host middleware for production
- **`.env.example`** - Added production configuration notes
- **`.env.production.example`** - New production environment template
- **`frontend/.env.example`** - New frontend environment template
- **`DEPLOYMENT.md`** - Comprehensive deployment guide (30+ pages)
- **`deploy.sh`** - Pre-deployment validation script

No breaking changes to existing code - all updates are backward compatible with local development.

---

## 🔧 Environment Variables Summary

### Backend (Railway)
```
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False
CORS_ORIGINS=https://your-vercel-url.vercel.app
ALLOWED_HOSTS=your-railway-backend-url.railway.app
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
# ... (add all from .env.production.example)
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-railway-backend-url
```

---

## 🆘 Troubleshooting

### API calls fail with CORS error
- ✓ Check CORS_ORIGINS in Railway environment variables
- ✓ Verify it matches your Vercel URL exactly (with https://)
- ✓ Restart the Railway service after updating

### Frontend shows "localhost:8000" errors
- ✓ Check VITE_API_URL is set correctly in Vercel
- ✓ Clear browser cache (Ctrl+Shift+Delete)
- ✓ Check browser console for error messages

### Video upload doesn't work
- ✓ Verify both services are deployed
- ✓ Check browser Network tab for actual error
- ✓ Review Railway logs for backend errors
- ✓ Verify file size is under 100MB

---

## 📚 For More Details

See the comprehensive deployment guide: [`DEPLOYMENT.md`](DEPLOYMENT.md)

Topics covered:
- Step-by-step deployment instructions (Railway + Vercel)
- Complete environment variables configuration
- Production testing procedures
- Debugging common issues
- Monitoring and maintenance
- Rollback instructions

---

## 🎯 Next Steps After Deployment

1. **Set up monitoring**
   - Railway: Dashboard → Analytics
   - Vercel: Project → Analytics

2. **Configure backups** (Supabase settings)

3. **Set up CI/CD** (optional - already auto-deploying on GitHub push)

4. **Monitor logs** regularly for errors

5. **Test regularly** - upload videos to ensure everything works

---

## 🔐 Security Notes

- Never commit `.env` files with real secrets
- Rotate JWT_SECRET regularly
- Use HTTPS everywhere (both platforms provide this)
- Keep dependencies updated
- Monitor logs for unauthorized access attempts
- Use Stripe live keys (not test keys) in production

---

**Questions?** Check [`DEPLOYMENT.md`](DEPLOYMENT.md) for comprehensive documentation.

**Ready to launch?** 🚀
