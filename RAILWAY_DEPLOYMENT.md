# Railway Deployment Guide - Portfolio RAG

Quick reference guide untuk deploy Portfolio RAG ke Railway.

---

## ✅ Pre-Deployment Checklist

Run this command untuk verify readiness:
```bash
python test_deployment.py
```

Harus muncul output: `[SUCCESS] ALL CHECKS PASSED`

---

## 🚀 Deploy to Railway (5 Minutes)

### Step 1: Login ke Railway
1. Go to: https://railway.app/
2. Click "Login with GitHub"
3. Authorize Railway access

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose repository: `Adamite123/portfolio_RAG`
4. Click "Deploy Now"

### Step 3: Configure Environment Variables
1. After project created, click on the service card
2. Click "Variables" tab
3. Click "New Variable" dan add:

```env
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
FLASK_SECRET_KEY=your-random-secret-key-min-32-chars
```

**Generate Flask Secret Key** (optional):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Wait for Build
- Railway will automatically:
  - Detect Python project from `runtime.txt`
  - Install dependencies from `requirements.txt`
  - Start app using `Procfile` command
- Build time: ~2-3 minutes

### Step 5: Get Your Live URL
- Once deployed, Railway will provide a URL
- Format: `https://portfolio-rag-production-xxxx.up.railway.app`
- Click to open your live website!

---

## 📁 Deployment Files

| File | Purpose |
|------|---------|
| [Procfile](Procfile) | Tells Railway how to start the app: `gunicorn index:app --bind 0.0.0.0:$PORT` |
| [runtime.txt](runtime.txt) | Specifies Python version: `python-3.11` |
| [requirements.txt](requirements.txt) | Lists all Python dependencies (fixed encoding) |
| [.env.example](.env.example) | Template for environment variables |

**Note**: We removed `nixpacks.toml` and `railway.json` to let Railway auto-detect configuration.

---

## 🐛 Troubleshooting

### Error: "pip: command not found"
**Status**: FIXED ✅

**Previous Issue**: Custom `nixpacks.toml` was causing this error

**Solution**: Removed nixpacks config, let Railway auto-detect

**Commits**:
- `8a75d9b` - Fixed requirements.txt encoding
- `e4a6c0e` - Removed nixpacks.toml

---

### Error: "Invalid requirement: F\x00l\x00a\x00s\x00k\x00..."
**Status**: FIXED ✅

**Cause**: requirements.txt was in UTF-16LE encoding with null bytes

**Solution**: Recreated requirements.txt in ASCII encoding

**Commit**: `8a75d9b`

---

### Error: "Cannot install ... conflicting dependencies"
**Status**: FIXED ✅

**Error Message**:
```
ERROR: Cannot install langchain-core==0.3.56
The conflict is caused by:
  langchain-chroma 0.2.6 depends on langchain-core>=0.3.76
```

**Cause**: Exact version pinning (==) caused dependency conflicts

**Solution**: Changed to minimum version requirements (>=) to allow pip to resolve compatible versions

**Changes**:
- `langchain-core==0.3.56` → `langchain-core>=0.3.0`
- Removed unused packages: `langchain-cli`, `langchain-redis`
- Let pip auto-resolve compatible versions

**Commit**: `31194b8`

---

### Error: "Application failed to start"
**Check**:
1. View logs in Railway dashboard
2. Verify environment variables are set:
   - `OPENAI_API_KEY`
   - `FLASK_SECRET_KEY`
3. Check if PORT binding is correct in Procfile

**Procfile should be**:
```
web: gunicorn index:app --bind 0.0.0.0:$PORT
```

---

### Error: "Module not found: langchain/openai/chromadb"
**Check**: requirements.txt includes all dependencies

**Verify**:
```bash
python test_deployment.py
```

Should show: `[OK] requirements.txt contains all required packages`

---

### App Crashes After Deploy
**Check logs for**:
- `OPENAI_API_KEY` not set
- Import errors
- Port binding issues

**Solution**:
1. Go to Railway → Deployments → View Logs
2. Look for error message
3. Fix and redeploy (auto-deploy on git push)

---

## 🔄 Update Deployment

After initial deployment, untuk update:

```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push origin main
```

Railway will **automatically redeploy** from GitHub!

---

## 📊 Railway Free Tier Limits

| Resource | Limit |
|----------|-------|
| **Credit** | $5/month |
| **Runtime** | ~500 hours/month |
| **Memory** | 512MB - 8GB |
| **Builds** | Unlimited |

**Tips**:
- Free tier is enough untuk portfolio/demo
- App tidak sleep (unlike Render free tier)
- Upgrade to $5/month Hobby plan untuk production

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain:
1. Railway Dashboard → Service → Settings
2. Scroll to "Domains"
3. Click "Add Domain"
4. Enter your domain: `portfolio.yourdomain.com`

### Update DNS (di Hostinger atau domain provider):
Add CNAME record:
```
Type: CNAME
Name: portfolio (or @)
Value: [provided by Railway]
```

Wait 5-60 minutes untuk DNS propagation.

---

## 📝 Environment Variables Reference

### Required Variables:

#### OPENAI_API_KEY
- **Type**: String
- **Format**: `sk-proj-...`
- **Get from**: https://platform.openai.com/api-keys
- **Required**: YES

#### FLASK_SECRET_KEY
- **Type**: String
- **Length**: Minimum 32 characters
- **Generate**: `python -c "import secrets; print(secrets.token_hex(32))"`
- **Required**: YES

### Optional Variables:

#### FLASK_ENV
- **Type**: String
- **Values**: `production` or `development`
- **Default**: `production`
- **Required**: NO

#### FLASK_DEBUG
- **Type**: Integer
- **Values**: `0` (off) or `1` (on)
- **Default**: `0`
- **Required**: NO
- **Production**: Should be `0`

---

## 🎯 Deployment Verification

After deployment, test these:

### 1. Homepage Loads
- Visit Railway URL
- Should see portfolio page with mountain theme

### 2. Chat Functionality
- Type a question in chat
- AI should respond (verify OPENAI_API_KEY works)

### 3. User Login
- Click "Login" button
- Enter username
- Chat history should save

### 4. All Sections Load
- About, Skills, Experience, Projects, etc.
- No 404 errors

### 5. Download CV
- Click "Download CV" button
- Should download text file

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app/
- **GitHub Repo**: https://github.com/Adamite123/portfolio_RAG
- **OpenAI API**: https://platform.openai.com/

---

## 📞 Support

Jika masih ada error:

1. **Check Logs**: Railway Dashboard → Deployments → View Logs
2. **Verify Config**: Run `python test_deployment.py` locally
3. **Check Environment Variables**: Railway Dashboard → Variables
4. **Review Commits**: Look at recent changes that might break deployment

---

## ✅ Current Status

| Item | Status |
|------|--------|
| requirements.txt encoding | ✅ FIXED (ASCII) |
| Procfile | ✅ READY (port binding correct) |
| runtime.txt | ✅ READY (python-3.11) |
| nixpacks.toml | ✅ REMOVED (using auto-detect) |
| railway.json | ✅ REMOVED (using auto-detect) |
| Environment template | ✅ READY (.env.example) |
| Test script | ✅ ADDED (test_deployment.py) |

**ALL SYSTEMS GO** - Ready to deploy! 🚀

---

**Last Updated**: December 2025
**Version**: 1.0
**Status**: Production Ready
