from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Optional

from my_app.models import User


class ArticlesForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    photo = FileField('Фотография статьи', validators=[Optional()])


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Такое имя пользователя уже занято!')


class CommentForm(FlaskForm):
    text = StringField('Оставить комменатрий')
    submit = SubmitField('Добавить комментарий')
