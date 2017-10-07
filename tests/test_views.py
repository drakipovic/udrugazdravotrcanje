import os
os.environ['TEST'] = '1'

from run import app

app = app.test_client()


def test_get_dashboard_returns_dashboard_page():

    response = app.get('/admin')

    assert response.status_code == 200

    assert 'Udruga Zdravo' in response.data