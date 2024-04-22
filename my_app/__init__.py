import os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy



from flask import Flask
#from flask_bootstrap import Bootstrap

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to unlock'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/myflask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#bootstrap = Bootstrap(my_app)

db = SQLAlchemy(app)

from models import *
migrate = Migrate(app, db)

from my_app import routes