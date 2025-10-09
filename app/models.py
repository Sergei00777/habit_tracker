from datetime import datetime, date
from app import db


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    completed = db.Column(db.Boolean, nullable=False)  # True - выполнено, False - не выполнено
    completion_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Уникальный constraint чтобы нельзя было дважды отметить одну привычку в один день
    __table_args__ = (db.UniqueConstraint('habit_id', 'completion_date', name='unique_habit_per_day'),)

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