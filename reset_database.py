from app import create_app, db
from app.models import User, Habit
import os

app = create_app()


def reset_database():
    with app.app_context():
        # Удаляем все таблицы
        print("🗑️ Удаляем старые таблицы...")
        db.drop_all()

        # Создаем таблицы заново
        print("🔄 Создаем новые таблицы...")
        db.create_all()

        # Создаем тестового пользователя
        print("👤 Создаем тестового пользователя...")
        user = User(username='test', email='test@example.com')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()

        # Создаем привычки для тестового пользователя
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
        print(f"✅ Создано {len(habits_data)} привычек для пользователя {user.username}")


if __name__ == '__main__':
    reset_database()