from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from main import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    gender = db.Column(db.String(5))
    age = db.Column(db.Integer)

    race_results = db.relationship('RaceResult', backref='user', lazy='select', cascade='all, delete, delete-orphan')

    def __init__(self, username, password, name, surname, gender, age):
        self.username = username
        self.password_hash = self._set_password(password)
        self.name = name
        self.surname = surname
        self.gender = gender
        self.age = age

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

    league_id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    name = db.Column(db.String(1500))
    rounds = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_by = db.relationship('User', backref='created_by')

    races = db.relationship('Race', backref='leagues', lazy='select', cascade='all, delete, delete-orphan')
    race_categories = db.relationship('RaceCategory', backref='leagues', lazy='select')

    def __init__(self, year, name, rounds, created_by, races, race_categories):
        self.year = year
        self.name = name
        self.rounds = rounds
        self.created_by = created_by
        self.races = races
        self.race_categories = race_categories

    def __iter__(self):
        yield 'id', self.league_id
        yield 'year', self.year
        yield 'name', self.name
        yield 'rounds', self.rounds
        yield 'created_by', self.created_by.username
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Race(db.Model):
    __tablename__ = 'races'

    race_id = db.Column(db.Integer, primary_key=True)
    league_round = db.Column(db.Integer)
    league_year = db.Column(db.Integer)
    finished = db.Column(db.Boolean)
    start_time = db.Column(db.DateTime())

    league_id = db.Column(db.Integer, db.ForeignKey('leagues.league_id'))
    race_results = db.relationship('RaceResult', backref='users', lazy='select', cascade='all, delete, delete-orphan')


    def __init__(self, league_year, league_round, start_time=None, finished=False):
        self.league_year = league_year
        self.league_round = league_round
        self.finished = finished
        self.start_time = start_time

    def __iter__(self):
        yield 'id', self.race_id
        yield 'round', self.league_round
        yield 'year', self.league_year
        yield 'finished', self.finished
        yield 'start_time', datetime.strftime(self.start_time, "%d/%m/%Y %H:%M") if self.start_time else False

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



class RaceCategory(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    race_length = db.Column(db.String(10))

    league_id = db.Column(db.Integer, db.ForeignKey('leagues.league_id'))

    def __init__(self, race_length):
        self.race_length = race_length
    
    def __iter__(self):
        yield 'id', self.category_id
        yield 'length', self.race_length
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class RaceResult(db.Model):
    __tablename__ = 'results'

    race_result_id = db.Column(db.Integer, primary_key=True)
    race_time = db.Column(db.Time())

    race_id = db.Column(db.Integer, db.ForeignKey('races.race_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, race_time):
        self.race_time = race_time
    
    def __iter__(self):
        yield 'id', self.race_result_id
        yield 'time', self.race_time.isoformat()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


