from datetime import datetime
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from proctor import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(80))
    notes = db.relationship('Note', backref='user', lazy='dynamic')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    last_modified = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.last_modified = datetime.utcnow()
        self.user_id = user_id
class verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(120))
    last_modified = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, status, content, user_id):
        self.status = status
        self.last_modified = datetime.utcnow()
        self.user_id = user_id

class Enrollment(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),  nullable=False, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    exam = db.Column(db.String(120))
    last_modified = db.Column(db.DateTime)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, username, email, exam):
        self.username = username
        self.email = email
        self.exam = exam
