/**
 * Whisper API integration for speech-to-text
 * Uses OpenAI's Whisper API
 */

const API_KEY = import.meta.env.VITE_OPENAI_API_KEY

/**
 * Record audio from the user's microphone
 */
export const recordAudio = async (onStart, onStop) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mediaRecorder = new MediaRecorder(stream)
    const audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data)
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      if (onStop) {
        await onStop(audioBlob)
      }
      
      // Stop all tracks to release the microphone
      stream.getTracks().forEach(track => track.stop())
    }

    if (onStart) {
      onStart()
    }

    mediaRecorder.start()

    return {
      stop: () => mediaRecorder.stop(),
      mediaRecorder
    }
  } catch (error) {
    console.error('Error accessing microphone:', error)
    throw new Error('Could not access microphone. Please grant permission.')
  }
}

/**
 * Transcribe audio using Whisper API
 */
export const transcribeAudio = async (audioBlob) => {
  if (!API_KEY) {
    throw new Error('VITE_OPENAI_API_KEY is not set. Please add it to your .env file.')
  }

  try {
    // Convert webm to a format Whisper accepts
    const formData = new FormData()
    formData.append('file', audioBlob, 'audio.webm')
    formData.append('model', 'whisper-1')
    formData.append('language', 'en')

    const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`
      },
      body: formData
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error?.message || 'Transcription failed')
    }

    const data = await response.json()
    return data.text
  } catch (error) {
    console.error('Transcription error:', error)
    throw error
  }
}

/**
 * Combined function: record and transcribe
 */
export const recordAndTranscribe = async (onTranscriptReady, onError) => {
  try {
    const recorder = await recordAudio(
      () => console.log('Recording started...'),
      async (audioBlob) => {
        try {
          console.log('Recording stopped. Transcribing...')
          const transcript = await transcribeAudio(audioBlob)
          if (onTranscriptReady) {
            onTranscriptReady(transcript)
          }
        } catch (error) {
          if (onError) {
            onError(error)
          }
        }
      }
    )

    return recorder
  } catch (error) {
    if (onError) {
      onError(error)
    }
    throw error
  }
}

