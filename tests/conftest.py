import pytest

from server.main import db

@pytest.fixture(autouse=True)
def tear_up_down_db():
    db.create_all()

    yield

    db.drop_all()
