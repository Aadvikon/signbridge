# Railway Deployment Guide for SignBridge Backend

## Overview
This guide walks you through deploying the SignBridge FastAPI backend with AWS Bedrock integration to Railway.

## Prerequisites ✅
- ✅ GitHub account connected to SignBridge repo
- ✅ AWS Bedrock credentials configured (in `.env`)
- ✅ Code pushed to GitHub (master branch)
- Railway account: https://railway.app

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start New Project" 
3. Sign up with GitHub (recommended) or email
4. Authorize Railway to access your GitHub repositories

## Step 2: Create New Railway Project

1. After login, click **"Create New Project"**
2. Select **"Deploy from GitHub repo"**
3. Click **"Configure GitHub App"** (if not already done)
4. Search for **"signbridge"** repository
5. Click **"Install & Authorize"** to connect Railway to your repo

## Step 3: Configure Backend Service

### 3.1 Add Service from GitHub

1. In Railway dashboard, click **"New Project"**
2. Select your **signbridge** repository
3. Railway will auto-detect the structure

### 3.2 Set Root Directory

1. Go to **Settings** (gear icon) → **Service Settings**
2. Under **"Root Directory"**, set to: `backend/`
3. Click **Save**

### 3.3 Configure Build & Deploy

1. Go to **Build** section
2. Verify settings:
   - **Build Command**: (leave empty - uses requirements.txt)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Step 4: Add Environment Variables

### 4.1 Add Variables to Railway

**⚠️ IMPORTANT:** Get these values from your `.env` file (created by setup_bedrock.py)

1. Go to **Variables** section in your service
2. Click **"Add Variable"** and add each of these:

```
# AWS Bedrock (copy from your .env file)
AWS_BEARER_TOKEN_BEDROCK=<paste-your-access-key-id>
AWS_SECRET_ACCESS_KEY=<paste-your-secret-access-key>
AWS_REGION=us-east-1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*

# JWT (generate new secret - use random string)
JWT_SECRET=your-super-secret-jwt-key-change-this-to-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

### Optional: Database & Storage Variables

If you're using Supabase or Cloudflare R2:

```
# Supabase (if used)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Cloudflare R2 (if used)
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=signbridge-videos

# Stripe (if used)
STRIPE_SECRET_KEY=sk_test_your_key
```

### Important: Generate JWT Secret

Replace `JWT_SECRET` with a secure random string. Generate one:

**Option A - Using Python:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option B - Using Online Generator:**
- https://randomkeygen.com/ (CodeIgniter Encryption Keys)

## Step 5: Deploy

### 5.1 Trigger Deployment

1. Railway automatically deploys when you push to GitHub
2. Or manually trigger:
   - Click **"Trigger Deploy"** button in Railway dashboard
   - Select **"Deploy"**

### 5.2 Monitor Deployment

1. Go to **Deployments** tab
2. Watch the build logs:
   - Installing dependencies (slow first time)
   - Building application
   - Starting service

3. When complete, look for **"Deployment Successful"** message

### 5.3 Get Your Backend URL

1. Go to **Settings** tab
2. Find **"Domains"** section
3. Your URL will be: `https://signbridge-backend-xxx.railway.app`
4. Copy this URL for frontend configuration

## Step 6: Test Your Deployment

### 6.1 Test Health Check

```bash
curl https://your-railway-backend-url/docs
```

You should see the FastAPI Swagger documentation.

### 6.2 Test Claude Endpoint

```bash
curl -X POST https://your-railway-backend-url/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, test this Claude integration"}'
```

Expected response:
```json
{
  "response": "Claude response here..."
}
```

### 6.3 Test Other Endpoints

```bash
# Check auth status
curl https://your-railway-backend-url/auth/status

# Check health
curl https://your-railway-backend-url/health
```

## Step 7: Configure Frontend

Once backend is deployed, update frontend to use Railway URL:

1. Go to [Vercel](https://vercel.com) (or your frontend host)
2. Set environment variable:
   ```
   VITE_API_URL=https://your-railway-backend-url
   ```
3. Redeploy frontend

## Troubleshooting

### Build Fails: Missing Dependencies

**Issue:** `ModuleNotFoundError: No module named 'boto3'`

**Fix:**
```bash
git add requirements.txt
git commit -m "Update requirements"
git push origin master
```

Then trigger new Railway deployment.

### Deployment Stuck

1. Check Railway logs: Click **"View Logs"** button
2. Look for error messages
3. Common issues:
   - Wrong Python version (use 3.11+)
   - Missing environment variables
   - Port conflicts

### Claude Model Access Denied

**Error:** `This Model is marked by provider as Legacy`

**Fix:**
1. Go to AWS Bedrock Console
2. Enable Claude model in **Model Access**
3. Restart Railway deployment

### CORS Errors

If frontend can't connect to backend:

1. Update `CORS_ORIGINS` in Railway Variables:
   ```
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```
2. Redeploy

## Monitoring & Logs

### View Logs

1. In Railway dashboard, click **"View Logs"**
2. Filter by:
   - **Build logs** (deployment process)
   - **Runtime logs** (application running)
   - **Error logs** (exceptions)

### Monitor Performance

1. Go to **Metrics** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Error rate

## Cost Optimization

- Railway free tier: $5/month credit
- Current setup uses minimal resources
- Monitor usage in Railway dashboard

## Next Steps

1. ✅ Deploy Backend to Railway
2. 📋 Deploy Frontend to Vercel (see `DEPLOYMENT.md`)
3. 🔗 Configure API URL in frontend
4. 🧪 Run end-to-end tests
5. 📊 Monitor production logs

## Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- SignBridge GitHub: https://github.com/Aadvikon/signbridge
- Backend Health: `https://your-url/docs`

## Support

For issues, check:
1. Railway deployment logs
2. AWS Bedrock console for model access
3. GitHub Actions for build failures
4. Backend logs in Railway dashboard