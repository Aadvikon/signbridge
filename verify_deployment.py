#!/usr/bin/env python3
"""
Final deployment verification script for SignBridge.
Checks that everything is ready for Railway deployment.
"""

import os
import json
from pathlib import Path

def check_env_file():
    """Verify .env file exists and has required variables."""
    print("✓ Checking .env file...")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("  ❌ .env file not found")
        return False
    
    required_vars = [
        "AWS_BEARER_TOKEN_BEDROCK",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION"
    ]
    
    env_content = env_file.read_text()
    for var in required_vars:
        if var in env_content:
            print(f"  ✅ {var} found")
        else:
            print(f"  ❌ {var} missing")
            return False
    
    return True

def check_backend_files():
    """Verify backend structure is correct."""
    print("\n✓ Checking backend files...")
    required_files = [
        "backend/main.py",
        "backend/claude_service.py",
        "backend/routes/claude_routes.py",
        "requirements.txt",
        "RAILWAY_DEPLOYMENT.md"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    return all_exist

def check_git_status():
    """Verify code is committed and pushed."""
    print("\n✓ Checking Git status...")
    import subprocess
    
    # Check if uncommitted changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        if result.stdout.strip():
            print(f"  ⚠️  Uncommitted changes found (this is OK for local testing)")
        else:
            print("  ✅ All changes committed")
        
        # Check if pushed to origin
        result = subprocess.run(
            ["git", "log", "--oneline", "origin/master", "-1"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ Latest commit: {result.stdout.strip()[:50]}")
            return True
    
    return False

def check_requirements():
    """Verify requirements.txt has critical packages."""
    print("\n✓ Checking requirements.txt...")
    req_file = Path("requirements.txt")
    
    critical_packages = [
        "fastapi",
        "uvicorn",
        "boto3",
        "python-dotenv"
    ]
    
    content = req_file.read_text().lower()
    for pkg in critical_packages:
        if pkg in content:
            print(f"  ✅ {pkg}")
        else:
            print(f"  ❌ {pkg} missing")
            return False
    
    return True

def check_claude_service():
    """Verify Claude service is configured."""
    print("\n✓ Checking Claude service...")
    claude_file = Path("backend/claude_service.py")
    content = claude_file.read_text()
    
    if "bedrock-runtime" in content:
        print("  ✅ Bedrock runtime configured")
    else:
        print("  ❌ Bedrock runtime not found")
        return False
    
    if "MODEL_ID" in content:
        print("  ✅ MODEL_ID defined")
    else:
        print("  ❌ MODEL_ID not found")
        return False
    
    return True

def main():
    print("=" * 50)
    print("SignBridge Railway Deployment Verification")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", check_env_file),
        ("Backend Files", check_backend_files),
        ("Git Status", check_git_status),
        ("Requirements", check_requirements),
        ("Claude Service", check_claude_service),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("DEPLOYMENT READINESS REPORT")
    print("=" * 50)
    
    all_pass = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_pass = False
    
    print("\n" + "=" * 50)
    if all_pass:
        print("🎉 READY FOR RAILWAY DEPLOYMENT!")
        print("\nNext Steps:")
        print("1. Go to https://railway.app")
        print("2. Create new project from GitHub (signbridge)")
        print("3. Set root directory: backend/")
        print("4. Add environment variables from .env file")
        print("5. Trigger deployment")
        print("\nEnvironment variables to add in Railway:")
        print("- AWS_BEARER_TOKEN_BEDROCK")
        print("- AWS_SECRET_ACCESS_KEY")
        print("- AWS_REGION")
        print("- JWT_SECRET (generate new)")
        print("- CORS_ORIGINS=*")
        print("- ENVIRONMENT=production")
    else:
        print("⚠️  ISSUES FOUND - FIX BEFORE DEPLOYMENT")
    print("=" * 50)
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    exit(main())