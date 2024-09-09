from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    favorites = db.relationship("Favorites", backref="user", lazy=True)

    def __repr__(self):
        return "<User %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    height = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "gender": self.gender,
        }


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    climate = db.Column(db.String(10), nullable=False)
    terrain = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    model = db.Column(db.String(10), nullable=False)
    class_name = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


# TYPES:
# 1: Character
# 2: Planet
# 3: Vehicle

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type_id = db.Column(db.Integer, nullable=True)
    type = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "<Favorites %r>" % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type_id": self.type_id,
            "type": self.type,
        }