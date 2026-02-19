import os

import requests
from dotenv import load_dotenv

from db import db
from models import Config

load_dotenv()
url = "https://melhorenvio.com.br/api/v2/me/shipment/calculate"

def calcular_frete(produtos, cep_destino):
    config_info = db.get_or_404(Config, 1)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('token_envio')}",
        "User-Agent": f"Aplicação {config_info.email}"
    }

    payload = {
        "from": { "postal_code": config_info.cep_origem
 },
        "to": { "postal_code": cep_destino },
        "products": produtos
    }
    response = requests.post(url, headers=headers, json=payload)
    lista_envios = []
    for i in range(len(response.json())):
        envio = response.json()[i]
        if envio['company']['name'] == 'Correios' and not envio.get('error'):
            lista_envios.append({'nome': envio['name'], 'preço': envio['price'], 'prazo': envio['delivery_time']})
    return lista_envios

