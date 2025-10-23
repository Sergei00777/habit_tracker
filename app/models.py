from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    habits = db.relationship('Habit', backref='user', lazy='dynamic')
    completions = db.relationship('Completion', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Связь с выполнениями
    completions = db.relationship('Completion', backref='habit', lazy='dynamic')

    def __repr__(self):
        return f'<Habit {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Completion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    completion_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Уникальный constraint чтобы нельзя было дважды отметить одну привычку в один день
    __table_args__ = (
        db.UniqueConstraint('habit_id', 'completion_date', 'user_id', name='unique_habit_per_day_per_user'),)

    def __repr__(self):
        status = "✓" if self.completed else "✗"
        return f'<Completion {self.habit_id} {self.completion_date} {status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'completed': self.completed,
            'completion_date': self.completion_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))