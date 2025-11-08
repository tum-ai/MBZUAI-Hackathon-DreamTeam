function EditorPage() {
  return (
    <div className="editor-page" data-nav-id="editor-page">
      <h1 className="text-3xl font-bold mb-6" data-nav-id="editor-title">
        Dynamic Content Editor
      </h1>
      
      <div className="instructions bg-blue-50 p-6 rounded-lg mb-6 border border-blue-200" data-nav-id="editor-instructions">
        <h2 className="font-semibold text-xl mb-3 text-blue-900">Testing Instructions:</h2>
        <ul className="list-disc ml-6 space-y-2 text-gray-700">
          <li>
            <strong>Create buttons:</strong> Say "Click the create button" to add new buttons to the canvas
          </li>
          <li>
            <strong>Interact with buttons:</strong> Say "Click button 1" or "Click external button 1" to click the first created button
          </li>
          <li>
            <strong>Navigate:</strong> Say "Go to home" to return to the main page
          </li>
          <li>
            <strong>Multi-step:</strong> Say "Go to home and show me testimonials" for complex navigation
          </li>
        </ul>
        <div className="mt-4 p-3 bg-white rounded border border-blue-300">
          <p className="text-sm text-gray-600">
            <strong className="text-blue-800">Note:</strong> The iframe below contains dynamically generated content. 
            All elements inside have IDs starting with "external-" to distinguish them from main app elements.
          </p>
        </div>
      </div>

      <div 
        className="iframe-container border-4 border-gray-300 rounded-lg overflow-hidden shadow-lg bg-gray-100" 
        data-nav-id="iframe-container"
      >
        <iframe
          id="dynamic-content-iframe"
          src="http://localhost:3001"
          className="w-full h-[600px]"
          title="Dynamic Content Canvas"
          data-nav-id="dynamic-content-iframe"
        />
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200" data-nav-id="editor-status">
        <h3 className="font-semibold text-lg mb-2">Status</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Main App:</span>
            <span className="ml-2 font-mono text-blue-600">http://localhost:3000</span>
          </div>
          <div>
            <span className="text-gray-600">iframe Server:</span>
            <span className="ml-2 font-mono text-green-600">http://localhost:3001</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EditorPage

