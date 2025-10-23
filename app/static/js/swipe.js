class SwipeHandler {
    constructor() {
        this.card = document.getElementById('habit-card');
        this.startX = 0;
        this.currentX = 0;
        this.isSwiping = false;
        this.swipeThreshold = 50;
        this.isProcessing = false;

        if (this.card) {
            this.init();
            console.log('👆 SwipeHandler initialized');
        } else {
            console.error('❌ Habit card not found for swipe handler');
        }
    }

    init() {
        // Touch события
        this.card.addEventListener('touchstart', this.handleTouchStart.bind(this));
        this.card.addEventListener('touchmove', this.handleTouchMove.bind(this));
        this.card.addEventListener('touchend', this.handleTouchEnd.bind(this));

        // Mouse события для десктопа
        this.card.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
    }

    handleTouchStart(e) {
        this.startSwipe(e.touches[0].clientX);
        e.preventDefault();
    }

    handleTouchMove(e) {
        if (!this.isSwiping) return;
        e.preventDefault();
        this.updateSwipe(e.touches[0].clientX);
    }

    handleTouchEnd(e) {
        this.endSwipe();
        e.preventDefault();
    }

    handleMouseDown(e) {
        this.startSwipe(e.clientX);
        e.preventDefault();
    }

    handleMouseMove(e) {
        if (!this.isSwiping) return;
        this.updateSwipe(e.clientX);
    }

    handleMouseUp(e) {
        this.endSwipe();
    }

    startSwipe(clientX) {
        if (this.isProcessing) return;

        this.startX = clientX;
        this.currentX = 0;
        this.isSwiping = true;
        this.card.style.transition = 'none';
        this.card.style.cursor = 'grabbing';
    }

    updateSwipe(clientX) {
        if (!this.isSwiping) return;

        this.currentX = clientX - this.startX;
        this.updateCardTransform();
        this.updateSwipeVisuals();
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

    endSwipe() {
        if (!this.isSwiping || this.isProcessing) return;

        this.isSwiping = false;
        this.card.style.transition = 'transform 0.3s ease';
        this.card.style.cursor = 'grab';

        const absX = Math.abs(this.currentX);

        if (absX > this.swipeThreshold) {
            const completed = this.currentX > 0;
            this.isProcessing = true;
            this.completeSwipe(completed);
        } else {
            this.resetCard();
        }

        this.clearSwipeVisuals();
    }

    resetCard() {
        this.card.style.transform = 'translateX(0) rotate(0)';
    }

    clearSwipeVisuals() {
        this.card.classList.remove('swiping-left', 'swiping-right');
    }

    completeSwipe(completed) {
        console.log(`🎯 Завершение свайпа: ${completed ? 'Выполнено' : 'Пропущено'}`);

        const direction = completed ? 1 : -1;
        const animationClass = completed ? 'swipe-right' : 'swipe-left';

        this.card.classList.add(animationClass);

        setTimeout(() => {
            // Вызываем основной обработчик
            if (window.habitTracker && typeof window.habitTracker.handleSwipe === 'function') {
                window.habitTracker.handleSwipe(completed);
            } else {
                console.error('❌ HabitTracker not available, using fallback');
                this.handleSwipeDirectly(completed);
            }

            // Разблокируем через 1 секунду
            setTimeout(() => {
                this.isProcessing = false;
                console.log('🔓 Swipe handler unlocked');
            }, 1000);
        }, 300);
    }

    async handleSwipeDirectly(completed) {
        try {
            const habitId = this.card.dataset.habitId;
            if (!habitId) {
                console.error('❌ No habit ID found');
                return;
            }

            console.log(`🔄 Прямой вызов API для привычки ${habitId}, completed: ${completed}`);

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
                console.log('✅ Свайп успешно сохранен, перезагрузка страницы');
                location.reload();
            } else {
                console.error('❌ Ошибка свайпа:', response.status);
            }
        } catch (error) {
            console.error('❌ Ошибка сети при свайпе:', error);
        }
    }
}

// Инициализация с задержкой чтобы HabitTracker успел загрузиться
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const card = document.getElementById('habit-card');
        if (card) {
            new SwipeHandler();
            console.log('👆 Swipe handler создан');
        } else {
            console.log('⏳ Карточка не найдена, повторная попытка через 500ms...');
            setTimeout(() => {
                const retryCard = document.getElementById('habit-card');
                if (retryCard) {
                    new SwipeHandler();
                    console.log('👆 Swipe handler создан при повторной попытке');
                }
            }, 500);
        }
    }, 100);
});