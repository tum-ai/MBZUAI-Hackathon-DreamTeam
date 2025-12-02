import React from 'react';
import { useVoiceAssistantContext } from '../context/VoiceAssistantContext';

export function VitePreview() {
    const { viteUrl, isInitializingSession } = useVoiceAssistantContext();

    if (isInitializingSession) {
        return (
            <div className="flex items-center justify-center h-full bg-gray-900 text-white">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p>Initializing development session...</p>
                </div>
            </div>
        );
    }

    if (!viteUrl) {
        return (
            <div className="flex items-center justify-center h-full bg-gray-900 text-white">
                <div className="text-center">
                    <p className="text-gray-400">Say "Create a website" to get started</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-white">
            <iframe
                src={viteUrl}
                className="w-full h-full border-none"
                title="Website Preview"
                allow="accelerometer; camera; encrypted-media; geolocation; gyroscope; microphone; midi; clipboard-read; clipboard-write"
            />
        </div>
    );
}
