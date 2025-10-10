class StatsManager {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadStats();
        this.setupAutoRefresh();
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            this.updateOverview(data);
            this.updateTodayProgress(data.today_progress);
            this.renderWeeklyChart(data.daily_stats);
        } catch (error) {
            console.error('Ошибка загрузки статистики:', error);
            this.showError('Не удалось загрузить статистику');
        }
    }

    updateOverview(data) {
        document.getElementById('total-completed').textContent = data.total_completed;
        document.getElementById('success-rate').textContent = data.success_rate + '%';
        document.getElementById('average-week').textContent = data.average_per_week;
    }

    updateTodayProgress(todayProgress) {
        const percentage = todayProgress.percentage;
        document.getElementById('today-progress-bar').style.width = percentage + '%';
        document.getElementById('today-progress-text').textContent =
            `${todayProgress.completed}/${todayProgress.total} выполнено (${percentage}%)`;
    }

    renderWeeklyChart(dailyStats) {
        const chart = document.getElementById('weekly-chart');
        chart.innerHTML = '';

        dailyStats.forEach(day => {
            const dayElement = document.createElement('div');
            dayElement.className = 'chart-day';

            const percentage = day.total > 0 ? (day.completed / day.total) * 100 : 0;

            dayElement.innerHTML = `
                <div class="chart-bar-container">
                    <div class="chart-bar" style="height: ${percentage}%"></div>
                </div>
                <div class="chart-label">${day.date}</div>
                <div class="chart-value">${day.completed}/${day.total}</div>
            `;

            chart.appendChild(dayElement);
        });
    }

    setupAutoRefresh() {
        // Обновляем статистику каждые 30 секунд
        setInterval(() => {
            this.loadStats();
        }, 30000);
    }

    showError(message) {
        const container = document.querySelector('.stats-container');
        container.innerHTML = `
            <div class="error-message">
                <h3>❌ Ошибка</h3>
                <p>${message}</p>
                <button onclick="location.reload()">Обновить страницу</button>
            </div>
        `;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new StatsManager();
});