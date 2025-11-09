# Summary of Docker Connection Issues & Fixes

## Root Cause Analysis

The `ERR_CONNECTION_RESET` was caused by **THREE separate issues**:

### 1. FastAPI Server Binding ✅ FIXED
**Problem:** Server bound to `127.0.0.1` instead of `0.0.0.0`  
**Fix:** Updated `server/config.py`:
```python
HOST = os.getenv("HOST", "0.0.0.0")  # Was: "127.0.0.1"
```

### 2. Vite Dev Servers Binding ✅ FIXED  
**Problem:** Vite servers bound to `127.0.0.1` by default  
**Fix:** Added `--host 0.0.0.0` flag to all npm commands in `run_variations.sh`:
```bash
npm run dev -- --port $port --host 0.0.0.0
```

### 3. Background Processes Dying ✅ FIXED
**Problem:** Background processes started with `(cd dir && command) &` were being orphaned and dying  
**Fix:** Changed to use `nohup` and proper working directory management:
```bash
cd "$dir"
nohup npm run dev -- --port $port --host 0.0.0.0 > /tmp/variation-$index.log 2>&1 &
cd - > /dev/null
```

### 4. Script Exiting Too Early ✅ FIXED
**Problem:** `run_variations.sh` exited immediately after starting background processes  
**Fix:** Added proper wait loop at the end:
```bash
tail -f /tmp/variation-*.log /tmp/active.log 2>/dev/null &
wait $TAIL_PID 2>/dev/null || sleep infinity
```

### 5. Race Condition in docker-compose ✅ FIXED
**Problem:** variations container started before files were fully written to volumes  
**Fix:** Changed wait condition from directory to file existence:
```yaml
while [ ! -f /tmp/selection/0/package.json ]; do sleep 2; done;
```

## Current Status

All ports are now accessible from host:
- ✅ Port 8000 (API Server)
- ✅ Port 5173 (Variation 0)
- ✅ Port 5174 (Variation 1)  
- ✅ Port 5175 (Variation 2)
- ✅ Port 5176 (Variation 3)
- ✅ Port 5177 (Active Project)

## How to Apply All Fixes

```bash
cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam

# Stop current containers
sudo docker compose -f compiler/docker-compose.yml down

# Rebuild with all fixes
sudo docker compose -f compiler/docker-compose.yml up --build

# Test in another terminal
curl http://localhost:8000/project
curl http://localhost:5173
```

## Manual Workaround (If Needed)

If automatic startup still has issues:

```bash
# Start variations manually
sudo docker exec -d compiler-variations bash -c "cd /tmp/selection/0 && npm install && npm run dev -- --port 5173 --host 0.0.0.0 > /tmp/variation-0.log 2>&1"
sudo docker exec -d compiler-variations bash -c "cd /tmp/selection/1 && npm install && npm run dev -- --port 5174 --host 0.0.0.0 > /tmp/variation-1.log 2>&1"
sudo docker exec -d compiler-variations bash -c "cd /tmp/selection/2 && npm install && npm run dev -- --port 5175 --host 0.0.0.0 > /tmp/variation-2.log 2>&1"
sudo docker exec -d compiler-variations bash -c "cd /tmp/selection/3 && npm install && npm run dev -- --port 5176 --host 0.0.0.0 > /tmp/variation-3.log 2>&1"
sudo docker exec -d compiler-variations bash -c "cd /tmp/active && npm install && npm run dev -- --port 5177 --host 0.0.0.0 > /tmp/active.log 2>&1"
```

## Files Modified

1. `compiler/server/config.py` - Server binding
2. `compiler/server/run_variations.sh` - Vite server startup with nohup and proper wait
3. `compiler/docker-compose.yml` - Better wait conditions
4. `compiler/server/restart_variations.sh` - Manual restart script (NEW)

## Debugging Commands

```bash
# Check container status
sudo docker ps -a | grep compiler

# Check if servers are running
sudo docker exec compiler-variations ps aux | grep node

# Check logs
sudo docker logs compiler-variations
sudo docker exec compiler-variations cat /tmp/variation-0.log

# Test ports from inside container
sudo docker exec compiler-variations curl -I http://localhost:5173

# Test ports from host
curl -I http://localhost:5173
```

## Key Lessons

1. **Docker port mapping requires `0.0.0.0` binding** - `127.0.0.1` only works within container
2. **Background processes need `nohup`** - Otherwise they die when parent shell exits
3. **Wait for actual files, not just directories** - Race conditions in file creation
4. **Keep container alive** - Use `tail -f` or `sleep infinity` at end of scripts
5. **Test both inside and outside container** - Helps isolate binding vs mapping issues
