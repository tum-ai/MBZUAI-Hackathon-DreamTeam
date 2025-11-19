# End-to-End Test Guide

## 🚀 All Servers Running

✅ **LLM Server**: http://localhost:8000  
✅ **Compiler API**: http://localhost:8000  
✅ **Template Variations**: http://localhost:5173-5177  
✅ **Main Webapp**: http://localhost:5178  

---

## 🧪 Browser-Based Testing Flow

### Step 1: Open the Webapp
Open your browser to: **http://localhost:5178**

### Step 2: Test Template Generation
Open browser console (F12) and run:

```javascript
// Generate 4 portfolio template variations
fetch('http://localhost:8000/generate-template-variations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    template_name: 'portfolio',
    palette: 'professional'
  })
})
.then(r => r.json())
.then(d => console.log('Template generated:', d))
```

### Step 3: Select a Template Variation
```javascript
// Select variation 0 (Professional) as active
fetch('http://localhost:8000/select-template-variation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    variation_index: 0
  })
})
.then(r => r.json())
.then(d => console.log('Template selected:', d))
```

### Step 4: View the Selected Template
Open new tab: **http://localhost:5177**  
You should see the Alex Chen portfolio with professional palette.

### Step 5: Test LLM Planning (Editor Flow)
```javascript
// Test Editor: Add a new button component
fetch('http://localhost:8000/plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'test-session-' + Date.now(),
    user_request: 'Add a contact button to the hero section'
  })
})
.then(r => r.json())
.then(d => {
  console.log('Plan response:', d);
  // The orchestrator will execute the plan automatically
})
```

### Step 6: Test Actor (Browser Action Flow)
```javascript
// Test Actor: Generate a scroll action
fetch('http://localhost:8000/plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'test-action-' + Date.now(),
    user_request: 'Scroll down to the projects section'
  })
})
.then(r => r.json())
.then(d => {
  console.log('Action plan:', d);
  // Action should be sent via WebSocket to frontend
})
```

### Step 7: Monitor WebSocket Messages
Open browser console and watch for:
- `[DomSnapshotBridge] Connected` - WebSocket active
- `[DomSnapshotBridge] Executing browser action:` - Actor commands received
- `[DomSnapshotBridge] Action executed:` - Success confirmation

---

## 🔍 Verification Checklist

### Template System
- [ ] Variations generated (check http://localhost:5173-5176)
- [ ] Active project selected (check http://localhost:5177)
- [ ] Portfolio renders with correct content

### LLM → Editor → Compiler
- [ ] /plan endpoint accepts requests
- [ ] Orchestrator routes to Editor
- [ ] Editor generates component
- [ ] JSON Patch POSTed to compiler
- [ ] Files copied to /tmp/active
- [ ] Changes visible on http://localhost:5177 (refresh if needed)

### LLM → Actor → Frontend
- [ ] /plan endpoint accepts action requests
- [ ] Orchestrator routes to Actor
- [ ] Actor generates action string
- [ ] Action sent via WebSocket
- [ ] DomSnapshotBridge receives message
- [ ] actionExecutor.js executes DOM action
- [ ] Visual feedback (highlight/scroll/click) occurs

---

## 🐛 Debugging Commands

### Check Server Logs
```bash
# LLM Server logs (terminal with python -m llm.server)
# Webapp logs (terminal with npm run dev)
# Docker logs:
sudo docker logs compiler-api -f
sudo docker logs compiler-variations -f
```

### Manual API Tests
```bash
# Test LLM health
curl http://localhost:8000/health

# Test Compiler health
curl http://localhost:8000/health

# Test template generation
curl -X POST http://localhost:8000/generate-template-variations \
  -H "Content-Type: application/json" \
  -d '{"template_name":"portfolio","palette":"professional"}'

# Test LLM plan
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test-123","user_request":"Add a button"}'
```

---

## 🎯 Success Criteria

**Full Integration Working** means:
1. ✅ Template variations load on ports 5173-5177
2. ✅ LLM /plan endpoint responds
3. ✅ Editor generates components → Compiler updates → Files visible
4. ✅ Actor generates actions → WebSocket → Frontend executes
5. ✅ No server crashes or connection errors
6. ✅ Browser console shows successful execution logs

---

## 🎬 Demo Script

For the hackathon demo:

1. **Show the webapp** - Open http://localhost:5178
2. **Generate templates** - Run Step 2 in console
3. **Show variations** - Open tabs for 5173-5176, show different palettes
4. **Select active** - Run Step 3, open 5177
5. **Voice command (simulated)** - "Add a contact button"
6. **Show LLM working** - Console logs from /plan
7. **Show result** - Refresh 5177, new button appears
8. **Action command** - "Scroll to projects"
9. **Show automation** - Watch page scroll automatically
10. **Celebrate** 🎉

---

**Current Status**: All servers running, ready for browser testing!
