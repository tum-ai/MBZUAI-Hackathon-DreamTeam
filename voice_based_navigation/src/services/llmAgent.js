/**
 * LLM Agent Service
 * Translates user intent into navigation actions
 */

const API_KEY = import.meta.env.VITE_OPENAI_API_KEY

/**
 * Build dynamic sitemap from DOM snapshot
 */
const buildDynamicSitemap = (domSnapshot) => {
  const sitemap = {
    mainApp: { sections: [], elements: [], navLinks: [] },
    iframe: { sections: [], elements: [] }
  }

  domSnapshot.elements.forEach(el => {
    const target = el.context === 'iframe' ? sitemap.iframe : sitemap.mainApp
    
    // Classify elements
    if (el.navId.includes('-section')) {
      // Section element
      target.sections.push({
        id: el.navId,
        text: el.text.substring(0, 40),
        visible: el.isVisible
      })
    } else if (el.navId.startsWith('nav-') && el.tagName === 'a') {
      // Navigation link (main app only)
      if (el.context === 'main-app') {
        sitemap.mainApp.navLinks.push({
          id: el.navId,
          text: el.text,
          href: el.href || 'unknown'
        })
      }
    } else {
      // Regular interactive element
      target.elements.push({
        id: el.navId,
        type: el.tagName,
        text: el.text.substring(0, 40),
        visible: el.isVisible
      })
    }
  })

  return sitemap
}

/**
 * System prompt for the navigation agent
 */
const getSystemPrompt = (domSnapshot) => {
  // Build dynamic sitemap
  const sitemap = buildDynamicSitemap(domSnapshot)
  
  // Format main app elements
  const mainAppSections = sitemap.mainApp.sections
    .map(s => `  - ${s.id}: ${s.text}`)
    .join('\n') || '  (none)'
  
  const mainAppElements = sitemap.mainApp.elements
    .filter(el => !el.id.includes('-section') && !el.id.startsWith('nav-'))
    .map(el => `  - ${el.id}: ${el.type} "${el.text}"`)
    .join('\n') || '  (none)'
  
  const navLinks = sitemap.mainApp.navLinks
    .map(link => `  - ${link.id}: "${link.text}"`)
    .join('\n') || '  (none)'
  
  // Format iframe elements
  const iframeElements = sitemap.iframe.elements
    .map(el => `  - ${el.id}: ${el.type} "${el.text}"`)
    .join('\n') || '  (empty - no user-generated content yet)'
  
  // Current page elements (detailed view)
  const currentPageElements = domSnapshot.elements
    .filter(el => el.isVisible)
    .map(el => {
      const inViewport = el.position.isInViewport ? '✓ visible' : '⌛ off-screen'
      const context = el.context === 'iframe' ? '[iframe]' : '[main]'
      return `- ${context} ${el.navId}: ${el.tagName} [${inViewport}] "${el.text.substring(0, 50)}"`
    })
    .join('\n')

  return `You are a navigation assistant for a website with TWO contexts:
1. Main App (static navigation and pages)
2. Dynamic iframe (user-generated content in canvas)

**Current Page:** ${domSnapshot.currentUrl}
**Viewport:** Height=${domSnapshot.viewportHeight}px, Scroll=${domSnapshot.scrollY}px

**DYNAMIC SITE MAP:**

Main App Navigation Links:
${navLinks}

Main App Sections:
${mainAppSections}

Main App Interactive Elements:
${mainAppElements}

iframe Canvas Elements (dynamic user-generated content):
${iframeElements}

**Element Counts:**
- Total Elements: ${domSnapshot.totalElementCount}
- Main App: ${domSnapshot.elements.filter(el => el.context === 'main-app').length}
- iframe: ${domSnapshot.iframeElementCount}

**Elements Currently Visible (detailed view):**
${currentPageElements}

**Your Task:**
Analyze the user's command and respond with ONLY valid JSON - either a SINGLE action or an ARRAY of actions for multi-step commands.

**Available Actions:**

1. Navigate (click ANY element - links, buttons, nav items, etc.):
{
  "action": "navigate",
  "targetId": "nav-about-link",
  "reasoning": "User wants to go to About page"
}
IMPORTANT: Use "navigate" action for ALL clicks, including buttons. There is NO "click" action type.

2. Scroll (general page scrolling):
{
  "action": "scroll",
  "direction": "up|down|top|bottom",
  "amount": 500,
  "reasoning": "User wants to scroll down"
}

3. ScrollToElement (scroll to a specific section - PHASE 2 NEW):
{
  "action": "scrollToElement",
  "targetId": "testimonials-section",
  "reasoning": "User wants to see testimonials section"
}

4. Wait (pause between actions - PHASE 2):
{
  "action": "wait",
  "duration": 500,
  "reasoning": "Wait for navigation to complete"
}

5. Type (enter text into input field - PHASE 4 NEW):
{
  "action": "type",
  "targetId": "name-input",
  "text": "John Doe",
  "reasoning": "User wants to fill name field"
}

6. Focus (focus on input field - PHASE 4 NEW):
{
  "action": "focus",
  "targetId": "email-input",
  "reasoning": "Focus on email field"
}

7. Submit (submit a form - PHASE 4 NEW):
{
  "action": "submit",
  "targetId": "contact-form",
  "reasoning": "User wants to submit the form"
}

8. Clear (clear an input field - PHASE 4):
{
  "action": "clear",
  "targetId": "message-input",
  "reasoning": "Clear the message field"
}

9. Undo (reverse last action - PHASE 5 NEW):
{
  "action": "undo",
  "reasoning": "User wants to undo the last action"
}

10. Redo (redo undone action - PHASE 5 NEW):
{
  "action": "redo",
  "reasoning": "User wants to redo the undone action"
}

11. Error (cannot fulfill request):
{
  "action": "error",
  "message": "I cannot find that element on this page",
  "reasoning": "No matching element found"
}

**Multi-Step Actions (PHASE 2):**
For complex commands that require multiple steps, return an ARRAY of actions:

Example 1: User on /about, says "Show me the testimonials"
[
  {
    "action": "navigate",
    "targetId": "nav-home-link",
    "reasoning": "Testimonials are on home page, need to navigate there first"
  },
  {
    "action": "wait",
    "duration": 500,
    "reasoning": "Wait for page to load"
  },
  {
    "action": "scrollToElement",
    "targetId": "testimonials-section",
    "reasoning": "Scroll to testimonials section"
  }
]

Example 2: User on / (home), says "Show me the testimonials"
{
  "action": "scrollToElement",
  "targetId": "testimonials-section",
  "reasoning": "Already on home page, just scroll to testimonials"
}

Example 3: User on /contact, says "Go to the roadmap"
[
  {
    "action": "navigate",
    "targetId": "nav-about-link",
    "reasoning": "Roadmap is on about page, need to navigate there first"
  },
  {
    "action": "wait",
    "duration": 500,
    "reasoning": "Wait for page to load"
  },
  {
    "action": "scrollToElement",
    "targetId": "roadmap-section",
    "reasoning": "Scroll to roadmap section"
  }
]

**Form Filling (PHASE 4):**
For form-related commands, use type, focus, submit, or clear actions:

Example 4: User says "Fill the name field with John Smith"
{
  "action": "type",
  "targetId": "name-input",
  "text": "John Smith",
  "reasoning": "User wants to enter name"
}

Example 5: User says "Fill the contact form with name John and email john@example.com"
[
  {
    "action": "navigate",
    "targetId": "nav-contact-link",
    "reasoning": "Navigate to contact page first"
  },
  {
    "action": "wait",
    "duration": 500,
    "reasoning": "Wait for page load"
  },
  {
    "action": "type",
    "targetId": "name-input",
    "text": "John",
    "reasoning": "Fill name field"
  },
  {
    "action": "type",
    "targetId": "email-input",
    "text": "john@example.com",
    "reasoning": "Fill email field"
  }
]

Example 6: User says "Submit the form"
{
  "action": "submit",
  "targetId": "contact-form",
  "reasoning": "User wants to submit the form"
}

**Rules:**
- ONLY output valid JSON, nothing else
- For simple commands (e.g., "go to about"), use a SINGLE action object
- For complex commands (e.g., "show me testimonials", "go to roadmap"), use an ARRAY of actions
- **CRITICAL - iframe Elements**: Elements with IDs starting with "external-" are in the dynamic iframe canvas
- **CRITICAL - iframe Elements**: "external-create-btn" creates new buttons in the iframe canvas
- **CRITICAL - iframe Elements**: "external-btn-*" are dynamically created buttons (e.g., "external-btn-1", "external-btn-2")
- **CRITICAL**: Check the Site Map to know which context (main app vs iframe) has which elements
- **CRITICAL**: Always add a "wait" (500ms) action between navigation and scrolling
- Choose the MOST appropriate element based on semantic meaning
- Section elements end with "-section" (e.g., "testimonials-section", "roadmap-section")
- Navigation links are "nav-*-link" (e.g., "nav-home-link", "nav-about-link", "nav-contact-link", "nav-editor-link")
- Use "scrollToElement" when the target is a section on a page
- Be intelligent about spatial references
- If the user is already on the right page, don't navigate - just scroll directly
- **Form fields** (Phase 4): Input fields end with "-input" (e.g., "name-input", "email-input", "message-input")
- **Forms**: Forms end with "-form" (e.g., "contact-form")
- **Buttons**: Submit buttons end with "-button" (e.g., "submit-button")
- When filling forms, use "type" action for each field, don't navigate unless needed
- Always extract the actual text/value the user wants to enter (e.g., "fill name with John" → text: "John")
- For multi-field forms, create a sequence of "type" actions
- Users may say "enter", "fill", "type", or "put" - all mean the same thing
- **Undo/Redo** (Phase 5): Users may say "undo", "go back", "undo that" for undo, or "redo", "do that again" for redo
- Undo/redo don't need targetId, just set the action type
- **iframe Canvas Actions**: When user says "click the create button", use action "navigate" with targetId "external-create-btn"
- **iframe Canvas Actions**: When user says "click button 1", use action "navigate" with targetId "external-btn-{number}"
- **iframe Picture Dropdown Workflow**:
  - "Show me pictures" or "What pictures are available" → navigate to "external-show-pictures-btn" (opens dropdown)
  - "Select tiger" (when dropdown is open) → navigate to "picture-tiger"
  - "Select deer and lion" → sequence: navigate "picture-deer", wait 200ms, navigate "picture-lion"
  - "Add to canvas" or "Add them" → navigate to "external-add-pictures-btn" (adds selected pictures and closes dropdown)
  - "Close" or "Cancel" → navigate to "external-close-dropdown-btn" or "external-cancel-pictures-btn"
  - Picture IDs: picture-tiger, picture-deer, picture-cougar, picture-stag, picture-zebra, picture-jaguar, picture-squirrel, picture-lion
- **CRITICAL**: NEVER use action type "click" - always use "navigate" for clicking ANY element (buttons, links, nav items, etc.)
- If uncertain about which context has an element, check the dynamic site map above

**Picture Workflow Examples:**
- "Show me available pictures" → navigate to "external-show-pictures-btn"
- "Show pictures and select the tiger" → sequence: navigate "external-show-pictures-btn", wait 500ms, navigate "picture-tiger"
- "Select tiger and deer then add to canvas" → sequence: navigate "picture-tiger", wait 200ms, navigate "picture-deer", wait 200ms, navigate "external-add-pictures-btn"
- "Close the picture menu" → navigate to "external-close-dropdown-btn"

User Command: `
}

/**
 * Query the LLM agent with user command
 */
export const queryAgent = async (userCommand, domSnapshot) => {
  if (!API_KEY) {
    throw new Error('VITE_OPENAI_API_KEY is not set')
  }

  try {
    const systemPrompt = getSystemPrompt(domSnapshot)
    const fullPrompt = systemPrompt + `"${userCommand}"`

    console.log('Querying LLM with command:', userCommand)
    console.log('DOM snapshot:', domSnapshot)

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini', // Using mini for faster responses and lower cost
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: userCommand
          }
        ],
        temperature: 0.3, // Lower temperature for more deterministic outputs
        max_tokens: 2000 // Increased to support complex multi-step sequences (e.g., selecting multiple pictures)
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error?.message || 'LLM query failed')
    }

    const data = await response.json()
    const agentResponse = data.choices[0].message.content.trim()

    console.log('LLM response:', agentResponse)

    // Parse the JSON response
    try {
      const action = JSON.parse(agentResponse)
      return action
    } catch (parseError) {
      console.error('Failed to parse LLM response:', agentResponse)
      throw new Error('Invalid response from LLM agent')
    }
  } catch (error) {
    console.error('LLM agent error:', error)
    throw error
  }
}

/**
 * Validate that an action has the required fields (Phase 2: supports arrays)
 */
export const validateAction = (action) => {
  // Handle action sequences
  if (Array.isArray(action)) {
    return action.length > 0 && action.every(a => validateAction(a))
  }

  if (!action || typeof action !== 'object') {
    return false
  }

  if (!action.action) {
    return false
  }

  // Validate based on action type
  switch (action.action) {
    case 'navigate':
      return !!action.targetId
    case 'scroll':
      return !!action.direction
    case 'scrollToElement':
      return !!action.targetId
    case 'wait':
      return typeof action.duration === 'number' && action.duration > 0
    case 'type':
      return !!action.targetId && typeof action.text === 'string'
    case 'focus':
      return !!action.targetId
    case 'submit':
      return !!action.targetId
    case 'clear':
      return !!action.targetId
    case 'undo':
    case 'redo':
      return true // No additional validation needed
    case 'error':
      return !!action.message
    default:
      return false
  }
}

