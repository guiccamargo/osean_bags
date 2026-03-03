from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user

from db import db
from extensions import sitemapper
from funcoes import limpar_carrinho, atualizar_quantia, excluir_item_carrinho, acessar_capa, \
    acessar_enderecos, produtos_para_envio, somar_valor_dos_items
from models import Carrinho, Produto
from rotas.utils import renderizar_header

carrinho_bp = Blueprint('carrinho', __name__, template_folder='templates')


@sitemapper.include()
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
        total_carrinho=somar_valor_dos_items(current_user.id),
        products=produtos_no_carrinho,
        **renderizar_header(current_user)
    )


@sitemapper.include()
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


@sitemapper.include()
@carrinho_bp.route('/carrinho/atualizar/<int:user_id>/<int:product_id>')
def atualizar_item(user_id: int, product_id: int):
    """Atualiza a quantidade de um item no carrinho e retorna os totais em JSON.

    :param user_id: ID do usuário dono do carrinho.
    :param product_id: ID do produto a ser atualizado.

    :queryparam quantidade: Nova quantidade do item. Deve ser um inteiro positivo.

    :return: JSON com o novo total do item e o total geral do carrinho::

                {
                    "novo_total": 199.80,
                    "total_carrinho": 349.70
                }

             Onde:

             - ``novo_total`` é o subtotal do item atualizado (``preco * quantidade``).
             - ``total_carrinho`` é a soma de todos os itens do carrinho do usuário.

    .. note::
        Ambos os valores são utilizados pelo frontend para atualizar os totais
        exibidos na página sem recarregar.

    .. warning::
        O ``total_carrinho`` é recalculado consultando todos os itens do carrinho
        após a atualização. Em carrinhos com muitos itens isso pode impactar
        a performance, considere otimizar com uma query agregada se necessário.
    """
    quantidade = request.args.get('quantidade', type=int)
    item = Carrinho.query.filter_by(usuario_id=user_id, produto_id=product_id).first_or_404()
    produto = Produto.query.get_or_404(product_id)
    item.quantidade = quantidade
    db.session.commit()
    novo_total = produto.preco * quantidade
    total_carrinho = somar_valor_dos_items(user_id)
    return jsonify({'novo_total': novo_total, 'total_carrinho': total_carrinho})

@sitemapper.include()
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
