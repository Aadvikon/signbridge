# SignBridge AWS Bedrock Deployment Guide

## Status ✅
AWS Bedrock credentials are successfully configured and connected to your AWS account.

## Next Steps

### 1. Enable Claude Model in AWS Bedrock

Your credentials work, but you need to enable Claude model access in Bedrock:

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Model Access** (left sidebar)
3. Click **Manage Model Access**
4. Find **Claude 3.5 Sonnet** or **Claude 3 Haiku**
5. Click the checkbox and submit

### 2. Update Backend Environment Variables

Your `.env` file has been created with:
- `AWS_BEARER_TOKEN_BEDROCK` (Access Key ID)
- `AWS_SECRET_ACCESS_KEY` (Secret Access Key)
- `AWS_REGION` (AWS Region)

### 3. Deploy to Railway

#### 3a. Connect Railway to GitHub

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "GitHub Repo"
3. Select your SignBridge repository
4. Configure Root Directory: `backend/`

#### 3b. Add Environment Variables to Railway

In Railway dashboard, go to **Variables** and add:

```
# AWS Bedrock
AWS_BEARER_TOKEN_BEDROCK=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-vercel-frontend.vercel.app

# JWT (generate a new secret)
JWT_SECRET=<generate-a-new-random-secret>
JWT_ALGORITHM=HS256

# Database (if using Supabase)
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

# Optional: Storage (Cloudflare R2)
R2_ACCOUNT_ID=<optional>
R2_ACCESS_KEY_ID=<optional>
R2_SECRET_ACCESS_KEY=<optional>
R2_BUCKET_NAME=<optional>

# Optional: Payments (Stripe)
STRIPE_SECRET_KEY=<optional>

# AI/ML
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

#### 3c. Deploy

1. Railway will automatically detect changes to the `backend/` directory
2. Wait for deployment to complete
3. Copy the Railway URL (e.g., `https://signbridge-backend.railway.app`)

### 4. Test the Deployment

Once deployed to Railway, test the Claude endpoint:

```bash
curl -X POST https://your-railway-backend.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, test this!"}'
```

### 5. Current Claude Model Recommendations

**For Production:**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Most capable, recommended)
- `anthropic.claude-3-haiku-20240307-v1:0` (Fast and cost-effective)

**Note:** Update the `MODEL_ID` in `backend/claude_service.py` based on what's enabled in your Bedrock account.

## File Locations

- Backend code: `backend/`
- Claude service: `backend/claude_service.py`
- Claude routes: `backend/routes/claude_routes.py`
- Environment config: `.env` (in root directory)

## Troubleshooting

If you encounter model access errors:

1. **Check Model Enable Status**: Verify the model is enabled in Bedrock console
2. **Check IAM Permissions**: Ensure your IAM user has `bedrock:InvokeModel` permission
3. **Try Another Model**: Test with a different Claude model version
4. **Check Region**: Ensure you're using a region where Claude is available (us-east-1, us-west-2, eu-west-1, etc.)

## Security Best Practices

⚠️ **IMPORTANT FOR PRODUCTION:**

1. **Never commit `.env` to GitHub** - Already in `.gitignore`
2. **Use Railway's Secrets** - Don't commit sensitive values
3. **Rotate credentials regularly** - Create new AWS access keys periodically
4. **Use IAM roles** - Prefer IAM roles over access keys when possible
5. **Enable Bedrock logging** - Monitor API usage in CloudWatch

## Cost Optimization

- **Claude 3.5 Haiku**: Fastest + cheapest for basic tasks
- **Claude 3.5 Sonnet**: Better quality, recommended for complex tasks
- Monitor usage in AWS Bedrock console to track costs

## Next: Deploy Frontend to Vercel

Once backend is deployed, deploy frontend:
1. Go to [Vercel](https://vercel.com)
2. Import `frontend/` directory
3. Set backend URL in environment variables
4. Deploy

For more details, see `DEPLOYMENT.md`