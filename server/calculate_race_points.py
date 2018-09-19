import os
import yaml

handicaps_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'handicaps.yaml')


class RacePoints(object):

    def __init__(self):
        self.handicaps = self._load()

    def _load(self):
        with open(handicaps_filename) as f:
            return yaml.load(f)

    def calculate(self, user, race_result, race):
        start_time = race.start_time
        
        if not user.birthdate or not user.gender: return 0
        
        age = (start_time.date() - user.birthdate).days / 365

        gender = user.gender
        race_length = race_result.race_length
        race_time = race_result.race_time

        predefined_time = self.handicaps.get('time').get(race_length)
        gender_handicaps = self.handicaps.get(gender)

        percentage = gender_handicaps.get(age, None)
        if not percentage:
            percentage = gender_handicaps.get('default')

  
        race_time_minutes = race_time.hour * 60 + race_time.minute + race_time.second / 60.0

        points = predefined_time / (race_time_minutes * ((100.0 - percentage) / 100.0))

        return float("{0:.2f}".format(points*100))

