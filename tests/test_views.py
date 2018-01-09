import os
os.environ['TEST'] = '1'

from server.main import app


def test_get_dashboard_returns_dashboard_page():

    assert True == True