from flask import (
    render_template, redirect, url_for, flash, request, session
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from sqlalchemy.exc import IntegrityError
from flask_mail import Message
from threading import Thread

from .forms import LoginForm, RegistrationForm
from . import auth
from .. import db
from ..models import User
from .. import mail


@auth.before_app_request
def before_request():
    """
    Проверка подтверждения аккаунта перед каждым запросом.
    """
    if current_user.is_authenticated and not current_user.confirmed:
        if request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(f"Email: {email}, Password: {password}")
        user = User.query.filter_by(email=form.email.data).first()
        print(f"User found: {user}")
        if user is not None and user.password_verification(form.password.data):
            print("Password verification successful")
            login_user(user)
            db.session.commit()
            flash('Вы успешно авторизовались!')
            return redirect(url_for('main.index', endpoint='main.index'))
        flash('Неверный логин или пароль', 'error')
    return render_template("login.html", form=form)


@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Страница регистрации
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
                gender=form.gender.data
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['username'] = form.username.data
            session['email'] = form.email.data
            session['gender'] = form.gender.data
            token = new_user.generate_confirmation_token()
            send_confirm(new_user, token)
            login_user(new_user)
            return redirect(url_for('main.index'))
        except IntegrityError as e:
            if "key 'email'" in str(e):
                flash('Аккаунт с данной почтой уже существует.', 'email_error')
            elif "key 'username'" in str(e):
                flash('Пользователь с таким именем уже существует', 'username_error')
            db.session.rollback()
            return redirect(url_for('auth.registration'))
    return render_template('registration.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """
    Выход из аккаунта.
    """
    logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    Подтверждение аккаунта
    Параметр token: токен подтверждения
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token.encode('utf-8')):
        db.session.commit()
        flash('Ваше подтверждение прошло успешно, спасибо!')
        send_mail(current_user.email, 'Welcome to the team', 'welcome_email', user=current_user)
    else:
        flash('Ваша ссылка не валидна или истекла')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    """
    Для не подтвержденных аккаунтов.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')


def send_confirm(new_user, token):
    """
    Отправка письма с подтверждением аккаунта.
    :param new_user: новый пользователь
    :param token: токен подтверждения
    """
    send_mail(new_user.email, 'Confirm your account', 'confirm', new_user=new_user, token=token)
    return redirect(url_for('main.index'))


def send_mail(to, subject, template, **kwargs):
    """
    Отправка электронного письма.
    :param to: адрес получателя
    :param subject: тема письма
    :param template: шаблон письма
    :param kwargs: дополнительные параметры
    """
    msg = Message(subject,
                  sender='testkaze01@gmail.com',
                  recipients=[to])
    try:
        msg.html = render_template(template + ".html", **kwargs)
    except:
        msg.body = render_template(template + ".txt", **kwargs)
    from app import flask_app
    thread = Thread(target=send_async_email, args=[flask_app, msg])
    thread.start()
    return thread
    mail.send(msg)


def send_async_email(app, msg):
    """
    Отправка электронного письма асинхронно
    :param app: приложение Flask
    :param msg: объект Message
    """
    with app.app_context():
        mail.send(msg)
