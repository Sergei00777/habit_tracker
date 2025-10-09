from app import create_app, db
from app.models import Habit

app = create_app()


def init_database():
    with app.app_context():
        # Создаем все таблицы
        db.create_all()

        # Добавляем тестовые привычки если их нет
        if Habit.query.count() == 0:
            habits = [
                Habit(
                    name="Быстрое выполнение задач",
                    description="Выполнять задачи без прокрастинации"
                ),
                Habit(
                    name="Утренняя зарядка",
                    description="15 минут физической активности утром"
                ),
                Habit(
                    name="Чтение книги",
                    description="Читать 30 минут в день"
                ),
                Habit(
                    name="Медитация",
                    description="10 минут медитации для ясности ума"
                ),
                Habit(
                    name="Изучение английского",
                    description="Практика языка 20 минут"
                ),
                Habit(
                    name="Прогулка на свежем воздухе",
                    description="Гулять не менее 30 минут"
                )
            ]

            for habit in habits:
                db.session.add(habit)

            db.session.commit()
            print("✅ База данных инициализирована! Добавлено 6 тестовых привычек.")
        else:
            print("✅ База данных уже существует.")


if __name__ == '__main__':
    init_database()