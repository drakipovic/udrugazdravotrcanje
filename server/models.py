from datetime import datetime, date
from random import randint

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.types import TypeDecorator, Unicode, UnicodeText

from main import db
from calculate_race_points import RacePoints


class CoerceUTF8(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value


class CoerceUTF8Text(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(CoerceUTF8(32), index=True)
    password_hash = db.Column(CoerceUTF8(128))
    email = db.Column(CoerceUTF8(100))
    name = db.Column(CoerceUTF8(50))
    surname = db.Column(CoerceUTF8(50))
    gender = db.Column(CoerceUTF8(5))
    birthdate = db.Column(db.Date())
    role = db.Column(CoerceUTF8(40))
    approved = db.Column(db.Boolean)
    avatar_url = db.Column(CoerceUTF8(100))

    race_results = db.relationship('RaceResult', backref='user', lazy='select', cascade='all, delete, delete-orphan')

    def __init__(self, username, password, email=None, name=None, surname=None, gender=None, birthdate=None, role='user', approved=False):
        self.username = username
        self.password_hash = self._set_password(password)
        self.email = email
        self.name = name
        self.surname = surname
        self.gender = gender
        self.birthdate = birthdate
        self.role = role
        self.approved = approved
        self.avatar_url = '/static/img/profile/{}/{}.png'.format(self.gender, randint(0, 2)) 

    def __iter__(self):
        yield 'id', self.user_id
        yield 'username', self.username
        yield 'email', self.email
        yield 'full_name', self.full_name
        yield 'gender', self.gender
        yield 'birthdate', self.birthdate
        yield 'age', self.age
        yield 'role', self.role
        yield 'approved', self.approved

    def _set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def age(self):
        if self.birthdate:
            return (date.today() - self.birthdate).days / 365
        
        return ""
    
    @property
    def full_name(self):
        if self.name and self.surname:
            return "{} {}".format(self.name.encode('utf-8'), self.surname.encode('utf-8'))
        
        return ""
    
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
    name = db.Column(CoerceUTF8(1500))
    rounds = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_by = db.relationship('User', backref='created_by')

    races = db.relationship('Race', backref='leagues', lazy='select', cascade='all, delete, delete-orphan')
    race_categories = db.relationship('RaceCategory', backref='leagues', lazy='select', cascade='all, delete, delete-orphan')

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
    race_results = db.relationship('RaceResult', backref='user_results', lazy='select', cascade='all, delete, delete-orphan')

    def __init__(self, league_year, league_round, start_time=None, finished=False):
        self.league_year = league_year
        self.league_round = league_round
        self.finished = finished
        self.start_time = datetime.strptime(start_time, '%d-%m-%Y %H:%M') if start_time else start_time

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
    race_length = db.Column(CoerceUTF8(10))

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
    race_length = db.Column(CoerceUTF8(10))
    start_number = db.Column(db.Integer)

    race_id = db.Column(db.Integer, db.ForeignKey('races.race_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, user_id, race_id, race_time=None, race_length=None, start_number=None):
        self.race_time = race_time
        self.race_length = race_length
        self.race_id = race_id
        self.user_id = user_id
        self.start_number = len(Race.query.get(race_id).race_results) + 1 if not start_number else start_number
        
    def __iter__(self):
        yield 'id', self.race_result_id
        yield 'position', '-'
        yield 'race_id', self.race_id
        yield 'time', self.race_time.isoformat() if self.race_time else '-'
        yield 'race_length', self.race_length
        yield 'start_number', self.start_number
        yield 'full_name', User.query.get(self.user_id).full_name
        yield 'points', RacePoints().calculate(User.query.get(self.user_id), self) if self.race_time else '-'

    def __eq__(self, other):
        if self.race_time and other.race_time and self.race_length and other.race_length:
            return self.race_time == other.race_time and self.race_length == other.race_length
        
        return False

    def __lt__(self, other):
        if self.race_time and other.race_time:
            return self.race_time < other.race_time
        
        if self.race_length and other.race_length:
            return self.race_length < other.race_length
        
        if not self.race_time:
            return False
        
        if not other.race_time:
            return True
        
        return True
        
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()