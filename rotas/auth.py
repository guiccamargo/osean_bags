from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from db import db
from forms import LoginForm, RegisterForm, AtualizarNomeForm, EditarEnderecoForm, AtualizarSenhaForm
from funcoes import registar, acessar_enderecos, editar_endereco, atualizar_senha, atualizar_nome, deletar_usuario
from models import Usuario, Endereco
from rotas.utils import renderizar_header

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    """
    Renderiza a página de login e autentica o usuário.

    No método GET, exibe o formulário de login. No método POST, valida as
    credenciais do usuário: verifica se o email está cadastrado e se a senha
    está correta, exibindo mensagens de erro via flash em caso de falha.

    Returns:
        GET: Template login.html com o formulário de login.
        POST (sucesso): Redirecionamento para home.
        POST (falha): Redirecionamento para login com mensagem de erro via flash.
    """
    if request.method == "POST":
        user = db.session.query(Usuario).filter_by(email=request.form.get('email')).first()
        if not user:
            flash("Este email não está cadastrado", category='error')
            return redirect(url_for("auth.login"))
        if check_password_hash(pwhash=user.password_hash, password=request.form.get('senha')):
            login_user(user)
            return redirect(url_for("geral.home"))
        else:
            flash("Senha incorreta", category='error')
            return render_template("login.html", form=LoginForm(), **renderizar_header(current_user))
    else:
        return render_template("login.html", form=LoginForm(), **renderizar_header(current_user))


@auth_bp.route("/logout")
def logout():
    """
    Encerra a sessão do usuário autenticado e redireciona para a página inicial.

    Returns:
        Response: Redirecionamento para geral.home.
    """
    logout_user()
    return redirect(url_for("geral.home"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Renderiza a página de registro e cadastra um novo usuário.

    No método GET, exibe o formulário de registro. No método POST, verifica se
    o email já está cadastrado — redirecionando para login com mensagem de erro
    se estiver — ou registra o novo usuário e redireciona para a página inicial.

    Returns:
        GET: Template register.html com o formulário de registro.
        POST (email existente): Redirecionamento para login com mensagem de erro.
        POST (sucesso): Redirecionamento para geral.home.
    """
    if request.method == "POST":
        user = db.session.execute(db.select(Usuario).where(Usuario.email == request.form.get("email"))).scalar()
        if user:
            flash("Esse Email já está cadastrado", category='error')
            return redirect(url_for("auth.login"))
        else:
            registar()
            return redirect(url_for("geral.home"))
    else:
        return render_template("register.html", form=RegisterForm(), **renderizar_header(current_user))


@auth_bp.route('/gerenciar/<int:usuario_id>', methods=['GET', 'POST'])
def gerenciar(usuario_id):
    """
    Renderiza a página de gerenciamento de conta do usuário.

    Suporta três fluxos distintos em uma mesma rota:

    POST JSON: Retorna os dados de um endereço específico em formato JSON,
    utilizado pelo frontend para preencher o formulário de edição via fetch.

    POST formulário (senha): Atualiza a senha do usuário se o formulário
    AtualizarSenhaForm for submetido e válido.

    POST formulário (nome): Atualiza o nome do usuário se o formulário
    AtualizarNomeForm for submetido e válido.

    POST formulário (endereço): Edita um endereço existente se o formulário
    EditarEnderecoForm for submetido e válido.

    GET: Exibe a página com os três formulários e a lista de endereços.

    Args:
        usuario_id (int): ID do usuário a ser gerenciado.

    Returns:
        POST JSON: JSON com os dados do endereço solicitado.
        POST formulário: Redirecionamento para gerenciar com mensagem flash.
        GET: Template gerenciar_conta.html com os formulários e endereços.
    """
    usuario = db.get_or_404(Usuario, usuario_id)
    senha_form = AtualizarSenhaForm()
    nome_form = AtualizarNomeForm(nome_atual=usuario.nome, sobrenome_atual=usuario.sobrenome)
    enderecoform = EditarEnderecoForm()
    enderecos = acessar_enderecos(usuario_id)

    if request.method == "POST" and request.is_json:
        data = request.get_json()
        endereco_id = data.get("endereco_id")
        endereco = db.get_or_404(Endereco, endereco_id)
        return jsonify({
            "status": "ok",
            "apelido": endereco.apelido,
            "cep": endereco.cep,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "rua": endereco.rua,
            "numero": endereco.numero,
            "complemento": endereco.complemento
        })

    if senha_form.submit_senha.data and senha_form.validate():
        atualizar_senha(usuario_id)
        flash("Senha atualizada com sucesso!", "senha_success")
        return redirect(url_for('auth.gerenciar', usuario_id=usuario_id))

    if nome_form.submit_nome.data and nome_form.validate():
        atualizar_nome(usuario_id)
        flash("Nome alterado com sucesso!", "nome_success")
        return redirect(url_for('auth.gerenciar', usuario_id=usuario_id))

    if enderecoform.submit_endereco.data and enderecoform.validate():
        editar_endereco(enderecoform.endereco_id.data)
        flash("Endereço atualizado!", "endereco_success")
        return redirect(url_for('auth.gerenciar', usuario_id=usuario_id))

    return render_template(
        "gerenciar_conta.html",
        senha_form=senha_form,
        nome_form=nome_form,
        enderecoform=enderecoform,
        enderecos=enderecos,
        **renderizar_header(current_user)
    )


@auth_bp.route('/deletar/<int:id_usuario>')
def deletar_conta(id_usuario):
    """
    Encerra a sessão e deleta permanentemente a conta do usuário.

    Realiza logout antes de deletar para evitar referências a um usuário
    inexistente na sessão após a exclusão.

    Args:
        id_usuario (int): ID do usuário a ser deletado.

    Returns:
        Response: Redirecionamento para geral.home após a exclusão.
    """
    logout_user()
    deletar_usuario(id_usuario)
    return redirect(url_for('geral.home'))
