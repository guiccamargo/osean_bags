from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user

from db import db
from extensions import sitemapper
from funcoes import acessar_fotos, acessar_capa
from models import Carrinho, Produto
from rotas.utils import renderizar_header

produtos_bp = Blueprint('produtos', __name__, template_folder='templates')


@sitemapper.include()
@produtos_bp.route('/produtos')
def produtos():
    """
    Renderiza a página de listagem de produtos.

    Suporta busca textual pelo nome do produto via parâmetro de query string
    'busca', processada internamente por listar_produtos().

    Returns:
        Response: Template produtos.html com a lista de produtos encontrados.
    """
    return render_template('produtos.html', **renderizar_header(current_user))


@sitemapper.include()
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


@sitemapper.include()
@produtos_bp.route('/produto/<produto_id>')
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
    return redirect(url_for('produtos.produtos'))


@sitemapper.include()
@produtos_bp.route('/produtos/buscar')
def buscar_produtos():
    """Busca produtos pelo nome e retorna os resultados em formato JSON.

    Rota utilizada pela busca dinâmica do frontend para filtrar produtos
    sem recarregar a página. Aceita um termo de busca via query parameter
    e retorna a lista de produtos cujo nome contenha o termo informado,
    ignorando maiúsculas e minúsculas.

    :queryparam busca: Termo de busca para filtrar produtos pelo nome.
                       Se não informado, retorna todos os produtos.

    :return: JSON contendo uma lista de produtos no formato::

                [
                    {
                        "id": 1,
                        "nome": "Produto X",
                        "preco": 99.90,
                        "imagem": "produto_x.png"
                    },
                    ...
                ]

    .. note::
        A busca utiliza ``ilike`` do SQLAlchemy, que é case-insensitive
        e funciona com o operador ``%termo%``, retornando qualquer produto
        cujo nome contenha o termo em qualquer posição.
    """
    termo = request.args.get('busca', '')
    resultado = Produto.query.filter(Produto.nome.ilike(f'%{termo}%')).all()
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'preco': p.preco,
        'imagem': acessar_capa(p.id)
    } for p in resultado])
