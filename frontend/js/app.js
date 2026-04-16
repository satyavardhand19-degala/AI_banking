/* Vaani Smart Data Intelligence — App Orchestrator */

const app = {
    history: [],
    sortState: { column: -1, ascending: true },
    currentResult: null,

    async init() {
        this.checkStatus();
        this.loadHistory();
        voice.init();
        this.bindEvents();
    },

    async checkStatus() {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        try {
            const health = await api.health();
            statusDot.className = health.database === 'connected' ? 'status-dot connected' : 'status-dot error';
            statusText.textContent = health.database === 'connected' ? 'System Active' : 'DB Offline';
        } catch (e) {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Offline';
        }
    },

    bindEvents() {
        const queryInput = document.getElementById('query-input');
        const submitBtn = document.getElementById('submit-btn');
        const micBtn = document.getElementById('mic-btn');
        const sqlToggle = document.getElementById('sql-toggle');

        submitBtn.addEventListener('click', () => this.handleQuery());
        queryInput.addEventListener('keydown', e => { if (e.ctrlKey && e.key === 'Enter') this.handleQuery(); });
        micBtn.addEventListener('click', () => this.handleVoice());
        sqlToggle.addEventListener('click', () => this.toggleSQL());

        // File upload
        const fileUpload = document.getElementById('file-upload');
        const uploadTriggerBtn = document.getElementById('upload-trigger-btn');
        uploadTriggerBtn.addEventListener('click', () => fileUpload.click());
        fileUpload.addEventListener('change', e => { if (e.target.files.length) this.handleFileUpload(e.target.files[0]); });
    },

    async handleQuery(text = null) {
        const queryInput = document.getElementById('query-input');
        const query = text || queryInput.value;
        if (!query.trim()) return this.showToast('Please enter a query.', 'error');

        this.showLoading(true);
        try {
            const response = await api.query(query);
            this.renderResults(response);
            this.addToHistory(query);
            if (!text) queryInput.value = '';
        } catch (err) {
            this.showToast('Query failed.', 'error');
        } finally {
            this.showLoading(false);
        }
    },

    async handleVoice() {
        const micBtn = document.getElementById('mic-btn');
        const lang = document.getElementById('language-select').value;
        if (micBtn.classList.contains('recording')) {
            try {
                const audioBlob = await voice.stopRecording();
                micBtn.classList.add('processing');
                this.showLoading(true);
                const response = await api.transcribeAndQuery(audioBlob, lang);
                this.renderResults(response);
                this.addToHistory('🎙 Voice Query');
            } catch (err) {
                this.showToast('Voice query failed.', 'error');
            } finally {
                this.showLoading(false);
                voice.resetState();
            }
        } else {
            voice.startRecording();
        }
    },

    async handleFileUpload(file) {
        this.showLoading(true);
        try {
            const response = await api.uploadData(file);
            if (response.success) {
                this.showToast(`Success! Inserted ${response.rows_inserted} rows.`, 'info');
                this.addToHistory('📄 Uploaded Data');
            } else {
                this.showToast(response.error, 'error');
            }
        } catch (err) {
            this.showToast('Upload failed.', 'error');
        } finally {
            this.showLoading(false);
        }
    },

    renderResults(res) {
        if (!res.success) return this.showToast(res.error || 'Query failed.', 'error');
        this.currentResult = res;
        document.getElementById('results-section').style.display = 'block';
        document.getElementById('row-count').textContent = `${res.count} rows found`;
        
        const summaryDisplay = document.getElementById('summary-display');
        summaryDisplay.style.display = res.summary ? 'block' : 'none';
        summaryDisplay.innerHTML = `<strong>Summary:</strong> ${res.summary}`;

        const ttsBtn = document.getElementById('tts-btn');
        ttsBtn.onclick = async () => {
            try {
                const lang = document.getElementById('language-select').value;
                const audioBlob = await api.speak(res.summary, lang);
                voice.playAudio(audioBlob);
            } catch (e) { this.showToast('TTS failed.', 'error'); }
        };

        this.renderSQL(res.sql);
        charts.render(res.columns, res.rows);
        this.renderTable(res.columns, res.rows);
    },

    renderSQL(sql) {
        document.getElementById('sql-display').textContent = sql || '';
    },

    renderTable(columns, rows) {
        const container = document.getElementById('table-container');
        if (!rows.length) { container.innerHTML = 'No data.'; return; }
        let html = '<table><thead><tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
        rows.forEach(row => { html += '<tr>' + row.map(v => `<td>${v ?? '—'}</td>`).join('') + '</tr>'; });
        html += '</tbody></table>';
        container.innerHTML = html;
    },

    toggleSQL() {
        const container = document.getElementById('sql-display-container');
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
    },

    addToHistory(query) {
        this.history = [query, ...this.history.filter(h => h !== query)].slice(0, 10);
        this.saveHistory();
        this.renderHistory();
    },

    renderHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        this.history.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            li.className = 'history-item';
            li.onclick = () => { document.getElementById('query-input').value = item; this.handleQuery(item); };
            list.appendChild(li);
        });
    },

    loadHistory() {
        this.history = JSON.parse(localStorage.getItem('vaani_history') || '[]');
        this.renderHistory();
    },

    saveHistory() { localStorage.setItem('vaani_history', JSON.stringify(this.history)); },

    showLoading(show) { document.getElementById('loading').style.display = show ? 'flex' : 'none'; },

    showToast(msg, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.classList.remove('show'), 4000);
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
