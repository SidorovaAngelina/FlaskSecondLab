from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Length(1, 100), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    gender = SelectField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')],
                         validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
