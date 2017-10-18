from flask import request, jsonify
from flask_restful import Resource

from models import League


class LeaguesView(Resource):

    def post(self):
        data = request.get_json()
        
        league = League(data['year'], data['name'], data['rounds'])
        league.save()

        return jsonify({"success": True, "league": dict(league)})