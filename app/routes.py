from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from datetime import date, timedelta
import random
from app import db
from app.models import User, Habit, Completion

bp = Blueprint('main', __name__)


# Главная страница - редирект на логин или сегодняшние привычки
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.today'))
    return redirect(url_for('main.login'))


# Страница входа
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.today'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.today'))
        else:
            flash('Неверное имя пользователя или пароль')

    return render_template('login.html')


# Страница регистрации
# Страница регистрации
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.today'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято')
        elif User.query.filter_by(email=email).first():
            flash('Email уже используется')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()  # Сначала сохраняем пользователя

            # Создаем базовые привычки для нового пользователя
            habits_data = [
                ("Регулярный сон", "Ложиться и вставать в одно время даже в выходные"),
                ("Вода с утра", "Выпить стакан воды сразу после пробуждения"),
                ("Ежедневное движение", "30 минут ходьбы, зарядки или растяжки"),
                ("Правило «1-3-5» на день", "Планируйте свой день так: 1 КРУПНОЕ дело, 3 СРЕДНИХ дела и 5 МЕЛКИХ дел."),
                ("Микро-обучение", "Выделите 15-20 минут в день на изучение чего-то нового"),
                ("Вечерняя подготовка", "Потратьте 10 минут вечером на подготовку к следующему дню"),
                ("Чтение", "Читайте 10 страниц в день (около 15-20 минут)")
            ]

            for name, description in habits_data:
                habit = Habit(name=name, description=description, user_id=user.id)
                db.session.add(habit)

            db.session.commit()  # Сохраняем привычки
            print(f"✅ Создано {len(habits_data)} привычек для пользователя {username}")

            flash('Регистрация успешна! Теперь вы можете войти.')
            return redirect(url_for('main.login'))

    return render_template('register.html')
# Выход
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# Главная страница с привычками (только для авторизованных)
@bp.route('/today')
@login_required
def today():
    return render_template('index.html')


# API для получения сегодняшней привычки
@bp.route('/api/today_habit')
@login_required
def get_today_habit():
    print(f"🔍 Получение привычки для пользователя: {current_user.username} (ID: {current_user.id})")

    # Получаем все активные привычки пользователя
    all_habits = Habit.query.filter_by(is_active=True, user_id=current_user.id).all()
    print(f"📊 Найдено привычек: {len(all_habits)}")

    if not all_habits:
        print("❌ Нет активных привычек для пользователя")
        return jsonify({'error': 'No habits found. Please create some habits first.'}), 404

    # Получаем привычки, которые еще НЕ были выполнены сегодня
    today = date.today()
    completed_today = Completion.query.filter_by(
        completion_date=today,
        user_id=current_user.id
    ).with_entities(Completion.habit_id).all()
    completed_habit_ids = [c.habit_id for c in completed_today]

    print(f"✅ Уже выполнено сегодня: {len(completed_habit_ids)} привычек")

    # Ищем привычки, которые еще не выполнены сегодня
    available_habits = [h for h in all_habits if h.id not in completed_habit_ids]
    print(f"📋 Доступно для выполнения: {len(available_habits)} привычек")

    if available_habits:
        # Берем случайную привычку из доступных
        habit = random.choice(available_habits)
        print(f"🎯 Выбрана привычка: {habit.name}")
        return jsonify({
            'habit': habit.to_dict(),
            'already_completed': False,
            'progress': {
                'completed': len(completed_habit_ids),
                'total': len(all_habits),
                'remaining': len(available_habits)
            }
        })
    else:
        # Все привычки выполнены на сегодня
        print("🎉 Все привычки выполнены на сегодня!")
        return jsonify({
            'habit': None,
            'already_completed': True,
            'progress': {
                'completed': len(completed_habit_ids),
                'total': len(all_habits),
                'remaining': 0
            },
            'message': 'Все привычки выполнены на сегодня! 🎉'
        })

# Обработка свайпа
@bp.route('/api/swipe', methods=['POST'])
@login_required
def handle_swipe():
    data = request.get_json()
    habit_id = data.get('habit_id')
    completed = data.get('completed')

    # Проверяем существование привычки и принадлежность пользователю
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404

    # Проверяем, не была ли уже отмечена эта привычка сегодня
    today = date.today()
    existing_completion = Completion.query.filter_by(
        habit_id=habit_id,
        user_id=current_user.id,
        completion_date=today
    ).first()

    if existing_completion:
        # Если уже есть запись, обновляем ее
        existing_completion.completed = completed
        db.session.commit()

        completion_data = existing_completion.to_dict()
        message = "Статус привычки обновлен"
    else:
        # Создаем новую запись о выполнении
        completion = Completion(
            habit_id=habit_id,
            user_id=current_user.id,
            completed=completed,
            completion_date=today
        )
        db.session.add(completion)
        db.session.commit()

        completion_data = completion.to_dict()
        message = "Привычка отмечена"

    # Получаем обновленный прогресс
    all_habits = Habit.query.filter_by(is_active=True, user_id=current_user.id).all()
    completed_today = Completion.query.filter_by(
        completion_date=today,
        user_id=current_user.id,
        completed=True
    ).count()

    return jsonify({
        'success': True,
        'completion': completion_data,
        'progress': {
            'completed': completed_today,
            'total': len(all_habits),
            'remaining': len(all_habits) - completed_today
        },
        'message': message
    })

# Страница статистики
@bp.route('/stats')
@login_required
def stats():
    return render_template('stats.html')


# API для получения статистики
@bp.route('/api/stats')
@login_required
def get_stats():
    # Статистика за последние 7 дней
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    completions = Completion.query.filter(
        Completion.completion_date.between(start_date, end_date),
        Completion.user_id == current_user.id
    ).all()

    # Группируем по дням
    daily_stats = {}
    current_date = start_date
    while current_date <= end_date:
        daily_stats[current_date.isoformat()] = {
            'completed': 0,
            'total': 0,
            'date': current_date.strftime('%d.%m')
        }
        current_date += timedelta(days=1)

    for completion in completions:
        date_key = completion.completion_date.isoformat()
        if date_key in daily_stats:
            daily_stats[date_key]['total'] += 1
            if completion.completed:
                daily_stats[date_key]['completed'] += 1

    # Преобразуем в список для фронтенда
    stats_list = []
    for date_key in sorted(daily_stats.keys()):
        day_data = daily_stats[date_key]
        if day_data['total'] > 0:
            day_data['percentage'] = (day_data['completed'] / day_data['total']) * 100
        else:
            day_data['percentage'] = 0
        stats_list.append(day_data)

    # Общая статистика
    total_completions = Completion.query.filter_by(
        completed=True,
        user_id=current_user.id
    ).count()
    total_attempts = Completion.query.filter_by(user_id=current_user.id).count()
    success_rate = (total_completions / total_attempts * 100) if total_attempts > 0 else 0

    # Получаем общее количество активных привычек пользователя
    total_habits = Habit.query.filter_by(is_active=True, user_id=current_user.id).count()

    # Статистика за сегодня
    today_completions = Completion.query.filter_by(
        completion_date=date.today(),
        completed=True,
        user_id=current_user.id
    ).count()

    return jsonify({
        'daily_stats': stats_list,
        'total_completed': total_completions,
        'total_attempts': total_attempts,
        'success_rate': round(success_rate, 1),
        'average_per_week': round(total_completions / max(1, (total_attempts / 7)), 1),
        'today_progress': {
            'completed': today_completions,
            'total': total_habits,
            'percentage': round((today_completions / total_habits * 100) if total_habits > 0 else 0, 1)
        }
    })


# Вспомогательные API endpoints
@bp.route('/api/habits')
@login_required
def get_all_habits():
    habits = Habit.query.filter_by(is_active=True, user_id=current_user.id).all()
    return jsonify({
        'habits': [habit.to_dict() for habit in habits],
        'total': len(habits)
    })


@bp.route('/api/today_completions')
@login_required
def get_today_completions():
    today = date.today()
    completions = Completion.query.filter_by(
        completion_date=today,
        user_id=current_user.id
    ).all()
    return jsonify({
        'completions': [completion.to_dict() for completion in completions],
        'total': len(completions)
    })