import sys
import os

# Добавляем путь к проекту
project_path = '/var/www/u3303458/data/www/xn---365-43dl5br6bk3f3b.xn--p1ai'
sys.path.insert(0, project_path)

# Указываем путь к виртуальному окружению
INTERP = '/var/www/u3303458/data/flaskenv/bin/python'
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

from app import create_app

# Создаем application объект для Passenger
application = create_app()