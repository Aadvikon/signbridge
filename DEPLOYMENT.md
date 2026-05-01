# SignBridge Production Deployment Guide

This guide walks through deploying SignBridge to production using Railway (backend) and Vercel (frontend).

## Prerequisites
- GitHub account with access to https://github.com/aadvikon/signbridge
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- Production environment variables prepared

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Account & Project

1. Go to [railway.app](https://railway.app)
2. Sign up or log in with GitHub
3. Click "Start a New Project"
4. Select "Deploy from GitHub repo"
5. Connect your GitHub account if not already connected

### 1.2 Configure Repository

1. Select **aadvikon/signbridge** repository
2. Select **Only select repositories** option
3. Click "Install & Authorize"

### 1.3 Create Railway Service

1. In the Railway dashboard, click "New Project"
2. Select "GitHub repo" deployment
3. Choose **aadvikon/signbridge**
4. Configure:
   - **Root Directory**: `backend/`
   - **Python Version**: Leave default (3.11+)
   - **Environment**: Production

### 1.4 Add Environment Variables

Navigate to the service settings and add the following environment variables:

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False

# CORS Configuration  
CORS_ORIGINS=https://your-vercel-frontend-url.vercel.app

# Database - Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Auth
JWT_SECRET=your-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage - Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=signbridge-videos

# Payments - Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# AI/ML Configuration
MODEL_PATH=models/trained/sign_language_model.h5
WLASL_DATASET_PATH=data/raw/wlasl_videos
MEDIAPIPE_CONFIDENCE_THRESHOLD=0.5

# OpenAI Whisper
WHISPER_MODEL=base
WHISPER_DEVICE=cpu

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

**Important Security Notes:**
- Never commit production secrets to GitHub
- Use Railway's environment variable management
- Rotate JWT_SECRET and other secrets regularly
- Update CORS_ORIGINS with your Vercel frontend URL after deployment

### 1.5 Deploy Backend

1. Railway automatically detects changes to `backend/` directory
2. Monitor the deployment in Railway dashboard
3. Wait for deployment to complete
4. Copy the public URL (e.g., `https://signbridge-backend-prod.railway.app`)
5. Note this URL for the frontend deployment

### 1.6 Verify Backend Deployment

```bash
# Test the API is running
curl https://your-railway-backend-url/docs

# Should return Swagger API documentation
```

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account & Project

1. Go to [vercel.com](https://vercel.com)
2. Sign up or log in with GitHub
3. Click "Add New..." → "Project"
4. Select "GitHub" as source

### 2.2 Configure Repository

1. Search for and select **aadvikon/signbridge**
2. Click "Import"

### 2.3 Configure Build Settings

1. **Project Settings**:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

2. **Root Directory**: `frontend/`

### 2.4 Add Environment Variables

1. Go to Settings → Environment Variables
2. Add the following:

```
VITE_API_URL=https://your-railway-backend-url
```

**Example:**
```
VITE_API_URL=https://signbridge-backend-prod.railway.app
```

### 2.5 Deploy Frontend

1. Click "Deploy"
2. Vercel will automatically build and deploy
3. Wait for deployment to complete
4. Copy the public URL (e.g., `https://signbridge-frontend.vercel.app`)

### 2.6 Update Backend CORS

After frontend deployment:

1. Return to Railway dashboard
2. Go to your backend service settings
3. Update the `CORS_ORIGINS` environment variable:

```
CORS_ORIGINS=https://your-vercel-frontend-url.vercel.app
```

4. Redeploy the backend (Railway will auto-redeploy on env var change)

---

## Step 3: Verify Code Changes

The frontend has been updated to use the `VITE_API_URL` environment variable:

**File**: [frontend/src/components/VideoUpload.jsx](frontend/src/components/VideoUpload.jsx)

- Changed from hardcoded `http://localhost:8000` 
- Now uses `import.meta.env.VITE_API_URL` with fallback to localhost
- Environment variable is set during build on Vercel

---

## Step 4: Testing Production Deployment

### 4.1 Basic Health Checks

1. **Backend API**:
   ```bash
   curl https://your-railway-backend-url/docs
   # Should show Swagger UI
   ```

2. **Frontend**:
   - Visit `https://your-vercel-frontend-url`
   - Should load without errors in browser console
   - Check Network tab: API calls should go to Railway URL (not localhost)

### 4.2 Full Flow Test

1. **Navigate to production frontend URL**
2. **Upload a test video**:
   - Drag & drop a video or click upload
   - Monitor browser Network tab
   - Upload should POST to Railway backend
   - Confirm upload completes

3. **Verify Processing**:
   - Backend should process video
   - Signs should be detected
   - Results should display on frontend
   - Check backend logs in Railway dashboard

4. **Test Avatar Display**:
   - Verify 3D avatar renders correctly
   - Check avatar animation with detected signs
   - Confirm no WebGL errors in browser console

### 4.3 Debugging Production Issues

**If API calls fail:**
1. Check browser Console tab for error messages
2. Check Network tab to verify request URLs
3. In Railway dashboard, check backend service logs
4. Verify CORS_ORIGINS includes your Vercel URL
5. Check that VITE_API_URL env var is set correctly on Vercel

**If frontend doesn't build:**
1. Check Vercel build logs
2. Verify root directory is set to `frontend/`
3. Confirm all dependencies are in `package.json`

**If backend crashes:**
1. Check Railway service logs for errors
2. Verify all required environment variables are set
3. Check that models are accessible

---

## Step 5: Enable Auto-Deployments

### 5.1 Railway Auto-Deploy
- Already configured: Railway deploys on GitHub push to main branch
- Disable via Repository Settings if needed

### 5.2 Vercel Auto-Deploy  
- Already configured: Vercel deploys on GitHub push to main branch
- Disable via Project Settings → Git if needed

---

## Production Checklist

- [ ] Backend deployed to Railway with all env vars
- [ ] Frontend deployed to Vercel with VITE_API_URL set
- [ ] Backend CORS_ORIGINS updated to include Vercel URL
- [ ] Video upload tested on production
- [ ] Video processing tested on production
- [ ] Avatar rendering tested on production
- [ ] All API calls use production URLs (not localhost)
- [ ] Error logging configured
- [ ] Security headers configured
- [ ] Backups configured (Database & Storage)

---

## Monitoring & Maintenance

### Railway Monitoring
- View logs: Dashboard → Service → Logs
- Monitor resources: Dashboard → Analytics
- View errors: Dashboard → Service → Error tracking

### Vercel Monitoring
- View logs: Project → Analytics → Real User Monitoring
- Monitor performance: Project → Analytics → Performance
- Check deployment status: Project → Deployments

---

## Rollback Instructions

If issues occur after deployment:

**Backend Rollback (Railway)**:
1. Go to Railway dashboard
2. Select your service
3. Click "Deployments"
4. Select previous working deployment
5. Click "Rollback"

**Frontend Rollback (Vercel)**:
1. Go to Vercel dashboard
2. Select your project
3. Click "Deployments"
4. Select previous working deployment
5. Click "..." → "Promote to Production"

---

## Common Issues & Solutions

### Issue: CORS errors when calling API
**Solution**: Verify CORS_ORIGINS in backend environment variables matches Vercel frontend URL

### Issue: 404 on /api/* endpoints
**Solution**: Check that API routes are properly exported and Railway deployment includes backend directory

### Issue: Environment variables not loaded
**Solution**: Restart deployment on Vercel/Railway after adding environment variables

### Issue: Avatar not rendering
**Solution**: Check WebGL support in browser, verify Three.js dependencies are installed

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI CORS Guide](https://fastapi.tiangolo.com/tutorial/cors/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-modes.html)

---

**Deployment Date**: April 26, 2026  
**Repository**: https://github.com/aadvikon/signbridge
