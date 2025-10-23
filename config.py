import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Безопасность
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Сессия
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Настройки приложения
    HABITS_PER_DAY = 6

    @classmethod
    def print_db_path(cls):
        db_path = os.path.join(basedir, "instance", "app.db")
        print(f"📁 Путь к базе данных: {db_path}")