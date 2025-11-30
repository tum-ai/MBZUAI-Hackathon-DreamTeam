import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Hook for streaming plan execution via WebSocket.
 * Streams individual step results as they complete.
 */
export function useStreamingPlan({ wsUrl = 'ws://localhost:8000/plan-stream' } = {}) {
    const wsRef = useRef(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const pendingRequestsRef = useRef(new Map());

    // Connect to WebSocket
    useEffect(() => {
        if (isConnecting || wsRef.current) return;

        setIsConnecting(true);

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('[StreamingPlan] WebSocket connected');
            setIsConnected(true);
            setIsConnecting(false);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const requestId = data.requestId;

                const handlers = pendingRequestsRef.current.get(requestId);
                if (!handlers) {
                    console.warn('[StreamingPlan] No handlers for requestId:', requestId);
                    return;
                }

                console.log('[StreamingPlan] Received:', data.type);

                switch (data.type) {
                    case 'step_completed':
                        handlers.onStepComplete?.(data);
                        break;

                    case 'plan_finished':
                        handlers.onFinish?.(data);
                        pendingRequestsRef.current.delete(requestId);
                        break;

                    case 'error':
                        handlers.onError?.(new Error(data.error || 'Unknown error'));
                        pendingRequestsRef.current.delete(requestId);
                        break;

                    default:
                        console.warn('[StreamingPlan] Unknown message type:', data.type);
                }
            } catch (err) {
                console.error('[StreamingPlan] Error parsing message:', err);
            }
        };

        ws.onerror = (error) => {
            console.error('[StreamingPlan] WebSocket error:', error);
            setIsConnected(false);
            setIsConnecting(false);
        };

        ws.onclose = () => {
            console.log('[StreamingPlan] WebSocket disconnected');
            setIsConnected(false);
            setIsConnecting(false);
            wsRef.current = null;

            // Clear pending requests
            pendingRequestsRef.current.forEach((handlers, requestId) => {
                handlers.onError?.(new Error('WebSocket connection closed'));
            });
            pendingRequestsRef.current.clear();
        };

        wsRef.current = ws;

        return () => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        };
    }, [wsUrl, isConnecting]);

    /**
     * Send a plan request and stream results.
     * @param {string} text - User command text
     * @param {string} sessionId - Session ID
     * @param {object} handlers - Callback handlers
     * @param {function} handlers.onStepComplete - Called when a step completes
     * @param {function} handlers.onFinish - Called when plan finishes
     * @param {function} handlers.onError - Called on error
     * @returns {string} requestId - Request ID for tracking
     */
    const sendPlanRequest = useCallback((text, sessionId, handlers = {}) => {
        if (!isConnected || !wsRef.current) {
            const error = new Error('WebSocket not connected');
            handlers.onError?.(error);
            return null;
        }

        const requestId = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
        const stepId = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;

        // Store handlers
        pendingRequestsRef.current.set(requestId, handlers);

        // Send request
        const message = {
            type: 'plan_request',
            requestId,
            sessionId,
            text,
            stepId,
        };

        console.log('[StreamingPlan] Sending request:', text);
        wsRef.current.send(JSON.stringify(message));

        return requestId;
    }, [isConnected]);

    return {
        isConnected,
        isConnecting,
        sendPlanRequest,
    };
}
