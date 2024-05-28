from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.jose import jwt
from authlib.jose import JsonWebSignature


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __int__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles.keys():
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0


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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    about_me = db.Column(db.Text())

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            if self.email == 'testlina@mail.ru':
                self.role_id = Role.query.filter_by(name='Administrator').first()
            if self.role_id is None:
                self.role_id = Role.query.filter_by(default=True).first()

    def generate_confirmation_token(self):
        header = {'alg': 'HS256'}
        payload = {'sub': str(self.id)}
        secret = 'secret'
        token = jwt.encode(header, payload, secret)
        return token.decode('utf-8')

    def can(self, perm):
        return self.role_id is not None and self.role_id.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

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


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_admin(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
