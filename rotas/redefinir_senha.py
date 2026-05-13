"""
Blueprint para redefinição de senha via e-mail.

Gerencia o fluxo completo: solicitação de link, geração de token seguro
e aplicação da nova senha após validação do token.
"""

from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_mail import Message

from db import db
from extensions import mail, sitemapper
from models import Usuario
from redefinir_senha import verificar_token, gerar_token

redefinir_bp = Blueprint('redefinir', __name__, template_folder='templates')


@sitemapper.include()
@redefinir_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Exibe e processa o formulário de solicitação de redefinição de senha.

    Em GET, renderiza o formulário onde o usuário informa seu e-mail.
    Em POST, verifica se o e-mail existe e, se sim, envia um link de
    redefinição por e-mail com token de expiração de 1 hora.

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
                sender=mail.username,  # usa o atributo da instância, não current_app
                recipients=[email]
            )
            msg.body = f'Clique no link para redefinir sua senha: {link}\nO link expira em 1 hora.'
            mail.send(msg)

        flash('Se esse e-mail estiver cadastrado, você receberá um link em breve.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('senha/esqueci_senha.html')


@sitemapper.include()
@redefinir_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """Exibe e processa o formulário de redefinição de senha via token.

    Valida o token recebido na URL. Se inválido ou expirado, redireciona
    para a página de solicitação de novo link. Se válido, em GET exibe o
    formulário; em POST aplica a nova senha e redireciona para o login.

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
        return redirect(url_for('redefinir.esqueci_senha'))  # corrigido: nome correto do endpoint

    if request.method == 'POST':
        nova_senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario.set_password(nova_senha)
            db.session.commit()
            flash('Senha redefinida com sucesso!', category='success')
            return redirect(url_for('auth.login'))

    return render_template('senha/redefinir_senha.html', token=token)