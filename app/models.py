from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))


class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    construction_year = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 'public' or 'private'
    visibility = db.Column(db.String(50), default='public')
    owner = db.relationship('Users', backref='houses')


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    house = db.relationship('House', backref='rooms')


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    room = db.relationship('Room', backref='features')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    user = db.relationship('Users', backref='comments')
    house = db.relationship('House', backref='comments')
