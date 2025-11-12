# Redis Verification Guide

## ✅ How to Verify Redis is Working

### 1. **Health Check via Docker** (Quickest)

```bash
docker-compose ps
```

Look for `user-service-redis` with status `Up X seconds (healthy)`

---

### 2. **Redis CLI Ping Test**

```bash
docker exec user-service-redis redis-cli ping
```

**Expected Output:** `PONG`

---

### 3. **Django Health Endpoint**

```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "database": "connected"
}
```

---

### 4. **Test Redis Write/Read**

```bash
# Write a test value
docker exec user-service-redis redis-cli SET test_key "Hello Redis"

# Read it back
docker exec user-service-redis redis-cli GET test_key

# Delete test key
docker exec user-service-redis redis-cli DEL test_key
```

**Expected Output:**
- SET returns: `OK`
- GET returns: `"Hello Redis"`
- DEL returns: `(integer) 1`

---

### 5. **Check Redis Info**

```bash
docker exec user-service-redis redis-cli INFO server
```

Shows Redis server version, uptime, and configuration.

---

### 6. **Monitor Redis Commands** (Real-time)

```bash
docker exec user-service-redis redis-cli MONITOR
```

Shows all Redis commands in real-time. Press `Ctrl+C` to stop.

---

## 🔧 Troubleshooting

### Redis Container Not Starting

**Check logs:**
```bash
docker logs user-service-redis
```

**Common issues:**
- Configuration file errors (check `docker-compose.yml`)
- Port conflicts (ensure 6379 is available)
- Memory limits

### Redis Container Restarting

**Check status:**
```bash
docker-compose ps
docker inspect user-service-redis
```

### Connection Refused from Django

**Verify network:**
```bash
docker network inspect user-service_user-service-network
```

Ensure both `user-service-app` and `user-service-redis` are on the same network.

---

## 📊 Current Configuration

- **Image:** `redis:7-alpine`
- **Port:** `6379` (exposed to host)
- **Persistence:** AOF (Append-Only File) enabled
- **Memory Limit:** 256MB
- **Eviction Policy:** `allkeys-lru` (Least Recently Used)
- **Password:** None (local development only)

⚠️ **Production:** Add `--requirepass <strong_password>` to the Redis command in `docker-compose.yml`

---

## 🚀 Quick Start Commands

```bash
# Start all services
docker-compose up -d

# Check Redis health
docker exec user-service-redis redis-cli ping

# View Redis logs
docker logs user-service-redis -f

# Stop all services
docker-compose down
```

---

## ✨ Redis is Working When:

✅ Container status shows `(healthy)`  
✅ `redis-cli ping` returns `PONG`  
✅ Django `/health` endpoint shows `"redis": "connected"`  
✅ No restart loops in `docker-compose ps`  
✅ Application can cache and retrieve data
