import os

from server.main import app, api
from server.views import *
from server.api import *


api.add_resource(LeaguesEndpoint, '/leagues')
api.add_resource(RaceEndpoint, '/races/<race_id>')
api.add_resource(RaceResultsEndpoint, '/race-results/<race_id>')
api.add_resource(RaceResultEndpoint, '/race-result/<race_result_id>')


if __name__ == '__main__':
    app.run(host='0.0.0.0')