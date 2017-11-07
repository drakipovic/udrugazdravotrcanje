from datetime import datetime

from flask import request, jsonify, g
from flask_restful import Resource

from models import League, Race


class LeaguesView(Resource):

    def post(self):
        data = request.get_json()
        year = data['year']
        name = data['name']
        rounds = data['rounds']

        races = [Race(year, round) for round in range(int(rounds))]

        for race in races:
            race.save()
        
        league = League(year, name, rounds, g.user, races)
        league.save()

        return jsonify({"success": True, "league": dict(league)})


class RaceView(Resource):

    def put(self, race_id):
        data = request.get_json()

        start_time = data['start_time']
        race_id = data['id']

        race = Race.query.get(race_id)
        race.start_time = datetime.strptime(start_time, '%d-%m-%Y %H:%M')
        race.save()

        return jsonify({"success": True, "race": dict(race)})