from my_app import app, db
from flask import render_template, request, redirect, url_for, session, flash
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from models import User

from . import mail

from my_app.forms import SimpleForm


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


coffee = {
    'americano': 'Американо — это напиток на основе эспрессо с добавлением горячей воды.',
    'cappuccino': 'Капчуино - это напиток объемом 150-180 мл, в котором гармонично сочетаются эспрессо и молоко.'
                  'Для приготовления капучино берут одну порцию эспрессо, а молоко предварительно взбивают.',
    'latte': 'Латте — кофейный напиток на основе молока, представляющий собой трёхслойную смесь из молочной пены, молока и кофе эспрессо.'
             'Соотношение эспрессо, взбитого молока и молочной пены составляет 1:2 или 1:3.'
}


@app.route("/coffee/<coffee_title>")
def show_coffee(coffee_title):
    if coffee_title in coffee:
        return f'<h1>{coffee_title.upper()}</h1>' \
               f'<p>{coffee[coffee_title]}</p>'
    else:
        return "Такого кофе пока нет в нашем меню."


@app.route("/about-us")
def show_about():
    return f'<h1>О нас</h1>' \
           f'<p>Мы используем только высококачественные ингредиенты, чтобы гарантировать вам наилучший вкус и качество наших напитков.</p>'


@app.errorhandler(404)
def forbidden(e):
    return render_template('404.html'), 404


def send_mail(to, subject, template, kwargs):
    msg = Message(subject,
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[to])
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)


@app.route('/form', methods=['GET', 'POST'])
def testForm():
    form = SimpleForm()
    if form.validate_on_submit():
        try:
            new_user = User(email=form.email.data, username=form.username.data, password=form.password.data,
                            gender=form.gender.data)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['email'] = form.email.data
            session['gender'] = form.gender.data
            email = request.form['email']
            send_mail(email, "Добро пожаловать!", "welcome_email", {'username': new_user.username})
            return redirect(url_for('show_data'))
        except IntegrityError as e:
            if "key 'email'" in str(e):
                flash('Аккаунт с данной почтой уже существует.', 'email_error')
            elif "key 'username'" in str(e):
                flash('Пользователь с таким логином уже существует', 'username_error')
            db.session.rollback()
            return redirect(url_for('testForm'))

    return render_template('formTemplate.html', form=form)


@app.route('/show_data')
def show_data():
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')
    gender = session.get('gender')
    return render_template('shownData.html', user_id=user_id, username=username, email=email, gender=gender)

