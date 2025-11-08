import { Link } from 'react-router-dom'

function Contact() {
  const handleSubmit = (e) => {
    e.preventDefault()
    alert('Form submitted! (This is just a demo)')
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-12" data-nav-id="contact-header">
        <h1 className="text-4xl font-bold mb-4 text-gray-800" data-nav-id="contact-title">
          Get in Touch
        </h1>
        <p className="text-xl text-gray-600" data-nav-id="contact-subtitle">
          Have questions? We'd love to hear from you!
        </p>
      </div>

      {/* Contact Form */}
      <div className="grid md:grid-cols-2 gap-8">
        <section className="bg-white p-8 rounded-lg shadow-md" data-nav-id="contact-form-section">
          <h2 className="text-2xl font-bold mb-6 text-gray-800" data-nav-id="form-heading">
            Send us a Message
          </h2>
          <form onSubmit={handleSubmit} data-nav-id="contact-form">
            <div className="mb-4">
              <label 
                htmlFor="name" 
                className="block text-gray-700 font-semibold mb-2"
                data-nav-id="name-label"
              >
                Name
              </label>
              <input
                type="text"
                id="name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your name"
                data-nav-id="name-input"
              />
            </div>
            <div className="mb-4">
              <label 
                htmlFor="email" 
                className="block text-gray-700 font-semibold mb-2"
                data-nav-id="email-label"
              >
                Email
              </label>
              <input
                type="email"
                id="email"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
                data-nav-id="email-input"
              />
            </div>
            <div className="mb-6">
              <label 
                htmlFor="message" 
                className="block text-gray-700 font-semibold mb-2"
                data-nav-id="message-label"
              >
                Message
              </label>
              <textarea
                id="message"
                rows="5"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your message..."
                data-nav-id="message-input"
              ></textarea>
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
              data-nav-id="submit-button"
            >
              Send Message
            </button>
          </form>
        </section>

        {/* Contact Info */}
        <section data-nav-id="contact-info-section">
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-8 rounded-lg shadow-md mb-6" data-nav-id="info-card">
            <h2 className="text-2xl font-bold mb-6" data-nav-id="info-heading">
              Contact Information
            </h2>
            <div className="space-y-4">
              <div className="flex items-center" data-nav-id="email-info">
                <span className="text-2xl mr-4">📧</span>
                <div>
                  <p className="font-semibold">Email</p>
                  <p>demo@voicenav.com</p>
                </div>
              </div>
              <div className="flex items-center" data-nav-id="location-info">
                <span className="text-2xl mr-4">📍</span>
                <div>
                  <p className="font-semibold">Location</p>
                  <p>MBZUAI, Abu Dhabi</p>
                </div>
              </div>
              <div className="flex items-center" data-nav-id="github-info">
                <span className="text-2xl mr-4">💻</span>
                <div>
                  <p className="font-semibold">GitHub</p>
                  <p>github.com/your-repo</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded" data-nav-id="voice-tip">
            <h3 className="font-bold text-yellow-800 mb-2">💡 Voice Tip</h3>
            <p className="text-yellow-700">
              Try saying "Fill the form with my name John" (Phase 4 feature - coming soon!)
            </p>
          </div>
        </section>
      </div>

      {/* Navigation */}
      <div className="mt-12" data-nav-id="contact-navigation">
        <Link 
          to="/about"
          className="text-blue-600 hover:text-blue-800 font-semibold"
          data-nav-id="back-to-about-link"
        >
          ← Back to About
        </Link>
      </div>
    </div>
  )
}

export default Contact

