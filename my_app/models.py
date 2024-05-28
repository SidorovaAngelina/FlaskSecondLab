from flask_login import UserMixin
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.jose import jwt
from authlib.jose import JsonWebSignature


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    genre = (db.String(100))
    users = db.relationship('User', backref='fav_playlist')

    def __repr__(self):
        return '<Song %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    gender = db.Column(db.String(10), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))
    confirmed = db.Column(db.Boolean, default=False)

    def generate_confirmation_token(self):
        header = {'alg': 'HS256'}
        payload = {'sub': str(self.id)}
        secret = 'secret'
        token = jwt.encode(header, payload, secret)
        return token.decode('utf-8')

    def confirm(self, token):
        try:
            data = jwt.decode(token, 'secret')
            if data['sub'] != str(self.id):
                print('It`s not your token')
                return False
            else:
                self.confirmed = True
                db.session.add(self)
                return True
        except jwt.DecodeError:
            print('Invalid token')
            return False

    @property
    def password(self):
        raise AttributeError('password not enable to read')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_verification(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
