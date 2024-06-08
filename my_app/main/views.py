import os
from flask import (
    render_template, redirect, url_for, session, flash
)
from werkzeug.utils import secure_filename
from flask import current_app
from my_app.models import User, Permission, Articles
from .forms import ProfileForm, ArticlesForm
from .. import db
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from .import main


@main.route('/')
@main.route('/index')
def index():
    """
    Отображает главную страницу приложения.
    """
    articles = Articles.query.all()
    return render_template('index.html', articles=articles)


@main.route("/about-us")
def show_about():
    """
    Отображает информацию о нас.
    """
    return render_template("about_us.html")


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


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    """
    Страница профиля пользователя.
    username: имя пользователя
    return: HTML-страница с информацией о пользователе
    """
    user = User.query.filter_by(username=username).first_or_404()
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        db.session.commit()
        flash('Данные обновлены успешно!')
        return redirect(url_for('main.index', username=user.username))
    return render_template('profile.html', user=user, form=form)


@main.route('/create_article', methods=['GET', 'POST'])
@admin_required
def create_article():
    form = ArticlesForm()
    if form.validate_on_submit():
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        article = Articles(title=form.title.data, description=form.description.data, photo=filename, current_user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        flash('Статья создана успешно!')
        return redirect(url_for('main.index'))
    return render_template('create_article.html', form=form)
