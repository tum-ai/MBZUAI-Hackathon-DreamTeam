// automation_agent.js
// This script runs INSIDE the compiled Vue.js iframe
// It is a vanilla JS combination of your domCapture.js and actionExecutor.js

(function() {
    console.log('[Automation Agent] Injected and running.');

    // --- Part 1: DOM Capture ("The Eyes") ---
    // Based on your domCapture.js
    
    /**
     * Checks if an element is actually visible on the page
     */
    const isElementVisible = (element) => {
        const style = window.getComputedStyle(element);
        return (
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            style.opacity !== '0'
        );
    };

    /**
     * V20: Enhanced to detect more interactive component types
     */
    const getComponentType = (element) => {
        // Check explicit component type marker
        const explicitType = element.getAttribute('data-component-type');
        if (explicitType) return explicitType;
        
        // Detect by ID patterns (semantic IDs)
        const navId = element.getAttribute('data-nav-id') || '';
        
        // Check for specific component patterns in ID
        if (navId.includes('accordion') && navId.includes('header')) return 'accordion-header';
        if (navId.includes('tab') && navId.includes('button')) return 'tab-button';
        if (navId.includes('dialog') && navId.includes('close')) return 'dialog-close';
        if (navId.includes('modal') && navId.includes('close')) return 'modal-close';
        if (navId.includes('toggle') || navId.includes('switch')) return 'toggle';
        
        // Check for role attribute
        const role = element.getAttribute('role');
        if (role === 'button' || role === 'tab' || role === 'switch') return role;
        
        // Check for click event handlers on divs (custom interactive elements)
        if (element.tagName === 'DIV' && element.hasAttribute('@click')) return 'clickable-div';
        
        // Standard form elements
        if (element.tagName === 'SELECT') return 'select';
        if (element.tagName === 'INPUT') {
            const inputType = element.getAttribute('type');
            if (inputType === 'checkbox') return 'checkbox';
            if (inputType === 'radio') return 'radio';
            return 'input';
        }
        
        return element.tagName.toLowerCase();
    };

    /**
     * V20: Determines if an element is interactive
     */
    const isInteractive = (element) => {
        const interactiveTags = ['button', 'a', 'input', 'textarea', 'select'];
        const componentType = getComponentType(element);
        const interactiveTypes = [
            'accordion-header', 'tab-button', 'dialog-close', 'modal-close',
            'toggle', 'switch', 'checkbox', 'radio', 'select', 'clickable-div'
        ];
        
        // Check if it's a standard interactive element
        if (interactiveTags.includes(element.tagName.toLowerCase())) return true;
        
        // Check if it has an interactive component type
        if (interactiveTypes.includes(componentType)) return true;
        
        // Check if it has click handlers (Vue @click attribute won't be in DOM, but check for onclick)
        if (element.onclick || element.hasAttribute('onclick')) return true;
        
        return false;
    };

    /**
     * Captures DOM snapshot of all elements with data-nav-id
     */
    const captureDOMSnapshot = () => {
        const elements = document.querySelectorAll('[data-nav-id]');
        const snapshot = [];
        const viewportHeight = window.innerHeight;

        console.log(`[Automation Agent] 🔍 Scanning DOM, found ${elements.length} elements with data-nav-id`);

        elements.forEach((element) => {
            const navId = element.getAttribute('data-nav-id');
            const rect = element.getBoundingClientRect();
            const isVisible = isElementVisible(element);
            const componentType = getComponentType(element);
            const interactive = isInteractive(element);

            snapshot.push({
                navId,
                tagName: element.tagName.toLowerCase(),
                componentType, // V20: Added component type detection
                isInteractive: interactive, // V20: Added interactivity flag
                text: (element.textContent || '').trim().substring(0, 100),
                isVisible: isVisible,
                position: {
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    isInViewport: isVisible && rect.top >= 0 && rect.top <= viewportHeight
                },
                type: element.getAttribute('type') || null,
                // --- THIS IS THE FIX for DataCloneError ---
                // element.className can be an SVGAnimatedString, which is not cloneable.
                // getAttribute('class') always returns a plain string.
                className: element.getAttribute('class') || '',
                // V20: Additional metadata
                role: element.getAttribute('role') || null,
                ariaLabel: element.getAttribute('aria-label') || null
            });
        });
        return snapshot;
    };

    // --- Part 2: Action Executor ("The Hands") ---
    // Based on your actionExecutor.js

    /**
     * Executes actions received from the main app
     */
    const executeAction = (action) => {
        console.log('[Automation Agent] Executing action:', action);
        try {
            switch (action.action) {
                case 'navigate': // This is 'click'
                    return executeClick(action);
                case 'scroll':
                    return executeScroll(action);
                case 'scrollToElement':
                    return executeScrollToElement(action);
                case 'type':
                    return executeType(action);
                case 'focus':
                    return executeFocus(action);
                case 'clear':
                    return executeClear(action);
                default:
                    return { success: false, message: `Unknown action type: ${action.action}` };
            }
        } catch (error) {
            return { success: false, message: error.message, error: error.toString() };
        }
    };

    const getElementByNavId = (targetId) => {
        if (!targetId) {
            throw new Error('No targetId specified for action');
        }
        const element = document.querySelector(`[data-nav-id="${targetId}"]`);
        if (!element) {
            throw new Error(`Element ${targetId} not found in iframe`);
        }
        return element;
    };

    const executeClick = (action) => {
        const element = getElementByNavId(action.targetId);
        
        // Highlight the element
        const originalOutline = element.style.outline;
        element.style.outline = '3px solid #3B82F6';
        element.style.transition = 'outline 0.2s ease';
        setTimeout(() => { element.style.outline = originalOutline; }, 1000);

        element.click();
        return { success: true, message: `Clicked ${action.targetId}` };
    };

    const executeScroll = (action) => {
        const { direction, amount = 300 } = action;
        switch (direction) {
            case 'up':
                window.scrollBy({ top: -amount, behavior: 'smooth' });
                break;
            case 'down':
                window.scrollBy({ top: amount, behavior: 'smooth' });
                break;
            case 'top':
                window.scrollTo({ top: 0, behavior: 'smooth' });
                break;
            case 'bottom':
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                break;
            default:
                return { success: false, message: `Unknown scroll direction: ${direction}` };
        }
        return { success: true, message: `Scrolled ${direction}` };
    };

    const executeScrollToElement = (action) => {
        const element = getElementByNavId(action.targetId);
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Highlight it
        const originalOutline = element.style.outline;
        element.style.outline = '3px solid #3B82F6';
        setTimeout(() => { element.style.outline = originalOutline; }, 2000);

        return { success: true, message: `Scrolled to ${action.targetId}` };
    };

    const executeType = (action) => {
        const element = getElementByNavId(action.targetId);
        if (element.tagName !== 'INPUT' && element.tagName !== 'TEXTAREA') {
            return { success: false, message: `Element ${action.targetId} is not an input field` };
        }
        element.value = action.text;
        // Dispatch events to trigger React/Vue reactivity
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return { success: true, message: `Typed "${action.text}" into ${action.targetId}` };
    };

    const executeFocus = (action) => {
        const element = getElementByNavId(action.targetId);
        element.focus();
        return { success: true, message: `Focused on ${action.targetId}` };
    };

    const executeClear = (action) => {
        const element = getElementByNavId(action.targetId);
        if (element.tagName !== 'INPUT' && element.tagName !== 'TEXTAREA') {
            return { success: false, message: `Element ${action.targetId} is not an input field` };
        }
        element.value = '';
        // Dispatch events
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return { success: true, message: `Cleared ${action.targetId}` };
    };


    // --- Part 3: The Message Listener ---
    // Based on your main.jsx

    window.addEventListener('message', (event) => {
        // IMPORTANT: In a real app, you MUST verify the origin
        // e.g., if (event.origin !== 'http://your-main-app.com') return;
        
        // --- FIX: Check for 'null' origin when running from file:// ---
        // If event.origin is "null" (from a local file), use "*" as the target.
        // Otherwise, use the event's origin.
        const targetOrigin = event.origin === 'null' ? '*' : event.origin;

        console.log('[Automation Agent] Received message:', event.data);

        // Handle DOM snapshot request
        if (event.data.type === 'DOM_SNAPSHOT_REQUEST') {
            const snapshot = captureDOMSnapshot();
            console.log('[Automation Agent] Sending DOM snapshot:', snapshot);
            
            event.source.postMessage({
                type: 'DOM_SNAPSHOT_RESPONSE',
                snapshot
            }, targetOrigin); // <-- USE THE FIXED targetOrigin
        }

        // Handle action execution request
        if (event.data.type === 'EXECUTE_ACTION') {
            const result = executeAction(event.data.action);
            console.log('[Automation Agent] Action result:', result);
            
            event.source.postMessage({
                type: 'ACTION_RESULT',
                result
            }, targetOrigin); // <-- USE THE FIXED targetOrigin
        }
    });

})();