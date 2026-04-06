/* Vaani AI Banking Intelligence — API Client */

const API_BASE_URL = '/api';

const api = {
    /**
     * Health check — verifies backend, DB, and Sarvam connectivity.
     */
    async health() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`, {
                signal: AbortSignal.timeout(8000)
            });
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', database: 'disconnected', sarvam: 'unreachable' };
        }
    },

    /**
     * Send a natural language query to the backend.
     * Returns QueryResponse { success, sql, columns, rows, count, summary, error }
     */
    async query(text) {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text }),
            signal: AbortSignal.timeout(30000)
        });

        const data = await this._parseJSON(response);

        if (!response.ok && !data.error) {
            throw new Error(`Server error (${response.status})`);
        }

        return data;
    },

    /**
     * Upload audio blob for voice transcription + query pipeline.
     * Returns QueryResponse with results.
     */
    async transcribeAndQuery(audioBlob, languageCode) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');
        formData.append('language_code', languageCode);

        const response = await fetch(`${API_BASE_URL}/voice/transcribe`, {
            method: 'POST',
            body: formData,
            signal: AbortSignal.timeout(30000)
        });

        const data = await this._parseJSON(response);

        if (!response.ok && !data.error) {
            throw new Error(`Transcription failed (${response.status})`);
        }

        return data;
    },

    /**
     * Send text to Sarvam TTS for speech synthesis.
     * Returns an audio Blob (WAV).
     */
    async speak(text, languageCode) {
        const response = await fetch(`${API_BASE_URL}/voice/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language_code: languageCode }),
            signal: AbortSignal.timeout(15000)
        });

        if (!response.ok) {
            let errorMsg = 'Text-to-speech failed';
            try {
                const err = await response.json();
                errorMsg = err.detail || err.error || errorMsg;
            } catch (_) {}
            throw new Error(errorMsg);
        }

        return await response.blob();
    },

    /**
     * Safe JSON parser — returns a fallback error object if parsing fails.
     */
    async _parseJSON(response) {
        try {
            return await response.json();
        } catch (e) {
            console.error('Failed to parse JSON response:', e);
            return {
                success: false,
                error: `Server returned an invalid response (${response.status})`
            };
        }
    }
};
