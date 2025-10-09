from flask import Blueprint, render_template, jsonify, request
from datetime import date, timedelta
import random
from app import db
from app.models import Habit, Completion

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Главная страница с карточкой привычки"""
    return render_template('index.html')


@bp.route('/api/today_habit')
def get_today_habit():
    """Получить случайную НЕВЫПОЛНЕННУЮ привычку на сегодня"""
    # Получаем все активные привычки
    all_habits = Habit.query.filter_by(is_active=True).all()

    if not all_habits:
        # Создаем тестовые привычки если нет в базе
        habits_data = [
            ("Быстрое выполнение задач", "Выполнять задачи без прокрастинации"),
            ("Утренняя зарядка", "15 минут физической активности утром"),
            ("Чтение книги", "Читать 30 минут в день"),
            ("Медитация", "10 минут медитации для ясности ума"),
            ("Изучение английского", "Практика языка 20 минут"),
            ("Прогулка на свежем воздухе", "Гулять не менее 30 минут")
        ]

        for name, description in habits_data:
            habit = Habit(name=name, description=description)
            db.session.add(habit)
        db.session.commit()
        all_habits = Habit.query.filter_by(is_active=True).all()

    # Получаем привычки, которые еще НЕ были выполнены сегодня
    today = date.today()
    completed_today = Completion.query.filter_by(
        completion_date=today
    ).with_entities(Completion.habit_id).all()
    completed_habit_ids = [c.habit_id for c in completed_today]

    # Ищем привычки, которые еще не выполнены сегодня
    available_habits = [h for h in all_habits if h.id not in completed_habit_ids]

    if available_habits:
        # Берем случайную привычку из доступных
        habit = random.choice(available_habits)
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


@bp.route('/api/swipe', methods=['POST'])
def handle_swipe():
    """Обработать свайп (выполнено/не выполнено)"""
    data = request.get_json()
    habit_id = data.get('habit_id')
    completed = data.get('completed')  # True - вправо, False - влево

    # Проверяем существование привычки
    habit = Habit.query.get(habit_id)
    if not habit:
        return jsonify({'error': 'Habit not found'}), 404

    # Создаем запись о выполнении
    completion = Completion(
        habit_id=habit_id,
        completed=completed,
        completion_date=date.today()
    )
    db.session.add(completion)
    db.session.commit()

    # Получаем обновленный прогресс
    all_habits = Habit.query.filter_by(is_active=True).all()
    today = date.today()
    completed_today = Completion.query.filter_by(completion_date=today).count()

    return jsonify({
        'success': True,
        'completion': completion.to_dict(),
        'progress': {
            'completed': completed_today,
            'total': len(all_habits),
            'remaining': len(all_habits) - completed_today
        }
    })


@bp.route('/stats')
def stats():
    """Страница статистики"""
    return render_template('stats.html')


@bp.route('/api/stats')
def get_stats():
    """API для получения статистики"""
    # Статистика за последние 7 дней
    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    completions = Completion.query.filter(
        Completion.completion_date.between(start_date, end_date)
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
    total_completions = Completion.query.filter_by(completed=True).count()
    total_attempts = Completion.query.count()
    success_rate = (total_completions / total_attempts * 100) if total_attempts > 0 else 0

    # Получаем общее количество активных привычек
    total_habits = Habit.query.filter_by(is_active=True).count()

    # Статистика за сегодня
    today_completions = Completion.query.filter_by(
        completion_date=date.today(),
        completed=True
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


@bp.route('/api/habits')
def get_all_habits():
    """Получить все привычки (для отладки)"""
    habits = Habit.query.filter_by(is_active=True).all()
    return jsonify({
        'habits': [habit.to_dict() for habit in habits],
        'total': len(habits)
    })


@bp.route('/api/today_completions')
def get_today_completions():
    """Получить выполненные привычки за сегодня (для отладки)"""
    today = date.today()
    completions = Completion.query.filter_by(completion_date=today).all()

    return jsonify({
        'completions': [completion.to_dict() for completion in completions],
        'total': len(completions)
    })