# Docker Quick Reference - User Service

## Common Commands

### Local Development

```bash
# Start all services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Build and start (after code changes)
docker-compose up --build

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f user-service
docker-compose logs -f db
docker-compose logs -f redis

# Stop services (keep data)
docker-compose down

# Stop and remove volumes (delete data)
docker-compose down -v

# Restart a specific service
docker-compose restart user-service

# Check service status
docker-compose ps
```

### Production

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production services
docker-compose -f docker-compose.prod.yml down

# Restart production service
docker-compose -f docker-compose.prod.yml restart user-service
```

### Executing Commands in Containers

```bash
# Run Django management commands
docker-compose exec user-service python manage.py migrate
docker-compose exec user-service python manage.py createsuperuser
docker-compose exec user-service python manage.py shell
docker-compose exec user-service python manage.py collectstatic

# Access Django shell
docker-compose exec user-service python manage.py shell

# Access database
docker-compose exec db psql -U user_service_user -d user_service_db

# Access Redis CLI
docker-compose exec redis redis-cli

# Access container bash
docker-compose exec user-service bash
docker-compose exec db sh
docker-compose exec redis sh
```

### Debugging

```bash
# Check container health
docker-compose ps

# Inspect container
docker inspect user-service-app

# View container resource usage
docker stats

# Check health endpoint
curl http://localhost:8000/health

# Check specific health endpoints
curl http://localhost:8000/health/liveness
curl http://localhost:8000/health/readiness

# View last 100 lines of logs
docker-compose logs --tail=100 user-service

# Follow logs from specific time
docker-compose logs --since 30m -f user-service
```

### Database Operations

```bash
# Create database backup
docker-compose exec db pg_dump -U user_service_user user_service_db > backup.sql

# Restore database from backup
docker-compose exec -T db psql -U user_service_user -d user_service_db < backup.sql

# List all databases
docker-compose exec db psql -U user_service_user -l

# Connect to database
docker-compose exec db psql -U user_service_user -d user_service_db

# Check database connection
docker-compose exec db pg_isready -U user_service_user
```

### Image Management

```bash
# Build image
docker-compose build

# Build without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# List images
docker images

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect user-service_postgres_data

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm user-service_postgres_data
```

### Network Management

```bash
# List networks
docker network ls

# Inspect network
docker network inspect user-service_user-service-network

# Remove unused networks
docker network prune
```

### Complete Cleanup

```bash
# Stop and remove everything
docker-compose down -v

# Remove all containers, images, volumes, networks
docker system prune -a --volumes

# Check disk usage
docker system df
```

## Environment Setup

### First Time Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your settings
notepad .env  # Windows
# or
vim .env      # Linux/Mac

# 3. Build and start services
docker-compose up --build -d

# 4. Check health
docker-compose ps
curl http://localhost:8000/health

# 5. Create superuser
docker-compose exec user-service python manage.py createsuperuser
```

### Updating After Code Changes

```bash
# 1. Stop services
docker-compose down

# 2. Rebuild with no cache
docker-compose build --no-cache

# 3. Start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f user-service
```

## Troubleshooting Commands

### Port Already in Use

```powershell
# Windows PowerShell - Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F
```

### Permission Issues (Linux/Mac)

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix log directory
chmod 755 logs/
```

### Container Won't Start

```bash
# Check detailed error
docker-compose logs user-service

# Check if port is in use
netstat -ano | findstr :8000

# Remove old containers
docker-compose down
docker-compose up --force-recreate
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Check database health
docker-compose exec db pg_isready -U user_service_user

# Test connection from app
docker-compose exec user-service python manage.py dbshell

# View database logs
docker-compose logs db
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis info
docker-compose exec redis redis-cli info

# View Redis logs
docker-compose logs redis
```

## Health Check Commands

```bash
# Check all health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/liveness
curl http://localhost:8000/health/readiness

# Pretty print JSON response
curl http://localhost:8000/health | python -m json.tool

# Check with authentication
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/<user_id>/
```

## Performance Monitoring

```bash
# Real-time resource usage
docker stats

# Container resource usage (specific)
docker stats user-service-app

# Check logs size
docker-compose exec user-service du -sh /app/logs

# PostgreSQL connection count
docker-compose exec db psql -U user_service_user -d user_service_db -c "SELECT count(*) FROM pg_stat_activity;"

# Redis memory usage
docker-compose exec redis redis-cli info memory

# Check Gunicorn workers
docker-compose exec user-service ps aux | grep gunicorn
```

## Production Deployment Checklist

```bash
# 1. Set environment variables
cp .env.example .env
# Edit .env with production values

# 2. Build production image
docker-compose -f docker-compose.prod.yml build

# 3. Test image locally
docker-compose -f docker-compose.prod.yml up

# 4. Check health
curl http://localhost:8000/health

# 5. Run migrations
docker-compose -f docker-compose.prod.yml exec user-service python manage.py migrate

# 6. Collect static files
docker-compose -f docker-compose.prod.yml exec user-service python manage.py collectstatic --noinput

# 7. Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# 8. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f

# 9. Verify health
curl http://your-domain.com/health
```

## Useful Aliases (Optional)

Add to your shell profile (.bashrc, .zshrc, or PowerShell profile):

```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up'
alias dcud='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcr='docker-compose restart'

# Docker Compose exec shortcuts
alias dce='docker-compose exec'
alias dceus='docker-compose exec user-service'
alias dcedb='docker-compose exec db psql -U user_service_user -d user_service_db'
alias dceredis='docker-compose exec redis redis-cli'

# Django management commands
alias dcm='docker-compose exec user-service python manage.py'
alias dcmigrate='docker-compose exec user-service python manage.py migrate'
alias dcshell='docker-compose exec user-service python manage.py shell'
```

## Emergency Recovery

### Service Crashed

```bash
# Check status
docker-compose ps

# Restart crashed service
docker-compose restart user-service

# View crash logs
docker-compose logs --tail=100 user-service

# Force recreate
docker-compose up -d --force-recreate user-service
```

### Database Corrupted

```bash
# Stop all services
docker-compose down

# Remove database volume
docker volume rm user-service_postgres_data

# Restart with fresh database
docker-compose up -d

# Restore from backup
docker-compose exec -T db psql -U user_service_user -d user_service_db < backup.sql

# Run migrations
docker-compose exec user-service python manage.py migrate
```

### Out of Disk Space

```bash
# Check disk usage
docker system df

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused containers
docker container prune

# Complete cleanup
docker system prune -a --volumes
```

## Monitoring in Production

```bash
# Set up cron job for health checks (Linux/Mac)
# Add to crontab: crontab -e
*/5 * * * * curl -f http://localhost:8000/health || echo "Service unhealthy" | mail -s "Alert" admin@example.com

# Monitor logs in real-time
docker-compose -f docker-compose.prod.yml logs -f | tee production.log

# Check container uptime
docker-compose -f docker-compose.prod.yml ps

# Monitor resource usage
watch docker stats user-service-app
```
