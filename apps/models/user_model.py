from datetime import datetime
from exts import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        return self.username


