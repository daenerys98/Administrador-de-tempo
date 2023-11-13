from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask.cli import FlaskGroup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_unico_e_seguro'
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/admintempo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

Base = db.Model

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    tarefas = relationship('Tarefa', back_populates='usuario')

class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id = Column(Integer, primary_key=True)
    nome_tarefa = Column(String(255), nullable=False)
    importancia = Column(Enum('baixa', 'media', 'importante'), nullable=False)
    anotacao = Column(Text)
    user_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    usuario = relationship('Usuario', back_populates='tarefas')

# Cria o banco de dados se não existir dentro do contexto do Flask
with app.app_context():
    db.create_all()

    # Adiciona usuários à tabela Usuario
    usuarios = [
        ("Karol Lima", "KL", generate_password_hash("alohomora")),
        ("Ramony Silva", "LR", generate_password_hash("arrozdeleite")),
        ("Cleonice", "Cake", generate_password_hash("pudim"))
    ]

    for nome, login, senha in usuarios:
        novo_usuario = Usuario(login=login, senha=senha)
        db.session.add(novo_usuario)

    # Commit para salvar as alterações no banco de dados
    db.session.commit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/contatos')
def contatos():
    return render_template("contatos.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(login=login).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, senha):
            session['user_id'] = usuario.id
            flash('Seja bem-vindo!')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Usuário ou senha incorretos')

    return render_template("login.html")

@app.route('/nova', methods=['GET', 'POST'])
def nova():
    if 'user_id' in session:
        if request.method == 'POST':
            nome_tarefa = request.form.get('nome_tarefa')
            importancia = request.form.get('importancia')
            anotacao = request.form.get('anotacao')

            nova_tarefa = Tarefa(nome_tarefa=nome_tarefa, importancia=importancia, anotacao=anotacao, user_id=session['user_id'])
            
            db.session.add(nova_tarefa)
            db.session.commit()

            flash('Tarefa adicionada com sucesso!', 'success')
            return redirect(url_for('tarefas'))

        return render_template("nova.html")

    else:
        flash('Você precisa fazer login para acessar esta página', 'error')
        return redirect(url_for('login'))
    
@app.route("/tarefas")
def tarefas():
    if 'user_id' in session:
        tarefas = Tarefa.query.filter_by(user_id=session['user_id']).all()
        return render_template("tarefas.html", tarefas=tarefas)

    else:
        flash('Você precisa fazer login para acessar esta página', 'error')
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))

    
if __name__ == '__main__':
    app.run(debug=True)
# rest of your code remains unchanged
