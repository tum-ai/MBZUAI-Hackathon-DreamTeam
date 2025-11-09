/**
 * Voice Navigation Test Sequences
 * 
 * This file contains test cases for the voice navigation system.
 * Tests can be executed from the browser console using window.testSequences
 */

import { executeAction } from '../services/actionExecutor'
import { captureDOMSnapshot } from '../utils/domSnapshot'

// Test case sequences
export const testSequences = {
  // Test Case TTS: Test Text-to-Speech with sphere visualization
  testTTS: async () => {
    console.log('🧪 Test Case TTS: Testing Text-to-Speech with visualization')
    const text = 'Hi my name is K2 and I am a language model'
    
    // Check if speakText is available from VoiceAssistantContext
    if (window.__speakText) {
      console.log('Speaking:', text)
      await window.__speakText(text)
      console.log('✅ TTS playback complete - sphere visualization should have animated')
    } else {
      console.error('❌ TTS function not available. Make sure VoiceAssistantContext is loaded.')
    }
  },

  // Test Case 1: Click "Get Started" button
  testCase1: async () => {
    console.log('🧪 Test Case 1: Click Get Started button')
    return await executeAction({
      action: 'navigate',
      targetId: 'create-project-cta'
    })
  },
  
  // Test Case 2: Navigate to templates, open second project, then close
  testCase2: async () => {
    console.log('🧪 Test Case 2: Get Started → Open Project B → Close Modal')
    return await executeAction([
      {
        action: 'navigate',
        targetId: 'create-project-cta',
        reasoning: 'Navigate to template selection'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for page to load'
      },
      {
        action: 'navigate',
        targetId: 'template-option-b',
        reasoning: 'Open second project (B)'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for modal to open'
      },
      {
        action: 'navigate',
        targetId: 'toolbar-close-btn',
        reasoning: 'Close the inspection modal using toolbar X button'
      }
    ])
  },
  
  // Test Case 3: Simple test - just toggle gallery and scroll once
  testCase3_galleryScroll: async () => {
    console.log('🧪 Test Case 3 (Gallery Test): Toggle Gallery → Scroll Once')
    console.log('⚠️  Make sure you are already in edit mode before running this!')
    return await executeAction([
      {
        action: 'navigate',
        targetId: 'toggle-gallery',
        reasoning: 'Toggle gallery to make it visible'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for gallery to appear'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Test one scroll'
      }
    ])
  },
  
  // Test Case 3b: Full setup then gallery scroll test
  testCase3b_fullGalleryScroll: async () => {
    console.log('🧪 Test Case 3b (Full Gallery Test): Open A → Select → Show Gallery → Scroll → Select Image → Close')
    return await executeAction([
      {
        action: 'navigate',
        targetId: 'create-project-cta',
        reasoning: 'Navigate to template selection'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for page to load'
      },
      {
        action: 'navigate',
        targetId: 'template-option-a',
        reasoning: 'Open first project (A)'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for modal to open'
      },
      {
        action: 'navigate',
        targetId: 'template-select-design',
        reasoning: 'Select this design for editing'
      },
      {
        action: 'wait',
        duration: 1000,
        reasoning: 'Wait for edit mode to activate'
      },
      {
        action: 'navigate',
        targetId: 'toggle-gallery',
        reasoning: 'Toggle gallery to make it visible'
      },
      {
        action: 'wait',
        duration: 1500,
        reasoning: 'Wait for gallery to fully appear and stabilize (needs time for initial render)'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll (1/3)'
      },
      {
        action: 'wait',
        duration: 1000,
        reasoning: 'Wait for scroll to complete and stabilize (>200ms for debounce)'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll (2/3)'
      },
      {
        action: 'wait',
        duration: 1000,
        reasoning: 'Wait for scroll to complete and stabilize (>200ms for debounce)'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll (3/3)'
      },
      {
        action: 'wait',
        duration: 1000,
        reasoning: 'Wait for final scroll to complete (>200ms for debounce)'
      },
      {
        action: 'navigate',
        targetId: 'gallery-strawberries',
        reasoning: 'Click on Strawberries image (should be visible after 3 scrolls)'
      },
      {
        action: 'wait',
        duration: 2000,
        reasoning: 'Wait and view enlarged image longer'
      },
      {
        action: 'navigate',
        targetId: 'toolbar-close-btn',
        reasoning: 'Close the enlarged image view using toolbar X button'
      },
      {
        action: 'wait',
        duration: 500,
        reasoning: 'Wait for enlarged view to close'
      },
      {
        action: 'navigate',
        targetId: 'toggle-gallery',
        reasoning: 'Toggle gallery to hide it'
      }
    ])
  },
  
  // Test Case 4: Full complex flow - Open B, close, open A, select design, click New York image
  testCase4: async () => {
    console.log('🧪 Test Case 4: Open B → Close → Open A → Select → Gallery → New York')
    return await executeAction([
      {
        action: 'navigate',
        targetId: 'create-project-cta',
        reasoning: 'Navigate to template selection'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for page to load'
      },
      {
        action: 'navigate',
        targetId: 'template-option-b',
        reasoning: 'Open second project (B)'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for modal to open'
      },
      {
        action: 'navigate',
        targetId: 'toolbar-close-btn',
        reasoning: 'Close the inspection modal using toolbar X button'
      },
      {
        action: 'wait',
        duration: 600,
        reasoning: 'Wait for modal to close'
      },
      {
        action: 'navigate',
        targetId: 'template-option-a',
        reasoning: 'Open first project (A)'
      },
      {
        action: 'wait',
        duration: 800,
        reasoning: 'Wait for modal to open'
      },
      {
        action: 'navigate',
        targetId: 'template-select-design',
        reasoning: 'Select this design for editing'
      },
      {
        action: 'wait',
        duration: 1000,
        reasoning: 'Wait for edit mode to activate'
      },
      {
        action: 'navigate',
        targetId: 'toggle-gallery',
        reasoning: 'Toggle gallery to make it visible'
      },
      {
        action: 'wait',
        duration: 500,
        reasoning: 'Wait for gallery to appear'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (1/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (2/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (3/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (4/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (5/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (6/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (7/8)'
      },
      {
        action: 'wait',
        duration: 400,
        reasoning: 'Wait for scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-scroll-next',
        reasoning: 'Scroll gallery forward (8/8) - New York should be visible'
      },
      {
        action: 'wait',
        duration: 500,
        reasoning: 'Wait for final scroll animation'
      },
      {
        action: 'navigate',
        targetId: 'gallery-new-york',
        reasoning: 'Click on New York image in gallery'
      }
    ])
  }
}

// Helper function for quick testing
export const testAction = (targetId) => {
  return executeAction({
    action: 'navigate',
    targetId: targetId
  })
}

// Helper to scroll gallery multiple times
export const scrollGallery = async (times = 1, direction = 'next') => {
  const actions = []
  for (let i = 0; i < times; i++) {
    actions.push({
      action: 'navigate',
      targetId: `gallery-scroll-${direction}`
    })
    actions.push({
      action: 'wait',
      duration: 400
    })
  }
  return await executeAction(actions)
}

// Initialize test helpers
export const initializeTestHelpers = () => {
  // Expose action executor functions to window for testing
  window.executeAction = executeAction
  window.captureDOMSnapshot = captureDOMSnapshot
  window.testAction = testAction
  window.testSequences = testSequences
  window.scrollGallery = scrollGallery

  console.log('✅ Voice Navigation Testing Enabled!')
  console.log('Available commands:')
  console.log('  - window.executeAction(action) - Execute a single action or sequence')
  console.log('  - window.captureDOMSnapshot() - View all navigatable elements')
  console.log('  - window.testAction(targetId) - Quick test: click an element by ID')
  console.log('  - window.scrollGallery(times, direction) - Scroll gallery wheel')
  console.log('')
  console.log('Test Sequences:')
  console.log('  - window.testSequences.testTTS() - Test TTS with sphere visualization')
  console.log('  - window.testSequences.testCase1() - Simple: Click Get Started')
  console.log('  - window.testSequences.testCase2() - Medium: Open & close project B')
  console.log('  - window.testSequences.testCase3_galleryScroll() - Quick: Toggle + 1 scroll')
  console.log('  - window.testSequences.testCase3b_fullGalleryScroll() - Full gallery test')
  console.log('  - window.testSequences.testCase4() - Complex: Full flow with gallery scroll')
  console.log('')
  console.log('Gallery Images (in order):')
  console.log('  Bridge → Desk Setup → Waterfall → Strawberries → Deep Diving →')
  console.log('  Train Track → Santorini → Blurry Lights → New York → Good Boy →')
  console.log('  Coastline → Palm Trees')
  console.log('')
  console.log('')
  console.log('Quick Test (if already in edit mode):')
  console.log('  window.testSequences.testCase3_galleryScroll()')
  console.log('')
  console.log('Full Test (from homepage):')
  console.log('  window.testSequences.testCase3b_fullGalleryScroll()')
}

