from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from db import db
from forms import LoginForm, RegisterForm, AtualizarNomeForm, EditarEnderecoForm, AtualizarSenhaForm
from funcoes import registar, acessar_enderecos, editar_endereco, atualizar_senha, atualizar_nome, deletar_usuario
from models import Usuario, Endereco
from rotas.utils import renderizar_header

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    """
    Renderiza a página de login e autentica o usuário.

    No metodo GET, exibe o formulário de login. No metodo POST, valida as
    credenciais do usuário: verifica se o email está cadastrado e se a senha
    está correta, exibindo mensagens de erro via flash em caso de falha.

    Returns:
        GET: Template login.html com o formulário de login.
        POST (sucesso): Redirecionamento para home.
        POST (falha): Redirecionamento para login com mensagem de erro via flash.
    """
    if request.method == 'POST':
        user = db.session.query(Usuario).filter_by(email=request.form.get('email')).first()
        if not user:
            flash('Este email não está cadastrado', category='error')
            return redirect(url_for('auth.login'))
        if check_password_hash(pwhash=user.password_hash, password=request.form.get('senha')):
            login_user(user)
            return redirect(url_for('geral.home'))
        else:
            flash('Senha incorreta', category='error')
            return render_template('login.html', form=LoginForm(), **renderizar_header(current_user))
    else:
        return render_template('login.html', form=LoginForm(), **renderizar_header(current_user))


@auth_bp.route('/logout')
def logout():
    """
    Encerra a sessão do usuário autenticado e redireciona para a página inicial.

    Returns:
        Response: Redirecionamento para geral.home.
    """
    logout_user()
    return redirect(url_for('geral.home'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Renderiza a página de registro e cadastra um novo usuário.

    No metodo GET, exibe o formulário de registro. No metodo POST, verifica se
    o email já está cadastrado — redirecionando para login com mensagem de erro
    se estiver — ou registra o novo usuário e redireciona para a página inicial.

    Returns:
        GET: Template register.html com o formulário de registro.
        POST (email existente): Redirecionamento para login com mensagem de erro.
        POST (sucesso): Redirecionamento para geral.home.
    """
    if request.method == 'POST':
        user = db.session.execute(db.select(Usuario).where(Usuario.email == request.form.get('email'))).scalar()
        if user:
            flash('Esse Email já está cadastrado', category='error')
            return redirect(url_for('auth.login'))
        else:
            registar()
            return redirect(url_for('geral.home'))
    else:
        return render_template('register.html', form=RegisterForm(), **renderizar_header(current_user))
