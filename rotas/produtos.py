from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from db import db
from funcoes import listar_produtos, acessar_fotos, acessar_capa
from models import Carrinho, Produto
from rotas.utils import renderizar_header

produtos_bp = Blueprint('produtos', __name__, template_folder='templates')


@produtos_bp.route('/produtos')
def produtos():
    """
    Renderiza a página de listagem de produtos.

    Suporta busca textual pelo nome do produto via parâmetro de query string
    'busca', processada internamente por listar_produtos().

    Returns:
        Response: Template produtos.html com a lista de produtos encontrados.
    """
    return render_template('produtos.html', lista_produtos=listar_produtos(), **renderizar_header(current_user))


@produtos_bp.route('/produtos/<int:produto_id>')
def pagina_produto(produto_id):
    """
    Renderiza a página de detalhes de um produto específico.

    Args:
        produto_id (int): ID do produto a ser exibido.

    Returns:
        Response: Template produto.html com os dados do produto e suas fotos.
    """
    produto = Produto.query.filter_by(id=produto_id).first()
    fotos = acessar_fotos(produto_id)
    return render_template('produto.html', produto=produto, fotos=fotos, **renderizar_header(current_user))


@produtos_bp.route("/produto/<produto_id>")
def buy_product(produto_id):
    """
    Adiciona um produto ao carrinho do usuário autenticado e redireciona para produtos.

    Se o produto já estiver no carrinho, incrementa a quantidade em 1.
    Caso contrário, cria um novo item no carrinho com quantidade 1.

    Args:
        produto_id (int): ID do produto a ser adicionado ao carrinho.

    Returns:
        Response: Redirecionamento para produtos.produtos após a operação.
    """
    usuario_id = current_user.id
    cart_item = Carrinho.query.filter_by(usuario_id=usuario_id, produto_id=produto_id).first()
    if cart_item:
        cart_item.quantidade += 1
    else:
        cart_item = Carrinho(usuario_id=usuario_id, produto_id=produto_id, quantidade=1)
        db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for("produtos.produtos"))
