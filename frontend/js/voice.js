/* Vaani AI Banking Intelligence — Voice Handler */

let mediaRecorder = null;
let audioChunks = [];
let voiceState = 'idle'; // 'idle' | 'recording' | 'processing'

const voice = {
    /**
     * Initialize voice module — check mic availability.
     */
    init() {
        const micBtn = document.getElementById('mic-btn');

        if (!this.isMicAvailable()) {
            micBtn.disabled = true;
            micBtn.title = 'Microphone requires HTTPS or localhost';
            console.warn('Mic unavailable: page not served over HTTPS or localhost');
            return;
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            micBtn.disabled = true;
            micBtn.title = 'Microphone not supported in this browser';
            console.warn('MediaDevices API not supported');
            return;
        }

        console.log('Voice module initialized ✓');
    },

    /**
     * Check if microphone is available (HTTPS or localhost required).
     */
    isMicAvailable() {
        return location.protocol === 'https:' ||
               location.hostname === 'localhost' ||
               location.hostname === '127.0.0.1';
    },

    /**
     * Start recording audio from the microphone.
     */
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Prefer webm if available, fallback to whatever is supported
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : (MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : '');

            const options = mimeType ? { mimeType } : {};
            mediaRecorder = new MediaRecorder(stream, options);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                this.resetState();
                app.showToast('Recording failed. Please try again.', 'error');
            };

            mediaRecorder.start(100); // Collect data every 100ms for smoother waveform
            voiceState = 'recording';
            this.updateUI('recording');

            console.log('Recording started');
        } catch (err) {
            console.error('Error accessing microphone:', err);
            if (err.name === 'NotAllowedError') {
                app.showToast('Microphone access denied. Please allow mic access in browser settings.', 'error');
            } else if (err.name === 'NotFoundError') {
                app.showToast('No microphone found. Please connect a microphone.', 'error');
            } else {
                app.showToast('Could not access microphone.', 'error');
            }
        }
    },

    /**
     * Stop recording and return the audio blob.
     */
    async stopRecording() {
        return new Promise((resolve, reject) => {
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                this.resetState();
                reject(new Error('No active recording'));
                return;
            }

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                voiceState = 'processing';
                this.updateUI('processing');

                // Stop all tracks to release the microphone
                if (mediaRecorder.stream) {
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                }

                console.log(`Recording stopped. Blob size: ${audioBlob.size} bytes`);
                resolve(audioBlob);
            };

            mediaRecorder.stop();
        });
    },

    /**
     * Update mic button UI based on state.
     */
    updateUI(state) {
        const btn = document.getElementById('mic-btn');
        btn.classList.remove('recording', 'processing');

        if (state === 'recording') {
            btn.classList.add('recording');
            btn.title = 'Click to stop recording';
        } else if (state === 'processing') {
            btn.classList.add('processing');
            btn.title = 'Processing voice...';
        } else {
            btn.title = 'Voice query';
        }
    },

    /**
     * Reset voice state to idle.
     */
    resetState() {
        voiceState = 'idle';
        audioChunks = [];
        this.updateUI('idle');
    },

    /**
     * Play an audio blob through the speakers.
     */
    async playAudio(blob) {
        try {
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);

            audio.onended = () => {
                URL.revokeObjectURL(url);
            };

            audio.onerror = () => {
                URL.revokeObjectURL(url);
                console.error('Audio playback failed');
            };

            await audio.play();
        } catch (err) {
            console.error('Error playing audio:', err);
            app.showToast('Could not play audio.', 'error');
        }
    }
};
