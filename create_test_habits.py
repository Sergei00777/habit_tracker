from app import create_app, db
from app.models import User, Habit

app = create_app()

def create_test_habits():
    with app.app_context():
        # Найдем первого пользователя
        user = User.query.first()
        if not user:
            print("❌ Нет пользователей в базе данных!")
            return

        print(f"👤 Найден пользователь: {user.username}")

        # Проверим, есть ли уже привычки
        existing_habits = Habit.query.filter_by(user_id=user.id).count()
        if existing_habits > 0:
            print(f"✅ У пользователя уже есть {existing_habits} привычек")
            return

        # Создаем тестовые привычки
        habits_data = [
            ("Регулярный сон", "Ложиться и вставать в одно время даже в выходные"),
            ("Вода с утра", "Выпить стакан воды сразу после пробуждения"),
            ("Ежедневное движение", "30 минут ходьбы, зарядки или растяжки"),
            ("Планирование дня", "Составить план на день утром"),
            ("Изучение нового", "15-20 минут в день на изучение чего-то нового"),
            ("Вечерний ритуал", "10 минут на подготовку к следующему дню")
        ]

        for name, description in habits_data:
            habit = Habit(name=name, description=description, user_id=user.id)
            db.session.add(habit)

        db.session.commit()
        print(f"✅ Создано {len(habits_data)} тестовых привычек для пользователя {user.username}")

if __name__ == '__main__':
    create_test_habits()