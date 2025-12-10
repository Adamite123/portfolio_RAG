# Deployment Guide - Portfolio RAG

Panduan lengkap untuk deploy Portfolio RAG ke berbagai platform hosting.

---

## ⚠️ PENTING: Hostinger Limitation

**Hostinger shared hosting TIDAK SUPPORT Python Flask applications!**

Hostinger shared hosting hanya support:
- PHP (WordPress, Laravel, CodeIgniter, dll)
- Static HTML/CSS/JS
- Node.js (pada beberapa paket premium)

Untuk deploy Flask app, gunakan platform berikut yang **FREE** dan support Python:

---

## 🚀 Recommended Platform (FREE & Python Support)

### 1. Railway (EASIEST & RECOMMENDED)

**Pros**:
- FREE tier dengan $5 credit/bulan
- Auto-deploy dari GitHub
- Built-in PostgreSQL/Redis jika diperlukan
- HTTPS otomatis

**Steps**:

1. **Signup di Railway**
   ```
   https://railway.app/
   ```
   Login dengan GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Pilih repository `portfolio_RAG`

3. **Add Environment Variables**
   Di Railway dashboard, click project → Settings → Variables:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here
   FLASK_SECRET_KEY=your-secret-key-here-random-string
   ```

4. **Deploy**
   - Railway akan otomatis detect Python project
   - Build dan deploy otomatis
   - Kamu akan dapat URL: `https://portfolio-rag-production.up.railway.app`

5. **Custom Domain (Optional)**
   - Settings → Domains → Add custom domain
   - Point CNAME record dari domain kamu ke Railway

**Files needed** (sudah ada):
- ✅ `Procfile` - Sudah dibuat
- ✅ `requirements.txt` - Sudah diperbaiki
- ✅ `runtime.txt` - Sudah dibuat
- ✅ `railway.json` - Sudah dibuat

---

### 2. Render (ALTERNATIVE)

**Pros**:
- FREE tier (tapi sleep after 15 min inactive)
- Auto-deploy dari GitHub
- HTTPS otomatis

**Steps**:

1. **Signup di Render**
   ```
   https://render.com/
   ```

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository `portfolio_RAG`

3. **Configure**
   - Name: `portfolio-rag`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn index:app`

4. **Add Environment Variables**
   - OPENAI_API_KEY
   - FLASK_SECRET_KEY

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 menit untuk build

**URL**: `https://portfolio-rag.onrender.com`

---

### 3. PythonAnywhere (GOOD FOR LONG-RUNNING)

**Pros**:
- FREE tier tidak sleep
- Always-on even on free tier

**Cons**:
- Manual deployment (no auto-deploy dari GitHub)
- Setup lebih kompleks

**Steps**:

1. **Signup**
   ```
   https://www.pythonanywhere.com/
   ```

2. **Upload Code**
   - Buka "Files" tab
   - Upload semua file atau clone dari GitHub:
     ```bash
     git clone https://github.com/Adamite123/portfolio_RAG.git
     ```

3. **Create Virtual Environment**
   Buka "Bash console":
   ```bash
   cd portfolio_RAG
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Tab "Web"
   - "Add a new web app"
   - Select "Manual configuration"
   - Python version: 3.10

5. **WSGI Configuration**
   Edit file WSGI (klik link di Web tab):
   ```python
   import sys
   import os

   # Add your project directory to the sys.path
   project_home = '/home/yourusername/portfolio_RAG'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path

   # Load environment variables
   os.environ['OPENAI_API_KEY'] = 'your-key-here'
   os.environ['FLASK_SECRET_KEY'] = 'your-secret-here'

   # Import Flask app
   from index import app as application
   ```

6. **Reload Web App**
   - Klik "Reload" button di Web tab

**URL**: `https://yourusername.pythonanywhere.com`

---

### 4. Vercel (STATIC + SERVERLESS)

**Note**: Vercel lebih cocok untuk Next.js/Node.js, tapi bisa untuk Flask dengan serverless functions.

**Steps**:

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd portfolio_RAG
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add FLASK_SECRET_KEY
   ```

Tapi **TIDAK RECOMMENDED** karena Flask app butuh long-running process untuk ChromaDB.

---

## 🔧 Files yang Sudah Disiapkan

### 1. `Procfile`
```
web: gunicorn index:app
```
Untuk Railway, Render, Heroku

### 2. `runtime.txt`
```
python-3.11.0
```
Specify Python version

### 3. `requirements.txt`
Sudah diperbaiki dengan semua dependencies + gunicorn

### 4. `railway.json`
Configuration untuk Railway deployment

### 5. `.gitignore`
Exclude sensitive files:
- `.env` (API keys)
- `users_data/` (user chat history)
- `chroma_db/` (vector database)
- `.claude/` (IDE config)

---

## 📝 Environment Variables yang Dibutuhkan

Untuk semua platform, set environment variables ini:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `FLASK_SECRET_KEY` | Flask session secret | Random string 32+ chars |

---

## ⚙️ Pre-Deployment Checklist

- [x] `Procfile` dibuat
- [x] `runtime.txt` dibuat
- [x] `requirements.txt` diperbaiki dan include `gunicorn`
- [x] `.gitignore` updated (exclude `.env`, `users_data/`, dll)
- [x] `railway.json` dibuat
- [ ] Environment variables siap (OPENAI_API_KEY, FLASK_SECRET_KEY)
- [ ] Test local dengan gunicorn:
  ```bash
  pip install gunicorn
  gunicorn index:app
  # Buka http://localhost:8000
  ```

---

## 🔄 Update Deployment (Push Changes)

Setelah deploy pertama kali, untuk update:

1. **Make changes locally**
2. **Commit & Push**
   ```bash
   git add .
   git commit -m "Update: description"
   git push origin main
   ```
3. **Auto-deploy**
   - Railway: Auto-deploy otomatis
   - Render: Auto-deploy otomatis
   - PythonAnywhere: Manual pull dari GitHub

---

## 🐛 Troubleshooting

### Error: "Application failed to start"
- Check logs di platform dashboard
- Pastikan `gunicorn` ada di `requirements.txt`
- Verify environment variables sudah di-set

### Error: "OpenAI API key not set"
- Check environment variables di platform dashboard
- Pastikan variable name exact: `OPENAI_API_KEY`

### Error: "ChromaDB error"
- ChromaDB butuh writable disk
- Check platform supports persistent storage
- Railway & Render support persistent volumes

### Error: "Module not found"
- Check `requirements.txt` include semua dependencies
- Rebuild deployment

---

## 💰 Cost Comparison

| Platform | FREE Tier | Limitations |
|----------|-----------|-------------|
| **Railway** | $5 credit/bulan | 500 hours, 1GB RAM |
| **Render** | Unlimited | Sleep after 15 min inactive |
| **PythonAnywhere** | Always-on | 512MB RAM, 1 web app |
| **Vercel** | Unlimited | 10s execution limit (NOT GOOD for Flask) |

---

## 🎯 Recommendation

**Untuk Portfolio RAG:**

1. **BEST**: Railway (easiest setup, no sleep)
2. **ALTERNATIVE**: Render (free but sleep)
3. **FOR PRODUCTION**: Railway Hobby Plan ($5/month) atau PythonAnywhere Hacker Plan ($5/month)

---

## 📞 Support

Jika ada masalah deployment:
1. Check platform documentation
2. Check logs di platform dashboard
3. Verify environment variables
4. Test local dengan gunicorn terlebih dahulu

---

**Last Updated**: December 2025
