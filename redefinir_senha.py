"""
Módulo de geração e validação de tokens para redefinição de senha.

Utiliza :class:`itsdangerous.URLSafeTimedSerializer` para criar tokens
assinados com prazo de expiração, garantindo que apenas links válidos
e recentes possam ser utilizados para redefinir a senha de um usuário.

"""
import logging
import os

from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = os.getenv('SECRET_KEY')
s = URLSafeTimedSerializer(SECRET_KEY)


def gerar_token(email: str) -> str:
    """Gera um token seguro e assinado associado ao e-mail do usuário.

    O token é criado com ``salt='redefinir-senha'``, garantindo que tokens
    gerados para outros fins não possam ser reutilizados aqui.

    :param email: E-mail do usuário que solicitou a redefinição de senha.
    :return: Token assinado em formato URL-safe para ser enviado por e-mail.

    Exemplo::

        token = gerar_token('joao@email.com')
        link = url_for('redefinir.redefinir_senha', token=token, _external=True)
    """
    return s.dumps(email, salt='redefinir-senha')


def verificar_token(token: str, expiracao: int = 3600) -> str | None:
    """Valida um token de redefinição de senha e retorna o e-mail associado.

    Verifica a assinatura e o prazo de expiração do token. Retorna ``None``
    silenciosamente em caso de token inválido, adulterado ou expirado —
    nunca relança a exceção, para que o fluxo de redefinição possa
    tratar a falha com uma mensagem amigável ao usuário.

    :param token: Token recebido via URL, gerado por :func:`gerar_token`.
    :param expiracao: Tempo máximo de validade em segundos. Padrão: ``3600`` (1 hora).
    :return: E-mail associado ao token se válido, ``None`` caso contrário.

    Exemplo::

        email = verificar_token(token)
        if email is None:
            flash('Link inválido ou expirado.')
            return redirect(url_for('redefinir.esqueci_senha'))
    """
    try:
        email = s.loads(token, salt='redefinir-senha', max_age=expiracao)
        return email
    except Exception:
        logging.warning('Token de redefinição inválido ou expirado.')
        return None