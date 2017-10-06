import os

from server.main import app
from server.views import *


if __name__ == '__main__':
    db_name = app.config['SQLALCHEMY_DATABASE_URI'][10:]
    if not os.path.exists(db_name):
        os.system('touch {}'.format(db_name))
        from server.models import User
        from server.main import db
        db.create_all()

    app.run(host='0.0.0.0', debug=True)