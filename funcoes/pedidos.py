from typing import List

from apis.envio import calcular_frete
from apis.pagamento import gerar_link_pagamento
from db import db
from models import Carrinho, Endereco, Produto, Config, Usuario


def produtos_para_envio(id_usuario: int, endereco_id: int) -> List[dict]:
    """Lista os produtos de um carrinho para realizar o cálculo de frete.

    Acessa as informações dos produtos em um carrinho e quantidade dos produtos para calcular o valor do frete.

    :param id_usuario: id do usuário atual.
    :param endereco_id: id do endereço de entrega fornecido pelo usuário.
    :return: lista com opções de frete encontradas para o endereço informado.
    """

    items = Carrinho.query.filter_by(usuario_id=id_usuario).all()
    lista_de_produtos = []
    endereco = db.get_or_404(Endereco, endereco_id)
    for item in items:
        produto = db.get_or_404(Produto, item.produto_id)
        lista_de_produtos.append(
            {'id': produto.id, 'width': produto.largura, 'height': produto.altura, 'length': produto.comprimento,
             'weight': produto.peso, 'quantity': item.quantidade})
    config_info = Config.query.first().__dict__  # Acessa informações sobre o endereço de envio

    return calcular_frete(produtos=lista_de_produtos, cep_destino=endereco.cep, cep_origem=config_info['cep_origem'],
                          email_contato=config_info['email'])


def fechar_pedido(id_usuario: int, endereco_id: int, frete: str) -> tuple[str, str]:
    """Formata os dados do pedido para realizar o pagamento.

    Acessa as informações dos produtos comprados, do comprador e da entrega
    e prepara os dados para gerar o link de pagamento.

    :param id_usuario: id do usuário atual.
    :param endereco_id: id do endereço de entrega.
    :param frete: tipo, valor e prazo de entrega.
    :return: tupla (preference_id, link_de_pagamento).
    """
    usuario = db.get_or_404(Usuario, id_usuario)
    itens = Carrinho.query.filter_by(usuario_id=id_usuario).all()
    endereco = db.get_or_404(Endereco, endereco_id)

    # Formata as informações do frete
    try:
        if frete and '|' in frete:
            nome_frete, preco_frete, prazo_frete = frete.split('|')
            custo_envio = float(preco_frete)
        else:
            custo_envio = 0.0
    except (ValueError, TypeError):
        custo_envio = 0.0

    # Lista os produtos do carrinho
    lista_de_produtos = []
    for item in itens:
        produto = db.get_or_404(Produto, item.produto_id)
        lista_de_produtos.append(
            {'id': str(produto.id), 'title': produto.nome, 'quantity': int(item.quantidade), 'currency_id': 'BRL',
             'unit_price': float(produto.preco),  # Garante que é float
             })

    # Constroi o dicionário para a api de pagamento
    preference_data = {'items': lista_de_produtos, 'shipments': {'cost': custo_envio, 'mode': 'not_specified', },
                       "payer": {
                           "name": usuario.nome,
                           "surname": usuario.sobrenome,
                           "email": usuario.email},
                       # URLs de redirecionamento
                       "back_urls": {
                           "success": "https://test.com/success",
                           "failure": "https://test.com/failure",
                           "pending": "https://test.com/pending",
                       }, 'auto_return': 'approved', }


    preference_id, init_point = gerar_link_pagamento(preference_data)
    return preference_id, init_point
