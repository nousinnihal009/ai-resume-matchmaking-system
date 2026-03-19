# Production Deployment Checklist

## 1. Secrets & Configuration
- [ ] `SECRET_KEY` generated securely (`openssl rand -hex 32`)
- [ ] `DEBUG` explicitly set to `False`  
- [ ] `DATABASE_URL` points to production PostgreSQL cluster
- [ ] `REDIS_URL` points to production Redis instance
- [ ] `CORS_ORIGINS` strictly limited to frontend production domain (no `*`)
- [ ] `SENTRY_DSN` configured for frontend and backend
- [ ] `SENDGRID_API_KEY` configured and verified

## 2. Platform & Database
- [ ] PostgreSQL max connections configured appropriately for Uvicorn + Celery
- [ ] Initial admin user created manually via DB console or secure script
- [ ] Redis configured with acceptable maxmemory policy (e.g., `allkeys-lru`)
- [ ] Scheduled DB backups enabled (pg_dump or managed service)

## 3. Deployment Build
- [ ] Frontend built with `VITE_USE_MOCK=false` and accurate `VITE_API_URL`
- [ ] Docker Compose override used for production overrides (logs, restart policies)
- [ ] Backend container built locally to verify size and syntax
- [ ] All CI/CD checks passing on `main` branch

## 4. Verification Check
- [ ] Hit `/api/v1/auth/login` and verify security headers are present
- [ ] Check `/docs` returns 404
- [ ] Verify test email flow via signup endpoint
- [ ] Upload a resume and verify Celery worker processes it successfully
