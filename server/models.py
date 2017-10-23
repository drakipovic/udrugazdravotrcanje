from werkzeug.security import generate_password_hash, check_password_hash

from main import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
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

    league_id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    name = db.Column(db.String(1500))
    rounds = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_by = db.relationship('User', backref='tasks')

    races = db.relationship('Race', backref='leagues', lazy='select', cascade='all, delete, delete-orphan')

    def __init__(self, year, name, rounds, created_by, races):
        self.year = year
        self.name = name
        self.rounds = rounds
        self.created_by = created_by
        self.races = races

    def __iter__(self):
        yield 'id', self.league_id
        yield 'year', self.year
        yield 'name', self.name
        yield 'rounds', self.rounds
        yield 'created_by', self.created_by
    
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

    league_id = db.Column(db.Integer, db.ForeignKey('leagues.league_id'))

    def __init__(self, league_id, league_round):
        self.league_id = league_id
        self.league_round = league_round

    def __iter__(self):
        yield 'id', self.race_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

