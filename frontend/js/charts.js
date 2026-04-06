/* Vaani AI Banking Intelligence — Chart Manager */

let currentChart = null;

const charts = {
    /**
     * Render the appropriate chart based on query results.
     * Detects type automatically: bar, line, bignumber, or none.
     */
    render(columns, rows) {
        const chartContainer = document.getElementById('chart-container');
        const bnContainer = document.getElementById('bignumber-container');
        const canvas = document.getElementById('chart-canvas');

        // Destroy previous chart instance
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }

        // Reset containers
        chartContainer.style.display = 'none';
        bnContainer.style.display = 'none';
        bnContainer.innerHTML = '';

        const type = this.detectType(columns, rows);

        if (type === 'none') return;

        if (type === 'bignumber') {
            this.renderBigNumber(columns, rows, bnContainer);
            return;
        }

        // Show chart canvas container
        chartContainer.style.display = 'block';

        const ctx = canvas.getContext('2d');
        const config = this.getConfig(type, columns, rows);
        currentChart = new Chart(ctx, config);
    },

    /**
     * Auto-detect chart type based on column structure and data.
     */
    detectType(columns, rows) {
        if (!rows || rows.length === 0) return 'none';

        // Big Number: 1 row, 1 column, numeric value
        if (rows.length === 1 && columns.length <= 2) {
            const val = rows[0][columns.length - 1];
            if (this._isNumeric(val)) return 'bignumber';
        }

        if (columns.length < 2) return 'none';

        // Check if second column is numeric
        const hasNumericCol = rows.some(r => this._isNumeric(r[1]));
        if (!hasNumericCol) return 'none';

        // Line chart: first column looks like a date
        const firstVals = rows.slice(0, 5).map(r => String(r[0]));
        const looksLikeDate = firstVals.every(v =>
            /\d{4}-\d{2}-\d{2}/.test(v) || !isNaN(Date.parse(v))
        );

        if (looksLikeDate && rows.length > 1) return 'line';

        // Bar chart: categorical first column + numeric second
        if (columns.length >= 2 && hasNumericCol) return 'bar';

        return 'none';
    },

    /**
     * Render a big number card (aggregate results like SUM, COUNT).
     */
    renderBigNumber(columns, rows, container) {
        const label = columns[columns.length - 1].replace(/_/g, ' ').toUpperCase();
        const value = rows[0][columns.length - 1];

        container.style.display = 'block';
        container.innerHTML = `
            <div class="big-number-label">${this._escapeHtml(label)}</div>
            <div class="big-number-value">${this.formatValue(value)}</div>
        `;
    },

    /**
     * Format a numeric value with Indian currency formatting.
     */
    formatValue(val) {
        if (!this._isNumeric(val)) return String(val);
        const num = parseFloat(val);
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(num);
    },

    /**
     * Build Chart.js configuration for bar or line chart.
     */
    getConfig(type, columns, rows) {
        const labels = rows.map(r => this._truncateLabel(String(r[0])));
        const data = rows.map(r => parseFloat(r[1]) || 0);

        const isBar = type === 'bar';

        return {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: columns[1].replace(/_/g, ' '),
                    data: data,
                    backgroundColor: isBar
                        ? 'rgba(212, 168, 83, 0.25)'
                        : 'rgba(45, 212, 191, 0.08)',
                    borderColor: isBar ? '#d4a853' : '#2dd4bf',
                    borderWidth: 2,
                    borderRadius: isBar ? 8 : 0,
                    pointBackgroundColor: isBar ? undefined : '#2dd4bf',
                    pointBorderColor: isBar ? undefined : '#2dd4bf',
                    pointRadius: isBar ? undefined : 4,
                    pointHoverRadius: isBar ? undefined : 6,
                    tension: isBar ? undefined : 0.3,
                    fill: !isBar
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#8b98b4',
                            font: { family: "'Syne', sans-serif", size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#111e35',
                        titleColor: '#f0ece3',
                        bodyColor: '#8b98b4',
                        borderColor: 'rgba(212,168,83,0.3)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: { family: "'Syne', sans-serif" },
                        bodyFont: { family: "'JetBrains Mono', monospace", size: 12 },
                        callbacks: {
                            label: function(ctx) {
                                const val = ctx.parsed.y;
                                return ' ₹' + new Intl.NumberFormat('en-IN').format(val);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
                        ticks: {
                            color: '#8b98b4',
                            font: { family: "'JetBrains Mono', monospace", size: 11 },
                            callback: function(val) {
                                if (val >= 1000) return '₹' + (val / 1000).toFixed(0) + 'k';
                                return '₹' + val;
                            }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: '#8b98b4',
                            font: { family: "'Syne', sans-serif", size: 11 },
                            maxRotation: 45
                        }
                    }
                }
            }
        };
    },

    /* ── Utility Methods ── */

    _isNumeric(val) {
        if (val === null || val === undefined || val === '') return false;
        return !isNaN(parseFloat(val)) && isFinite(val);
    },

    _truncateLabel(label, maxLen = 20) {
        if (label.length <= maxLen) return label;
        return label.substring(0, maxLen - 1) + '…';
    },

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
};
