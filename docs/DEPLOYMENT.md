# Deployment Guide

This guide covers deploying the Recipe Management System to production.

## Architecture Overview

- **Frontend**: Vercel (Next.js)
- **Backend**: Railway or Render (Django)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis Cloud or Upstash
- **Storage**: Supabase Storage
- **AI**: Groq API

## Frontend Deployment (Vercel)

### 1. Prepare Repository

Ensure your code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Import your repository
5. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Environment Variables

Add these in Vercel dashboard (Settings → Environment Variables):

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=Recipe Management System
```

### 4. Deploy

Click "Deploy" and wait for the build to complete.

Your frontend will be live at: `https://your-project.vercel.app`

## Backend Deployment (Railway)

### 1. Prepare for Deployment

Create a `runtime.txt` in backend folder:

```
python-3.11
```

Create a `Procfile` in backend folder:

```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A core.celery worker --loglevel=info
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Configure service:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements/production.txt`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### 3. Environment Variables

Add in Railway dashboard (Variables tab):

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=generate-a-new-secret-key-for-production
DEBUG=False
ALLOWED_HOSTS=.railway.app,.vercel.app

# Database (from Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Groq
GROQ_API_KEY=your-groq-api-key

# Redis (Railway provides this)
REDIS_URL=${REDIS_URL}

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Optional: Sentry for error tracking
SENTRY_DSN=your-sentry-dsn
```

### 4. Add Redis

1. In Railway, click "New" → "Database" → "Redis"
2. Railway will automatically set the `REDIS_URL` environment variable

### 5. Run Migrations

```bash
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

## Alternative: Render

### Backend on Render

1. Go to [render.com](https://render.com)
2. Create "New Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: recipe-backend
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements/production.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn config.wsgi:application`

Add environment variables same as Railway.

## Database Setup (Production)

Your Supabase database is already production-ready. Just ensure:

1. RLS policies are enabled
2. Backups are configured (automatic in Supabase)
3. Connection pooling is enabled

## Redis Cloud Setup

If not using Railway's Redis:

1. Go to [redis.com/try-free](https://redis.com/try-free/)
2. Create free database (30MB)
3. Copy connection URL to `REDIS_URL`

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) will:
- Run on every push and PR
- Execute tests
- Check linting
- Run security scans

Deployments:
- **Frontend**: Auto-deploys from `main` via Vercel
- **Backend**: Auto-deploys from `main` via Railway/Render

## Post-Deployment Checklist

- [ ] Frontend is accessible
- [ ] Backend API responds
- [ ] User registration works
- [ ] Login/Logout works
- [ ] Ingredient CRUD operations work
- [ ] Recipe upload (text) works
- [ ] Recipe upload (image) works
- [ ] Chatbot responds
- [ ] Shopping list functions
- [ ] Check error logs (Sentry/Railway logs)

## Monitoring

### Railway

- View logs in Railway dashboard
- Set up log alerts
- Monitor resource usage

### Vercel

- Check deployment logs
- Monitor function invocations
- Review analytics

### Sentry (Recommended)

1. Create account at [sentry.io](https://sentry.io)
2. Create new project
3. Add DSN to environment variables
4. Monitor errors in real-time

## Scaling Considerations

### Backend Scaling
- Railway auto-scales based on traffic
- Consider upgrading to paid plan for:
  - More RAM (2GB+ for ML models)
  - Persistent disk storage
  - Multiple workers

### Frontend Scaling
- Vercel scales automatically
- CDN edge caching included
- No action needed

### Database Scaling
- Supabase free tier: Good for up to 500MB
- Upgrade to Pro for:
  - 8GB database
  - More concurrent connections
  - Daily backups

## Backup Strategy

### Database Backups
- Supabase: Automatic daily backups (Pro plan)
- Manual backup: Use Supabase CLI or pg_dump

### File Storage Backups
- Supabase Storage: Included in database backups
- Consider additional backup to S3

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY in production
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS correctly
- [ ] Review CORS settings
- [ ] Enable rate limiting
- [ ] Set up CSP headers
- [ ] Regular dependency updates

## Cost Estimation (Free Tiers)

| Service | Free Tier | Usage Limit |
|---------|-----------|-------------|
| Vercel | Yes | 100GB bandwidth/month |
| Railway | $5 credit/month | ~500 hours runtime |
| Supabase | Yes | 500MB database, 1GB storage |
| Groq | Yes | 14,400 requests/day |
| Redis Cloud | Yes | 30MB storage |

**Estimated monthly cost**: $0-10 depending on usage

## Troubleshooting

### Build Failures

**Frontend build fails**
- Check Node version (should be 20+)
- Verify all environment variables are set
- Review build logs in Vercel

**Backend build fails**
- Verify Python version in runtime.txt
- Check requirements.txt for version conflicts
- Review Railway/Render logs

### Runtime Errors

**500 Internal Server Error**
- Check Django logs
- Verify database connection
- Ensure all migrations ran
- Check Sentry for error details

**Database Connection Issues**
- Verify DATABASE_URL is correct
- Check Supabase status
- Ensure IP allowlist includes Railway/Render IPs

**Groq API Errors**
- Verify API key is valid
- Check rate limits
- Monitor quota usage

## Rolling Back

### Vercel
1. Go to Deployments
2. Find previous working deployment
3. Click "Promote to Production"

### Railway
1. Go to Deployments tab
2. Select previous deployment
3. Click "Redeploy"

## Support

For deployment issues:
- Check service status pages
- Review documentation
- Contact support (Vercel, Railway, Supabase)
- Open GitHub issue for application bugs
