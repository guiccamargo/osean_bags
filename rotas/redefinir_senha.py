"""
Blueprint para redefinição de senha via e-mail.

O envio de e-mail é feito em thread separada para evitar que o worker
do Gunicorn fique bloqueado aguardando a resposta SMTP, o que causaria
timeout e SIGKILL do processo.
"""

import threading

from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app
from flask_mail import Message

from db import db
from extensions import mail, sitemapper
from models import Usuario
from redefinir_senha import verificar_token, gerar_token

redefinir_bp = Blueprint('redefinir', __name__, template_folder='templates')


def _enviar_email_async(app, msg):
    """Envia um e-mail em thread separada para não bloquear o worker WSGI.

    Abre um novo contexto de aplicação antes do envio, pois threads
    não herdam o contexto Flask da thread principal.

    :param app: Instância da aplicação Flask.
    :param msg: Objeto :class:`flask_mail.Message` pronto para envio.
    """
    with app.app_context():
        mail.send(msg)


@sitemapper.include()
@redefinir_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Exibe e processa o formulário de solicitação de redefinição de senha.

    Em GET, renderiza o formulário onde o usuário informa seu e-mail.
    Em POST, verifica se o e-mail existe e, se sim, dispara o envio do
    link de redefinição em background (thread separada), retornando
    imediatamente para evitar timeout do Gunicorn.

    A resposta é sempre a mesma independentemente de o e-mail estar
    cadastrado, evitando enumeração de usuários.

    :return: Template ``senha/esqueci_senha.html`` em GET.
             Redireciona para ``auth.login`` após o POST.
    """
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = gerar_token(email)
            link = url_for('redefinir.redefinir_senha', token=token, _external=True)

            msg = Message(
                subject='Redefinição de senha',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = (
                f'Clique no link para redefinir sua senha: {link}\n'
                f'O link expira em 1 hora.'
            )

            # Captura a app antes de sair do contexto da requisição
            app = current_app._get_current_object()
            threading.Thread(target=_enviar_email_async, args=(app, msg)).start()

        flash('Se esse e-mail estiver cadastrado, você receberá um link em breve.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('senha/esqueci_senha.html')


@sitemapper.include()
@redefinir_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """Exibe e processa o formulário de redefinição de senha via token.

    Valida o token recebido na URL. Se inválido ou expirado, redireciona
    para a página de solicitação de novo link. Se válido, em GET exibe
    o formulário; em POST aplica a nova senha e redireciona para o login.

    :param token: Token assinado gerado por :func:`redefinir_senha.gerar_token`,
                  enviado ao usuário por e-mail.

    :return: Redireciona para ``redefinir.esqueci_senha`` se o token for inválido.
             Renderiza ``senha/redefinir_senha.html`` em GET com token válido.
             Redireciona para ``auth.login`` após redefinição bem-sucedida.

    .. warning::
        O token é de uso único por tempo limitado. Após a expiração,
        o usuário deve solicitar um novo link.
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


@redefinir_bp.route('/testar-email')
def testar_email():
    """Rota temporária de diagnóstico para verificar configuração de e-mail.

    Remove esta rota após confirmar que o envio funciona.
    """
    import traceback
    from flask import current_app

    config_info = {
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_PORT': current_app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
        'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD_SET': bool(current_app.config.get('MAIL_PASSWORD')),
    }

    try:
        msg = Message(
            subject='Teste de e-mail',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=["test1.course.python@gmail.com"]
        )
        msg.body = 'Se você recebeu este e-mail, a configuração está correta.'
        app = current_app._get_current_object()
        threading.Thread(target=_enviar_email_async, args=(app, msg)).start()
        return f'Envio disparado. Config: {config_info}'
    except Exception as e:
        return f'ERRO: {traceback.format_exc()}<br>Config: {config_info}'