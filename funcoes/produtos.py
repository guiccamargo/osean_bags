from typing import List

import sqlalchemy
from flask import request

from db import db
from models import Produto, Foto


def listar_produtos() -> List[dict]:
    """Lista os produtos do banco de dados.

    Acessa os produtos do banco de dados, gera dicionários com as informações
    relevantes dos produtos.


    :return: lista de produtos.
    """
    busca = request.args.get('busca')  # Buscar por produtos pelo nome

    # Realizar busca
    produtos = Produto.query.filter(Produto.nome.ilike(f'%{busca}%')).all()


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


def atualizar_quantidade_vendas(id_produto: int, quantidade_adicional: int) -> None:
    """
    Incrementa o contador de vendas de um produto.

    Acessa o produto no banco de dados e adiciona a quantidade informada
    ao total de vendas acumulado. Utilizado após a confirmação de um pedido
    para manter o ranking de bestsellers atualizado.

    Args:
        id_produto (int): ID do produto a ser atualizado.
        quantidade_adicional (int): Quantidade vendida a ser somada ao total.

    Raises:
        404: Se nenhum produto for encontrado com o id informado.

    Example:
        # Após confirmar um pedido com 3 unidades do produto 42:
        atualizar_quantidade_vendas(id_produto=42, quantidade_adicional=3)
    """
    produto = db.get_or_404(Produto, id_produto)
    produto.vendas += quantidade_adicional
    db.session.commit()
