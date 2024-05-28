from flask import render_template, request, redirect, url_for, session, flash, current_app
from my_app.models import User
from flask_mail import Message
from flask_login import login_required

from . import main


@main.route('/')
@main.route('/index')
def index():
    return render_template("index.html")


coffee = {
    'americano': 'Американо — это напиток на основе эспрессо с добавлением горячей воды.',
    'cappuccino': 'Капчуино - это напиток объемом 150-180 мл, в котором гармонично сочетаются эспрессо и молоко.'
                  'Для приготовления капучино берут одну порцию эспрессо, а молоко предварительно взбивают.',
    'latte': 'Латте — кофейный напиток на основе молока, представляющий собой трёхслойную смесь из молочной пены, молока и кофе эспрессо.'
             'Соотношение эспрессо, взбитого молока и молочной пены составляет 1:2 или 1:3.'
}


@main.route("/coffee/<coffee_title>")
def show_coffee(coffee_title):
    if coffee_title in coffee:
        return f'<h1>{coffee_title.upper()}</h1>' \
               f'<p>{coffee[coffee_title]}</p>'
    else:
        return "Такого кофе пока нет в нашем меню."


@main.route("/about-us")
def show_about():
    return f'<h1>О нас</h1>' \
           f'<p>Мы используем только высококачественные ингредиенты, чтобы гарантировать вам наилучший вкус и качество наших напитков.</p>'

'''
def send_mail(to, subject, template, kwargs):
    msg = Message(subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to])
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
'''


@main.route('/show_data')
def show_data():
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')
    gender = session.get('gender')
    return render_template('shownData.html', user_id=user_id, username=username, email=email, gender=gender)


@main.route('/secret')
@login_required
def secret():
    return 'only for auth'


@main.route('/testConfirm')
def testConfirm():
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)

