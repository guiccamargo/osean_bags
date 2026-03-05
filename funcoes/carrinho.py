from db import db
from models import Carrinho, Produto


def soma_itens(id_usuario: int) -> int:
    """Soma todos os itens do Carrinho.

    Acessa um Carrinho do banco de dados correspondente ao id do usuário e soma o valor dos itens neste carrinho.

    :argument id_usuario: id do usuário atual.
    :return: Total dos itens.
    """
    soma = 0
    todos_itens = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == id_usuario)).scalars()
    for item in todos_itens:
        soma += item.quantidade
    return soma

def somar_valor_dos_items(id_usuario: int) -> float:
    """Calcula o valor total dos itens no carrinho do usuário.

    Acessa todos os itens do carrinho e soma o produto entre
    quantidade e preço unitário de cada produto.

    :param id_usuario: ID do usuário cujo carrinho será somado.
    :return: Valor total dos itens em reais (float).
    """
    soma = 0
    todos_itens = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == id_usuario)).scalars()
    for item in todos_itens:
        produto = db.get_or_404(Produto, item.produto_id)
        soma += item.quantidade * produto.preco
    return soma

def limpar_carrinho(id_usuario: int):
    """Deleta produtos do carrinho.

    Acessa o caarinho no banco de dados associado com o id do usuário informado.

    :argument id_usuario: id do usuário atual.
    """

    items = Carrinho.query.filter_by(usuario_id=id_usuario).delete()
    db.session.commit()


def atualizar_quantia(id_usuario: int, id_produto: int, nova_quantidade: int) -> None:
    """Atualiza a quantidade de um produto no carrinho.

    Acessa o carrinho do usuário correspondente no banco de dados, atualiza a quantidade do produto informado.

    :param id_usuario: id do usuário referente ao carrinho.
    :param id_produto: id do produto a ser atualizado.
    :param nova_quantidade: nova quantidade.
    :return: None
    """

    cart_item = Carrinho.query.filter_by(usuario_id=id_usuario, produto_id=id_produto).first()
    cart_item.quantidade = nova_quantidade
    db.session.commit()


def excluir_item_carrinho(id_usuario: int, id_produto: int) -> None:
    """Exclui um produto do carrinho.

    Acessa o Carrinho no banco de dados e exclui o produto selecionado.

    :param id_usuario: id do usuário referente ao carrinho.
    :param id_produto: id do produto a ser excluido.
    :return: None
    """

    produto = Carrinho.query.filter_by(usuario_id=id_usuario, produto_id=id_produto).first()
    db.session.delete(produto)
    db.session.commit()
