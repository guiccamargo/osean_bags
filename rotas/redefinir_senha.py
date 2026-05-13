"""
Blueprint para redefinição de senha via e-mail.

Versão otimizada para Render.com:
- evita bloqueio do Gunicorn
- evita timeout SMTP
- evita threads órfãs
- usa ThreadPoolExecutor reutilizável
- tratamento robusto de erros
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_mail import Message

from db import db
from extensions import mail, sitemapper
from models import Usuario
from redefinir_senha import verificar_token, gerar_token

# =========================================================
# CONFIGURAÇÃO
# =========================================================

logging.basicConfig(level=logging.INFO)

redefinir_bp = Blueprint(
    'redefinir',
    __name__,
    template_folder='templates'
)

# Pool reutilizável de threads
executor = ThreadPoolExecutor(max_workers=2)


# =========================================================
# EMAIL ASYNC
# =========================================================

def _send_email(app, msg):
    """
    Executa o envio do e-mail dentro da thread.

    IMPORTANTE:
    - abre app_context corretamente
    - cria conexão SMTP separada
    - evita travar worker do Gunicorn
    """

    with app.app_context():

        try:
            current_app.logger.info(
                'Tentando enviar e-mail para: %s',
                msg.recipients
            )

            # conexão SMTP dedicada
            with mail.connect() as conn:
                conn.send(msg)

            current_app.logger.info(
                'E-mail enviado com sucesso para: %s',
                msg.recipients
            )

        except Exception:
            current_app.logger.exception(
                'Falha ao enviar e-mail para: %s',
                msg.recipients
            )


def enviar_email_async(subject, recipients, body):
    """
    Função pública para disparar e-mail assíncrono.
    """

    app = current_app._get_current_object()

    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )

    executor.submit(_send_email, app, msg)


# =========================================================
# ESQUECI SENHA
# =========================================================

@sitemapper.include()
@redefinir_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():

    if request.method == 'POST':

        email = request.form['email'].strip().lower()

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:

            token = gerar_token(email)

            link = url_for(
                'redefinir.redefinir_senha',
                token=token,
                _external=True
            )

            corpo = (
                'Você solicitou a redefinição de senha.\n\n'
                f'Acesse o link abaixo:\n\n{link}\n\n'
                'O link expira em 1 hora.\n\n'
                'Se você não solicitou esta alteração, ignore este e-mail.'
            )

            enviar_email_async(
                subject='Redefinição de senha',
                recipients=[email],
                body=corpo
            )

        # resposta idêntica evita enumeração de usuários
        flash(
            'Se esse e-mail estiver cadastrado, '
            'você receberá um link em breve.',
            category='success'
        )

        return redirect(url_for('auth.login'))

    return render_template('senha/esqueci_senha.html')


# =========================================================
# REDEFINIR SENHA
# =========================================================

@sitemapper.include()
@redefinir_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):

    email = verificar_token(token)

    if not email:

        flash(
            'Link inválido ou expirado.',
            category='error'
        )

        return redirect(url_for('redefinir.esqueci_senha'))

    if request.method == 'POST':

        nova_senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:

            usuario.set_password(nova_senha)

            db.session.commit()

            flash(
                'Senha redefinida com sucesso!',
                category='success'
            )

            return redirect(url_for('auth.login'))

    return render_template(
        'senha/redefinir_senha.html',
        token=token
    )


# =========================================================
# TESTE SMTP
# =========================================================

@redefinir_bp.route('/testar-email')
def testar_email():

    config_info = {
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_PORT': current_app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': current_app.config.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD_SET': bool(
            current_app.config.get('MAIL_PASSWORD')
        ),
    }

    try:

        enviar_email_async(
            subject='Teste de e-mail',
            recipients=['test1.course.python@gmail.com'],
            body='Se você recebeu este e-mail, a configuração está correta.'
        )

        return {
            'success': True,
            'message': 'E-mail enviado para fila async.',
            'config': config_info
        }

    except Exception as e:

        current_app.logger.exception(e)

        return {
            'success': False,
            'error': str(e),
            'config': config_info
        }, 500