from main import another_app
from flask import request
from flask import make_response
import random


'''
@another_app.before_request
def test():
    print('Hi')
'''


class User:
    def __init__(self, id_user, name):
        self.id_user = id_user
        self.name = name



def index():
    user_agent = request.headers.get('User-Agent')
    if "Firefox" in user_agent:
        response = make_response("<H1>Вы зашли через Firefox..! Проверьте куки<H1>")
        response.set_cookie('flag', f'{random.randint(1, 100)}')
        return response
    return '<h2>Всё гуд, вы зашли не через Firefox.<h2>'


coffee = {
    'americano': 'Американо — это напиток на основе эспрессо с добавлением горячей воды.',
    'cappuccino': 'Капчуино - это напиток объемом 150-180 мл, в котором гармонично сочетаются эспрессо и молоко.'
                  'Для приготовления капучино берут одну порцию эспрессо, а молоко предварительно взбивают.',
    'latte': 'Латте — кофейный напиток на основе молока, представляющий собой трёхслойную смесь из молочной пены, молока и кофе эспрессо.'
             'Соотношение эспрессо, взбитого молока и молочной пены составляет 1:2 или 1:3.'
}


@another_app.route("/coffee/<coffee_title>")
def show_coffee(coffee_title):
    if coffee_title in coffee:
        return f'<h1>{coffee_title.upper()}</h1>' \
               f'<p>{coffee[coffee_title]}</p>'
    else:
        return "Такого кофе пока нет в нашем меню."


@another_app.route("/about-us")
def show_about():
    return f'<h1>О нас</h1>' \
           f'<p>Мы используем только высококачественные ингредиенты, чтобы гарантировать вам наилучший вкус и качество наших напитков.</p>'



def load_user(user_id):
    if user_id == "42":
        return User(42, "Lina")
    elif user_id == "100":
        return User(100, "Mark")
    else:
        return None


'''
@another_app.route('/user/<name>')
def hello_user(name):
    return '<h2>Hello, {}</h2>'.format(name)
'''

@another_app.route('/bad_request')
def bad_fill(code=400):
    return '<h3>Bad Request<h3>', code



'''
@another_app.route('/user/<user_id>')
def get_user(user_id):
    user = load_user(user_id)
#    print = ("!", user)
    if user is None:
        return bad_fill(404)
    else:
        return '<h1>Hello, {}<h1>'.format(user.name)

'''
another_app.add_url_rule('/', 'index', index)





