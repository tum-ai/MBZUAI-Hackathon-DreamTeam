# Quick Start: Cross-Origin iframe Voice Navigation

## 🚀 Get Started in 2 Minutes

### Step 1: Start iframe Server

```bash
cd /Users/jonas/MBZUAI-Hackathon/mvp/iframe_content_server
npm run dev
```

**Expected:** Server starts on http://localhost:3001

---

### Step 2: Start Main App

```bash
cd /Users/jonas/MBZUAI-Hackathon/mvp/voice_based_navigation
npm run dev
```

**Expected:** Server starts on http://localhost:3000

---

### Step 3: Test Voice Commands

Open http://localhost:3000/editor and try these commands:

1. **"Click the create button"**
   - ✅ Creates a button in the iframe canvas
   - Button appears with green background

2. **"Click button 1"**
   - ✅ Clicks the first created button
   - Alert pops up: "You clicked Button 1!"

3. **"Click the create button"** (again)
   - ✅ Creates a second button
   - Counter shows "Total: 2"

4. **"Click button 2"**
   - ✅ Clicks the second button

5. **"Go to home"**
   - ✅ Navigates back to home page

---

## ✅ Success Checklist

- [ ] iframe server running on port 3001
- [ ] Main app running on port 3000
- [ ] Console shows: "[iframe] postMessage listeners initialized"
- [ ] Console shows: "[Main] Combined snapshot: { total: X, iframe: Y }"
- [ ] "Click the create button" creates a button in iframe
- [ ] "Click button 1" triggers alert
- [ ] No errors in console

---

## 🐛 Troubleshooting

**Problem:** "iframe not found"
- **Solution:** Navigate to http://localhost:3000/editor

**Problem:** "iframe snapshot timeout"
- **Solution:** Check iframe server is running on port 3001
- **Test:** Visit http://localhost:3001 directly

**Problem:** Cross-origin errors
- **Solution:** Ensure iframe URL is exactly http://localhost:3001
- **Check:** Origin validation in `iframe_content_server/src/main.jsx`

**Problem:** LLM doesn't understand iframe commands
- **Solution:** Check console for combined DOM snapshot
- **Expected:** Should show `iframeElementCount >= 1`

---

## 📚 Full Documentation

- **Testing Guide:** `IFRAME_TESTING.md` (8 test scenarios)
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md` (architecture, data flow)
- **Architecture:** `ARCHITECTURE_NOTES.md` (how it relates to main project)

---

## 🎯 Key Concepts

- **"external-" prefix:** All iframe elements start with "external-"
- **postMessage:** Communication between main app and iframe
- **Dynamic sitemap:** Built from actual DOM on every request
- **Action routing:** Automatically routes to main app or iframe

---

## 🎤 More Voice Commands

### iframe Commands
- "Click the create button"
- "Click button 1"
- "Click external button 2"

### Main App Commands
- "Go to home"
- "Go to about"
- "Go to editor"
- "Show me testimonials"

### Multi-Step Commands
- "Go to editor and click the create button"
- "Go home and show me features"

---

## 🔧 Console Debugging

Monitor postMessage communication:

```javascript
window.addEventListener('message', (e) => {
  console.log('📩 Message:', e.origin, e.data)
})
```

Check combined DOM snapshot:

```javascript
// Run in browser console on /editor page
const snapshot = await window.__captureCombinedDOMSnapshot?.()
console.log('Snapshot:', snapshot)
```

---

## ✨ What You Built

You now have a working voice-first navigation system that:

- Controls main app pages via voice
- Controls iframe content via voice
- Dynamically generates sitemap from DOM
- Routes actions intelligently (main app vs iframe)
- Handles cross-origin communication securely
- Provides visual feedback for all actions

**Next:** Try saying "Click the create button" 5 times and then interact with all buttons via voice! 🎉

