from flask_login import UserMixin
import os
import datetime
from sqlalchemy.orm import relationship
path = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.append(path)
from db_config import db

UserTask = db.Table('user_task',
            db.Column('id', db.Integer, primary_key=True),
            db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
                        nullable=False),
            db.Column('ml_task_id', db.Integer, db.ForeignKey('ml_task.id', ondelete='CASCADE'),
                        nullable=False))

class MethodType(db.Model):
    __tablename__ = 'ml_task_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(100))
    method = relationship("Method", backref='task_type')

class DataMethod(db.Model):
    __tablename__ = 'data_method'
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'), primary_key=True)
    data_charact_id = db.Column(db.Integer, db.ForeignKey('data_charact.id'), primary_key=True)
    points = db.Column(db.Integer)
    method = relationship('Method', back_populates="characters")
    character = relationship('DataCharact', back_populates="methods")

class Method(db.Model):
    __tablename__ = 'method'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable=False)
    task_type_id = db.Column(db.Integer, db.ForeignKey('ml_task_type.id'), nullable=False)
    description = db.Column(db.String(500))
    characters = db.relationship('DataMethod', back_populates="method")

class MlTool(db.Model):
    __tablename__ = 'implementation_tool'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('method.id', ondelete='CASCADE'), nullable=False)
    level_type_id = db.Column(db.Integer, db.ForeignKey('level_type.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(200))
    link = db.Column(db.Text)

class MlTask(db.Model):
    __tablename__ = 'ml_task'
    id = db.Column(db.Integer, primary_key=True)
    ml_type = db.Column(db.Integer, db.ForeignKey('ml_task_type.id'))
    description = db.Column(db.String(200))
    create_datetime = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    outliers = db.Column(db.String(200))
    data_rows = db.Column(db.String(200))
    data_features = db.Column(db.String(200))
    class_imbalance = db.Column(db.String(200))
    categorical_data = db.Column(db.String(200))
    blank_data = db.Column(db.String(200))
    recommend_method = db.Column(db.Text)
    recomment_tool = db.Column(db.Text)
    link = db.Column(db.Text)

class DataCharact(db.Model):
    __tablename__ = 'data_charact'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    form_class = db.Column(db.Integer)
    methods = relationship('DataMethod', back_populates="character")


    


