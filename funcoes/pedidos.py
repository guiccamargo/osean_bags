from typing import List, Optional

from flask import url_for

from apis.envio import calcular_frete
from apis.pagamento import gerar_link_pagamento
from db import db
from funcoes.cupons import registrar_uso_cupom
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

    config = Config.query.first() # Acessa informações sobre o endereço de envio
    if not config:
        raise RuntimeError("Configurações da loja não encontradas.")
    config_info = config.__dict__

    return calcular_frete(produtos=lista_de_produtos, cep_destino=endereco.cep, cep_origem=config_info['cep_origem'],
                          email_contato=config_info['email'])


def fechar_pedido(
    id_usuario: int,
    endereco_id: int,
    frete: str,
    cupom_id: Optional[int] = None,
    desconto_percentual: float = 0.0,
    cupom_frete_gratis: bool = False,
) -> tuple[str, str]:
    """Consolida o carrinho em um pedido e gera o link de pagamento.

    Aplica, se fornecidos, desconto percentual sobre os produtos e/ou
    frete grátis, refletindo ambos no payload enviado ao Mercado Pago.

    :param id_usuario: ID do usuário autenticado realizando a compra.
    :param endereco_id: ID do endereço de entrega selecionado.
    :param frete: Dados do frete no formato ``'nome|preco|prazo'``.
    :param cupom_id: ID do cupom aplicado, ou ``None`` se ausente.
    :param desconto_percentual: Percentual de desconto sobre produtos (0–100).
    :param cupom_frete_gratis: Se ``True``, zera o custo de frete.

    :return: Tupla ``(preference_id, init_point)``.
    """
    usuario = db.get_or_404(Usuario, id_usuario)
    itens = Carrinho.query.filter_by(usuario_id=id_usuario).all()
    endereco = db.get_or_404(Endereco, endereco_id)

    # --- Parse do frete ---
    nome_frete, preco_frete, prazo_frete = None, 0.0, None
    try:
        if frete and '|' in frete:
            nome_frete, preco_frete, prazo_frete = frete.split('|')
            preco_frete = float(preco_frete)
            prazo_frete = int(prazo_frete)
    except (ValueError, TypeError):
        pass

    # Zera o frete se o cupom conceder frete grátis
    custo_envio = 0.0 if cupom_frete_gratis else float(preco_frete)

    # --- Montar itens e calcular total ---
    lista_mp = []   # itens para o Mercado Pago
    total_produtos = 0.0

    novo_pedido = Pedido(
        usuario_id=id_usuario,
        status='pendente',
        metodo_envio=nome_frete,
        valor_frete=custo_envio,
        prazo_envio=prazo_frete,
        rua=endereco.rua,
        numero=endereco.numero,
        cidade=endereco.cidade,
        cep=endereco.cep,
        total_pedido=0.0,
    )

    for item in itens:
        produto = db.get_or_404(Produto, item.produto_id)

        # Preço unitário já com desconto proporcional aplicado
        preco_com_desconto = round(
            produto.preco * (1 - desconto_percentual / 100), 2
        )

        lista_mp.append({
            'id': str(produto.id),
            'title': produto.nome,
            'quantity': int(item.quantidade),
            'currency_id': 'BRL',
            'unit_price': preco_com_desconto,
        })

        item_venda = ItemPedido(
            produto_id=produto.id,
            nome=produto.nome,
            quantidade=item.quantidade,
            preco_unitario=preco_com_desconto,  # snapshot já com desconto
        )
        novo_pedido.itens.append(item_venda)
        total_produtos += preco_com_desconto * item.quantidade

    novo_pedido.total_pedido = round(total_produtos + custo_envio, 2)
    db.session.add(novo_pedido)
    db.session.commit()

    # Registra uso do cupom após commit (pedido já tem ID)
    if cupom_id:
        registrar_uso_cupom(
            cupom_id=cupom_id,
            usuario_id=id_usuario,
            pedido_id=novo_pedido.id,
        )

    # --- Frete como item separado no Mercado Pago ---
    # Só adiciona se houver custo; cupom de frete grátis → não adiciona
    if custo_envio > 0:
        lista_mp.append({
            'id': 'frete',
            'title': f'Frete – {nome_frete}',
            'quantity': 1,
            'currency_id': 'BRL',
            'unit_price': custo_envio,
        })

    preference_data = {
        'items': lista_mp,
        'external_reference': str(novo_pedido.id),
        'payer': {
            'name': usuario.nome,
            'surname': usuario.sobrenome,
            'email': usuario.email,
        },
        'back_urls': {
            'success': url_for('pagamento.pagamento_sucesso', _external=True),
            'failure': url_for('pagamento.pagamento_falha', _external=True),
            'pending': url_for('pagamento.pagamento_pendente', _external=True),
        },
        'auto_return': 'approved',
    }

    preference_id, init_point = gerar_link_pagamento(preference_data)
    return preference_id, init_point
