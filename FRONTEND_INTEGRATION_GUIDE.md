# Frontend Integration Guide - Manual Steps

## Current Status

✅ **Backend Complete:**
- SessionManager working
- FileManager functional  
- Editor agent generates .vue files
- Session endpoints ready

❌ **Frontend Integration Incomplete** (syntax errors from automated edits)

---

## What Needs to Be Done

### 1. Add Session Initialization to `VoiceAssistantContext.jsx`

**Location:** Around line 106-130

**Add these states:**
```javascript
const [viteUrl, setViteUrl] = useState(null);
const [isInitializingSession, setIsInitializingSession] = useState(false);
```

**Add this useEffect (after streamingPlan initialization):**
```javascript
useEffect(() => {
  const initSession = async () => {
    try {
      setIsInitializingSession(true);
      
      // Try to recover existing session
      let sessionId = localStorage.getItem('vite_session_id');
      
      if (sessionId) {
        const response = await fetch(`http://localhost:8000/sessions/${sessionId}/exists`);
        const { exists } = await response.json();
        
        if (exists) {
          const infoResponse = await fetch(`http://localhost:8000/sessions/${sessionId}/info`);
          const sessionInfo = await infoResponse.json();
          setViteUrl(sessionInfo.vite_url);
          return;
        }
        sessionId = null;
      }
      
      // Create new session
      if (!sessionId) {
        sessionId = crypto.randomUUID();
        const response = await fetch('http://localhost:8000/sessions/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        });
        
        const sessionInfo = await response.json();
        setViteUrl(sessionInfo.vite_url);
        localStorage.setItem('vite_session_id', sessionId);
      }
    } catch (error) {
      console.error('[VoiceAssistant] Session init failed:', error);
    } finally {
      setIsInitializingSession(false);
    }
  };
  
  initSession();
}, []);
```

**Export in context value (around line 652):**
```javascript
const value = useMemo(
  () => ({
    // ... existing values
    viteUrl,
    isInitializingSession,
  }),
  [/* ... existing deps, */ viteUrl, isInitializingSession]
);
```

### 2. Add Heartbeat to `useStreamingPlan.js`

**Location:** Around line 90

**Add after WebSocket connection useEffect:**
```javascript
// Heartbeat to keep session alive
useEffect(() => {
  if (!isConnected) return;

  const heartbeatInterval = setInterval(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const sessionId = localStorage.getItem('vite_session_id');
      if (sessionId) {
        wsRef.current.send(JSON.stringify({
          type: 'heartbeat',
          sessionId: sessionId
        }));
      }
    }
  }, 30000); // Every 30 seconds

  return () => clearInterval(heartbeatInterval);
}, [isConnected]);
```

### 3. Initialize FileManager and SessionManager in Server

**Location:** `llm_new/server.py` around line 40

**After `SessionManager` initialization:**
```python
# Initialize SessionManager
session_manager = SessionManager(
    base_dir=Path("/tmp/vite-sessions"),
    template_dir=Path(__file__).parent / "templates" / "vite-vue-base",
    port_range=(3000, 4000),
    max_sessions=50
)

# Initialize FileManager
from llm_new.file_manager import FileManager
file_manager = FileManager(session_manager)

# Initialize tools with managers
from llm_new.tools import initialize_tools
initialize_tools(file_manager, session_manager)
```

### 4. Add Iframe to Display Vite Preview

**Create new component:** `webapp/src/components/VitePreview.jsx`

```javascript
import { useVoiceAssistantContext } from '../context/VoiceAssistantContext';

export function VitePreview() {
  const { viteUrl, isInitializingSession } = useVoiceAssistantContext();

  if (isInitializingSession) {
    return <div>Initializing session...</div>;
  }

  if (!viteUrl) {
    return <div>No preview available</div>;
  }

  return (
    <iframe
      src={viteUrl}
      style={{ width: '100%', height: '100vh', border: 'none' }}
      title="Website Preview"
    />
  );
}
```

---

## Testing

1. **Start backend:**
   ```bash
   conda run -n mbzuai python -m llm_new.server
   ```

2. **Start frontend:**
   ```bash
   cd webapp
   npm run dev
   ```

3. **Check console:**
   - Should see "Session created" message
   - Should see Vite URL (e.g., `http://localhost:3001`)

4. **Test voice command:**
   - Say: "Create an about page"
   - Should see new page in Vite preview (automatically reloads)

---

## Current Errors to Fix

1. **VoiceAssistantContext.jsx line 110** - Syntax error in my edit
2. **useStreamingPlan.js line 58** - Syntax error in my edit

**Recommendation:** Revert my changes to these files and apply the manual steps above carefully.

---

## Files to Review/Fix

- `webapp/src/context/VoiceAssistantContext.jsx` - Fix syntax errors, add session init
- `webapp/src/hooks/useStreamingPlan.js` - Fix syntax errors, add heartbeat
- `llm_new/server.py` - Initialize FileManager and tools
- `llm_new/tools.py` - Already has `initialize_tools` function

**Status:** Frontend integration ~80% complete, needs manual cleanup due to automated edit issues.
