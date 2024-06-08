import os
from flask import (
    render_template, request, redirect, url_for, session, flash, current_app
)
from my_app.models import User, Permission, Articles
from ..decorators import admin_required, permission_required
from flask_mail import Message
from flask_login import login_required

from .import main


@main.route('/')
@main.route('/index')
def index():
    """
    Отображает главную страницу приложения.
    """
    return render_template("index.html")


@main.route("/about-us")
def show_about():
    return render_template("about_us.html")


@main.route("/new_releases")
@login_required
def releases():
    return render_template("new_releases.html")


@main.route('/show_data')
def show_data():
    """
    Отображает данные пользователя, если он авторизован.
    """
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')
    gender = session.get('gender')
    return render_template('shownData.html', user_id=user_id,
                           username=username, email=email, gender=gender)

'''
@main.route('/admin')
@login_required
@admin_required
def for_admin():
    """
    Страница досутпная только администраторам.
    """
    return 'Only for admin'
'''


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderator():
    """
    Страница досутпная только модераторам.
    """
    return 'Only for moderator'


@main.route('/secret')
@login_required
def secret():
    """
    Страница досутпная только авторизированным пользователям.
    """
    return 'only for auth'


@main.route('/testConfirm')
def testConfirm():
    """
    Тестовая страница для подтверждения по электронной почте.
    """
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)


@main.route('/user/<username>')
def user(username):
    """
    Страница профиля пользователя.
    username: имя пользователя
    return: HTML-страница с информацией о пользователе
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

'''
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
'''


@main.route('/articles')
def articles():
    articles = Articles.query.all()
    return render_template('articles.html', articles=articles)

