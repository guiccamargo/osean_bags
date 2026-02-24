import os
from typing import List

import requests
from dotenv import load_dotenv

load_dotenv()


def calcular_frete(produtos: List[dict], cep_destino: str, cep_origem: str, email_contato: str) -> List[dict]:
    """Calcula opções de frete para o pedido
    
    Usa a api do Melhor Envio para estimar o valor do envio dos produtos comprados, 
    filtrando apenas as opções ofertadas pelos Correios.
    
    :param produtos: lista dos produtos comprados.
    :param cep_destino: cep do comprador.
    :param cep_origem: cep do vendedor.
    :param email_contato: email do vendedor
    :return: 
    """

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': f'Bearer {os.getenv("token_envio")}', 'User-Agent': f'Aplicação {email_contato}'}

    payload = {'from': {'postal_code': cep_origem}, 'to': {'postal_code': cep_destino}, 'products': produtos}

    response = requests.post(os.getenv('url_melhor_envio'), headers=headers, json=payload)

    lista_envios = []
    # Filtra opções ofertadas pelos Correios
    for i in range(len(response.json())):
        envio = response.json()[i]
        if envio['company']['name'] == 'Correios' and not envio.get('error'):
            lista_envios.append({'nome': envio['name'], 'preco': envio['price'], 'prazo': envio['delivery_time']})

    return lista_envios
