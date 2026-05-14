"""
Módulo de integração com a API do Promailer para envio de e-mails transacionais.

Utiliza o endpoint autenticado do Promailer, que exige um SMTP connection ID
cadastrado na plataforma e uma chave de API no header ``Authorization``.

Base URL: https://mailserver.automationlounge.com/api/v1

Variáveis de ambiente necessárias:
    - ``PROMAILER_API_KEY``: Chave de API gerada no painel do Promailer.
    - ``PROMAILER_SMTP_ID``: ID da conexão SMTP cadastrada no Promailer.
    - ``PROMAILER_FROM_EMAIL``: Endereço de e-mail remetente (opcional;
      utiliza o padrão da conexão SMTP se omitido).

Exemplo de uso::

    from apis.promailer import enviar_email

    enviar_email(
        destinatario='cliente@email.com',
        assunto='Redefinição de senha',
        texto='Clique no link para redefinir sua senha: https://...',
        html='<p>Clique <a href="https://...">aqui</a> para redefinir.</p>'
    )
"""

import logging
import os
from typing import Optional

import requests

PROMAILER_BASE_URL = 'https://mailserver.automationlounge.com/api/v1'
PROMAILER_SEND_ENDPOINT = f'{PROMAILER_BASE_URL}/messages/send'

logger = logging.getLogger(__name__)


def enviar_email(
    destinatario: str,
    assunto: str,
    texto: str,
    html: Optional[str] = None,
    remetente: Optional[str] = None,
) -> dict:
    """Envia um e-mail transacional via API autenticada do Promailer.

    Realiza uma requisição ``POST`` para o endpoint ``/messages/send-auth``
    do Promailer, utilizando Bearer Token no header de autenticação e o
    SMTP connection ID configurado na plataforma.

    :param destinatario: Endereço de e-mail do destinatário.
    :param assunto: Assunto do e-mail.
    :param texto: Corpo do e-mail em texto plano. Sempre obrigatório como
                  fallback para clientes que não suportam HTML.
    :param html: Corpo do e-mail em HTML. Opcional — se omitido, apenas o
                 texto plano é enviado.
    :param remetente: Endereço de e-mail remetente personalizado. Opcional —
                      se omitido, utiliza o valor de ``PROMAILER_FROM_EMAIL``
                      ou o padrão da conexão SMTP cadastrada no Promailer.

    :return: Dicionário com a resposta da API do Promailer em caso de sucesso.

    :raises EnvironmentError: Se ``PROMAILER_API_KEY`` ou ``PROMAILER_SMTP_ID``
                              não estiverem definidos nas variáveis de ambiente.
    :raises requests.HTTPError: Se a API retornar um status HTTP de erro (4xx/5xx).
    :raises requests.RequestException: Para erros de rede ou timeout.

    Exemplo::

        resposta = enviar_email(
            destinatario='joao@email.com',
            assunto='Redefinição de senha',
            texto='Acesse o link: https://osean.com.br/redefinir-senha/TOKEN',
            html='<p>Acesse o <a href="https://osean.com.br/redefinir-senha/TOKEN">link</a>.</p>',
        )
        print(resposta)  # {'message': 'Email sent successfully', ...}
    """
    api_key = os.getenv('PROMAILER_API_KEY')
    smtp_id = os.getenv('PROMAILER_SMTP_ID')

    if not api_key:
        raise EnvironmentError(
            'Variável de ambiente PROMAILER_API_KEY não definida. '
            'Adicione-a no painel do Render ou no arquivo .env.'
        )
    if not smtp_id:
        raise EnvironmentError(
            'Variável de ambiente PROMAILER_SMTP_ID não definida. '
            'Copie o SMTP ID do painel do Promailer e adicione ao ambiente.'
        )

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload: dict = {
        'smtpId': smtp_id,
        'to': destinatario,
        'subject': assunto,
        'text': texto,
    }

    if html:
        payload['html'] = html

    from_email = remetente or os.getenv('PROMAILER_FROM_EMAIL')
    if from_email:
        payload['from'] = from_email

    try:
        response = requests.post(
            PROMAILER_SEND_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        logger.info('E-mail enviado com sucesso para %s via Promailer.', destinatario)
        return response.json()

    except requests.HTTPError as exc:
        logger.error(
            'Erro HTTP ao enviar e-mail via Promailer. Status: %s | Resposta: %s',
            exc.response.status_code,
            exc.response.text,
        )
        raise

    except requests.RequestException as exc:
        logger.error('Erro de rede ao contatar a API do Promailer: %s', exc)
        raise