import flask_admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib import sqla
from flask_login import LoginManager, current_user
from flask import Flask, abort, redirect, url_for, request
from flask_mail import Mail
from config import config
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
from flask_admin import Admin, expose


mail = Mail()
db = SQLAlchemy()
oauth = OAuth()
migrate = Migrate()
admin = Admin()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.can(16)
                )

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('main.index', next=request.url))


class MyAdminIndexView(flask_admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return super(MyAdminIndexView, self).index()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'my_app/static/uploads'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, config=config)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    admin = flask_admin.Admin(app, index_view=MyAdminIndexView())
    from my_app.models import User, Articles
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Articles, db.session))

    return app
