import os

from flask import Blueprint, request, flash, redirect, url_for, jsonify, session, render_template
from flask_login import current_user

from db import db
from funcoes import produtos_para_envio, fechar_pedido
from models import Pedido, Carrinho, Usuario, ItemPedido, Produto

pagamento_bp = Blueprint('pagamento', __name__, template_folder='templates')


@pagamento_bp.route('/calcular-frete', methods=['POST'])
def calcular_frete_rota():
    """
    Calcula as opções de frete para um endereço informado via JSON.

    Recebe uma requisição POST com um endereco_id no corpo JSON, consulta
    as dimensões e pesos dos produtos no carrinho do usuário e retorna as
    opções de frete disponíveis via API de envio.

    Request JSON:
        endereco_id (int): ID do endereço de destino para cálculo do frete.

    Returns:
        JSON: Lista de opções de frete disponíveis em caso de sucesso.
        JSON (400): Mensagem de erro se os dados forem insuficientes.
        JSON (500): Mensagem de erro em caso de falha no cálculo.
    """
    data = request.get_json()

    if not data or 'endereco_id' not in data:
        return jsonify({'erro': 'Dados insuficientes'}), 400

    endereco_id = data['endereco_id']

    try:
        opcoes_envio = produtos_para_envio(current_user.id, endereco_id)
        return jsonify(opcoes_envio)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@pagamento_bp.route('/pagamento/<int:user_id>', methods=['GET', 'POST'])
def ir_para_pagamento(user_id):
    """
    Processa o fechamento do pedido e redireciona para o link de pagamento.

    No metodo POST, coleta o endereço e o meodo de envio selecionados pelo
    usuário, gera o link de pagamento via API e redireciona para ele.
    Exibe mensagem de erro via flash se nenhum frete for selecionado.

    No metodo GET, redireciona para o carrinho pois o acesso direto a esta
    rota sem submissão de formulário não é suportado.

    Args:
        user_id (int): ID do usuário realizando o pedido.

    Returns:
        POST (sucesso): Redirecionamento para o link de pagamento externo.
        POST (sem frete): Redirecionamento para carrinho.ir_para_carrinho com flash.
        GET: Redirecionamento para carrinho.ir_para_carrinho.

    Note:
        O frete é recebido no formato 'nome|preco|prazo' e parseado
        internamente por fechar_pedido().
    """
    if request.method == 'POST':
        endereco_escolhido = request.form.get('endereco_id')
        metodo_envio = request.form.get('envio')

        if not metodo_envio:
            flash('Por favor, selecione uma opção de frete.')
            return redirect(url_for('carrinho.ir_para_carrinho'))
        preference_id, init_point = fechar_pedido(
            user_id,
            endereco_id=endereco_escolhido,
            frete=metodo_envio
        )
        return redirect(init_point)  # Redireciona direto para o Mercado Pago

    return redirect(url_for('carrinho.ir_para_carrinho'))


@pagamento_bp.route('/pagamento/sucesso')
def pagamento_sucesso():
    """Processa o retorno do Mercado Pago após um pagamento bem-sucedido.

    Rota de callback chamada automaticamente pelo Mercado Pago ao final do
    checkout. Valida o pagamento recebido via query params, atualiza o status
    do pedido no banco de dados, limpa o carrinho do usuário e exibe a página
    de confirmação.

    O Mercado Pago envia os seguintes parâmetros na URL de retorno:

    :queryparam external_reference: ID do pedido gerado internamente,
                                    definido na preferência de pagamento.
    :queryparam payment_id: ID único do pagamento gerado pelo Mercado Pago.
    :queryparam status: Status do pagamento (ex: ``approved``, ``pending``, ``rejected``).

    :return: Renderiza ``redirect/sucesso.html`` com os dados do pedido quando
             o pagamento for aprovado. Redireciona para a página inicial
             (``geral.home``) caso o status não seja ``approved`` ou o
             ``external_reference`` esteja ausente.

    .. note::
        O carrinho do usuário é apagado do banco de dados somente após a
        confirmação do pagamento com status ``approved``.

    .. warning::
        Esta rota não exige autenticação pois é acessada via redirecionamento
        externo do Mercado Pago. Certifique-se de validar os dados recebidos
        antes de qualquer operação sensível. Para maior segurança, considere
        também verificar o pagamento via webhook ou consulta direta à API.
    """

    pedido_id = request.args.get('external_reference')
    payment_id = request.args.get('payment_id')
    status = request.args.get('status')
    if status == 'approved' and pedido_id:
        pedido = Pedido.query.get(pedido_id)
        nome = db.get_or_404(Usuario, pedido.usuario_id).nome
        carrinho = Carrinho.query.filter_by(usuario_id=pedido.usuario_id)
        if pedido:
            pedido.status = 'pago'
            pedido.payment_id_mercadopago = payment_id
            all_items = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == pedido.usuario_id)).scalars()
            produtos = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
            for item in all_items:
                if item.produto_id == 0:
                    continue
            # Limpa o carrinho do banco de dados agora que a venda foi concluída
            carrinho.delete()

            db.session.commit()
            return render_template('redirect/sucesso.html', pedido=pedido, nome=nome, produtos=produtos)

    return redirect(url_for('geral.home'))