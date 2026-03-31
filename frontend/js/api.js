/* Vaani AI Banking Intelligence — API Client */

const API_BASE_URL = 'http://localhost:8000/api';

const api = {
    async health() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', database: 'disconnected' };
        }
    },

    async query(text) {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Query failed');
        }
        
        return await response.json();
    },

    async transcribeAndQuery(audioBlob, languageCode) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');
        formData.append('language_code', languageCode);

        const response = await fetch(`${API_BASE_URL}/voice/transcribe`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Transcription failed');
        }

        return await response.json();
    },

    async speak(text, languageCode) {
        const response = await fetch(`${API_BASE_URL}/voice/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language_code: languageCode })
        });

        if (!response.ok) throw new Error('TTS failed');

        return await response.blob();
    }
};
