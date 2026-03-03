from typing import List

from flask import url_for

from apis.envio import calcular_frete
from apis.pagamento import gerar_link_pagamento
from db import db
from models import Carrinho, Endereco, Produto, Config, Usuario, Pedido, ItemPedido


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
             'weight': produto.peso, 'quantity': item.quantidade, 'time': produto.producao})
    config_info = Config.query.first().__dict__  # Acessa informações sobre o endereço de envio

    return calcular_frete(produtos=lista_de_produtos, cep_destino=endereco.cep, cep_origem=config_info['cep_origem'],
                          email_contato=config_info['email'])


def fechar_pedido(id_usuario: int, endereco_id: int, frete: str) -> tuple[str, str]:
    """Consolida o carrinho em um pedido e gera o link de pagamento.

    Reúne os dados do usuário, endereço de entrega, itens do carrinho e frete
    para criar um :class:`Pedido` com seus respectivos :class:`ItemPedido` no
    banco de dados e montar a preferência de pagamento para o Mercado Pago.

    :param id_usuario: ID do usuário autenticado realizando a compra.
    :param endereco_id: ID do endereço de entrega selecionado pelo usuário.
    :param frete: String com os dados do frete no formato ``'nome|preco|prazo'``.

                  - ``nome``: nome ou modalidade do serviço de entrega.
                  - ``preco``: valor do frete em reais (convertido para ``float``).
                  - ``prazo``: prazo de entrega em dias úteis (convertido para ``int``).

                  Exemplo: ``'PAC|29.90|8'``

    :return: Tupla ``(preference_id, init_point)`` onde:

             - ``preference_id`` é o ID da preferência criada no Mercado Pago.
             - ``init_point`` é a URL de checkout para redirecionar o usuário.

    .. note::
        O pedido é persistido no banco de dados antes da chamada à API do
        Mercado Pago, pois o seu ``id`` é usado como ``external_reference``
        para identificação no retorno do pagamento.

    .. note::
        O total do pedido é calculado somando ``preco * quantidade`` de cada
        item do carrinho ao valor do frete.

    .. warning::
        Se a string ``frete`` estiver ausente ou em formato inválido, o custo
        de envio será tratado como ``0.0`` e os campos de frete do pedido
        podem ficar nulos, podendo causar erros. Certifique-se de validar
        o dado antes de chamar esta função.

    As URLs de redirecionamento configuradas na preferência são:

    - **success** e **pending** → ``pagamento.pagamento_sucesso``
    - **failure** → ``geral.home``

    Exemplo de uso::

        preference_id, link = fechar_pedido(
            id_usuario=1,
            endereco_id=3,
            frete='PAC|29.90|8'
        )
        return redirect(link)
    """
    sucesso_url = url_for('pagamento.pagamento_sucesso', _external=True)
    usuario = db.get_or_404(Usuario, id_usuario)
    itens = Carrinho.query.filter_by(usuario_id=id_usuario).all()
    endereco = db.get_or_404(Endereco, endereco_id)

    nome_frete, preco_frete, prazo_frete = None, None, None
    custo_envio = 0.0
    try:
        if frete and '|' in frete:
            nome_frete, preco_frete, prazo_frete = frete.split('|')
            custo_envio = float(preco_frete)
        else:
            pass
    except (ValueError, TypeError):
        pass

    novo_pedido = Pedido(
        usuario_id=id_usuario,
        status='pendente',
        metodo_envio=nome_frete,
        valor_frete=float(preco_frete),
        prazo_envio=int(prazo_frete),
        rua=endereco.rua,
        numero=endereco.numero,
        cidade=endereco.cidade,
        cep=endereco.cep,
        total_pedido=0.0  # Calculado posteriormente
    )

    lista_de_produtos = []
    for item in itens:
        produto = db.get_or_404(Produto, item.produto_id)
        lista_de_produtos.append(
            {'id': str(produto.id), 'title': produto.nome, 'quantity': int(item.quantidade), 'currency_id': 'BRL',
             'unit_price': float(produto.preco),
             })

    total = float(preco_frete)
    for item in itens:
        produto = db.get_or_404(Produto, item.produto_id)
        item_venda = ItemPedido(
            produto_id=produto.id,
            nome=produto.nome,
            quantidade=item.quantidade,
            preco_unitario=produto.preco
        )
        novo_pedido.itens.append(item_venda)
        total += (produto.preco * item.quantidade)

    novo_pedido.total_pedido = total
    db.session.add(novo_pedido)
    db.session.commit()  # Pedido agora tem um ID

    preference_data = {'items': lista_de_produtos,
                       'external_reference': str(novo_pedido.id),  # Crucial para identificar na volta
                       'shipments': {'cost': custo_envio, 'mode': 'not_specified', },
                       'payer': {
                           'name': usuario.nome,
                           'surname': usuario.sobrenome,
                           'email': usuario.email},
                       'back_urls': {
                           'success': url_for('pagamento.pagamento_sucesso', _external=True),
                           'failure': url_for('pagamento.pagamento_falha', _external=True),
                           'pending': url_for('pagamento.pagamento_pendente', _external=True),
                       }, 'auto_return': 'approved', }

    preference_id, init_point = gerar_link_pagamento(preference_data)
    return preference_id, init_point
