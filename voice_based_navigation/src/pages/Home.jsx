import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section 
        className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-12 mb-12"
        data-nav-id="hero-section"
      >
        <h1 className="text-5xl font-bold mb-4" data-nav-id="hero-title">
          Welcome to Voice Navigation Demo
        </h1>
        <p className="text-xl mb-8" data-nav-id="hero-subtitle">
          Control this website using only your voice. Try saying "Go to About" or "Show me Contact"
        </p>
        <button 
          className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
          data-nav-id="hero-cta-button"
          onClick={() => alert('CTA clicked!')}
        >
          Get Started
        </button>
      </section>

      {/* Features Section */}
      <section className="mb-12" data-nav-id="features-section">
        <h2 className="text-3xl font-bold mb-6 text-gray-800" data-nav-id="features-heading">
          Features
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md" data-nav-id="feature-card-1">
            <div className="text-4xl mb-4">🎤</div>
            <h3 className="text-xl font-semibold mb-2">Voice Control</h3>
            <p className="text-gray-600">Navigate the entire website using natural language commands</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md" data-nav-id="feature-card-2">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI Powered</h3>
            <p className="text-gray-600">LLM agent understands your intent and executes actions</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md" data-nav-id="feature-card-3">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-2">Real-time</h3>
            <p className="text-gray-600">Instant feedback and smooth navigation experience</p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="mb-12 bg-gradient-to-br from-purple-50 to-blue-50 p-8 rounded-lg" data-nav-id="how-it-works-section">
        <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center" data-nav-id="how-it-works-heading">
          How It Works
        </h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center" data-nav-id="step-speak">
            <div className="bg-blue-500 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              1
            </div>
            <h3 className="font-semibold text-lg mb-2">Speak</h3>
            <p className="text-gray-600 text-sm">Click the mic and say your command</p>
          </div>
          <div className="text-center" data-nav-id="step-understand">
            <div className="bg-purple-500 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              2
            </div>
            <h3 className="font-semibold text-lg mb-2">Understand</h3>
            <p className="text-gray-600 text-sm">AI analyzes your intent</p>
          </div>
          <div className="text-center" data-nav-id="step-act">
            <div className="bg-indigo-500 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              3
            </div>
            <h3 className="font-semibold text-lg mb-2">Act</h3>
            <p className="text-gray-600 text-sm">Actions execute automatically</p>
          </div>
          <div className="text-center" data-nav-id="step-see">
            <div className="bg-pink-500 text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              4
            </div>
            <h3 className="font-semibold text-lg mb-2">See</h3>
            <p className="text-gray-600 text-sm">Watch the page respond</p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="mb-12" data-nav-id="testimonials-section">
        <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center" data-nav-id="testimonials-heading">
          What People Say
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md" data-nav-id="testimonial-1">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                JD
              </div>
              <div className="ml-3">
                <p className="font-semibold">John Doe</p>
                <p className="text-sm text-gray-500">Developer</p>
              </div>
            </div>
            <p className="text-gray-600 italic">"This is the future of web interaction! No more clicking around."</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md" data-nav-id="testimonial-2">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                SA
              </div>
              <div className="ml-3">
                <p className="font-semibold">Sarah Ahmed</p>
                <p className="text-sm text-gray-500">Designer</p>
              </div>
            </div>
            <p className="text-gray-600 italic">"Accessibility game-changer. Voice navigation is so intuitive!"</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md" data-nav-id="testimonial-3">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                MK
              </div>
              <div className="ml-3">
                <p className="font-semibold">Mike Kumar</p>
                <p className="text-sm text-gray-500">Product Manager</p>
              </div>
            </div>
            <p className="text-gray-600 italic">"Perfect for hands-free browsing. The AI understands exactly what I want."</p>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="mb-12 bg-white p-8 rounded-lg shadow-md" data-nav-id="use-cases-section">
        <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center" data-nav-id="use-cases-heading">
          Use Cases
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="flex items-start" data-nav-id="use-case-accessibility">
            <div className="text-3xl mr-4">♿</div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Accessibility</h3>
              <p className="text-gray-600">Enable users with mobility or vision impairments to navigate effortlessly</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="use-case-multitask">
            <div className="text-3xl mr-4">🎯</div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Multitasking</h3>
              <p className="text-gray-600">Browse while cooking, exercising, or doing other activities</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="use-case-speed">
            <div className="text-3xl mr-4">⚡</div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Speed</h3>
              <p className="text-gray-600">Navigate faster than clicking - just say where you want to go</p>
            </div>
          </div>
          <div className="flex items-start" data-nav-id="use-case-innovation">
            <div className="text-3xl mr-4">🚀</div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Innovation</h3>
              <p className="text-gray-600">Next-gen UI/UX that feels like science fiction</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-100 p-8 rounded-lg text-center" data-nav-id="cta-section">
        <h2 className="text-3xl font-bold mb-4 text-gray-800" data-nav-id="cta-heading">
          Ready to Try?
        </h2>
        <p className="text-gray-600 mb-6" data-nav-id="cta-text">
          Click the microphone button at the bottom of the page to start
        </p>
        <Link 
          to="/about"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          data-nav-id="cta-learn-more-button"
        >
          Learn More
        </Link>
      </section>
    </div>
  )
}

export default Home

