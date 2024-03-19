from flask import Flask
#from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to unlock'
#bootstrap = Bootstrap(my_app)

from my_app import routes
