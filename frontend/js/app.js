/* Vaani AI Banking Intelligence — App Orchestrator */

const app = {
    history: [],
    
    async init() {
        console.log('Vaani App Initializing...');
        
        // 1. Health check
        this.checkStatus();
        
        // 2. Load History
        this.loadHistory();
        
        // 3. Init Voice
        voice.init();
        
        // 4. Bind Events
        this.bindEvents();
    },

    async checkStatus() {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        const health = await api.health();
        if (health.database === 'connected') {
            statusDot.className = 'status-dot connected';
            statusText.innerText = 'System Active';
        } else {
            statusDot.className = 'status-dot error';
            statusText.innerText = 'DB Offline';
        }
    },

    bindEvents() {
        const queryInput = document.getElementById('query-input');
        const submitBtn = document.getElementById('submit-btn');
        const micBtn = document.getElementById('mic-btn');
        const sqlToggle = document.getElementById('sql-toggle');

        submitBtn.onclick = () => this.handleQuery();
        
        queryInput.onkeydown = (e) => {
            if (e.ctrlKey && e.key === 'Enter') this.handleQuery();
        };

        micBtn.onclick = () => this.handleVoice();
        
        sqlToggle.onclick = () => {
            const container = document.getElementById('sql-display-container');
            const icon = document.getElementById('sql-toggle-icon');
            const isHidden = container.style.display === 'none';
            container.style.display = isHidden ? 'block' : 'none';
            icon.innerText = isHidden ? '▲' : '▼';
        };
    },

    async handleQuery(text = null) {
        const query = text || document.getElementById('query-input').value;
        if (!query.trim()) return;

        this.showLoading(true);
        try {
            const response = await api.query(query);
            this.renderResults(response);
            this.addToHistory(query);
            document.getElementById('query-input').value = '';
        } catch (err) {
            this.showToast(err.message, 'error');
        } finally {
            this.showLoading(false);
        }
    },

    async handleVoice() {
        const micBtn = document.getElementById('mic-btn');
        const lang = document.getElementById('language-select').value;

        if (micBtn.classList.contains('recording')) {
            const audioBlob = await voice.stopRecording();
            this.showLoading(true);
            try {
                const response = await api.transcribeAndQuery(audioBlob, lang);
                this.renderResults(response);
                this.addToHistory(response.sql ? "Voice Query" : "Voice Failed");
            } catch (err) {
                this.showToast(err.message, 'error');
            } finally {
                this.showLoading(false);
            }
        } else {
            voice.startRecording();
        }
    },

    renderResults(res) {
        if (!res.success) {
            this.showToast(res.error, 'error');
            return;
        }

        const section = document.getElementById('results-section');
        section.style.display = 'block';
        
        // 1. SQL
        document.getElementById('sql-display').innerText = res.sql;
        
        // 2. Meta
        document.getElementById('row-count').innerText = `${res.count} rows found`;
        
        // 3. TTS Button
        const ttsBtn = document.getElementById('tts-btn');
        ttsBtn.style.display = res.summary ? 'block' : 'none';
        ttsBtn.onclick = async () => {
            const lang = document.getElementById('language-select').value;
            const audioBlob = await api.speak(res.summary, lang);
            voice.playAudio(audioBlob);
        };

        // 4. Chart
        charts.render(res.columns, res.rows);

        // 5. Table
        this.renderTable(res.columns, res.rows);
        
        section.scrollIntoView({ behavior: 'smooth' });
    },

    renderTable(columns, rows) {
        const container = document.getElementById('table-container');
        if (rows.length === 0) {
            container.innerHTML = '<div style="padding:40px; text-align:center; color:var(--text-muted)">No data available for this query.</div>';
            return;
        }

        let html = '<table><thead><tr>';
        columns.forEach(col => {
            html += `<th>${col.replace(/_/g, ' ')}</th>`;
        });
        html += '</tr></thead><tbody>';

        rows.forEach((row, i) => {
            html += `<tr style="animation: fade-up 0.3s ease forwards; animation-delay: ${i * 0.05}s">`;
            row.forEach(val => {
                html += `<td>${val === null ? '-' : val}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    },

    addToHistory(query) {
        if (this.history.includes(query)) return;
        this.history.unshift(query);
        if (this.history.length > 10) this.history.pop();
        this.saveHistory();
        this.renderHistory();
    },

    renderHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = this.history.map(item => `
            <li class="history-item" onclick="app.handleQuery('${item}')">${item}</li>
        `).join('');
    },

    loadHistory() {
        const saved = localStorage.getItem('vaani_history');
        if (saved) {
            this.history = JSON.parse(saved);
            this.renderHistory();
        }
    },

    saveHistory() {
        localStorage.setItem('vaani_history', JSON.stringify(this.history));
    },

    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
    },

    showToast(msg, type = 'info') {
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
