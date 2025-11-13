# Leapcell Deployment Guide

## 🚀 Quick Deploy to Leapcell

### Prerequisites
- Leapcell account: https://leapcell.io
- GitHub repository connected
- Branch: `user-service`

---

## 📝 Deployment Steps

### 1. **Push Configuration File to GitHub**

The `leapcell.yaml` file in your root directory tells Leapcell how to build and deploy your app.

```bash
git add leapcell.yaml LEAPCELL_DEPLOY.md
git commit -m "feat: add Leapcell deployment configuration"
git push
```

### 2. **Create New Project in Leapcell**

1. Go to https://leapcell.io dashboard
2. Click "New Project" or "Deploy"
3. Select "Import from GitHub"
4. Choose repository: `abisoyeo/distributed-notification-system`
5. Select branch: `user-service`
6. **Root directory:** `user-service`
7. Leapcell will auto-detect the `leapcell.yaml` file

### 3. **Set Environment Variables in Leapcell Dashboard**

⚠️ **IMPORTANT:** Set these sensitive values in the Leapcell dashboard (not in `leapcell.yaml`):

#### Required Secrets:
```env
SECRET_KEY=your-django-secret-key-min-50-chars-change-this
DB_PASSWORD=your-aiven-postgresql-password
```

#### Optional (if using Redis with password):
```env
REDIS_HOST=your-leapcell-redis-host
REDIS_PASSWORD=your-redis-password-if-any
```

#### Optional (if you want to customize):
```env
ALLOWED_HOSTS=.leapcell.io,.leapcell.app,yourdomain.com
```

### 4. **Create Redis Instance (Optional but Recommended)**

In Leapcell dashboard:
1. Go to "Databases" or "Add-ons"
2. Create a Redis instance
3. Copy the connection details:
   - Host (e.g., `redis-abc123.leapcell.io`)
   - Port (usually `6379`)
   - Password
4. Set these as environment variables:
   ```env
   REDIS_HOST=redis-abc123.leapcell.io
   REDIS_PASSWORD=your-redis-password
   ```

**OR skip Redis:**
Set `USE_REDIS=false` in environment variables (app will work without caching)

### 5. **Deploy**

Click "Deploy" button in Leapcell dashboard.

Leapcell will:
1. ✅ Clone your repository
2. ✅ Read `leapcell.yaml` configuration
3. ✅ Build your Docker image using `Dockerfile`
4. ✅ Run migrations (`python manage.py migrate`)
5. ✅ Collect static files
6. ✅ Start Gunicorn server on port 8000
7. ✅ Expose your app at a public URL

---

## 🔧 Configuration Details

### What `leapcell.yaml` Does:

- **Build:** Uses your existing `Dockerfile` (no changes to Docker setup)
- **Port:** Exposes port 8000 (matches your Django app)
- **Health Check:** Uses `/health` endpoint for monitoring
- **Resources:** Allocates 512MB RAM and 0.5 CPU (adjust as needed)
- **Environment:** Sets non-sensitive environment variables

### Database Configuration

**Using Aiven PostgreSQL (Recommended):**
- Your app will connect to your existing Aiven database
- No migration needed
- Data stays where it is
- Just set `DB_PASSWORD` in Leapcell environment variables

**Using Leapcell PostgreSQL (Alternative):**
1. Create PostgreSQL in Leapcell dashboard
2. Update environment variables:
   ```env
   DB_HOST=your-leapcell-postgres-host
   DB_USER=postgres
   DB_PASSWORD=your-leapcell-postgres-password
   DB_NAME=user_service_db
   DB_PORT=5432
   ```
3. Run migrations to set up database

---

## ✅ Post-Deployment Verification

### 1. Check Deployment Status
In Leapcell dashboard, verify:
- ✅ Build succeeded
- ✅ Container is running
- ✅ Health check passing

### 2. Test Your Endpoints

```bash
# Get your Leapcell URL (e.g., https://user-service-abc123.leapcell.io)
LEAPCELL_URL="https://your-app.leapcell.io"

# Test health endpoint
curl $LEAPCELL_URL/health

# Expected response:
# {"status": "healthy", "redis": "connected", "database": "connected"}

# Test user registration
curl -X POST $LEAPCELL_URL/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "name": "Test User"
  }'

# Test login
curl -X POST $LEAPCELL_URL/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Check Logs

In Leapcell dashboard:
- View application logs
- Check for any errors
- Monitor performance

---

## 🔄 Continuous Deployment

### Automatic Deployments

Leapcell can automatically deploy when you push to GitHub:

1. In Leapcell dashboard, go to your project settings
2. Enable "Auto Deploy"
3. Choose branch: `user-service`
4. Every push to `user-service` branch will trigger a new deployment

### Manual Deployments

Click "Redeploy" button in Leapcell dashboard anytime.

---

## 📊 Environment Variables Reference

### Complete List (Set in Leapcell Dashboard):

```env
# ===== REQUIRED =====
SECRET_KEY=your-django-secret-key-at-least-50-characters-long
DB_PASSWORD=your-aiven-postgresql-password

# ===== OPTIONAL =====
DEBUG=False
ALLOWED_HOSTS=.leapcell.io,.leapcell.app,yourdomain.com

# Database (these are pre-configured in leapcell.yaml, only change if needed)
USE_POSTGRES=true
DB_NAME=user_service_db
DB_USER=avnadmin
DB_HOST=user-contries-currency1.i.aivencloud.com
DB_PORT=18360

# Redis (set if using Leapcell Redis or external Redis)
USE_REDIS=true
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password-if-any

# App Settings
DJANGO_SETTINGS_MODULE=user_service.settings
PYTHONUNBUFFERED=1
```

---

## 🌍 Custom Domain (Optional)

### Add Your Domain:

1. In Leapcell dashboard, go to "Domains"
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed by Leapcell
4. Update `ALLOWED_HOSTS` environment variable:
   ```env
   ALLOWED_HOSTS=.leapcell.io,.leapcell.app,api.yourdomain.com
   ```

---

## 🛠️ Troubleshooting

### Deployment Fails

**Check build logs in Leapcell dashboard:**
- Docker build errors
- Missing dependencies
- Port conflicts

**Common issues:**
- Forgot to set `SECRET_KEY` environment variable
- Forgot to set `DB_PASSWORD` environment variable
- Wrong `Dockerfile` path (should be just `Dockerfile`)

### App Starts but Crashes

**Check application logs:**
- Database connection errors → Check `DB_PASSWORD` is set
- Redis connection errors → Set `USE_REDIS=false` or provide Redis credentials
- Migration errors → Check database is accessible

### Health Check Failing

**Check:**
- Database connection (Aiven PostgreSQL accessible?)
- Redis connection (if enabled)
- `/health` endpoint returning 200

### Can't Access App

**Check:**
- App is deployed and running
- Health check is passing
- URL is correct (check Leapcell dashboard for URL)
- Firewall/network restrictions

---

## 📈 Scaling & Performance

### Increase Resources

In `leapcell.yaml`, adjust:
```yaml
resources:
  memory: 1Gi      # Increase to 1GB
  cpu: 1           # Increase to 1 CPU core
```

### Multiple Instances

Leapcell may support horizontal scaling (check their docs):
```yaml
replicas: 3  # Run 3 instances
```

---

## 💰 Cost Optimization

### Free Tier Tips:
- Use existing Aiven PostgreSQL (free)
- Use Leapcell Redis free tier (if available)
- Start with minimal resources (512MB RAM)
- Set `DEBUG=False` (better performance)
- Enable Redis caching (reduces database queries)

### Monitor Usage:
- Check Leapcell dashboard for resource usage
- Watch logs for errors
- Monitor response times

---

## 🎯 Summary

**Your Docker setup is untouched!** ✅
- `Dockerfile` - No changes
- `docker-compose.yml` - No changes
- All existing files - No changes

**New files added:**
- `leapcell.yaml` - Leapcell configuration
- `LEAPCELL_DEPLOY.md` - This deployment guide

**Next steps:**
1. ✅ Push files to GitHub
2. ✅ Connect Leapcell to GitHub
3. ✅ Set environment variables in Leapcell
4. ✅ Deploy!

Your User Service will be live at: `https://your-app.leapcell.io` 🚀
