#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify deployment readiness
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[FAIL] {description} MISSING: {filepath}")
        return False

def check_requirements():
    """Check requirements.txt"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False

    with open('requirements.txt', 'r') as f:
        content = f.read()
        required_packages = ['Flask', 'gunicorn', 'langchain', 'openai', 'chromadb']
        missing = []

        for pkg in required_packages:
            if pkg.lower() not in content.lower():
                missing.append(pkg)

        if missing:
            print(f"[FAIL] Missing packages in requirements.txt: {missing}")
            return False
        else:
            print(f"[OK] requirements.txt contains all required packages")
            return True

def check_env_example():
    """Check .env.example"""
    if not os.path.exists('.env.example'):
        print("[WARN] .env.example not found (optional)")
        return True

    with open('.env.example', 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content and 'FLASK_SECRET_KEY' in content:
            print("[OK] .env.example contains required variables")
            return True
        else:
            print("[WARN] .env.example missing some required variables")
            return True

def main():
    print("\n=== Checking Railway Deployment Readiness ===\n")

    checks = []

    # Check essential files
    checks.append(check_file_exists('Procfile', 'Procfile'))
    checks.append(check_file_exists('runtime.txt', 'Runtime specification'))
    checks.append(check_file_exists('requirements.txt', 'Dependencies'))
    checks.append(check_file_exists('index.py', 'Flask application'))

    # Check requirements content
    checks.append(check_requirements())

    # Check .env.example
    check_env_example()

    # Check if nixpacks/railway.json exist (should NOT exist now)
    if os.path.exists('nixpacks.toml'):
        print("[WARN] nixpacks.toml found - should be removed for auto-detection")
    else:
        print("[OK] nixpacks.toml not found (good - using auto-detection)")

    if os.path.exists('railway.json'):
        print("[WARN] railway.json found - consider removing for auto-detection")

    print("\n" + "="*50)

    if all(checks):
        print("[SUCCESS] ALL CHECKS PASSED - Ready to deploy to Railway!")
        print("\nNext steps:")
        print("1. Go to https://railway.app/")
        print("2. Deploy from GitHub: Adamite123/portfolio_RAG")
        print("3. Add environment variables:")
        print("   - OPENAI_API_KEY")
        print("   - FLASK_SECRET_KEY")
        return 0
    else:
        print("[FAIL] Some checks failed - please fix before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
