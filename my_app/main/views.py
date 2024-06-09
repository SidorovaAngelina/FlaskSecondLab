import os
from flask import (
    render_template, redirect, url_for, session, flash
)
from werkzeug.utils import secure_filename
from flask import current_app
from my_app.models import User, Permission, Articles, Comment
from .forms import ProfileForm, ArticlesForm, CommentForm
from .. import db
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from .import main


@main.route('/')
@main.route('/index')
def index():
    """
    Display the main page of the application.
    This function retrieves all articles from the database and renders the index template.
    :return: render template for the index page.
    """
    articles = Articles.query.all()
    return render_template('index.html', articles=articles)


@main.route("/about-us")
def show_about():
    """
    Display the about us page.
    This function renders the about us template.
    :return: render template for the about us page.
    """
    return render_template("about_us.html")


@main.route('/show_data')
def show_data():
    """
    Display user data.
    This function retrieves user data from the session and renders the show data template.
    :return: render template for showing user data/
    """
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')
    gender = session.get('gender')
    return render_template('shownData.html', user_id=user_id,
                           username=username, email=email, gender=gender)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderator():
    """
    Display a page only accessible to moderators.
    This function checks if the user has the moderate permission and renders a template only accessible to them.
    :return: render template for moderators.
    """
    return 'Only for moderator'


@main.route('/testConfirm')
def testConfirm():
    """
    Test user confirmation.
    This function generates a confirmation token for a user and confirms it.
    :return: None
    """
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    """
    Display a user's profile.
    This function retrieves a user's data and renders a template for their profile.
    :param username: The username of the user to display
    :return: render template for the user's profile
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
    """
    Create a new article.
    This function handles the creation of a new article. It validates the form data,
    saves the article to the database, and redirects the user to the index page.
    :return: A rendered template for creating an article or a redirect to the index page
    """
    form = ArticlesForm()
    if form.validate_on_submit():
        if form.photo.data:
            photo = form.photo.data
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            article = Articles(title=form.title.data, description=form.description.data, photo=filename)
        else:
            article = Articles(title=form.title.data, description=form.description.data)
        article.user_id = current_user.id
        db.session.add(article)
        db.session.commit()
        flash('Статья создана успешно!')
        return redirect(url_for('main.index'))
    return render_template('create_article.html', form=form)


@main.route('/article/<int:article_id>/comment', methods=['GET', 'POST'])
def add_comment(article_id):
    """
    Add a comment to an article.
    This function handles the addition of a new comment to an article. It validates the form data,
    saves the comment to the database, and redirects the user to the index page.
    :param article_id: The ID of the article to which the comment is being added
    :return: render template for adding a comment or a redirect to the index page
    """
    article = Articles.query.get_or_404(article_id)
    form = CommentForm()
    if form.validate_on_submit():
        if form.text.data.strip() == '':
            flash('Комментарий не может быть пустым', 'error')
            return render_template('add_comment.html', form=form, article=article)
        comment = Comment(text=form.text.data, article=article, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен успешно!')
        return redirect(url_for('main.index'))
    return render_template('add_comment.html', form=form, article=article)
