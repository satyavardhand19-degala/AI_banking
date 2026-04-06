/* Vaani AI Banking Intelligence — App Orchestrator */

const app = {
    history: [],
    sortState: { column: -1, ascending: true },
    currentResult: null,

    /* ── Initialization ── */

    async init() {
        console.log('Vaani App Initializing...');

        // 1. Health check
        this.checkStatus();

        // 2. Load History from localStorage
        this.loadHistory();

        // 3. Initialize Voice module
        voice.init();

        // 4. Bind all events
        this.bindEvents();

        console.log('Vaani App Ready ✓');
    },

    /* ── Status Check ── */

    async checkStatus() {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');

        try {
            const health = await api.health();
            if (health.database === 'connected') {
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'System Active';
            } else {
                statusDot.className = 'status-dot error';
                statusText.textContent = 'DB Offline';
            }
        } catch (e) {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Offline';
        }
    },

    /* ── Event Binding ── */

    bindEvents() {
        const queryInput = document.getElementById('query-input');
        const submitBtn = document.getElementById('submit-btn');
        const micBtn = document.getElementById('mic-btn');
        const sqlToggle = document.getElementById('sql-toggle');
        const sidebarToggle = document.getElementById('sidebar-toggle');

        // Submit query
        submitBtn.addEventListener('click', () => this.handleQuery());

        // Ctrl+Enter to submit
        queryInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.handleQuery();
            }
        });

        // Voice recording toggle
        micBtn.addEventListener('click', () => this.handleVoice());

        // SQL toggle
        sqlToggle.addEventListener('click', () => this.toggleSQL());
        sqlToggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleSQL();
            }
        });

        // Mobile sidebar toggle
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                const sidebar = document.getElementById('sidebar');
                sidebar.classList.toggle('open');
            });

            // Close sidebar on clicking outside (mobile)
            document.addEventListener('click', (e) => {
                const sidebar = document.getElementById('sidebar');
                if (sidebar.classList.contains('open') &&
                    !sidebar.contains(e.target) &&
                    !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            });
        }
    },

    /* ── Query Handling ── */

    async handleQuery(text = null) {
        const queryInput = document.getElementById('query-input');
        const query = text || queryInput.value;
        if (!query.trim()) {
            this.showToast('Please enter a query.', 'error');
            return;
        }

        this.showLoading(true);
        try {
            const response = await api.query(query);
            this.renderResults(response);
            this.addToHistory(query);
            if (text === null) queryInput.value = '';
        } catch (err) {
            this.showToast(err.message || 'Connection error. Is the backend running?', 'error');
        } finally {
            this.showLoading(false);
        }
    },

    /* ── Voice Handling ── */

    async handleVoice() {
        const micBtn = document.getElementById('mic-btn');
        const lang = document.getElementById('language-select').value;

        if (micBtn.classList.contains('processing')) return;

        if (micBtn.classList.contains('recording')) {
            // Stop recording and process
            try {
                const audioBlob = await voice.stopRecording();
                this.showLoading(true);
                const response = await api.transcribeAndQuery(audioBlob, lang);
                this.renderResults(response);
                if (response.success) {
                    this.addToHistory('🎙 Voice Query');
                }
            } catch (err) {
                this.showToast(err.message || 'Voice query failed.', 'error');
                voice.resetState();
            } finally {
                this.showLoading(false);
                voice.resetState();
            }
        } else {
            // Start recording
            voice.startRecording();
        }
    },

    /* ── Results Rendering ── */

    renderResults(res) {
        if (!res.success) {
            this.showToast(res.error || 'Query failed.', 'error');
            return;
        }

        this.currentResult = res;

        const section = document.getElementById('results-section');
        section.style.display = 'block';

        // 1. SQL display
        this.renderSQL(res.sql);

        // 2. Row count
        document.getElementById('row-count').textContent = `${res.count} row${res.count !== 1 ? 's' : ''} found`;

        // 3. TTS Button
        const ttsBtn = document.getElementById('tts-btn');
        if (res.summary) {
            ttsBtn.style.display = 'flex';
            ttsBtn.onclick = async () => {
                try {
                    ttsBtn.disabled = true;
                    ttsBtn.textContent = '⏳';
                    const lang = document.getElementById('language-select').value;
                    const audioBlob = await api.speak(res.summary, lang);
                    voice.playAudio(audioBlob);
                } catch (err) {
                    this.showToast('Could not play summary audio.', 'error');
                } finally {
                    ttsBtn.disabled = false;
                    ttsBtn.textContent = '🔊';
                }
            };
        } else {
            ttsBtn.style.display = 'none';
        }

        // 4. Chart / Big Number
        charts.render(res.columns, res.rows);

        // 5. Table with sorting
        this.sortState = { column: -1, ascending: true };
        this.renderTable(res.columns, res.rows);

        // Scroll to results
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    /* ── SQL Syntax Highlighting ── */

    renderSQL(sql) {
        if (!sql) return;
        const display = document.getElementById('sql-display');

        // SQL keyword highlighting
        const keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
            'INNER JOIN', 'OUTER JOIN', 'ON', 'AND', 'OR', 'NOT', 'IN',
            'LIKE', 'ILIKE', 'BETWEEN', 'IS', 'NULL', 'AS', 'ORDER BY',
            'GROUP BY', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT', 'COUNT',
            'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE',
            'END', 'CAST', 'DESC', 'ASC', 'UNION', 'EXISTS', 'WITH'
        ];

        let highlighted = this._escapeHtml(sql);

        // Highlight string literals (single-quoted)
        highlighted = highlighted.replace(/'([^']*)'/g, '<span class="str">\'$1\'</span>');

        // Highlight numbers
        highlighted = highlighted.replace(/\b(\d+\.?\d*)\b/g, '<span class="num">$1</span>');

        // Highlight keywords (case-insensitive, whole word)
        keywords.sort((a, b) => b.length - a.length); // Longest first
        keywords.forEach(kw => {
            const regex = new RegExp('\\b(' + kw.replace(/ /g, '\\s+') + ')\\b', 'gi');
            highlighted = highlighted.replace(regex, '<span class="kw">$1</span>');
        });

        // Highlight functions
        highlighted = highlighted.replace(/\b(date|datetime|strftime|now|interval)\b/gi, '<span class="fn">$1</span>');

        display.innerHTML = highlighted;
    },

    /* ── Table with Sorting ── */

    renderTable(columns, rows) {
        const container = document.getElementById('table-container');

        if (!rows || rows.length === 0) {
            container.innerHTML = '<div class="empty-state">No data available for this query.</div>';
            return;
        }

        let html = '<table><thead><tr>';
        columns.forEach((col, idx) => {
            const arrow = this.sortState.column === idx
                ? (this.sortState.ascending ? ' ↑' : ' ↓')
                : ' ↕';
            const sortedClass = this.sortState.column === idx ? ' sorted' : '';
            const displayName = col.replace(/_/g, ' ');
            html += `<th data-col="${idx}" class="${sortedClass}">${this._escapeHtml(displayName)}<span class="sort-arrow">${arrow}</span></th>`;
        });
        html += '</tr></thead><tbody>';

        rows.forEach((row, i) => {
            const delay = Math.min(i * 0.04, 1.5); // Cap max delay at 1.5s
            html += `<tr style="animation-delay: ${delay}s">`;
            row.forEach(val => {
                const display = val === null || val === undefined ? '—' : this._formatCell(val);
                html += `<td>${display}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;

        // Bind sort handlers
        container.querySelectorAll('th[data-col]').forEach(th => {
            th.addEventListener('click', () => {
                const colIdx = parseInt(th.dataset.col);
                this._sortTable(colIdx);
            });
        });
    },

    _sortTable(colIdx) {
        if (!this.currentResult) return;

        if (this.sortState.column === colIdx) {
            this.sortState.ascending = !this.sortState.ascending;
        } else {
            this.sortState.column = colIdx;
            this.sortState.ascending = true;
        }

        const sorted = [...this.currentResult.rows].sort((a, b) => {
            let valA = a[colIdx];
            let valB = b[colIdx];

            // Handle nulls
            if (valA === null || valA === undefined) return 1;
            if (valB === null || valB === undefined) return -1;

            // Numeric comparison
            const numA = parseFloat(valA);
            const numB = parseFloat(valB);
            if (!isNaN(numA) && !isNaN(numB)) {
                return this.sortState.ascending ? numA - numB : numB - numA;
            }

            // String comparison
            const strA = String(valA).toLowerCase();
            const strB = String(valB).toLowerCase();
            if (strA < strB) return this.sortState.ascending ? -1 : 1;
            if (strA > strB) return this.sortState.ascending ? 1 : -1;
            return 0;
        });

        this.renderTable(this.currentResult.columns, sorted);
    },

    _formatCell(val) {
        const str = String(val);
        // Format numbers that look like currency (> 999)
        const num = parseFloat(str);
        if (!isNaN(num) && isFinite(num) && num > 999 && !str.includes('-') && !str.includes(':')) {
            return '₹' + new Intl.NumberFormat('en-IN').format(num);
        }
        return this._escapeHtml(str);
    },

    /* ── SQL Toggle ── */

    toggleSQL() {
        const container = document.getElementById('sql-display-container');
        const icon = document.getElementById('sql-toggle-icon');
        const toggle = document.getElementById('sql-toggle');
        const isHidden = container.style.display === 'none';
        container.style.display = isHidden ? 'block' : 'none';
        icon.textContent = isHidden ? '▲' : '▼';
        toggle.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
    },

    /* ── History ── */

    addToHistory(query) {
        // Remove duplicate if exists
        const idx = this.history.indexOf(query);
        if (idx !== -1) this.history.splice(idx, 1);

        this.history.unshift(query);
        if (this.history.length > 10) this.history.pop();

        this.saveHistory();
        this.renderHistory();
    },

    renderHistory() {
        const list = document.getElementById('history-list');
        const empty = document.getElementById('sidebar-empty');

        if (this.history.length === 0) {
            list.innerHTML = '';
            if (empty) empty.classList.remove('hidden');
            return;
        }

        if (empty) empty.classList.add('hidden');

        list.innerHTML = '';
        this.history.forEach((item, i) => {
            const li = document.createElement('li');
            li.className = 'history-item';
            li.textContent = item;
            li.title = item;
            li.style.animationDelay = `${i * 0.05}s`;
            li.addEventListener('click', () => {
                // Close sidebar on mobile
                document.getElementById('sidebar').classList.remove('open');
                // Set query text and submit
                document.getElementById('query-input').value = item;
                this.handleQuery(item);
            });
            list.appendChild(li);
        });
    },

    loadHistory() {
        try {
            const saved = localStorage.getItem('vaani_history');
            if (saved) {
                this.history = JSON.parse(saved);
                this.renderHistory();
            }
        } catch (e) {
            console.error('Failed to load history:', e);
            this.history = [];
        }
    },

    saveHistory() {
        try {
            localStorage.setItem('vaani_history', JSON.stringify(this.history));
        } catch (e) {
            console.error('Failed to save history:', e);
        }
    },

    /* ── UI Helpers ── */

    showLoading(show) {
        const loading = document.getElementById('loading');
        const submitBtn = document.getElementById('submit-btn');
        const micBtn = document.getElementById('mic-btn');

        loading.style.display = show ? 'flex' : 'none';
        submitBtn.disabled = show;

        if (show) {
            micBtn.disabled = true;
        } else {
            // Only re-enable mic if voice is available
            micBtn.disabled = !voice.isMicAvailable() ||
                              !navigator.mediaDevices ||
                              !navigator.mediaDevices.getUserMedia;
        }
    },

    showToast(msg, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.className = `toast show ${type}`;

        // Auto-dismiss after 4 seconds
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    },

    _toastTimer: null,

    /* ── Utility ── */

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }
};

/* ── Bootstrap ── */
document.addEventListener('DOMContentLoaded', () => app.init());
