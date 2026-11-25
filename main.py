# Importações
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from perguntas import perguntas
import random
app = Flask(__name__)

# Chave secreta para uso de session
app.secret_key = 'my_top_secret_123'

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o banco
db = SQLAlchemy(app)


# -------------------------|
# Tabela de Cards          |
# -------------------------|
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Card {self.id}>'


# -------------------------|
# Cria a tabela User       |
# -------------------------|
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    xp = db.Column(db.Integer, nullable=False)
    dias = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'


# -------------------------|
# Cria a tabela dos quizes |
# -------------------------|
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    ideia = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<tema {self.tema}>'


"""!!! Não mexer não funções login e reg!!!"""


# Aproveite enquando elas funcionam!
# Iniciando página de conteúdo
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']

        users_db = User.query.all()

        for user in users_db:
            if form_login == user.email and form_password == user.password:
                session['user_email'] = user.email  # Salva o usuário  e o nome no session | # noqa: E501
                return redirect('/index')

        return render_template('login.html', error='Tente novamente, email ou senha incorretos')  # noqa: E501

    return render_template('login.html')


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        if User.query.filter_by(email=email).first():
            return render_template('registration.html', error="email já existente")  # noqa: E501

        # Cria o usuário
        user = User(email=email, name=name, password=password, xp=0, dias=0)
        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template('registration.html')


# Iniciando página de conteúdo
# (Estruturar página para também suportar forms e nível)
@app.route('/index')
def index():
    if session.get('user_email') == "admin@admin.com":
        cards = Card.query.order_by(Card.id).all()
    else:
        cards = Card.query.filter_by(user_email=session.get('user_email')).order_by(Card.id).all()  # noqa: E501

    dados = {
        "users": User.query.filter_by(email=session.get("user_email")).first(),
        "pessoa": User.name,
        "xp": User.xp,
        "dia": User.dias
    }
    return render_template('index.html', cards=cards, dados=dados)


# Iniciando página de cartãos
@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)

    return render_template('card.html', card=card)


# Iniciando página de criação de cartão
@app.route('/create')
def create():
    return render_template('create_card.html')


@app.route('/delete/<int:id>')
def delete_card(id):
    # Removendo do Banco de Dados
    card = Card.query.get(id)
    db.session.delete(card)
    db.session.commit()
    return redirect('/index')


# Diario da pessoa
@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        card = Card(title=title, subtitle=subtitle, text=text, user_email=session.get('user_email'))  # noqa: E501

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')


# Questionário diário
@app.route('/questions/<str:tema>', methods=['GET', 'POST'])
def questions(tema):

    if request.method == 'POST':
        form = request.form  # Pega todos os valores
        final = [question for question in form.values()]
        nota = sum(final) / len(final)  # Média para gerar um resuldado até 10

        quiz = Quiz(tema=tema, nota=nota, ideia=random.choice(perguntas[tema]), user_email=session.get("user_email"))  # Jesus cristo | # noqa: E501
        # Lembrar de adicionar cor específica a partir da nota

        db.session.add(quiz)  # Adiciona os dados do quiz

        usuario = User.query.filter_by(email=session.get("user_email")).first()  # Atualiza para o user ganhar +10 xp | # noqa: E501
        usuario.xp += 10
        usuario.dias += 1

        db.session.commit()
        return redirect('/index')

    else:
        return render_template('questions.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
