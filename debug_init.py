import os
from app import create_app, db
from app.models import Habit

app = create_app()


def debug_database():
    with app.app_context():
        print("🔍 Отладочная информация:")

        # Проверяем пути
        db_path = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"📁 Путь к БД из конфига: {db_path}")

        # Пытаемся создать БД
        try:
            print("🔄 Создаем таблицы...")
            db.create_all()
            print("✅ Таблицы созданы успешно!")

            # Добавляем тестовые данные
            print("🔄 Добавляем тестовые привычки...")
            if Habit.query.count() == 0:
                habits = [
                    # 💡 Продуктивность и Фокус
                    Habit(name="Регулярный сон", description="Ложиться и вставать в одно время даже в выходные"),
                    Habit(name="Вода с утра", description="Выпить стакан воды сразу после пробуждения"),
                    Habit(name="Ежедневное движение", description="30 минут ходьбы, зарядки или растяжки"),
                    Habit(name="Правило «1-3-5» на день", description="Планируйте свой день так: 1 КРУПНОЕ дело, 3 СРЕДНИХ дела и 5 МЕЛКИХ дел."),

                    # 🧠 Мышление и Психическое здоровье
                    Habit(name="Микро-обучение", description="Выделите 15-20 минут в день на изучение чего-то нового"),
                    Habit(name="Вечерняя подготовка", description="Потратьте 10 минут вечером на то, чтобы подготовить что-то, помыть посуду"),
                    Habit(name="Читайте 10 страниц в день", description="Это около 15-20 минут. За год вы прочитаете 12-15 книг."),


                ]

                for habit in habits:
                    db.session.add(habit)

                db.session.commit()
                print("Привычки успешно добавлены в базу данных!")
                for habit in habits:
                    db.session.add(habit)
                db.session.commit()
                print("✅ Тестовые привычки добавлены!")
            else:
                print("✅ Привычки уже есть в базе")

            # Проверяем существование файла БД
            db_file_path = db_path.replace('sqlite:///', '')
            print(f"📁 Файл БД существует: {os.path.exists(db_file_path)}")
            if os.path.exists(db_file_path):
                print(f"📁 Размер файла: {os.path.getsize(db_file_path)} байт")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    debug_database()