import os

from server.main import app
from server.views import *


if __name__ == '__main__':
    app.run(host='0.0.0.0')