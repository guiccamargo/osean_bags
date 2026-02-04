from flask_login import UserMixin

from db import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, default=False)

    items_carrinho = db.relationship('Carrinho', lazy='dynamic')

    def __init__(self, email, name, password):
        self.email = email
        self.nome = name
        self.password_hash = password
    def is_admin(self):
        return self.admin


class Carrinho(db.Model):
    __tablename__ = 'carrinho'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=True)
    quantidade = db.Column(db.Integer, default=1)
    produto = db.relationship('Produto')

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200))
    vendas = db.Column(db.Integer, default=0)

class Carrossel(db.Model):
    __tablename__ = 'carrossel'
    id = db.Column(db.Integer, primary_key=True)
    primeira_imagem = db.Column(db.String(200))
    segunda_imagem = db.Column(db.String(200))
