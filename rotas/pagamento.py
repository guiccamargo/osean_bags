import os

from flask import Blueprint, request, flash, redirect, url_for, jsonify, session, render_template
from flask_login import current_user

from funcoes import produtos_para_envio, fechar_pedido

pagamento_bp = Blueprint('pagamento', __name__, template_folder='templates')


@pagamento_bp.route("/calcular-frete", methods=["POST"])
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

    if not data or "endereco_id" not in data:
        return jsonify({"erro": "Dados insuficientes"}), 400

    endereco_id = data["endereco_id"]

    try:
        opcoes_envio = produtos_para_envio(current_user.id, endereco_id)
        return jsonify(opcoes_envio)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pagamento_bp.route("/pagamento/<int:user_id>", methods=["GET", "POST"])
def ir_para_pagamento(user_id):
    """
    Processa o fechamento do pedido e redireciona para o link de pagamento.

    No método POST, coleta o endereço e o método de envio selecionados pelo
    usuário, gera o link de pagamento via API e redireciona para ele.
    Exibe mensagem de erro via flash se nenhum frete for selecionado.

    No método GET, redireciona para o carrinho pois o acesso direto a esta
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
    if request.method == "POST":
        endereco_escolhido = request.form.get("endereco_id")
        metodo_envio = request.form.get("envio")

        if not metodo_envio:
            flash("Por favor, selecione uma opção de frete.")
            return redirect(url_for('carrinho.ir_para_carrinho'))
        preference_id, init_point = fechar_pedido(
            user_id,
            endereco_id=endereco_escolhido,
            frete=metodo_envio
        )
        return redirect(init_point)  # Redireciona direto para o Mercado Pago

    return redirect(url_for('carrinho.ir_para_carrinho'))


@pagamento_bp.route("/pagamento/sucesso")
def pagamento_sucesso():
    """
    Renderiza a página de confirmação após pagamento aprovado.

    Recebe os parâmetros de retorno do Mercado Pago via query string,
    verifica o status do pagamento e exibe a página de sucesso se aprovado.
    Redireciona para home em caso de status diferente de 'approved'.

    Query Params:
        payment_id (str): ID do pagamento gerado pelo Mercado Pago.
        status (str): Status do pagamento (ex: 'approved', 'failure', 'pending').

    Returns:
        Response: Template redirect/sucesso.html se o pagamento for aprovado.
        Response: Redirecionamento para geral.home caso contrário.

    Note:
        O resumo do pedido é recuperado da sessão via 'ultimo_pedido'.
        Considere implementar a limpeza do carrinho nesta rota após confirmar
        o pagamento aprovado, chamando limpar_carrinho(current_user.id).
    """
    payment_id = request.args.get('payment_id')
    status = request.args.get('status')
    resumo_pedido = session.get('ultimo_pedido')

    if status == "approved":
        return render_template("redirect/sucesso.html", pedido=resumo_pedido, payment_id=payment_id)

    return redirect(url_for('geral.home'))
