from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import *
from wtforms.validators import DataRequired


class ArticlesForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
#   photo = FileField('Изображение', validators=[FileAllowed(['1.mp4', 'avi', 'mov'])])
    submit = SubmitField('Добавить')


class CommentForm(FlaskForm):
    text = TextAreaField('Что думаете?', validators=[DataRequired()])
    submit = SubmitField('Отправить!')
