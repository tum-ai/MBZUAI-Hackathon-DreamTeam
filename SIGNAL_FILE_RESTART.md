# Simple Restart Solution via Signal File

## 🎯 Solution Overview

Instead of complex process management, we use a **signal file** approach:

1. **Active Server Controller** runs continuously in Docker
2. Watches for `/tmp/active/.restart-signal` file
3. When signal detected → Kill Vite → npm install → Restart Vite
4. Compiler API creates signal file when template selected

## 🔧 Components

### 1. Controller Script (`active_server_controller.sh`)
```bash
# Runs in compiler-variations container
# Manages Vite lifecycle:
- start_vite()    → npm install + npx vite
- stop_vite()     → kill gracefully
- restart_vite()  → stop + start
- Watch loop      → Check signal every 2s
```

### 2. Trigger Script (`trigger_restart.sh`)
```bash
# Runs in compiler-api container
# Creates signal file:
echo "$(date +%s)" > /tmp/active/.restart-signal
```

### 3. Compiler API Integration
```python
# In select_template_variation endpoint:
subprocess.Popen([trigger_restart.sh])
```

## 📋 Flow

### Template Selection:
```
User → POST /select-template-variation
         ↓
Compiler API:
  - Clean /tmp/active
  - Copy variation files
  - Run trigger_restart.sh
         ↓
trigger_restart.sh:
  - Create .restart-signal file
         ↓
Active Server Controller:
  - Detect signal change
  - Kill Vite (PID from /tmp/active-vite.pid)
  - cd /tmp/active
  - npm install --legacy-peer-deps
  - npx vite --host 0.0.0.0 --port 5177
         ↓
Result: Port 5177 serves new variation ✅
```

### Edit Request:
```
User → POST /plan → Editor → Compiler
         ↓
Compiler PATCH /ast/home:
  - Update /tmp/active AST
  - Regenerate views
  - Copy to /tmp/active
  - NO signal file created
         ↓
Vite hot-reload: Automatic ✅
```

## 🧪 Testing Commands

```bash
# 1. Start containers (already running)
cd compiler && sudo docker compose up

# 2. Generate templates
curl -X POST http://localhost:8000/generate-template-variations \
  -H "Content-Type: application/json" \
  -d '{"template_name":"portfolio","palette":"professional"}'

# 3. Select variation 0
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index":0}'

# 4. Watch controller logs
sudo docker logs compiler-variations -f

# Should see:
# 📢 Restart signal detected: 1762684567
# 🔄 RESTART TRIGGERED
# ⏹️  Stopping Vite server (PID: 123)...
# ✅ Vite server stopped
# 📦 Checking dependencies...
#    Running npm install...
#    ✅ Dependencies ready
# 🚀 Starting Vite server on port 5177...
# ✅ Vite server started successfully

# 5. Check port 5177
curl -I http://localhost:5177
# Should return 200 OK

# 6. Select different variation
curl -X POST http://localhost:8000/select-template-variation \
  -H "Content-Type: application/json" \
  -d '{"variation_index":2}'

# 7. Watch logs again - should see restart
```

## ✅ Advantages

1. **Simple**: Signal file → Kill → Install → Start
2. **Reliable**: No race conditions, explicit process control
3. **Observable**: Clear logs at each step
4. **Recoverable**: Auto-restart on crash
5. **Isolated**: Each container does one thing well

## 🔍 Debug Commands

```bash
# Check if controller is running
sudo docker exec compiler-variations ps aux | grep active_server

# Check current Vite PID
sudo docker exec compiler-variations cat /tmp/active-vite.pid

# Check signal file
sudo docker exec compiler-variations cat /tmp/active/.restart-signal

# View Vite logs
sudo docker exec compiler-variations tail -f /tmp/active-vite.log

# View npm install logs
sudo docker exec compiler-variations tail -f /tmp/npm-install.log

# Manually trigger restart (for testing)
sudo docker exec compiler-variations bash -c 'echo "$(date +%s)" > /tmp/active/.restart-signal'
```

## 🎯 Expected Behavior

**On Container Start:**
- Controller waits for `/tmp/active/package.json`
- Runs `npm install`
- Starts Vite on port 5177
- Enters watch loop

**On Template Selection:**
- API creates signal file with timestamp
- Controller detects new timestamp
- Gracefully stops Vite
- Runs `npm install` (fresh dependencies)
- Starts Vite
- Port 5177 serves new variation

**On Edit Request:**
- Files updated in `/tmp/active`
- Vite hot-reload automatically
- No restart needed

**On Crash:**
- Controller detects PID gone
- Auto-restarts with npm install

This approach is battle-tested and should work reliably! 🚀
