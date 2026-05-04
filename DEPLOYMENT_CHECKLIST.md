# SignBridge Deployment Checklist

## AWS Bedrock Setup ✅
- [x] AWS credentials configured
- [x] Credentials tested with boto3
- [x] Backend code updated with Claude model
- [x] Code committed to GitHub

## Before Railway Deployment

### AWS Bedrock (Required)
- [ ] Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
- [ ] Navigate to **Model Access**
- [ ] Enable **Claude 3.5 Sonnet** or **Claude 3 Haiku**
- [ ] Submit request for access

### GitHub (Already Done ✅)
- [x] Code pushed to GitHub (master branch)
- [x] AWS credentials NOT in code (in .env only)
- [x] requirements.txt updated

### Railway Setup
- [ ] Create Railway account: https://railway.app
- [ ] Sign in with GitHub
- [ ] Grant Railway access to GitHub repo

## Railway Deployment Steps

1. [ ] Create new project in Railway
2. [ ] Connect GitHub repo (signbridge)
3. [ ] Set root directory to `backend/`
4. [ ] Add environment variables:
   - [ ] AWS_BEARER_TOKEN_BEDROCK
   - [ ] AWS_SECRET_ACCESS_KEY
   - [ ] AWS_REGION
   - [ ] JWT_SECRET (generate new)
   - [ ] Other optional variables
5. [ ] Trigger deployment
6. [ ] Monitor build in Railway logs
7. [ ] Verify deployment successful
8. [ ] Copy backend URL from Railway

## Testing After Deployment

- [ ] Test health endpoint: `GET /docs`
- [ ] Test Claude endpoint: `POST /chat`
- [ ] Check logs for errors
- [ ] Verify AWS Bedrock connection works

## Frontend Setup

- [ ] Deploy frontend to Vercel (or similar)
- [ ] Set `VITE_API_URL` to Railway backend URL
- [ ] Test frontend connects to backend
- [ ] Verify all features work

## Production Checks

- [ ] Enable HTTPS (Railway provides this)
- [ ] Set up monitoring/alerts
- [ ] Review API logs regularly
- [ ] Monitor AWS Bedrock costs
- [ ] Setup auto-scaling if needed

## Important Files

- [AWS_BEDROCK_SETUP.md](AWS_BEDROCK_SETUP.md) - Bedrock configuration details
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Step-by-step Railway deployment
- [DEPLOYMENT.md](DEPLOYMENT.md) - Overall deployment architecture
- [.env](.env) - AWS credentials (DON'T COMMIT)

## Quick Commands

```bash
# Check git status
git status

# View uncommitted changes
git diff

# Push latest code
git push origin master

# Test locally before deploying
python backend/main.py
```

## Support Resources

- Railway Docs: https://docs.railway.app
- AWS Bedrock Docs: https://docs.aws.amazon.com/bedrock
- FastAPI Docs: https://fastapi.tiangolo.com
- GitHub Issues: https://github.com/Aadvikon/signbridge/issues