from my_app import db


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


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))

    def __repr__(self):
        return '<User %r>' % self.username
