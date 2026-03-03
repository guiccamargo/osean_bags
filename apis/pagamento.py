import os

import mercadopago

def gerar_link_pagamento(preference_data: dict) -> tuple[str, str]:
    """Gera o ID e o link de pagamento no Mercado Pago.

    Cria uma preferência de pagamento na API do Mercado Pago e retorna
    o ID da preferência e o link de redirecionamento para o checkout.

    :param preference_data: Dicionário com os dados da preferência de pagamento.
                            Deve seguir a estrutura da API do Mercado Pago, contendo
                            campos como ``items``, ``payer``, ``back_urls``, etc.

    :return: Tupla ``(preference_id, init_point)`` onde:
             - ``preference_id`` é o ID único da preferência criada.
             - ``init_point`` é a URL de checkout para redirecionar o usuário.

    .. note::
        Em produção, use ``init_point``.
        Em desenvolvimento, substitua por ``sandbox_init_point``.

    .. warning::
        A chave ``mercado_pago_teste`` deve estar definida nas variáveis de ambiente.

    Exemplo de uso::

        preference_data = {
            'items': [{
                'title': 'Produto X',
                'quantity': 1,
                'unit_price': 99.90
            }]
        }

        preference_id, link = gerar_link_pagamento(preference_data)
        return redirect(link)
    """

    sdk = mercadopago.SDK(os.getenv('mercado_pago_teste'))
    result = sdk.preference().create(preference_data)

    return result['response']['id'], result['response']['init_point']
