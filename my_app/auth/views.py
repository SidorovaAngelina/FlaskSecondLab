from flask import (
    render_template, redirect, url_for, flash, request
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

    Check if the user is confirmed before each request.
    If the user is not confirmed, redirect them to the unconfirmed page.
    """
    if current_user.is_authenticated and not current_user.confirmed:
        if request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """

    The authorization page.
    Processes the authorization form and authenticates the user.
    If the user has entered the correct data, they will be logged in and redirected to the index page.
    If the data is incorrect, an error message will be displayed.
    :return: Authorization page or redirection to the index page
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_verification(form.password.data):
            login_user(user)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for('main.index')
                return redirect(next)
            flash('Неверный логин или пароль', 'error')
    return render_template("login.html", form=form)


@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    """

    The registration page.
    Processes the registration form and creates a new user.
    If the form is valid, a new user is created and a confirmation email is sent.
    If the form is not valid, an error message is displayed.
    :return: Registration page or redirection to the index page
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                email=form.email.data,
                username=form.username.data,
                gender=form.gender.data
            )
            db.session.add(new_user)
            new_user.set_password(form.password.data)
            db.session.commit()
            token = new_user.generate_confirmation_token()
            send_confirm(new_user, token)
            login_user(new_user)
            return redirect(url_for('main.index'))
        except IntegrityError as e:
            if "key 'email'" in str(e):
                flash('Аккаунт с данной почтой уже существует.', 'email_error')
            elif "key 'username'" in str(e):
                flash('Пользователь с таким именем уже существует', 'username_error')
    return render_template('registration.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """

    Log out of your account.
    Logs out of the account and redirects to the index page.
    """
    logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """

    Account confirmation.
    Processes account confirmation and updates the user's confirmation status.
    If the confirmation is successful, a welcome email is sent.
    If the confirmation is not successful, an error message is displayed.
    :param token: Confirmation
    token :return: Redirection to the index page
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token.encode('utf-8')):
        db.session.commit()
        flash('Ваше подтверждение прошло успешно, спасибо! Прислали вам письмо на почту.')
        send_mail(current_user.email, 'Welcome to the team', 'welcome_email', user=current_user)
    else:
        flash('Ваша ссылка не валидна или истекла')
    return redirect(url_for('main.index'))



@auth.route('/unconfirmed')
def unconfirmed():
    """

    A page for unconfirmed accounts.
    Displays a page for users who have not verified their account.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')


def send_confirm(new_user, token):
    """

    Send a confirmation email to a new user.
    :param new_user: The new user object
    :param token: The confirmation token
    :return: A redirect to the main index page
    """
    send_mail(new_user.email, 'Confirm your account', 'confirm', new_user=new_user, token=token)
    return redirect(url_for('main.index'))


def send_mail(to, subject, template, **kwargs):
    """

    Sending an email to a user.
    :param to: The recipient's email address
    :param subject: The email subject
    :param template: The email template
    :param kwargs: Additional keyword arguments for the email template
    :return: A thread object that sends the email asynchronously
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

    Send an email asynchronously.
    :param app: The Flask app object
    :param msg: The email message object
    :return: None
    """
    with app.app_context():
        mail.send(msg)
