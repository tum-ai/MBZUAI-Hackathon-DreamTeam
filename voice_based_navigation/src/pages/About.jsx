import { Link } from 'react-router-dom'

function About() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-12" data-nav-id="about-header">
        <h1 className="text-4xl font-bold mb-4 text-gray-800" data-nav-id="about-title">
          About Voice Navigation
        </h1>
        <p className="text-xl text-gray-600" data-nav-id="about-subtitle">
          A proof of concept for voice-controlled web navigation
        </p>
      </div>

      {/* Architecture Section */}
      <section className="bg-white p-8 rounded-lg shadow-md mb-8" data-nav-id="architecture-section">
        <h2 className="text-3xl font-bold mb-4 text-gray-800" data-nav-id="architecture-heading">
          How It Works
        </h2>
        <div className="space-y-4 text-gray-700">
          <div className="flex items-start" data-nav-id="step-1">
            <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
              1
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Voice Capture</h3>
              <p>Your voice is captured and transcribed using Whisper API</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="step-2">
            <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
              2
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Intent Analysis</h3>
              <p>LLM agent analyzes your command and determines the appropriate action</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="step-3">
            <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
              3
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Action Execution</h3>
              <p>The action is executed programmatically in the browser</p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="bg-white p-8 rounded-lg shadow-md mb-8" data-nav-id="tech-stack-section">
        <h2 className="text-3xl font-bold mb-4 text-gray-800" data-nav-id="tech-stack-heading">
          Technology Stack
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="border-l-4 border-blue-500 pl-4" data-nav-id="tech-frontend">
            <h3 className="font-semibold text-lg mb-2">Frontend</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              <li>React with Vite</li>
              <li>React Router for navigation</li>
              <li>Tailwind CSS for styling</li>
            </ul>
          </div>
          <div className="border-l-4 border-purple-500 pl-4" data-nav-id="tech-ai">
            <h3 className="font-semibold text-lg mb-2">AI Services</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              <li>Whisper API for speech-to-text</li>
              <li>GPT-4 for intent understanding</li>
              <li>Custom action executor</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Future Roadmap Section */}
      <section className="bg-gradient-to-r from-purple-50 to-pink-50 p-8 rounded-lg mb-8" data-nav-id="roadmap-section">
        <h2 className="text-3xl font-bold mb-4 text-gray-800" data-nav-id="roadmap-heading">
          Roadmap
        </h2>
        <div className="space-y-4">
          <div className="flex items-start" data-nav-id="roadmap-phase1">
            <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0 font-bold">
              ✓
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Phase 1: Navigation (Completed)</h3>
              <p className="text-gray-600">Basic voice navigation and page routing</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="roadmap-phase2">
            <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0 font-bold">
              ⚡
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Phase 2: Multi-Step (In Progress)</h3>
              <p className="text-gray-600">Section scrolling and action sequences</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="roadmap-phase3">
            <div className="bg-gray-300 text-gray-700 rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0 font-bold">
              3
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Phase 3: Disambiguation (Next)</h3>
              <p className="text-gray-600">Ask clarifying questions when needed</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="roadmap-phase4">
            <div className="bg-gray-300 text-gray-700 rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0 font-bold">
              4
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-1">Phase 4: Form Interactions (Future)</h3>
              <p className="text-gray-600">Fill forms and input data via voice</p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="bg-white p-8 rounded-lg shadow-md mb-8" data-nav-id="team-section">
        <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center" data-nav-id="team-heading">
          Built By
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center" data-nav-id="team-member-1">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
              AI
            </div>
            <h3 className="font-semibold text-lg">Voice Team</h3>
            <p className="text-gray-600 text-sm">Voice capture & transcription</p>
          </div>
          <div className="text-center" data-nav-id="team-member-2">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
              LLM
            </div>
            <h3 className="font-semibold text-lg">Intelligence Team</h3>
            <p className="text-gray-600 text-sm">Intent understanding & planning</p>
          </div>
          <div className="text-center" data-nav-id="team-member-3">
            <div className="w-24 h-24 bg-gradient-to-br from-pink-400 to-red-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
              UX
            </div>
            <h3 className="font-semibold text-lg">Experience Team</h3>
            <p className="text-gray-600 text-sm">UI/UX & visual feedback</p>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded mb-8" data-nav-id="faq-section">
        <h2 className="text-2xl font-bold mb-4 text-gray-800" data-nav-id="faq-heading">
          Frequently Asked Questions
        </h2>
        <div className="space-y-4">
          <div data-nav-id="faq-1">
            <h3 className="font-semibold text-lg mb-1">How accurate is the voice recognition?</h3>
            <p className="text-gray-700">We use OpenAI's Whisper API, which has 95%+ accuracy for clear speech.</p>
          </div>
          <div data-nav-id="faq-2">
            <h3 className="font-semibold text-lg mb-1">Does it work offline?</h3>
            <p className="text-gray-700">Currently no, as we rely on cloud APIs. Offline support is on the roadmap.</p>
          </div>
          <div data-nav-id="faq-3">
            <h3 className="font-semibold text-lg mb-1">What languages are supported?</h3>
            <p className="text-gray-700">English for now, but Whisper supports 50+ languages. We'll expand soon.</p>
          </div>
        </div>
      </section>

      {/* Navigation */}
      <div className="flex justify-between items-center" data-nav-id="about-navigation">
        <Link 
          to="/"
          className="text-blue-600 hover:text-blue-800 font-semibold"
          data-nav-id="back-to-home-link"
        >
          ← Back to Home
        </Link>
        <Link 
          to="/contact"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          data-nav-id="go-to-contact-button"
        >
          Contact Us →
        </Link>
      </div>
    </div>
  )
}

export default About

