import uuid
from datetime import datetime, time

from flask import request, jsonify, g
from flask_restful import Resource

from models import League, Race, RaceCategory, RaceResult, User
from main import auth


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    if not user or not user.check_password(password):
        return False

    return True


class LeaguesEndpoint(Resource):

    @auth.login_required
    def post(self):
        data = request.get_json()
        year = data['year']
        name = data['name']
        rounds = data['rounds'].replace('_', '')
        categories = data['categories']

        categories = [RaceCategory(race_length) for race_length in categories]            
        races = [Race(year, round) for round in range(int(rounds))]

        for race in races:
            race.save()
        
        league = League(year, name, rounds, g.user, races, categories)
        league.save()

        return jsonify({"success": True, "league": dict(league)})


class LeagueEndpoint(Resource):
    
    @auth.login_required
    def delete(self, league_id):
        league = League.query.get(league_id)

        league.delete()

        return jsonify({"success": True})


class RaceEndpoint(Resource):

    @auth.login_required
    def put(self, race_id):
        data = request.get_json()

        race = Race.query.get(race_id)

        start_time = data['start_time'] if data.get('start_time', False) else race.start_time
        finished = data['finished'] if data.get('finished', False) else race.finished

        race.start_time = datetime.strptime(start_time, '%d-%m-%Y %H:%M') if type(start_time) == unicode else start_time
        
        race.finished = finished
        race.save()

        return jsonify({"success": True, "race": dict(race)})

    @auth.login_required
    def delete(self, race_id):
        race = Race.query.get(race_id)

        race.delete()

        return jsonify({"success": True})


class RaceResultEndpoint(Resource):

    @auth.login_required
    def put(self, race_result_id):
        data = request.get_json()

        race_time = data['time']
        race_time = race_time.split(":") #time is in format hh:mm:ss
        race_length = data['race_length']

        race_result = RaceResult.query.get(race_result_id)

        race_result.race_time = time(int(race_time[0]), int(race_time[1]), int(race_time[2]))
        race_result.race_length = race_length
        race_result.save()

        return jsonify({"success": True, "race_result": dict(race_result)})


class RaceResultsEndpoint(Resource):

    @auth.login_required
    def get(self, race_id):
        race_results = [dict(race_result) for race_result in sorted(Race.query.get(race_id).race_results)]
        
        for i, race_result in enumerate(race_results):
            if race_result.get('time', None):
                race_result['position'] = i + 1

        return jsonify(race_results)

    @auth.login_required
    def post(self, race_id):
        data = request.get_json()

        user_id = data['user_id']
        race_length = data['race_length']

        race_result = RaceResult(race_length=race_length, race_id=race_id, user_id=user_id)
        race_result.save()

        return jsonify({"success": True, "race_result": dict(race_result)})


class RegisterAnonymousUserForRaceEndpoint(Resource):

    def post(self, race_id):
        data = request.get_json()

        name = data['name']
        start_number = data['start_number']

        name, surname = tuple(name.split())

        user = User(username=name, password=str(uuid.uuid4()), name=name, surname=surname, approved=True)
        user.save()

        race_result = RaceResult(user.user_id, race_id, start_number=start_number)
        race_result.save();
        
        return jsonify({"success": True})


class NotApprovedUsersEndpoint(Resource):

    @auth.login_required
    def get(self):
        users = [dict(user) for user in User.query.filter_by(approved=False)]

        return jsonify(users)


class ApproveUserEndpoint(Resource):

    #username is unique
    @auth.login_required
    def put(self, username):
        
        user = User.query.filter_by(username=username).first()
        user.approved = True

        user.save()

        return jsonify({"success": True})