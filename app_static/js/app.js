// Основная логика приложения
class HabitTracker {
    constructor() {
        this.currentHabit = null;
        this.completedToday = 0;
        this.totalHabits = 6;
        this.init();
    }

    async init() {
        await this.loadTodayHabit();
        this.setupEventListeners();
    }

    async loadTodayHabit() {
        try {
            const response = await fetch('/api/today_habit');
            const data = await response.json();

            // Обновляем прогресс
            if (data.progress) {
                this.completedToday = data.progress.completed;
                this.totalHabits = data.progress.total;
                this.updateProgress();
            }

            if (data.habit) {
                this.currentHabit = data.habit;
                this.displayHabit(data.habit);

                // Показываем карточку и скрываем сообщение
                document.getElementById('habit-card').style.display = 'block';
                document.getElementById('completion-message').classList.add('hidden');

                // Показываем кнопки десктопа
                const desktopButtons = document.querySelector('.desktop-buttons');
                if (desktopButtons) {
                    desktopButtons.style.display = 'flex';
                }
            } else if (data.already_completed) {
                // Все привычки выполнены
                this.showAllCompletedMessage();
            }
        } catch (error) {
            console.error('Ошибка загрузки привычки:', error);
            this.displayError('Не удалось загрузить привычку');
        }
    }

    displayHabit(habit) {
        document.getElementById('habit-name').textContent = habit.name;
        document.getElementById('habit-description').textContent = habit.description || '';

        // Добавляем ID привычки в карточку для свайпа
        document.getElementById('habit-card').dataset.habitId = habit.id;
    }

    displayError(message) {
        document.getElementById('habit-name').textContent = 'Ошибка';
        document.getElementById('habit-description').textContent = message;
    }

    async handleSwipe(completed) {
        if (!this.currentHabit) return;

        try {
            const response = await fetch('/api/swipe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    habit_id: this.currentHabit.id,
                    completed: completed
                })
            });

            const result = await response.json();

            if (result.success) {
                // Обновляем прогресс
                if (result.progress) {
                    this.completedToday = result.progress.completed;
                    this.totalHabits = result.progress.total;
                    this.updateProgress();
                }

                this.animateSwipe(completed);

                // Загружаем следующую привычку через небольшую задержку
                setTimeout(() => {
                    this.loadTodayHabit();
                }, 500);
            }
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            this.showError('Ошибка сохранения результата');
        }
    }

    animateSwipe(completed) {
        const card = document.getElementById('habit-card');
        card.classList.add(completed ? 'swipe-right' : 'swipe-left');

        setTimeout(() => {
            card.classList.remove('swipe-right', 'swipe-left');
            card.style.transform = 'translateX(0) rotate(0)';
            card.style.opacity = '1';
        }, 500);
    }

    showAllCompletedMessage() {
        document.getElementById('habit-card').style.display = 'none';
        const messageEl = document.getElementById('completion-message');
        messageEl.classList.remove('hidden');
        messageEl.innerHTML = `
            <h3>🎉 Отлично!</h3>
            <p>Все ${this.completedToday} из ${this.totalHabits} привычек выполнены на сегодня!</p>
            <p>Возвращайтесь завтра для новых привычек</p>
        `;

        // Скрываем кнопки десктопа
        const desktopButtons = document.querySelector('.desktop-buttons');
        if (desktopButtons) {
            desktopButtons.style.display = 'none';
        }
    }

    showError(message) {
        const messageEl = document.getElementById('completion-message');
        messageEl.classList.remove('hidden');
        messageEl.innerHTML = `
            <h3>❌ Ошибка</h3>
            <p>${message}</p>
            <button onclick="location.reload()" class="btn btn-success">Обновить страницу</button>
        `;
    }

    updateProgress() {
        document.getElementById('completed-count').textContent = this.completedToday;
        document.getElementById('total-habits').textContent = this.totalHabits;

        // Обновляем прогресс-бар если есть
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            const percentage = (this.completedToday / this.totalHabits) * 100;
            progressBar.style.width = `${percentage}%`;
        }
    }

    setupEventListeners() {
        // Глобальные функции для кнопок десктопа
        window.handleSwipe = (completed) => {
            this.handleSwipe(completed);
        };

        // Обработчик для обновления страницы
        window.refreshApp = () => {
            this.loadTodayHabit();
        };
    }
}

// Логика обработки свайпов для мобильных устройств
class SwipeHandler {
    constructor() {
        this.card = document.getElementById('habit-card');
        this.startX = 0;
        this.currentX = 0;
        this.isSwiping = false;
        this.swipeThreshold = 50;

        if (this.card) {
            this.init();
        }
    }

    init() {
        this.card.addEventListener('touchstart', this.handleTouchStart.bind(this));
        this.card.addEventListener('touchmove', this.handleTouchMove.bind(this));
        this.card.addEventListener('touchend', this.handleTouchEnd.bind(this));

        // Для десктопа тоже добавим поддержку мыши
        this.card.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
    }

    // Touch события
    handleTouchStart(e) {
        this.startSwipe(e.touches[0].clientX);
    }

    handleTouchMove(e) {
        if (!this.isSwiping) return;
        e.preventDefault();
        this.updateSwipe(e.touches[0].clientX);
    }

    handleTouchEnd() {
        this.endSwipe();
    }

    // Mouse события
    handleMouseDown(e) {
        this.startSwipe(e.clientX);
        e.preventDefault();
    }

    handleMouseMove(e) {
        if (!this.isSwiping) return;
        this.updateSwipe(e.clientX);
    }

    handleMouseUp() {
        this.endSwipe();
    }

    // Общая логика свайпа
    startSwipe(clientX) {
        this.startX = clientX;
        this.currentX = 0;
        this.isSwiping = true;
        this.card.style.transition = 'none';
    }

    updateSwipe(clientX) {
        if (!this.isSwiping) return;

        this.currentX = clientX - this.startX;
        this.updateCardTransform();
        this.updateSwipeVisuals();
    }

    endSwipe() {
        if (!this.isSwiping) return;

        this.isSwiping = false;
        this.card.style.transition = 'transform 0.3s ease';

        // Проверяем превышен ли порог свайпа
        if (Math.abs(this.currentX) > this.swipeThreshold) {
            const completed = this.currentX > 0; // вправо - выполнено, влево - не выполнено
            this.completeSwipe(completed);
        } else {
            // Возвращаем карточку на место
            this.resetCard();
        }

        this.clearSwipeVisuals();
    }

    updateCardTransform() {
        const rotation = (this.currentX / 10) * (this.currentX > 0 ? 1 : -1);
        this.card.style.transform = `translateX(${this.currentX}px) rotate(${rotation}deg)`;
    }

    updateSwipeVisuals() {
        this.card.classList.remove('swiping-left', 'swiping-right');

        if (this.currentX < -this.swipeThreshold) {
            this.card.classList.add('swiping-left');
        } else if (this.currentX > this.swipeThreshold) {
            this.card.classList.add('swiping-right');
        }
    }

    clearSwipeVisuals() {
        this.card.classList.remove('swiping-left', 'swiping-right');
    }

    resetCard() {
        this.card.style.transform = 'translateX(0) rotate(0)';
    }

    completeSwipe(completed) {
        // Анимация улетания карточки
        const direction = completed ? 1 : -1;
        this.card.style.transform = `translateX(${direction * 200}px) rotate(${direction * 20}deg)`;
        this.card.style.opacity = '0';

        // Вызываем обработчик из основного приложения
        setTimeout(() => {
            if (window.habitTracker) {
                window.habitTracker.handleSwipe(completed);
            }
        }, 300);
    }
}

// Утилиты для работы с датами
class DateUtils {
    static formatDate(date) {
        return new Date(date).toLocaleDateString('ru-RU');
    }

    static getToday() {
        return new Date().toISOString().split('T')[0];
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Создаем глобальный экземпляр трекера
    window.habitTracker = new HabitTracker();

    // Инициализируем обработчик свайпов
    new SwipeHandler();

    // Добавляем стили для прогресс-бара если его нет
    if (!document.querySelector('#progress-bar-styles')) {
        const style = document.createElement('style');
        style.id = 'progress-bar-styles';
        style.textContent = `
            .progress-bar {
                width: 100%;
                height: 6px;
                background: #e8e8e8;
                border-radius: 3px;
                margin: 10px 0;
                overflow: hidden;
            }

            .progress-bar-fill {
                height: 100%;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                border-radius: 3px;
                transition: width 0.3s ease;
            }
        `;
        document.head.appendChild(style);
    }
});

// Глобальные функции для отладки
window.debugApp = async () => {
    console.log('=== Debug Information ===');

    try {
        const [habitsResponse, completionsResponse] = await Promise.all([
            fetch('/api/habits'),
            fetch('/api/today_completions')
        ]);

        const habitsData = await habitsResponse.json();
        const completionsData = await completionsResponse.json();

        console.log('Все привычки:', habitsData);
        console.log('Выполненные сегодня:', completionsData);
        console.log('Текущая привычка:', window.habitTracker?.currentHabit);
        console.log('Прогресс:', {
            completed: window.habitTracker?.completedToday,
            total: window.habitTracker?.totalHabits
        });
    } catch (error) {
        console.error('Ошибка отладки:', error);
    }
};