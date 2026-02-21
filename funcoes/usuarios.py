from flask import request
from flask_login import login_user
from werkzeug.security import generate_password_hash

from db import db
from models import Usuario


def registar() -> None:
    """Registra um novo usuário.

    Coleta as informações do usuário informadas no formulário e cria um novo registro
     na tabela de usuários no banco de dados, em seguida o usuário é logado.

     :return: None
    """

    nome = request.form.get('nome')
    sobrenome = request.form.get('sobrenome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    new_user = Usuario(email=email, name=nome, last_name=sobrenome,
                       password=generate_password_hash(senha, method='pbkdf2:sha256', salt_length=8))
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)  # Logar novo usuário


def acessar_inicial(usuario_id: int) -> str:
    """Acessa a inicial do nome do usuário logado.

    Acessa a inicial do usuário para exibir na barra de nagevação.

    :param usuario_id: id do usuário logado.
    :return: Inicial do usuário.
    """

    usuario = db.get_or_404(Usuario, usuario_id)

    return usuario.get_inicial()


def atualizar_senha(usuario_id: int) -> None:
    """Atualiza senha do usuário logado.

    Atualiza a senha do usuário logado na página de gerenciar conta.

    :param usuario_id: id do usuário logado.
    :return: None
    """

    usuario = db.get_or_404(Usuario, usuario_id)
    senha = request.form.get('senha_nova')
    usuario.password_hash = generate_password_hash(senha, method='pbkdf2:sha256', salt_length=8)  # Criptografar senha

    db.session.commit()


def atualizar_nome(usuario_id: int) -> None:
    """Edita nome do usuário atual.

    Muda o nome e sobrenome do usuário logado na página de gerenciar conta.

    :param usuario_id: id do usuário logado.
    :return: None
    """

    usuario = db.get_or_404(Usuario, usuario_id)
    nome = request.form.get('nome')
    sobrebnome = request.form.get('sobrenome')
    usuario.nome = nome
    usuario.sobrenome = sobrebnome
    db.session.commit()


def deletar_usuario(usuario_id: int) -> None:
    """Deleta a conta do usuário atual.

    Deleta conta quando o usuário solicita a exclusão no site de gerenciar conta e confrima a esclusão.

    :param usuario_id: id do usuário logado.
    :return: None
    """

    usuario = db.get_or_404(Usuario, usuario_id)
    db.session.delete(usuario)
    db.session.commit()
