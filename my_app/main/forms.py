from flask_wtf import FlaskForm
from wtforms import *
from wtforms import StringField
from wtforms.validators import DataRequired

from my_app.models import User


class ArticlesForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    photo = FileField('Фотография статьи', validators=[DataRequired()])
#   submit = SubmitField('Добавить')


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Такое имя пользователя уже занято!')

