from flask_login import UserMixin
import os
path = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.append(path)
from db_config import db
sys.path.append(os.path.abspath(__file__))
from .directory import MlTask, UserTask
import datetime

UserRole = db.Table('userrole',
            db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                        nullable=False),
            db.Column('role_id', db.Integer, db.ForeignKey('role.id'),
                        nullable=False))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    email = db.Column(db.String(200))
    type = db.Column(db.Integer, db.ForeignKey('level_type.id'))
    password = db.Column(db.String(100))
    create_datetime = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    roles = db.relationship('Role', secondary=UserRole, backref=db.backref('users', lazy=True), passive_deletes=True)
    tasks = db.relationship('MlTask', secondary=UserTask, backref=db.backref('users', lazy=True), passive_deletes=True)
    
    def __init__ (self, name, email, type, password):
        self.name = name
        self.email = email
        self.type = type
        self.password = password

class Role(UserMixin, db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))

    def __init__ (self, name, description):
        self.name = name
        self.description = description

class LevelType(db.Model):
    __tablename__ = 'level_type'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))


