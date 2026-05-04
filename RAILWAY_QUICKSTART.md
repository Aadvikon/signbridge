# 🚀 RAILWAY DEPLOYMENT - QUICK START

## Your SignBridge Backend is Ready to Deploy!

### What's Done ✅
- AWS Bedrock credentials configured
- Backend code with Claude integration ready
- All dependencies in requirements.txt
- Deployment verification passed

### What You Need (Before Starting)
1. GitHub account (you have this)
2. Railway account → Sign up at https://railway.app (5 mins)
3. Your AWS credentials from `.env` file (you have these)

---

## DEPLOYMENT IN 5 MINUTES

### Phase 1: Railway Setup (1 min)

1. Go to **https://railway.app**
2. Click **"Start New Project"** (top right)
3. Select **"Deploy from GitHub repo"**
4. Sign in with GitHub when prompted
5. When asked for permissions, click **"Authorize"**

### Phase 2: Connect SignBridge Repo (2 mins)

1. Search for **"signbridge"** repository
2. Click **"Install & Authorize"** to connect Railway
3. Select repository **"aadvikon/signbridge"** (or your fork)
4. Click **"Create"** or **"Deploy"**

### Phase 3: Configure Backend (1 min)

Railway creates a service. Now configure it:

1. Look for your service in the Railway dashboard
2. Click **⚙️ Settings** (gear icon)
3. Find **"Root Directory"** field
4. Enter: `backend/`
5. Click **Save**

### Phase 4: Add Environment Variables (2 mins)

1. In your service, go to **Variables** tab
2. Click **"Add Variable"** for each:

```
AWS_BEARER_TOKEN_BEDROCK
→ Paste your AWS Access Key ID from .env

AWS_SECRET_ACCESS_KEY
→ Paste your AWS Secret Key from .env

AWS_REGION
→ us-east-1

JWT_SECRET
→ Generate random: python -c "import secrets; print(secrets.token_urlsafe(32))"

CORS_ORIGINS
→ *

ENVIRONMENT
→ production

DEBUG
→ False

LOG_LEVEL
→ INFO

API_HOST
→ 0.0.0.0

API_PORT
→ 8000
```

### Phase 5: Deploy! (1 min)

1. Click **"Trigger Deploy"** button
2. Watch the build logs
3. You'll see:
   - Installing dependencies
   - Building the application
   - Starting service

4. Wait for ✅ **"Deployment Successful"**

### Phase 6: Get Your URL (30 seconds)

1. Go to **Settings** tab
2. Look for **Domains** section
3. You'll see: `https://signbridge-backend-xxxx.railway.app`
4. **Copy this URL** - you'll need it for frontend!

---

## TEST YOUR DEPLOYMENT

Once deployed, test it immediately:

### Test 1: API Documentation
```
https://your-railway-url/docs
```
You should see FastAPI Swagger UI

### Test 2: Claude Endpoint
```bash
curl -X POST https://your-railway-url/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, is Claude working?"}'
```

Expected response: Claude's answer

### Test 3: Check Logs
In Railway dashboard → **View Logs** to see:
- Build output
- Application startup
- Any errors

---

## TROUBLESHOOTING QUICK FIXES

### Build Failed?
- Check logs for error messages
- Ensure `backend/` root directory is set correctly
- Verify all environment variables are filled

### Claude Error: "Model Access Denied"?
1. Go to https://console.aws.amazon.com/bedrock
2. Click **Model Access**
3. Enable Claude 3.5 Sonnet or Claude 3 Haiku
4. Wait 5 minutes, then redeploy

### CORS Errors?
- Set `CORS_ORIGINS=*` for testing
- Later update to your frontend URL

### Still Broken?
Check Railway logs:
1. Click service → **View Logs**
2. Look for error messages
3. Common issues:
   - Wrong AWS credentials
   - Missing environment variables
   - Port already in use

---

## NEXT STEPS AFTER BACKEND DEPLOYS

### Step 1: Update Frontend (When Ready)
Copy your Railway URL and update frontend environment:
```
VITE_API_URL=https://your-railway-backend-url
```

### Step 2: Deploy Frontend to Vercel
1. Go to https://vercel.com
2. Import `frontend/` directory from GitHub
3. Set `VITE_API_URL` environment variable
4. Deploy

### Step 3: Test End-to-End
1. Open your frontend
2. Test Claude chat feature
3. Verify all API calls work

---

## IMPORTANT REMINDERS ⚠️

✅ **DO:**
- Save your Railway URL after deployment
- Test endpoints immediately after deploy
- Monitor Railway logs for errors
- Enable Claude model in AWS Bedrock first

❌ **DON'T:**
- Share your AWS credentials
- Commit `.env` file to GitHub (already in .gitignore)
- Leave DEBUG=True in production
- Forget to set JWT_SECRET

---

## YOUR CREDENTIALS (FROM .ENV)

Copy these values from your `.env` file (NOT shown here for security):
- AWS_BEARER_TOKEN_BEDROCK: <your-access-key-id>
- AWS_SECRET_ACCESS_KEY: <your-secret-access-key>
- AWS_REGION: us-east-1

⚠️ NEVER commit or share these credentials publicly!

---

## HELPFUL LINKS

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- AWS Bedrock: https://console.aws.amazon.com/bedrock
- SignBridge GitHub: https://github.com/aadvikon/signbridge

---

## READY? 

**Go to https://railway.app and start deploying! 🎉**

Time estimate: **10-15 minutes total**

Questions? Check:
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Full detailed guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Complete checklist
- [AWS_BEDROCK_SETUP.md](AWS_BEDROCK_SETUP.md) - AWS details