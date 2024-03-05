'''
from flask import Flask

another_app = Flask(__name__)


@another_app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    another_app.run()

'''

from flask import Flask

another_app = Flask(__name__)

from app import routes