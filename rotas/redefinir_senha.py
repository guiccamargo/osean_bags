from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app
from flask_mail import Message

from db import db
from extensions import sitemapper
from models import Usuario
from redefinir_senha import verificar_token, gerar_token

redefinir_bp = Blueprint('redefinir', __name__, template_folder='templates')


@sitemapper.include()
@redefinir_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Exibe e processa o formulário de solicitação de redefinição de senha.

    Em requisições GET, renderiza o formulário onde o usuário informa seu e-mail.
    Em requisições POST, verifica se o e-mail existe no banco de dados e, caso
    exista, gera um token seguro e envia um link de redefinição por e-mail.

    A mensagem de resposta é sempre a mesma independentemente de o e-mail estar
    ou não cadastrado, evitando a enumeração de usuários.

    :return: Renderiza ``senha/esqueci_senha.html`` em requisições GET.
             Redireciona para ``auth.login`` após o processamento do formulário (POST).

    .. note::
        O link enviado por e-mail expira em 1 hora, conforme definido em
        ``gerar_token`` / ``verificar_token``.
    """
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = gerar_token(email)
            link = url_for('redefinir.redefinir_senha', token=token, _external=True)

            msg = Message(
                subject='Redefinição de senha',
                sender='seu@email.com',
                recipients=[email]
            )
            msg.body = f'Clique no link para redefinir sua senha: {link}\nO link expira em 1 hora.'
            mail = current_app.extensions['mail']
            mail.send(msg)

        flash('Se esse e-mail estiver cadastrado, você receberá um link em breve.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('senha/esqueci_senha.html')


@sitemapper.include()
@redefinir_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """Exibe e processa o formulário de redefinição de senha via token.

    Valida o token recebido na URL. Se válido, em requisições GET exibe o
    formulário para o usuário definir uma nova senha. Em requisições POST,
    aplica a nova senha ao usuário correspondente e redireciona para o login.

    :param token: Token assinado e com prazo de expiração gerado por ``gerar_token``,
                  enviado ao usuário por e-mail na rota ``esqueci_senha``.

    :return: Redireciona para ``esqueci_senha`` se o token for inválido ou expirado.
             Renderiza ``senha/redefinir_senha.html`` em requisições GET com token válido.
             Redireciona para ``auth.login`` após a redefinição bem-sucedida (POST).

    .. note::
        A senha é armazenada com hash via ``usuario.set_password()``,
        que deve utilizar ``werkzeug.security`` ou ``bcrypt``.

    .. warning::
        O token é de uso único por tempo limitado. Após a expiração, o usuário
        deverá solicitar um novo link pela rota ``esqueci_senha``.
    """
    email = verificar_token(token)

    if not email:
        flash('Link inválido ou expirado.', category='error')
        return redirect(url_for('esqueci_senha'))

    if request.method == 'POST':
        nova_senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario.set_password(nova_senha)
            db.session.commit()
            flash('Senha redefinida com sucesso!', category='success')
            return redirect(url_for('auth.login'))

    return render_template('senha/redefinir_senha.html', token=token)
