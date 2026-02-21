import os

import mercadopago


def gerar_link_pagamento(preference_data: dict) -> str:
    """Gera o link de pagamento.

    Utiliza os dados do pedido para gerar um link que direciona o usuário
    para a plataforma do Mercado Pago onde é possível realizar o pagamento.

    :param preference_data: dicionário contendo as informações do pedido.
    :return: link de pagamento.
    """

    sdk = mercadopago.SDK(os.getenv('mercado_pago_teste'))
    result = sdk.preference().create(preference_data)
    print(result['response'])
    return result['response']['id'], result['response']['init_point'] # init_point para produção ou sandbox_init_point para desenvolvimento
