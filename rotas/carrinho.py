from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from db import db
from funcoes import limpar_carrinho, atualizar_quantia, excluir_item_carrinho, acessar_capa, \
    acessar_enderecos, produtos_para_envio
from models import Carrinho, Produto
from rotas.utils import renderizar_header

carrinho_bp = Blueprint('carrinho', __name__, template_folder='templates')


@carrinho_bp.route('/carrinho', methods=['GET', 'POST'])
def ir_para_carrinho():
    """
    Renderiza a página do carrinho de compras.

    No metodo GET, exibe os produtos no carrinho do usuário autenticado com
    nome, imagem, quantidade e valor total por item.

    No metodo POST (via fetch/JSON), recebe um endereco_id e retorna as opções
    de frete disponíveis para aquele endereço. O resultado é passado ao template
    para exibição via envio.

    Returns:
        GET: Template cart.html com os produtos do carrinho e endereços cadastrados.
        POST: Template cart.html com as opções de frete calculadas para o endereço.

    Note:
        Itens com produto_id igual a 0 são ignorados na listagem, pois indicam
        registros inválidos ou produtos removidos do catálogo.
    """
    produtos_no_carrinho = []
    all_items = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == current_user.id)).scalars()
    for item in all_items:
        if item.produto_id == 0:
            continue
        produto = db.get_or_404(Produto, item.produto_id)
        produtos_no_carrinho.append({
            'id': produto.id,
            'name': produto.nome,
            'img': acessar_capa(produto.id),
            'total': round(produto.preco * item.quantidade, 2),
            'quantidade': item.quantidade
        })

    if request.method == 'POST':
        data = request.get_json()
        endereco_id = data['endereco_id']
        opcoes_envio = produtos_para_envio(current_user.id, endereco_id)
    else:
        opcoes_envio = None

    return render_template(
        'cart.html',
        envio=opcoes_envio,
        enderecos=acessar_enderecos(current_user.id),
        products=produtos_no_carrinho,
        **renderizar_header(current_user)
    )


@carrinho_bp.route('/cart/clear', methods=['GET', 'POST'])
def clear_checkout():
    """
    Remove todos os itens do carrinho do usuário autenticado.

    Utilizado após a conclusão de um pedido para limpar o carrinho.

    Returns:
        Response: Redirecionamento para carrinho.ir_para_carrinho.
    """
    limpar_carrinho(current_user.id)
    return redirect(url_for('carrinho.ir_para_carrinho'))


@carrinho_bp.route('/atualizar/<int:user_id>/<int:product_id>', methods=['GET', 'POST'])
def atualizar_item(user_id, product_id):
    """
    Atualiza a quantidade de um produto no carrinho.

    Se a nova quantidade for 0, o item é removido do carrinho.
    Caso contrário, a quantidade é atualizada para o valor informado.

    Args:
        user_id (int): ID do usuário dono do carrinho.
        product_id (int): ID do produto a ser atualizado.

    Query Params:
        quantidade (int): Nova quantidade desejada para o produto.

    Returns:
        Response: Redirecionamento para carrinho.ir_para_carrinho.
    """
    quantidade = request.args.get('quantidade', type=int)
    if quantidade == 0:
        excluir_item_carrinho(user_id, product_id)
    else:
        atualizar_quantia(user_id, product_id, quantidade)
    return redirect(url_for('carrinho.ir_para_carrinho'))


@carrinho_bp.route('/deletar/<int:user_id>/<int:product_id>', methods=['GET', 'POST'])
def deletar_item(user_id, product_id):
    """
    Remove um produto específico do carrinho do usuário.

    Args:
        user_id (int): ID do usuário dono do carrinho.
        product_id (int): ID do produto a ser removido.

    Returns:
        Response: Redirecionamento para carrinho.ir_para_carrinho.
    """
    excluir_item_carrinho(user_id, product_id)
    return redirect(url_for('carrinho.ir_para_carrinho'))
