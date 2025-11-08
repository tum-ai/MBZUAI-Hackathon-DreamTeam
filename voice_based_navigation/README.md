# Voice-Based Navigation Demo - Phase 1

A proof-of-concept for voice-controlled website navigation using Whisper API and GPT-4.

## 🎯 What This Demonstrates

- **Voice Input**: Record voice commands using browser microphone
- **Speech-to-Text**: Transcribe audio using OpenAI's Whisper API
- **Intent Understanding**: Use GPT-4 to parse user commands and generate actions
- **Action Execution**: Programmatically navigate and interact with the website
- **Visual Feedback**: Real-time action history and element highlighting

## 🏗️ Architecture

```
Voice Input → Whisper API → GPT-4 Agent → Action Executor → DOM Manipulation
                ↓              ↓              ↓
            Transcript    JSON Action    Visual Feedback
```

### Key Concepts

1. **data-nav-id Attributes**: Every interactive element has a unique `data-nav-id` for reliable targeting
2. **DOM Snapshot**: Captures current page state before each command
3. **Action Schema**: Structured JSON format for navigation actions
4. **Deterministic Execution**: Same command → same action → same result

## 📦 Setup

### Prerequisites

- Node.js 18+ and npm
- OpenAI API key (for Whisper and GPT-4)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to `.env`:
```
VITE_OPENAI_API_KEY=sk-your-key-here
```

### Running

```bash
npm run dev
```

The app will open at http://localhost:3000

## 🎤 How to Use

1. **Click the microphone button** at the bottom of the page
2. **Speak your command** (e.g., "Go to About page")
3. **Watch the action execute** - the page will navigate automatically
4. **View action history** in the feedback panel (top-right)

### Example Commands

**Phase 1 - Basic Navigation:**
- "Go to About" → Navigates to About page
- "Take me to Contact" → Navigates to Contact page
- "Go to Home" → Navigates to Home page
- "Scroll down" → Scrolls down the page
- "Scroll to top" → Scrolls to top of page

**Phase 2 - Multi-Step & Sections:**
- "Show me testimonials" → Navigates to home + scrolls to testimonials section
- "Go to the roadmap" → Navigates to about + scrolls to roadmap section
- "Show me the FAQ" → Navigates to about + scrolls to FAQ section
- "Take me to the contact form" → Navigates to contact + scrolls to form
- "Show me how it works" → Scrolls to how-it-works section (if on home page)

**Phase 4 - Form Interactions (NEW!):**
- "Fill the name field with John Smith" → Types into name input
- "Enter my email as john@example.com" → Types into email field
- "Fill the contact form with name John and email john@test.com" → Multi-field form filling
- "Type hello world in the message field" → Types into textarea
- "Submit the form" → Submits the contact form
- "Clear the name field" → Clears an input field

## 🧩 Project Structure

```
src/
├── components/
│   ├── Navigation.jsx          # Top navigation bar
│   ├── VoiceControl.jsx        # Voice input UI and controller
│   └── ActionFeedback.jsx      # Action history display
├── pages/
│   ├── Home.jsx                # Home page
│   ├── About.jsx               # About page
│   └── Contact.jsx             # Contact page
├── services/
│   ├── whisper.js              # Whisper API integration
│   ├── llmAgent.js             # GPT-4 agent for intent parsing
│   └── actionExecutor.js       # Executes navigation actions
├── utils/
│   └── domSnapshot.js          # Captures page state
├── context/
│   └── VoiceContext.jsx        # React context for voice state
└── App.jsx                     # Main app component
```

## 🔧 Technical Details

### Action Schema

The LLM agent outputs structured JSON actions:

**Navigate Action:**
```json
{
  "action": "navigate",
  "targetId": "nav-about-link",
  "reasoning": "User wants to go to About page"
}
```

**Scroll Action:**
```json
{
  "action": "scroll",
  "direction": "down",
  "amount": 500,
  "reasoning": "User wants to scroll down"
}
```

**ScrollToElement Action (Phase 2):**
```json
{
  "action": "scrollToElement",
  "targetId": "testimonials-section",
  "reasoning": "User wants to see testimonials"
}
```

**Wait Action (Phase 2):**
```json
{
  "action": "wait",
  "duration": 500,
  "reasoning": "Wait for page load"
}
```

**Multi-Step Sequence (Phase 2):**
```json
[
  {
    "action": "navigate",
    "targetId": "nav-home-link"
  },
  {
    "action": "wait",
    "duration": 500
  },
  {
    "action": "scrollToElement",
    "targetId": "testimonials-section"
  }
]
```

**Error Action:**
```json
{
  "action": "error",
  "message": "Cannot find that element",
  "reasoning": "No matching element on page"
}
```

### DOM Snapshot Format

```javascript
{
  elements: [
    {
      navId: "nav-about-link",
      tagName: "a",
      text: "About",
      isVisible: true,
      position: { top: 20, left: 100, isInViewport: true }
    }
  ],
  currentUrl: "/about",
  scrollY: 0,
  viewportHeight: 900
}
```

## 🚀 Phase 1 Success Criteria ✅

- [x] Multi-page React website with navigation
- [x] Voice recording with microphone access
- [x] Whisper API integration for transcription
- [x] GPT-4 agent for intent understanding
- [x] Action executor for navigation
- [x] Visual feedback with action history
- [x] Element highlighting before actions

## 🎯 Phase 2 Success Criteria ✅

- [x] Extended pages with scrollable sections
- [x] Multi-step action sequences support
- [x] New action types (scrollToElement, wait)
- [x] LLM agent plans complex multi-step actions
- [x] Visual feedback shows all steps in sequence
- [x] Section-aware navigation ("show me testimonials")

## 🎉 Phase 4 Success Criteria ✅

- [x] Voice-based text input (type action)
- [x] Form field focusing (focus action)
- [x] Form submission (submit action)
- [x] Input clearing (clear action)
- [x] Multi-field form filling with sequences
- [x] Visual feedback shows typed text
- [x] HTML5 validation support

## 📈 Next Phases

### Phase 3: DOM Context Awareness
- Disambiguation ("which button?")
- Spatial reasoning ("the button at the top")
- Clarification questions
- Context-aware suggestions

### Phase 5: Advanced Features
- Undo/redo functionality
- Voice feedback (text-to-speech)
- Continuous listening mode
- Session memory

## 🐛 Troubleshooting

### Microphone not working
- Ensure you've granted microphone permission
- Check browser console for errors
- Try HTTPS (some browsers require secure context)

### API errors
- Verify your `.env` file has the correct API key
- Check OpenAI API quota/billing
- Look at browser console for detailed error messages

### Actions not executing
- Check that elements have `data-nav-id` attributes
- Verify the LLM response is valid JSON
- Check browser console for execution errors

## 🔒 Security Notes

- API key is exposed in client-side code (development only)
- For production, use a backend proxy for API calls
- Implement rate limiting and user authentication

## 📝 License

MIT - Built for MBZUAI Hackathon

