from app import app
from flask import request, render_template
from flask import make_response
import random


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