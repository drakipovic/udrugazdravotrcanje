from run import app

app = app.test_client()

def test_hello_in_home():

    response = app.get('/')

    assert 'Hello' in response.data