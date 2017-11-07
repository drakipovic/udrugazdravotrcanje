import os

from server.main import app, api
from server.views import *
from server.api import *

api.add_resource(LeaguesView, '/leagues')
api.add_resource(RaceView, '/races/<race_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0')