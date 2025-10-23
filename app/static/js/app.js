class HabitTracker {
    constructor() {
        this.currentHabit = null;
        this.completedToday = 0;
        this.totalHabits = 0;
        this.init();
    }

    async init() {
        await this.loadTodayHabit();
        this.setupEventListeners();
        console.log('HabitTracker initialized');
    }

    async loadTodayHabit() {
        try {
            console.log("🔄 Загрузка сегодняшней привычки...");
            const response = await fetch('/api/today_habit');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("📦 Получены данные:", data);

            if (data.error) {
                this.displayError(data.error);
                return;
            }

            if (data.progress) {
                this.completedToday = data.progress.completed;
                this.totalHabits = data.progress.total;
                this.updateProgress();
            }

            if (data.habit) {
                this.currentHabit = data.habit;
                this.displayHabit(data.habit);
                this.showHabitCard();
                console.log("✅ Привычка загружена:", data.habit.name);
            } else if (data.already_completed) {
                this.showAllCompletedMessage();
                console.log("ℹ️ Все привычки выполнены");
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки привычки:', error);
            this.displayError('Не удалось загрузить привычку. Проверьте подключение.');
        }
    }

    displayHabit(habit) {
        const habitName = document.getElementById('habit-name');
        const habitDescription = document.getElementById('habit-description');

        // Обрезаем длинный текст если нужно
        let displayName = habit.name;
        if (displayName.length > 30) {
            displayName = displayName.substring(0, 30) + '...';
        }

        let displayDescription = habit.description || 'Описание отсутствует';
        if (displayDescription.length > 80) {
            displayDescription = displayDescription.substring(0, 80) + '...';
        }

        habitName.textContent = displayName;
        habitDescription.textContent = displayDescription;
        document.getElementById('habit-card').dataset.habitId = habit.id;

        // Сбрасываем стили
        habitName.style.color = '#2c3e50';
    }

    showHabitCard() {
        const card = document.getElementById('habit-card');
        card.style.display = 'block';
        card.style.opacity = '1';
        card.style.transform = 'translateX(0) rotate(0)';
        card.classList.remove('swipe-left', 'swipe-right');
        document.getElementById('completion-message').classList.add('hidden');
    }

    displayError(message) {
        const habitName = document.getElementById('habit-name');
        const habitDescription = document.getElementById('habit-description');

        habitName.textContent = 'Ошибка загрузки';
        habitDescription.textContent = message;
        habitName.style.color = '#e74c3c';
    }

    showAllCompletedMessage() {
        document.getElementById('habit-card').style.display = 'none';
        document.getElementById('completion-message').classList.remove('hidden');
    }

    updateProgress() {
        document.getElementById('completed-count').textContent = this.completedToday;
        document.getElementById('total-habits').textContent = this.totalHabits;
    }

    async handleSwipe(completed) {
        if (!this.currentHabit) {
            console.error('❌ Нет текущей привычки для свайпа');
            return;
        }

        console.log(`🔄 Обработка свайпа: ${completed ? 'Выполнено' : 'Пропущено'} для привычки`, this.currentHabit);

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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('📦 Результат свайпа:', result);

            if (result.success) {
                if (result.progress) {
                    this.completedToday = result.progress.completed;
                    this.totalHabits = result.progress.total;
                    this.updateProgress();
                }

                // Анимируем исчезновение карточки
                this.animateSwipe(completed);

                // Загружаем следующую привычку через 500ms
                setTimeout(() => {
                    this.loadTodayHabit();
                }, 500);

            } else {
                console.error('❌ Ошибка свайпа:', result.error);
                this.showError(result.error || 'Ошибка при сохранении');
            }
        } catch (error) {
            console.error('❌ Ошибка сети:', error);
            this.showError('Ошибка сети при сохранении');
        }
    }

    animateSwipe(completed) {
        const card = document.getElementById('habit-card');
        const direction = completed ? 1 : -1;

        // Анимация улетания
        card.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
        card.style.transform = `translateX(${direction * 300}px) rotate(${direction * 25}deg)`;
        card.style.opacity = '0';
    }

    showError(message) {
        // Простой показ ошибки
        alert(message);
    }

    setupEventListeners() {
        // Делаем функцию глобальной для вызова из HTML
        window.handleSwipe = (completed) => {
            this.handleSwipe(completed);
        };

        console.log('📝 Event listeners setup');
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM загружен, инициализация HabitTracker...');
    window.habitTracker = new HabitTracker();
});