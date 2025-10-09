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
                    Habit(name="Съесть лягушку утром", description="Выполнить самое сложное дело первым делом с утра"),
                    Habit(name="Вечернее планирование",
                          description="Потратить 5 минут на план задач на завтрашний день"),
                    Habit(name="Техника Pomodoro", description="Работать 25 минут, затем 5 минут отдыха"),
                    Habit(name="Правило одного процента", description="Улучшать навык на 1% каждый день"),
                    Habit(name="Метод 'Только начать'", description="Начать задачу всего на 5-10 минут"),

                    # 🧠 Мышление и Психическое здоровье
                    Habit(name="Дневник благодарности", description="Записать 3 вещи, за которые благодарен сегодня"),
                    Habit(name="Утренние страницы", description="Выписать все мысли на 3 листа после пробуждения"),
                    Habit(name="Качественные вопросы",
                          description="Спросить 'Как решить?' вместо 'Почему я неудачник?'"),
                    Habit(name="Информационная диета", description="Ограничить потребление новостей и соцсетей"),
                    Habit(name="Цифровой детокс", description="Провести 1 час без гаджетов"),

                    # 💪 Физическое здоровье и Энергия
                    Habit(name="Вода с утра", description="Выпить стакан воды сразу после пробуждения"),
                    Habit(name="Ежедневное движение", description="30 минут ходьбы, зарядки или растяжки"),
                    Habit(name="Приготовление еды", description="Заготовить здоровую еду на неделю"),
                    Habit(name="Регулярный сон", description="Ложиться и вставать в одно время даже в выходные"),
                    Habit(name="Утреннее солнце", description="Провести 15-20 минут на утреннем солнце"),

                    # 🤝 Отношения и Личностный рост
                    Habit(name="Активное слушание", description="Слушать собеседника, не думая о ответе"),
                    Habit(name="Глубокое общение", description="Провести время с близкими без гаджетов"),
                    Habit(name="Ежедневное чтение", description="Читать 20-30 минут в день"),
                    Habit(name="Выход из зоны комфорта", description="Сделать что-то новое и пугающее"),
                    Habit(name="Еженедельное ревью", description="Проанализировать неделю и составить планы")
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