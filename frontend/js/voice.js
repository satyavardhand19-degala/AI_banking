/* Vaani AI Banking Intelligence — Voice Handler */

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const voice = {
    async init() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.warn('MediaDevices API not supported');
            document.getElementById('mic-btn').disabled = true;
            document.getElementById('mic-btn').title = 'Microphone not supported on this browser/connection';
            return;
        }
    },

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.start();
            isRecording = true;
            this.updateUI(true);
        } catch (err) {
            console.error('Error accessing microphone:', err);
            app.showToast('Could not access microphone', 'error');
        }
    },

    async stopRecording() {
        return new Promise((resolve) => {
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                isRecording = false;
                this.updateUI(false);
                resolve(audioBlob);
            };
            mediaRecorder.stop();
            // Stop all tracks in the stream
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        });
    },

    updateUI(active) {
        const btn = document.getElementById('mic-btn');
        if (active) {
            btn.classList.add('recording');
        } else {
            btn.classList.remove('recording');
        }
    },

    async playAudio(blob) {
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        await audio.play();
    }
};
