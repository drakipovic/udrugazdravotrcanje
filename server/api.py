import uuid
from datetime import datetime, time

from flask import request, jsonify, g
from flask_restful import Resource, reqparse

from models import League, Race, RaceCategory, RaceResult, User
from calculate_race_points import RacePoints
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

    def get(self, race_id):
        parser = reqparse.RequestParser()
        parser.add_argument('gender')
        parser.add_argument('category')
        parser.add_argument('age')
        args = parser.parse_args()

        gender = args.get('gender')
        category = args.get('category')
        age = args.get('age')

        if gender == 'null': gender = None
        if category == 'null': category = None
        if age == 'null': age = None

        if age and not gender and not category:
            age_from, age_to = int(age.split('-')[0]), int(age.split('-')[1])

            race_results = [
                race_result for race_result in sorted(
                    RaceResult.query.join(Race, RaceResult.race_id==race_id).join(User, User.user_id==RaceResult.user_id)
                )  
            ]

            race_results = [dict(race_result)for race_result in race_results if age_from <= race_result.user.age <= age_to]
        
        if gender and category:
            race_results = [
                dict(race_result) for race_result in sorted(
                    RaceResult.query.join(Race, RaceResult.race_id==race_id).join(User, User.user_id==RaceResult.user_id)
                                    .filter(RaceResult.race_length==category, User.gender==gender).all())
            ]
        
        elif gender and not category:
            race_results = [
                dict(race_result) for race_result in sorted(
                    RaceResult.query.join(Race, RaceResult.race_id==race_id).join(User, User.user_id==RaceResult.user_id)
                                    .filter(User.gender==gender).all())
            ]

        elif category and not gender:
            race_results = [
                dict(race_result) for race_result in sorted(
                    RaceResult.query.join(Race, RaceResult.race_id==race_id).join(User, User.user_id==RaceResult.user_id)
                                    .filter(RaceResult.race_length==category).all())
            ]

        elif not category and not age and not gender:
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

        race_result = RaceResult.query.filter_by(race_id=race_id, user_id=user_id).first()

        if not race_result:
            race_result = RaceResult(race_length=race_length, race_id=race_id, user_id=user_id)
            race_result.save()

        return jsonify({"success": True, "race_result": dict(race_result)})


class RegisterAnonymousUserForRaceEndpoint(Resource):

    def post(self, race_id):
        data = request.get_json()

        name = data['name']
        start_number = data['start_number']
        race_length = data['race_length']
        gender = data['gender']
        birthyear = data['birthyear']

        name, surname = tuple(name.split())

        birthdate = datetime(int(birthyear), 1, 1)

        user = User(username=u"{}.{}{}".format(name, surname, birthyear), password=str(uuid.uuid4()), 
                    name=name, surname=surname, approved=True, gender=gender, birthdate=birthdate)

        user.save()

        race_result = RaceResult(user.user_id, race_id, start_number=start_number, race_length=race_length)
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


class UsersEndpoint(Resource):

    @auth.login_required
    def get(self):
        users = [dict(user) for user in User.query.filter_by(approved=True).all()]

        return jsonify(users)


class UserEndpoint(Resource):

    @auth.login_required
    def get(self, user_id):
        user = User.query.get(user_id)

        return jsonify({"user": dict(user)})

    @auth.login_required
    def put(self, user_id):
        user = User.query.get(user_id)

        errors = []
        old_password = request.json.get('old-password')

        if old_password and not user.check_password(old_password):
            errors.append({"old-password": "Kriva lozinka!"})

        password = request.json.get('password')
        email = request.json.get('email')
        birthdate = request.json.get('birthdate')

        if not email: errors.append({"email": "Ne smije ostati prazno!"})
        if not birthdate: errors.append({"birthdate": "Ne smije ostati prazno!"})

        if errors:
            return {"errors": errors}, 400

        birthdate = datetime.strptime(birthdate, "%d-%m-%Y")

        user.email = email
        user.birthdate = birthdate
        
        if password:
            user.password_hash = user.set_password(password)

        user.save()

        return jsonify({"user": dict(user)})


class LeagueResultsEndpoint(Resource):

    @auth.login_required
    def get(self, league_id):
        parser = reqparse.RequestParser()
        parser.add_argument('gender')
        parser.add_argument('age')
        args = parser.parse_args()

        gender = args.get('gender')
        age = args.get('age')

        if gender == 'null': gender = None
        if age == 'null': age = None
        
        league = League.query.get(league_id)

        league_points = {}
        rp = RacePoints()

        for race in sorted(league.races, key=lambda x: x.race_id):
            if race.start_time:
                for result in race.race_results:
                    if result.race_time:
                        user = User.query.get(result.user_id)
                        if not user.birthdate:
                            continue
                            
                        if league_points.get(result.user_id, None):
                            league_points[result.user_id]['points'] += rp.calculate(user, result, race)
                            league_points[result.user_id]['races'] += 1
                        else:
                            league_points[result.user_id] = {}
                            league_points[result.user_id]['points'] = rp.calculate(user, result, race)
                            league_points[result.user_id]['user'] = dict(user)
                            league_points[result.user_id]['races'] = 1
        
        league_points = [user_points[1] for user_points in sorted(league_points.iteritems(), key=lambda (x, y): y['points'], reverse=True)]
        
        if age and not gender:
            age_from, age_to = int(age.split('-')[0]), int(age.split('-')[1])
            league_points = [user_points for user_points in league_points if age_from <= user_points['user']['age'] <= age_to]

        if gender and not age:
            league_points = [user_points for user_points in league_points if user_points['user']['gender'] == gender]

        if age and gender:
            age_from, age_to = int(age.split('-')[0]), int(age.split('-')[1])
            league_points = [user_points for user_points in league_points if age_from <= user_points['user']['age'] <= age_to and user_points['user']['gender'] == gender]

        pos = 1
        for user in league_points:
            user['position'] = pos
            pos += 1


        return jsonify(league_points)


class UsersMergeEndpoint(Resource):

    def get(self, user_id_1, user_id_2):
        user_1 = User.query.get(user_id_1)
        user_2 = User.query.get(user_id_2)

        race_results_1 = user_1.race_results
        race_results_2 = user_2.race_results
        
        merged = []
        merged.extend(race_results_1)
        merged.extend(race_results_2)

        for race_result in merged:
            race_result.user_id = user_id_2
        
        race_results = [dict(race_result) for race_result in merged]

        return jsonify({"user": dict(user_2), "race_results": race_results})

    def post(self, user_id_1, user_id_2):
        user_1 = User.query.get(user_id_1)
        user_2 = User.query.get(user_id_2)

        race_results_1 = user_1.race_results
        race_results_2 = user_2.race_results
        
        merged = []
        merged.extend(race_results_1)
        merged.extend(race_results_2)

        for race_result in merged:
            race_result.user_id = user_id_2

        user_2.race_results = merged
        user_2.save()

        user_1.delete()
        
        return jsonify({"success": True})