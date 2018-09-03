import os

from server.main import app, api
from server.views import *
from server.api import *


api.add_resource(LeaguesEndpoint, '/leagues')
api.add_resource(RaceEndpoint, '/races/<race_id>')
api.add_resource(RaceResultsEndpoint, '/race-results/<race_id>')
api.add_resource(RaceResultEndpoint, '/race-result/<race_result_id>')
api.add_resource(RegisterAnonymousUserForRaceEndpoint, '/race-results/<race_id>/register')
api.add_resource(NotApprovedUsersEndpoint, '/users/not-approved')
api.add_resource(ApproveUserEndpoint, '/users/<username>/approve')
api.add_resource(LeagueEndpoint, '/leagues/<league_id>')
api.add_resource(UsersEndpoint, '/users')
api.add_resource(UserEndpoint, '/users/<user_id>')
api.add_resource(LeagueResultsEndpoint, '/leagues/<league_id>/results')
api.add_resource(UsersMergeEndpoint, '/users-merge/<user_id_1>/<user_id_2>')

if __name__ == '__main__':
    app.run(host='0.0.0.0')