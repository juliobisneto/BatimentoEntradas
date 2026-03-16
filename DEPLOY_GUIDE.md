# 🚀 Deploy Guide - Ticket Revenue Reconciliation System

Complete guide for deploying the application to production using free cloud services.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step 1: Supabase Setup (Database + Storage)](#step-1-supabase-setup)
4. [Step 2: Render Setup (Backend)](#step-2-render-setup)
5. [Step 3: Vercel Setup (Frontend)](#step-3-vercel-setup)
6. [Step 4: Testing](#step-4-testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, make sure you have:

- [ ] GitHub account
- [ ] Git installed and repository pushed to GitHub
- [ ] All code committed (no pending changes)

**Create accounts on these platforms (all free):**
- [ ] [Supabase](https://supabase.com) - Database & Storage
- [ ] [Render](https://render.com) - Backend hosting
- [ ] [Vercel](https://vercel.com) - Frontend hosting

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  VERCEL (Frontend)                      │
│  • React + Vite                         │
│  • CDN Global                           │
│  URL: your-app.vercel.app               │
└─────────────────────────────────────────┘
              ↓ API Calls
┌─────────────────────────────────────────┐
│  RENDER (Backend)                       │
│  • FastAPI + Python                     │
│  • Free 750h/month                      │
│  URL: your-backend.onrender.com         │
└─────────────────────────────────────────┘
              ↓ Database
┌─────────────────────────────────────────┐
│  SUPABASE                               │
│  • PostgreSQL (500MB)                   │
│  • Storage for CSVs (1GB)               │
│  URL: xxx.supabase.co                   │
└─────────────────────────────────────────┘
```

---

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in:
   - **Name**: `batimento-storage` (or your choice)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users (e.g., `South America (São Paulo)`)
   - **Plan**: Free
4. Click "Create Project" (takes ~2 minutes)

### 1.2 Get Database Credentials

1. Go to **Settings** → **Database**
2. Scroll to "Connection string"
3. Copy the **URI** connection string
4. Save it as: `postgresql://postgres:[YOUR-PASSWORD]@xxx.supabase.co:5432/postgres`
5. Replace `[YOUR-PASSWORD]` with your actual password

### 1.3 Create Storage Bucket

1. Go to **Storage** in sidebar
2. Click "New bucket"
3. Fill in:
   - **Name**: `csv-files`
   - **Public**: ✅ (check if you want public access) or leave unchecked for private
4. Click "Create bucket"

### 1.4 Configure Storage Policies

1. Click on `csv-files` bucket
2. Click "Policies"
3. Click "New Policy"
4. Use template "Allow authenticated users to upload"
5. Modify if needed
6. Click "Save policy"

### 1.5 Get API Keys

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJhbG...` (long token)
3. Save them for later

**✅ Supabase Setup Complete!**

---

## Step 2: Render Setup

### 2.1 Create PostgreSQL Database

1. Go to https://render.com and sign in
2. Click "New +" → "PostgreSQL"
3. Fill in:
   - **Name**: `batimento-db`
   - **Database**: `batimento_entradas`
   - **Region**: `Oregon (US West)` (free tier available)
   - **Plan**: **Free** (0 GB RAM)
4. Click "Create Database"
5. Wait ~1 minute for database to be ready

### 2.2 Get Database URL

1. On the database page, find "Connections"
2. Copy **Internal Database URL** (starts with `postgres://`)
3. Save it for later

### 2.3 Create Web Service (Backend)

1. Click "New +" → "Web Service"
2. Connect your GitHub account
3. Select your repository
4. Fill in:
   - **Name**: `batimento-backend`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `.` (leave empty or put `.`)
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

### 2.4 Configure Environment Variables

In the "Environment" section, add these variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | (paste the Internal Database URL from step 2.2) |
| `SECRET_KEY` | (generate with: `openssl rand -hex 32`) |
| `FRONTEND_URL` | `https://batimento-frontend.vercel.app` (will update later) |
| `SUPABASE_URL` | (paste from Supabase step 1.5) |
| `SUPABASE_KEY` | (paste from Supabase step 1.5) |
| `PYTHON_VERSION` | `3.11.0` |

### 2.5 Deploy Backend

1. Click "Create Web Service"
2. Wait for deployment (~3-5 minutes)
3. Check logs for any errors
4. Copy the service URL (e.g., `https://batimento-backend.onrender.com`)

### 2.6 Initialize Database

1. On Render service page, click "Shell" tab
2. Run these commands:

```bash
# Create tables
python scripts/init_db.py

# Create admin user
python scripts/create_admin.py

# Test connection
python scripts/test_connection.py
```

3. Verify all scripts run successfully

**✅ Render Backend Setup Complete!**

---

## Step 3: Vercel Setup

### 3.1 Prepare Frontend

1. Update `frontend/.env.production`:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```
   (Replace with your actual Render backend URL)

2. Commit and push:
   ```bash
   git add .
   git commit -m "Configure production environment"
   git push
   ```

### 3.2 Deploy to Vercel

1. Go to https://vercel.com and sign in
2. Click "Add New..." → "Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 3.3 Add Environment Variables

In "Environment Variables" section:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://your-backend.onrender.com` |

### 3.4 Deploy

1. Click "Deploy"
2. Wait ~2-3 minutes
3. Copy the deployment URL (e.g., `https://batimento-frontend.vercel.app`)

### 3.5 Update Backend CORS

1. Go back to Render
2. Update `FRONTEND_URL` environment variable with your Vercel URL
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for redeployment

**✅ Vercel Frontend Setup Complete!**

---

## Step 4: Testing

### 4.1 Test Backend

1. Visit `https://your-backend.onrender.com/docs`
2. You should see the API documentation
3. Try the `/health` endpoint

### 4.2 Test Frontend

1. Visit your Vercel URL
2. Try to login:
   - Email: `admin@admin.com`
   - Password: `admin`
3. Check all pages:
   - Dashboard
   - Payment Calendar
   - Payment Methods

### 4.3 Test Full Flow

1. Create a CSV file in the format:
   ```csv
   Date,Event Sponsor,Venue,Event,Payment Method,Transaction Type,Quantity,Gross Amount,Returns,Net Amount,Tax/Fee,Net to Receive,Settlement Date
   2025-01-15,Sponsor A,Venue 1,Event 1,Credit Card,Sale,100,1000.00,0,1000.00,50.00,950.00,2025-02-15
   ```

2. Upload via the system
3. Check Dashboard for data
4. Verify Payment Calendar

**✅ All Testing Complete!**

---

## Environment Variables Summary

### Backend (Render)
```bash
DATABASE_URL=postgresql://user:pass@host.supabase.co:5432/postgres
SECRET_KEY=<generate-with-openssl-rand-hex-32>
FRONTEND_URL=https://batimento-frontend.vercel.app
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
PYTHON_VERSION=3.11.0
```

### Frontend (Vercel)
```bash
VITE_API_URL=https://batimento-backend.onrender.com
```

---

## Troubleshooting

### Backend won't start

**Issue**: Build fails on Render

**Solution**:
- Check `requirements.txt` is present
- Verify Python version in `runtime.txt`
- Check logs in Render dashboard
- Ensure all dependencies are listed

### Database connection error

**Issue**: Can't connect to database

**Solution**:
- Verify `DATABASE_URL` is correct
- Check if it starts with `postgresql://` (not `postgres://`)
- Ensure database is running in Render
- Test with `python scripts/test_connection.py`

### CORS errors in frontend

**Issue**: API calls fail with CORS error

**Solution**:
- Verify `FRONTEND_URL` in Render matches Vercel URL exactly
- Include `https://` protocol
- Redeploy backend after changing
- Clear browser cache

### Frontend shows blank page

**Issue**: White screen or build errors

**Solution**:
- Check `VITE_API_URL` is set in Vercel
- Verify build logs in Vercel
- Check browser console for errors
- Ensure `frontend/` is set as root directory

### CSV upload not working

**Issue**: Files don't upload

**Solution**:
- Check Supabase storage bucket is created
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check storage policies allow uploads
- Test with `python scripts/test_connection.py`

---

## 🎉 Deployment Complete!

Your application is now live and accessible from anywhere!

### URLs:
- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.onrender.com
- **API Docs**: https://your-backend.onrender.com/docs

### Next Steps:
1. Change admin password
2. Add more users if needed
3. Configure custom domain (optional)
4. Set up monitoring/alerts
5. Regular backups (Supabase does this automatically)

---

## 💰 Cost Summary

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Render** | ✅ Free | 750h/month, 512MB RAM |
| **Vercel** | ✅ Free | 100GB bandwidth/month |
| **Supabase** | ✅ Free | 500MB DB, 1GB storage |
| **TOTAL** | **$0/month** | Perfect for production use |

---

## 📞 Support

If you encounter issues:
1. Check logs in each service dashboard
2. Run `python scripts/test_connection.py` locally
3. Verify all environment variables are set correctly
4. Check this guide again

**Happy Deploying! 🚀**



