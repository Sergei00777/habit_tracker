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
            } else {
                // Fallback если habitTracker не инициализирован
                this.handleSwipeDirectly(completed);
            }
        }, 300);
    }

    async handleSwipeDirectly(completed) {
        // Прямой вызов API если основной трекер не доступен
        try {
            const habitId = this.card.dataset.habitId;
            if (!habitId) return;

            const response = await fetch('/api/swipe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    habit_id: parseInt(habitId),
                    completed: completed
                })
            });

            if (response.ok) {
                location.reload(); // Перезагружаем страницу как fallback
            }
        } catch (error) {
            console.error('Ошибка свайпа:', error);
        }
    }
}

// Инициализация свайпа
document.addEventListener('DOMContentLoaded', () => {
    new SwipeHandler();
});