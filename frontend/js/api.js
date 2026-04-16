/* Vaani Smart Data Intelligence — API Client */

const API_BASE_URL = '/api';

const api = {
    async health() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(8000) });
            return await response.json();
        } catch (error) {
            return { status: 'error', database: 'disconnected', sarvam: 'unreachable' };
        }
    },

    async query(text) {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        });
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
    },

    async uploadData(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/upload-data`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    }
};
