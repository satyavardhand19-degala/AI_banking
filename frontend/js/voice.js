/* Vaani — Voice Module */

let mediaRecorder = null;
let audioChunks = [];

const voice = {
    init() {
        const btn = document.getElementById('mic-btn');
        if (!location.protocol === 'https:' && !['localhost', '127.0.0.1'].includes(location.hostname)) {
            btn.disabled = true;
            btn.title = 'HTTPS required for microphone';
        }
    },

    isMicAvailable() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    },

    async startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.start();
        document.getElementById('mic-btn').classList.add('recording');
    },

    async stopRecording() {
        return new Promise(resolve => {
            mediaRecorder.onstop = () => {
                const blob = new Blob(audioChunks, { type: 'audio/webm' });
                mediaRecorder.stream.getTracks().forEach(t => t.stop());
                document.getElementById('mic-btn').classList.remove('recording');
                resolve(blob);
            };
            mediaRecorder.stop();
        });
    },

    resetState() {
        document.getElementById('mic-btn').classList.remove('recording', 'processing');
    },

    async playAudio(blob) {
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.onended = () => URL.revokeObjectURL(url);
        await audio.play();
    }
};
