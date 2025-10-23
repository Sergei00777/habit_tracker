from app import create_app, db
from app.models import User

app = create_app()


def init_database():
    with app.app_context():
        # Создаем все таблицы
        print("🔄 Создаем таблицы базы данных...")
        db.create_all()
        print("✅ Таблицы созданы успешно!")

        # Проверяем создание (совместимый способ)
        try:
            # Для SQLAlchemy >= 1.4
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
        except AttributeError:
            # Для SQLAlchemy < 1.4
            tables = db.engine.table_names()

        print(f"📊 Созданные таблицы: {tables}")

        # Проверяем, что можем работать с моделями
        try:
            users_count = User.query.count()
            print(f"👥 Пользователей в БД: {users_count}")
        except Exception as e:
            print(f"⚠️ Ошибка при проверке пользователей: {e}")


if __name__ == '__main__':
    init_database()