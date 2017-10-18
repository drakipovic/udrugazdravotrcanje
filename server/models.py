from werkzeug.security import generate_password_hash, check_password_hash

from main import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))

    def __init__(self, username, password, name, surname):
        self.username = username
        self.password_hash = self._set_password(password)
        self.name = name
        self.surname = surname

    def _set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class League(db.Model):
    __tablename__ = 'leagues'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    name = db.Column(db.String(1500))
    rounds = db.Column(db.Integer)

    def __init__(self, year, name, rounds):
        self.year = year
        self.name = name
        self.rounds = rounds

    def __iter__(self):
        yield 'id', self.id
        yield 'year', self.year
        yield 'name', self.name
        yield 'rounds', self.rounds
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()