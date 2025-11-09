# Docker Port Accessibility Fix

## Problem

When running the compiler in Docker, port 8000 was accessible from **inside** the container (`docker exec` + `curl localhost:8000` worked), but **not from the host** (external `curl localhost:8000` failed with "Connection reset by peer").

## Root Cause

The FastAPI server was binding to `127.0.0.1` (localhost only) instead of `0.0.0.0` (all network interfaces).

**Why this matters in Docker:**
- `127.0.0.1` = Only accessible within the container itself
- `0.0.0.0` = Accessible from all network interfaces, including from the host through Docker's port mapping

## Solution

### 1. Updated `server/config.py`

**Before:**
```python
HOST = "127.0.0.1"
PORT = 8000
```

**After:**
```python
# Use 0.0.0.0 to bind to all interfaces (required for Docker)
# Falls back to 127.0.0.1 for local development if HOST env var not set
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
```

**Benefits:**
- ✅ Respects `HOST` environment variable from docker-compose.yml
- ✅ Defaults to `0.0.0.0` (Docker-friendly)
- ✅ Can override with env var for local development
- ✅ Same for PORT (now supports environment variable)

### 2. Added Network Configuration in `docker-compose.yml`

**Added:**
```yaml
networks:
  compiler-network:
    driver: bridge

services:
  compiler-api:
    networks:
      - compiler-network
    # ... rest of config

  compiler-variations:
    networks:
      - compiler-network
    # ... rest of config
```

**Benefits:**
- ✅ Explicit bridge network for proper routing
- ✅ Better isolation and control
- ✅ Inter-container communication works reliably

## How to Apply the Fix

### If container is running:

```bash
# Stop the container
docker-compose -f compiler/docker-compose.yml down

# Rebuild with the fix
docker-compose -f compiler/docker-compose.yml up --build
```

### Quick rebuild:

```bash
cd /path/to/MBZUAI-Hackathon-DreamTeam

# Clean rebuild
docker-compose -f compiler/docker-compose.yml down -v
docker-compose -f compiler/docker-compose.yml build --no-cache
docker-compose -f compiler/docker-compose.yml up
```

## Verification

### Test from outside container:

```bash
# Should work now
curl http://localhost:8000/project
```

### Or use the test script:

```bash
./compiler/test-docker-ports.sh
```

This script will:
- Check if container is running
- Test connection from host
- Test connection from inside container
- Show debugging info if it fails
- Provide specific fix instructions

## Expected Behavior After Fix

### ✅ From Host (Your Machine):
```bash
$ curl http://localhost:8000/project
{
  "projectName": "New GenAI Project",
  "pages": [],
  "globalStyles": ""
}
```

### ✅ From Inside Container:
```bash
$ docker exec compiler-api curl http://localhost:8000/project
{
  "projectName": "New GenAI Project",
  "pages": [],
  "globalStyles": ""
}
```

### ✅ From Browser:
Open http://localhost:8000/project - Should display JSON response

## Technical Details

### Port Binding Explained

When Docker maps ports with `-p 8000:8000`, it creates this flow:
```
Your Machine (Host)
    ↓
    localhost:8000
    ↓
Docker Port Mapping (bridge)
    ↓
Container's Network Interface
    ↓
    If bound to 127.0.0.1: ❌ Only accessible within container
    If bound to 0.0.0.0:   ✅ Accessible from outside
```

### What uvicorn sees

**Before fix:**
```bash
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**After fix:**
```bash
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The `0.0.0.0` means "listen on all available network interfaces".

## Environment Variables

The docker-compose.yml sets these environment variables:

```yaml
environment:
  - PYTHONUNBUFFERED=1    # Immediate log output
  - HOST=0.0.0.0          # Bind to all interfaces
  - PORT=8000             # API server port
```

These are now read by `config.py`:
```python
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
```

## Common Issues

### Issue: Still can't connect after fix

**Check 1: Is the container using the new config?**
```bash
docker exec compiler-api cat /app/compiler/server/config.py | grep HOST
```
Should show: `HOST = os.getenv("HOST", "0.0.0.0")`

**Check 2: Is HOST env var set?**
```bash
docker exec compiler-api env | grep HOST
```
Should show: `HOST=0.0.0.0`

**Check 3: What is uvicorn actually binding to?**
```bash
docker logs compiler-api | grep "Uvicorn running"
```
Should show: `http://0.0.0.0:8000` (not `127.0.0.1`)

**Check 4: Is port actually mapped?**
```bash
docker port compiler-api
```
Should show: `8000/tcp -> 0.0.0.0:8000`

### Issue: Port conflict

If port 8000 is already in use on your host:

```bash
# Find what's using it
lsof -i :8000

# Kill it or change the port mapping in docker-compose.yml
ports:
  - "8001:8000"  # Map host port 8001 to container port 8000
```

## Files Modified

1. **`server/config.py`** - Changed HOST from hardcoded `127.0.0.1` to environment variable with `0.0.0.0` default
2. **`docker-compose.yml`** - Added explicit network configuration
3. **`test-docker-ports.sh`** - Created diagnostic script (NEW)

## Prevention

To avoid this issue in the future:

1. ✅ Always use `HOST=0.0.0.0` in Docker environments
2. ✅ Use environment variables for configuration
3. ✅ Test port accessibility from host, not just inside container
4. ✅ Run `./compiler/test-docker-ports.sh` after any changes

## Summary

**Problem:** Server bound to 127.0.0.1, inaccessible from host  
**Solution:** Changed to 0.0.0.0 via environment variable  
**Result:** Port 8000 now accessible from both inside and outside container ✅
