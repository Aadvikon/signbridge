#!/bin/bash
# SignBridge Production Deployment Script
# This script helps validate your environment before deploying

echo "SignBridge Production Deployment Checklist"
echo "=========================================="
echo ""

# Check if GitHub repo exists
echo "[1/5] Checking GitHub repository..."
if git remote -v | grep -q "aadvikon/signbridge"; then
    echo "✓ GitHub repository configured"
else
    echo "✗ GitHub repository not found"
    echo "  Please ensure your remote is set to: git@github.com:aadvikon/signbridge.git"
    exit 1
fi

# Check frontend environment
echo ""
echo "[2/5] Checking frontend setup..."
if [ -f "frontend/.env.example" ]; then
    echo "✓ Frontend .env.example found"
else
    echo "✗ Frontend .env.example not found"
fi

if [ -f "frontend/package.json" ]; then
    echo "✓ Frontend package.json found"
else
    echo "✗ Frontend package.json not found"
fi

if [ -f "frontend/vite.config.js" ]; then
    echo "✓ Frontend vite.config.js found"
else
    echo "✗ Frontend vite.config.js not found"
fi

# Check backend environment
echo ""
echo "[3/5] Checking backend setup..."
if [ -f "backend/main.py" ]; then
    echo "✓ Backend main.py found"
else
    echo "✗ Backend main.py not found"
fi

if [ -f ".env.production.example" ]; then
    echo "✓ Production environment template found"
else
    echo "✗ Production environment template not found"
fi

# Check for required documentation
echo ""
echo "[4/5] Checking deployment documentation..."
if [ -f "DEPLOYMENT.md" ]; then
    echo "✓ DEPLOYMENT.md found"
else
    echo "✗ DEPLOYMENT.md not found"
fi

if [ -f "README.md" ]; then
    echo "✓ README.md found"
else
    echo "✗ README.md not found"
fi

# Final instructions
echo ""
echo "[5/5] Deployment Instructions"
echo "=============================="
echo ""
echo "Next Steps:"
echo ""
echo "1. BACKEND DEPLOYMENT (Railway):"
echo "   - Go to https://railway.app"
echo "   - Create new project from GitHub"
echo "   - Select aadvikon/signbridge repo"
echo "   - Set root directory to: backend/"
echo "   - Add environment variables from .env.production.example"
echo "   - Note the Railway URL when deployment completes"
echo ""
echo "2. FRONTEND DEPLOYMENT (Vercel):"
echo "   - Go to https://vercel.com"
echo "   - Create new project from GitHub"
echo "   - Select aadvikon/signbridge repo"
echo "   - Set root directory to: frontend/"
echo "   - Set VITE_API_URL env var to your Railway backend URL"
echo "   - Note the Vercel URL when deployment completes"
echo ""
echo "3. UPDATE BACKEND CORS:"
echo "   - Update CORS_ORIGINS in Railway to: your-vercel-frontend-url"
echo "   - Restart the backend service"
echo ""
echo "4. TESTING:"
echo "   - Visit your Vercel frontend URL"
echo "   - Upload a test video"
echo "   - Verify it connects to your Railway backend"
echo "   - Check browser console for errors"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
echo ""
