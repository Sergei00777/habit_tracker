from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__,
        template_folder='../app_templates',
        static_folder='../app_static'
    )
    app.config.from_object(config_class)

    # Выведем путь к БД для отладки
    config_class.print_db_path()

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp
    app.register_blueprint(bp)

    return app