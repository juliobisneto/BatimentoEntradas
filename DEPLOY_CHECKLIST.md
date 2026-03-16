# ✅ Deploy Checklist

Quick checklist for deploying the Ticket Revenue Reconciliation System.

## Pre-Deployment

- [ ] All code committed and pushed to GitHub
- [ ] `.env` files are NOT committed (in .gitignore)
- [ ] Created accounts on Supabase, Render, and Vercel
- [ ] Generated SECRET_KEY: `openssl rand -hex 32`

---

## 1. Supabase (5-10 min)

- [ ] Create new project
- [ ] Choose region (São Paulo recommended for Brazil)
- [ ] Save database password
- [ ] Create storage bucket `csv-files`
- [ ] Configure storage policies
- [ ] Copy Project URL and anon public key

---

## 2. Render Backend (10-15 min)

- [ ] Create PostgreSQL database (free tier)
- [ ] Copy Internal Database URL
- [ ] Create Web Service
- [ ] Connect GitHub repository
- [ ] Set Runtime: Python 3
- [ ] Add environment variables:
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY`
  - [ ] `FRONTEND_URL`  (temporary, will update)
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `PYTHON_VERSION=3.11.0`
- [ ] Deploy and wait for build
- [ ] Copy service URL
- [ ] Run in Shell:
  - [ ] `python scripts/init_db.py`
  - [ ] `python scripts/create_admin.py`
  - [ ] `python scripts/test_connection.py`

---

## 3. Vercel Frontend (5 min)

- [ ] Update `frontend/.env.production` with Render URL
- [ ] Commit and push
- [ ] Create new project in Vercel
- [ ] Import GitHub repository
- [ ] Set Root Directory: `frontend`
- [ ] Framework: Vite
- [ ] Add environment variable:
  - [ ] `VITE_API_URL` = Render backend URL
- [ ] Deploy
- [ ] Copy Vercel URL

---

## 4. Update Backend CORS (2 min)

- [ ] Go back to Render
- [ ] Update `FRONTEND_URL` with Vercel URL
- [ ] Redeploy backend

---

## 5. Testing (5 min)

- [ ] Visit backend `/docs` endpoint
- [ ] Visit frontend URL
- [ ] Login with admin@admin.com / admin
- [ ] Check Dashboard
- [ ] Check Payment Calendar
- [ ] Check Payment Methods
- [ ] Try importing a CSV file

---

## 6. Post-Deployment

- [ ] Change admin password
- [ ] Save all URLs:
  - Frontend: `________________`
  - Backend: `________________`
  - Database: `________________`
- [ ] Document credentials securely
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts (optional)

---

## Environment Variables Reference

### Backend (Render)
```
DATABASE_URL=postgresql://...
SECRET_KEY=<generated>
FRONTEND_URL=https://your-app.vercel.app
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
PYTHON_VERSION=3.11.0
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend.onrender.com
```

---

## Total Time: ~30-40 minutes

## 💰 Total Cost: $0/month

---

## Need Help?

See `DEPLOY_GUIDE.md` for detailed step-by-step instructions.



