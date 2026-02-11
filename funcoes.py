from typing import List

import sqlalchemy.exc
from flask import request, redirect, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash

from db import db
from models import Produto, Usuario, Carrinho, Carrossel, Foto


def soma_itens(id_usuario: int) -> int:
    """
    Soma os itens do Carrinho
    :argument id_usuario: id do usuário atual
    :return: Total de itens
    """
    soma = 0
    todos_itens = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == id_usuario)).scalars()
    for item in todos_itens:
        soma += item.quantidade
    return soma


def listar_produtos():
    """
    Acessa os produtos do Banco de Dados
    :return: lista de produtos
    """
    lista_produtos = []
    todos_produtos = Produto.query.all()
    for produto in todos_produtos:
        lista_produtos.append({
            "id": produto.id,
            "imagem": acessar_capa(produto.id),
            "nome": produto.nome,
            "preco": produto.preco,
        })
    return lista_produtos


def limpar_carrinho(id_usuario: int):
    """
    Deleta produtos do carrinho
    :argument id_usuario: id dousuário atual
    """
    items = Carrinho.query.filter_by(usuario_id=id_usuario).delete()
    db.session.commit()


def acessar_carrossel() -> List[str]:
    """
    Acessa os itens do carrossel
    :return: lista com o caminho das imagens do carrossel
    """
    try:
        banners = []
        return Carrossel.query.all()
    except sqlalchemy.exc.OperationalError:
        return None


def registar():
    """
    Registra um novo usuário
    """
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    new_user = Usuario(email=email, name=nome,
                       password=generate_password_hash(senha, method="pbkdf2:sha256",
                                                       salt_length=8))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)

def atualizar_quantia(id_usuario, id_produto, nova_quantidade):
    cart_item = Carrinho.query.filter_by(usuario_id=id_usuario, produto_id=id_produto).first()
    cart_item.quantidade = nova_quantidade
    db.session.commit()

def excluir_item_carrinho(id_usuario, id_produto):
    produto = Carrinho.query.filter_by(usuario_id=id_usuario, produto_id=id_produto).first()
    db.session.delete(produto)
    db.session.commit()

def acessar_fotos(produto_id):
    return db.session.execute(db.select(Foto).where(Foto.produto_id == produto_id)).scalars()

def acessar_capa(produto_id):
    capa = Foto.query.filter_by(produto_id=produto_id).first()
    return capa.arquivo

def acessar_bestsellers():
    lista_produtos = []
    todos_produtos = Produto.query.order_by(Produto.vendas).limit(5).all()
    for produto in todos_produtos:
        lista_produtos.append({
            "id": produto.id,
            "imagem": acessar_capa(produto.id),
            "nome": produto.nome,
            "preco": produto.preco,
        })
    return lista_produtos

def acessar_novidades():
    lista_produtos = []
    novidades = Produto.query.filter_by(novidade=True).all()
    for produto in novidades:
        lista_produtos.append({
            "id": produto.id,
            "imagem": acessar_capa(produto.id),
            "nome": produto.nome,
            "preco": produto.preco,
        })
    return lista_produtos

def acessar_escolha_do_mes():
    escolha = Produto.query.filter_by(escolha_do_mes=True).first()
    return {
            "id": escolha.id,
            "imagem": acessar_capa(escolha.id),
            "nome": escolha.nome,
        }