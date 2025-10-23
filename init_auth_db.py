from app import create_app, db
from app.models import User, Habit

app = create_app()

def init_database():
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("✅ Таблицы базы данных созданы!")

if __name__ == '__main__':
    init_database()