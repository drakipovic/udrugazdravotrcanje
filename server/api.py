from flask import request, jsonify
from flask_restful import Resource

from models import League


class LeaguesView(Resource):

    def post(self):
        data = request.get_json()
        year = data['year']
        name = data['name']
        rounds = data['rounds']
        
        league = League(year, name, rounds)
        league.save()

        return jsonify({"success": True, "league": dict(league)})