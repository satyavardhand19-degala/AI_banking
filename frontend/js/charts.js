/* Vaani AI Banking Intelligence — Chart Manager */

let currentChart = null;

const charts = {
    render(columns, rows) {
        const container = document.getElementById('chart-container');
        const canvas = document.getElementById('chart-canvas');
        
        // Clear previous
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }
        
        const type = this.detectType(columns, rows);
        
        if (type === 'none') {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';

        if (type === 'bignumber') {
            this.renderBigNumber(columns, rows);
            return;
        }

        const ctx = canvas.getContext('2d');
        const config = this.getConfig(type, columns, rows);
        currentChart = new Chart(ctx, config);
    },

    detectType(columns, rows) {
        if (rows.length === 0) return 'none';
        
        // Big Number: 1 row, 1 numeric column
        if (rows.length === 1 && columns.length === 1 && !isNaN(rows[0][0])) {
            return 'bignumber';
        }

        // Bar Chart: 2 columns (category, value)
        if (columns.length === 2 && !isNaN(rows[0][1])) {
            return 'bar';
        }

        return 'none';
    },

    renderBigNumber(columns, rows) {
        const container = document.getElementById('chart-container');
        const label = columns[0].replace(/_/g, ' ').toUpperCase();
        const value = rows[0][0];
        
        container.innerHTML = `
            <div class="big-number-container">
                <div class="big-number-label">${label}</div>
                <div class="big-number-value">${this.formatValue(value)}</div>
            </div>
        `;
    },

    formatValue(val) {
        if (isNaN(val)) return val;
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(val);
    },

    getConfig(type, columns, rows) {
        const labels = rows.map(r => r[0]);
        const data = rows.map(r => r[1]);

        return {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: columns[1].replace(/_/g, ' '),
                    data: data,
                    backgroundColor: 'rgba(45, 212, 191, 0.2)',
                    borderColor: '#2dd4bf',
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#8b98b4' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#8b98b4' }
                    }
                }
            }
        };
    }
};
