"""
Blueprint de redefinição de senha via link por e-mail.

Fornece duas rotas:

- ``/esqueci-senha`` — formulário onde o usuário informa o e-mail para receber
  o link de redefinição.
- ``/redefinir-senha/<token>`` — formulário onde o usuário define a nova senha
  após validar o token recebido por e-mail.

O envio do e-mail é feito via API do Promailer (``apis.promailer.enviar_email``),
substituindo o Flask-Mail. O token é gerado e validado por
:mod:`redefinir_senha` com expiração de 1 hora.
"""

import logging

from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app

from apis.promailer import enviar_email
from db import db
from extensions import sitemapper
from models import Usuario
from redefinir_senha import verificar_token, gerar_token

logger = logging.getLogger(__name__)

redefinir_bp = Blueprint('redefinir', __name__, template_folder='templates')


@sitemapper.include()
@redefinir_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Exibe e processa o formulário de solicitação de redefinição de senha.

    Em requisições GET, renderiza o formulário onde o usuário informa seu e-mail.

    Em requisições POST, verifica se o e-mail existe no banco de dados e, caso
    exista, gera um token seguro e envia um link de redefinição via API do
    Promailer. A mensagem de resposta é sempre a mesma independentemente de o
    e-mail estar ou não cadastrado, evitando a enumeração de usuários.

    O e-mail enviado contém:
        - Versão texto plano com o link de redefinição.
        - Versão HTML formatada com o link clicável.

    :return: Renderiza ``senha/esqueci_senha.html`` em requisições GET.
             Redireciona para ``auth.login`` após o processamento do POST,
             exibindo mensagem flash de confirmação.

    .. note::
        O link enviado expira em 1 hora, conforme definido em
        :func:`redefinir_senha.gerar_token`.

    .. note::
        Falhas no envio do e-mail são registradas no log mas não interrompem
        o fluxo — o usuário sempre recebe a mesma mensagem genérica para
        evitar enumeração de endereços.
    """
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = gerar_token(email)
            link = url_for('redefinir.redefinir_senha', token=token, _external=True)
            site_name = current_app.jinja_env.globals.get('SITE_NAME', 'Osean Bags')

            texto_plano = (
                f'Olá, {usuario.nome}!\n\n'
                f'Recebemos uma solicitação para redefinir a senha da sua conta na {site_name}.\n\n'
                f'Acesse o link abaixo para criar uma nova senha:\n{link}\n\n'
                f'O link expira em 1 hora. Se você não solicitou a redefinição, ignore este e-mail.\n\n'
                f'Equipe {site_name}'
            )

            html_corpo = f"""
            <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; color: #6B5F3B;">
                <h2 style="text-align: center;">Redefinição de Senha</h2>
                <p>Olá, <strong>{usuario.nome}</strong>!</p>
                <p>Recebemos uma solicitação para redefinir a senha da sua conta na {site_name}.</p>
                <p>Clique no botão abaixo para criar uma nova senha:</p>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{link}"
                       style="background-color: #6B5F3B; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 8px; font-size: 16px;">
                        Redefinir Senha
                    </a>
                </div>
                <p style="font-size: 13px; color: #999;">
                    O link expira em <strong>1 hora</strong>. Se você não solicitou a redefinição,
                    ignore este e-mail — sua senha permanece a mesma.
                </p>
                <hr style="border: none; border-top: 1px solid #C8BC9A; margin: 24px 0;">
                <p style="font-size: 12px; color: #bbb; text-align: center;">Equipe {site_name}</p>
            </div>
            """

            try:
                enviar_email(
                    destinatario=email,
                    assunto=f'Redefinição de senha — {site_name}',
                    texto=texto_plano,
                    html=html_corpo,
                )
            except Exception:
                logger.exception(
                    'Falha ao enviar e-mail de redefinição de senha para %s via Promailer.',
                    email,
                )

        flash('Se esse e-mail estiver cadastrado, você receberá um link em breve.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('senha/esqueci_senha.html')


@sitemapper.include()
@redefinir_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """Exibe e processa o formulário de redefinição de senha via token.

    Valida o token recebido na URL com :func:`redefinir_senha.verificar_token`.
    Se válido, em requisições GET exibe o formulário para o usuário definir uma
    nova senha. Em requisições POST, aplica a nova senha ao usuário e redireciona
    para o login.

    :param token: Token assinado com prazo de expiração gerado por
                  :func:`redefinir_senha.gerar_token` e enviado por e-mail.

    :return: Redireciona para ``redefinir.esqueci_senha`` se o token for
             inválido ou expirado.
             Renderiza ``senha/redefinir_senha.html`` em requisições GET
             com token válido.
             Redireciona para ``auth.login`` após a redefinição bem-sucedida.

    .. warning::
        O token é de uso único por tempo limitado (1 hora). Após a expiração,
        o usuário deverá solicitar um novo link pela rota ``esqueci_senha``.
    """
    email = verificar_token(token)

    if not email:
        flash('Link inválido ou expirado.', category='error')
        return redirect(url_for('redefinir.esqueci_senha'))

    if request.method == 'POST':
        nova_senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario.set_password(nova_senha)
            db.session.commit()
            flash('Senha redefinida com sucesso!', category='success')
            return redirect(url_for('auth.login'))

    return render_template('senha/redefinir_senha.html', token=token)