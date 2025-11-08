# iframe Cross-Origin Navigation Testing Guide

## Setup

### 1. Start the iframe Server

```bash
cd /Users/jonas/MBZUAI-Hackathon/mvp/iframe_content_server
npm run dev
```

The iframe server should start on **http://localhost:3001**

### 2. Start the Main App

```bash
cd /Users/jonas/MBZUAI-Hackathon/mvp/voice_based_navigation
npm run dev
```

The main app should start on **http://localhost:3000**

### 3. Navigate to Editor Page

Open your browser to: **http://localhost:3000/editor**

---

## Test Scenarios

### ✅ Test 1: DOM Snapshot Capture

**Objective:** Verify that the main app can capture DOM elements from both contexts

**Steps:**
1. Open browser console (F12)
2. Navigate to /editor page
3. Click the microphone button (or just load the page)
4. Check console logs

**Expected Output:**
```
[Main] Requesting DOM snapshot from iframe...
[iframe] Received message: { type: 'DOM_SNAPSHOT_REQUEST' }
[iframe] Capturing DOM snapshot...
[iframe] Sending DOM snapshot: { elements: [...], source: 'iframe' }
[Main] Received iframe DOM snapshot: { elements: [...] }
[Main] Combined snapshot: { total: X, mainApp: Y, iframe: Z }
```

**Expected:** 
- `iframe` element count >= 1 (at least "external-create-btn")
- `mainApp` element count >= 10 (navigation, page elements)
- No errors in console

---

### ✅ Test 2: Create Button (Main → iframe)

**Objective:** Voice command from main app creates a button in the iframe

**Voice Command:** *"Click the create button"*

**Expected Behavior:**
1. LLM identifies targetId: `"external-create-btn"`
2. Action Router detects context: `iframe` (prefix "external-")
3. postMessage sent to iframe with action
4. iframe receives action and executes click
5. New button appears in iframe canvas
6. Canvas shows "Button 1"

**Console Logs:**
```
[VoiceControl] LLM action: { action: "navigate", targetId: "external-create-btn" }
[Router] Action targets iframe (prefix match): external-create-btn
[Router] → Routing to iframe: { action: "navigate", targetId: "external-create-btn" }
[iframe] Executing action: { action: "navigate", targetId: "external-create-btn" }
[iframe] Created new button: { id: "external-btn-1234567890", text: "Button 1" }
[Router] Received action result from iframe: { success: true, source: "iframe" }
```

**Visual Result:**
- Button appears in iframe canvas with green background
- Counter shows "Total: 1"
- Action Feedback panel shows success

---

### ✅ Test 3: Create Multiple Buttons

**Objective:** Create several buttons to test dynamic ID generation

**Voice Commands:**
1. *"Click the create button"*
2. *"Click the create button"*
3. *"Click the create button"*

**Expected:**
- Canvas shows: Button 1, Button 2, Button 3
- Each has unique `data-nav-id`: `external-btn-[timestamp]`
- Counter shows "Total: 3"
- All buttons are green

---

### ✅ Test 4: Click Dynamic Button (Main → iframe)

**Objective:** Click a dynamically created button

**Voice Command:** *"Click button 1"* or *"Click external button 1"*

**Expected Behavior:**
1. LLM identifies the first button ID (e.g., `external-btn-1234567890`)
2. Action Router routes to iframe
3. iframe highlights button with blue outline (1 second)
4. Alert pops up: "You clicked Button 1!"

**Console Logs:**
```
[VoiceControl] LLM action: { action: "navigate", targetId: "external-btn-1234567890" }
[Router] → Routing to iframe
[iframe] Clicked external-btn-1234567890 in iframe
```

---

### ✅ Test 5: Navigate Back to Main (iframe → Main)

**Objective:** Ensure main app navigation still works

**Voice Command:** *"Go to home"*

**Expected:**
1. LLM identifies: `nav-home-link` (main app context)
2. Action Router routes to main app (not iframe)
3. Navigates to home page
4. No errors

**Console Logs:**
```
[Router] Action targets main app: nav-home-link
[Router] → Routing to main app
```

---

### ✅ Test 6: Cross-Context Navigation

**Objective:** Navigate across pages and then interact with iframe

**Voice Commands:**
1. *"Go to home"*
2. *"Go to editor"*
3. *"Click the create button"*

**Expected:**
1. Navigates to home page (main app)
2. Navigates to editor page (main app)
3. Clicks create button in iframe
4. New button appears in iframe

---

### ✅ Test 7: Error Handling - Element Not Found

**Objective:** Test error handling for non-existent iframe elements

**Voice Command:** *"Click button 99"*

**Expected:**
- LLM tries to find `external-btn-99` or similar
- iframe returns error: "Element not found"
- Action Feedback shows error message
- No crashes

---

### ✅ Test 8: Multi-Step Action

**Objective:** Complex command with navigation + iframe interaction

**Voice Command:** *"Go to editor and click the create button"*

**Expected:**
1. Navigate to /editor (main app)
2. Wait 500ms
3. Click external-create-btn (iframe)
4. Button appears in canvas
5. Action Feedback shows sequence of 2-3 actions

---

## Debugging

### Check iframe Communication

Add this to browser console to monitor all postMessages:

```javascript
window.addEventListener('message', (e) => {
  console.log('📩 Message:', e.origin, e.data)
})
```

### Manual DOM Snapshot Request

Test communication manually:

```javascript
const iframe = document.querySelector('#dynamic-content-iframe')
iframe.contentWindow.postMessage({ 
  type: 'DOM_SNAPSHOT_REQUEST' 
}, 'http://localhost:3001')
```

### Manual Action Execution

Test action execution manually:

```javascript
const iframe = document.querySelector('#dynamic-content-iframe')
iframe.contentWindow.postMessage({ 
  type: 'EXECUTE_ACTION',
  action: {
    action: 'navigate',
    targetId: 'external-create-btn'
  }
}, 'http://localhost:3001')
```

### Check Routing Logic

Look for these console logs to verify routing:

- **"[Router] Action targets iframe (prefix match)"** → Correctly identified as iframe action
- **"[Router] → Routing to iframe"** → Sending to iframe
- **"[Router] → Routing to main app"** → Executing locally

### Common Issues

**Issue:** "iframe not found"
- **Solution:** Make sure you're on /editor page
- **Check:** `document.querySelector('#dynamic-content-iframe')` should return element

**Issue:** "iframe snapshot timeout"
- **Solution:** iframe server may not be running
- **Check:** Visit http://localhost:3001 directly - should show white page with "Create Button"

**Issue:** Cross-origin errors
- **Solution:** Ensure iframe is served from localhost:3001
- **Solution:** Check origin validation in main.jsx (should be http://localhost:3000)

**Issue:** LLM doesn't recognize external- elements
- **Solution:** Check LLM prompt includes iframe elements
- **Check:** Console log `domSnapshot.elements` - should show both contexts

---

## Expected Element IDs

### Main App Elements (context: 'main-app')
- `nav-home-link`, `nav-about-link`, `nav-contact-link`, `nav-editor-link`
- `editor-page`, `editor-title`, `editor-instructions`
- `iframe-container`, `dynamic-content-iframe`

### iframe Elements (context: 'iframe')
- `external-create-btn` (always present)
- `external-btn-{timestamp}` (dynamically created)
- `canvas-container` (the canvas div)
- `button-counter` (the counter display)

---

## Success Criteria

✅ **Phase 1 Complete** when:
- Main app can capture iframe DOM via postMessage
- Combined snapshot shows elements from both contexts
- No cross-origin errors in console

✅ **Phase 2 Complete** when:
- Voice command "Click the create button" creates a button in iframe
- Button appears with correct `external-btn-*` ID
- Action Feedback shows "routedTo: iframe"

✅ **Phase 3 Complete** when:
- Voice command "Click button 1" clicks the first dynamic button
- Alert appears confirming button click
- iframe element highlights with blue outline

✅ **Full Integration Complete** when:
- Can navigate between main app pages via voice
- Can navigate to /editor via voice
- Can create and click buttons in iframe via voice
- Can return to main app pages via voice
- Action Feedback correctly shows routing information (main-app vs iframe)
- No errors or timeouts in console

---

## Cleanup

After testing, stop both servers:

```bash
# Ctrl+C in both terminal windows
```

---

## Next Steps

After successful testing:
1. Add more iframe interactions (form filling, etc.)
2. Implement error recovery for failed postMessage
3. Add retry logic for timeout scenarios
4. Extend to support multiple iframes
5. Add WebSocket for real-time updates instead of postMessage polling

