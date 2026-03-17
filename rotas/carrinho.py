from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from flask_login import current_user, login_required

from db import db
from extensions import sitemapper
from funcoes import (
    limpar_carrinho, atualizar_quantia, excluir_item_carrinho,
    acessar_capa, acessar_enderecos, produtos_para_envio,
    somar_valor_dos_items, checar_cupom, aplicar_desconto,
    cupom_ja_usado, usuario_tem_pedido_pago,
)
from models import Carrinho, Produto
from rotas.utils import renderizar_header

carrinho_bp = Blueprint('carrinho', __name__, template_folder='templates')


@sitemapper.include()
@login_required
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
        produtos_no_carrinho.append({'id': produto.id, 'name': produto.nome, 'img': acessar_capa(produto.id),
            'total': round(produto.preco * item.quantidade, 2), 'quantidade': item.quantidade})

    if request.method == 'POST':
        data = request.get_json()
        endereco_id = data['endereco_id']
        opcoes_envio = produtos_para_envio(current_user.id, endereco_id)
    else:
        opcoes_envio = None

    return render_template('cart.html', envio=opcoes_envio, enderecos=acessar_enderecos(current_user.id),
        total_carrinho=somar_valor_dos_items(current_user.id), products=produtos_no_carrinho,
        **renderizar_header(current_user))


@sitemapper.include()
@login_required
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
@login_required
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
@login_required
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


@carrinho_bp.route('/carrinho/cupom', methods=['POST'])
@login_required
def aplicar_cupom():
    """Valida e aplica um cupom de desconto ao total do carrinho.

    Executa as seguintes verificações em ordem antes de aplicar o desconto:

    1. Presença do campo ``codigo`` no JSON da requisição.
    2. Existência do cupom na base de dados.
    3. Se o cupom já foi utilizado pelo usuário em um pedido pago anterior.
    4. Se o cupom é do tipo ``primeira_compra`` e o usuário já possui pedidos pagos.

    O desconto é calculado sobre o valor dos produtos e não inclui o frete.

    Request JSON:
        codigo (str): Código do cupom enviado pelo usuário.

    Returns:
        JSON (200): ``total_com_desconto`` (float), ``desconto_aplicado`` (float)
            e ``cupom_id`` (int) em caso de sucesso. O ``cupom_id`` deve ser
            armazenado pelo frontend para ser enviado ao confirmar o pedido.
        JSON (400): Campo ``codigo`` ausente na requisição.
        JSON (404): Cupom não encontrado ou inválido.
        JSON (409): Cupom já utilizado pelo usuário, ou cupom de primeira
            compra sendo aplicado por usuário com compras anteriores.

    Example::

        # Request
        POST /carrinho/cupom
        { "codigo": "BEMVINDO10" }

        # Response (sucesso)
        { "total_com_desconto": 225.00, "desconto_aplicado": 25.00, "cupom_id": 3 }

        # Response (já usado)
        { "erro": "Você já utilizou este cupom anteriormente." }
    """
    data = request.get_json()

    if not data or 'codigo' not in data:
        return jsonify({'erro': 'Código do cupom não informado.'}), 400

    cupom = checar_cupom(data['codigo'])
    if not cupom:
        return jsonify({'erro': 'Cupom inválido ou não encontrado.'}), 404

    if cupom_ja_usado(cupom.id, current_user.id):
        return jsonify({'erro': 'Você já utilizou este cupom anteriormente.'}), 409

    if cupom.primeira_compra and usuario_tem_pedido_pago(current_user.id):
        return jsonify({'erro': 'Este cupom é válido apenas na primeira compra.'}), 409

    total_original = somar_valor_dos_items(current_user.id)
    total_com_desconto = aplicar_desconto(total_original, cupom)
    desconto_aplicado = round(total_original - total_com_desconto, 2)
    session['cupom_id'] = cupom.id
    session['desconto_percentual'] = cupom.desconto
    return jsonify(
        {'total_com_desconto': total_com_desconto, 'desconto_aplicado': desconto_aplicado, 'cupom_id': cupom.id, })
