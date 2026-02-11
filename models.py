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

    def get_inicial(self):
        return str(self.nome[0]).upper()

class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text(), nullable=False)
    fotos = db.relationship(
        'Foto',
        backref='produto',
        cascade='all, delete-orphan',
        lazy=True
    )
    vendas = db.Column(db.Integer, nullable=False, default=0)
    novidade = db.Column(db.Boolean, default=False)
    escolha_do_mes = db.Column(db.Boolean, default=False)

class Foto(db.Model):
    __tablename__ = 'fotos'

    id = db.Column(db.Integer, primary_key=True)
    arquivo = db.Column(db.String(200), nullable=False)

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id'),
        nullable=False
    )

# class Produto(db.Model):
#     __tablename__ = 'produtos'
#
#     id = db.Column(db.Integer, primary_key=True)
#     nome = db.Column(db.String(100), nullable=False)
#     preco = db.Column(db.Float, nullable=False)
#     capa = db.Column(db.String(200))
#     descricao = db.Column(db.Text(), nullable=False)
#     vendas = db.Column(db.Integer, default=0)
#
#     fotos = db.relationship('Foto', backref='produto', lazy=True)


class Carrossel(db.Model):
    __tablename__ = 'carrossel'

    id = db.Column(db.Integer, primary_key=True)
    arquivo = db.Column(db.String(200), nullable=False)



class Carrinho(db.Model):
    __tablename__ = 'carrinho'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=True)
    quantidade = db.Column(db.Integer, default=1)
    produto = db.relationship('Produto')