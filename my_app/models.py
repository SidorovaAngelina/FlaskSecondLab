from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from authlib.jose import JsonWebSignature, jwt


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

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role%>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = "User"
        for r in roles:
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


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    gender = db.Column(db.String(10), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    articles = db.relationship('Articles', backref='creator', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == "testlinaan@mail.ru":
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def generate_confirmation_token(self):
        header = {'alg': 'HS256'}
        payload = {'sub': str(self.id)}
        secret = 'secret'
        token = jwt.encode(header, payload, secret)
        return token.decode('utf-8')

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

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
        raise AttributeError('password not enable for read')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def confirm(self, token):
        try:
            data = jwt.decode(token, 'secret')
            if data['sub'] != str(self.id):
                print('It`s not your token')
                return False
            else:
                self.confirmed = True
                db.session.add(self)
                db.session.commit()
                return True
        except jwt.DecodeError:
            print('Invalid token')
            return False

    def password_verification(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Articles(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    photo = db.Column(db.String(255), nullable=True)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    articles_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_admin(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
