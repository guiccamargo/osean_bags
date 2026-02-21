from typing import List

import sqlalchemy
from flask import request

from db import db
from models import Produto, Foto, Usuario


def listar_produtos() -> List[dict]:
    """Lista os produtos do banco de dados.

    Acessa os produtos do banco de dados, gera dicionários com as informações
    relevantes dos produtos e implementa a barra de buscas.


    :return: lista de produtos.
    """
    busca = request.args.get('busca')  # Buscar por produtos pelo nome

    # Realizar busca
    if busca:
        produtos = Produto.query.filter(Produto.nome.ilike(f'%{busca}%')).all()
    else:
        produtos = Produto.query.all()

    lista_produtos = []

    # Listar produtos
    for produto in produtos:
        lista_produtos.append(
            {'id': produto.id, 'imagem': acessar_capa(produto.id), 'nome': produto.nome, 'preco': produto.preco, })

    return lista_produtos


def acessar_capa(produto_id: int) -> str:
    """Acessa a primeira foto de um produto.

    Acessa a primeira foto registrada no banco de dados referente ao produto selecionado.
    :param produto_id: id do produto selecionado.
    :return: caminho do arquivo com a foto.
    """

    capa = Foto.query.filter_by(produto_id=produto_id).first()
    return capa.arquivo


def acessar_fotos(produto_id: int) -> sqlalchemy.engine.result.ScalarResult:
    """Acessa fotos de um produto.

    Localiza as fotos correspondentes a um produto.

    :param produto_id: id do produto selecionado.
    :return: fotos extraidas do banco de dados.
    """

    return db.session.execute(db.select(Foto).where(Foto.produto_id == produto_id)).scalars()


def acessar_bestsellers() -> List[dict]:
    """Acessa os produtos mais vendidos do site.

    Gera uma lista com dicionários contendo informações dos produtos mais vendidos.

    :return: lista de produtos mais vendidos.
    """

    lista_produtos = []

    todos_produtos = Produto.query.order_by(Produto.vendas).limit(5).all()  # Acessa os 5 produtos mais vendidos

    for produto in todos_produtos:
        lista_produtos.append(
            {'id': produto.id, 'imagem': acessar_capa(produto.id), 'nome': produto.nome, 'preco': produto.preco, })

    return lista_produtos


def acessar_novidades() -> List[dict]:
    """Acessa os produtos da seção de novidades.

    Acessa os produtos no banco de dados que estão marcados como novidade.

    :return: Lista com dicionários contendo informações relevantes dos produtos.
    """

    lista_produtos = []

    novidades = Produto.query.filter_by(novidade=True).all()

    for produto in novidades:
        lista_produtos.append(
            {'id': produto.id, 'imagem': acessar_capa(produto.id), 'nome': produto.nome, 'preco': produto.preco, })

    return lista_produtos


def acessar_escolha_do_mes() -> dict[str, str] | None:
    """Acessa o produto do mês.

    Acessa o produto do banco de dados marcado como escolha do mês.

    :return: dicionário contendo informações do produto do mês se ele for localizado, caso contrário, retorna None.
    """

    escolha = Produto.query.filter_by(escolha_do_mes=True).first()

    if not escolha:  # Checa se a escolha do mês existe
        return None
    return {'id': escolha.id, 'imagem': acessar_capa(escolha.id), 'nome': escolha.nome, }


def acessar_inicial(usuario_id: int) -> str:
    """Acessa a inicial do nome do usuário logado.

    Acessa a inicial do usuário para exibir na barra de nagevação.

    :param usuario_id: id do usuário logado.
    :return: Inicial do usuário.
    """

    usuario = db.get_or_404(Usuario, usuario_id)

    return usuario.get_inicial()
