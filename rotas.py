import stripe
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from db import db
from forms import LoginForm, RegisterForm, AtualizarNomeForm, EnderecoForm, EditarEnderecoForm, AtualizarSenhaForm
from funcoes import soma_itens, acessar_carrossel, registar, listar_produtos, limpar_carrinho, atualizar_quantia, \
    excluir_item_carrinho, acessar_capa, acessar_fotos, acessar_bestsellers, acessar_novidades, acessar_escolha_do_mes, \
    acessar_inicial, deletar_usuario, produtos_para_envio, adicionar_endereco, \
    acessar_enderecos, editar_endereco, atualizar_senha, atualizar_nome, fechar_pedido
from models import Usuario, Carrinho, Produto, Endereco

site_bp = Blueprint('site', __name__, template_folder='templates')

BASE_DOMAIN = "http://127.0.0.1:5000"


def renderizar_header(usuario):
    try:
        logged_in = usuario.is_authenticated
    except AttributeError:
        logged_in = False

    try:
        is_admin = usuario.is_admin()
    except AttributeError:
        is_admin = False

    # Autenticação de usuário
    if usuario.is_authenticated:
        soma = soma_itens(usuario.id)
    else:
        soma = None

    if logged_in:
        id_usuario_atual = current_user.id
    else:
        id_usuario_atual = None

    if logged_in:
        inicial_nome = acessar_inicial(usuario.id)
    else:
        inicial_nome = None

    return {
        'logged_in': logged_in,
        'total_items': soma,
        'admin': is_admin,
        'id_usuario': id_usuario_atual,
        'inicial_nome': inicial_nome,
    }


@site_bp.route('/gerenciar/<int:usuario_id>', methods=['GET', 'POST'])
def gerenciar(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    senha_form = AtualizarSenhaForm()
    nome_form = AtualizarNomeForm(nome_atual=usuario.nome, sobrenome_atual=usuario.sobrenome)
    enderecoform = EditarEnderecoForm()

    enderecos = acessar_enderecos(usuario_id)
    # ---------- CASO 1: POST vindo do fetch (JSON) ----------
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
    # ---------- CASO 2: POST vindo do submit do formulário ----------
    # 👉 POST do formulário de senha
    if senha_form.submit_senha.data and senha_form.validate():
        atualizar_senha(usuario_id)
        flash("Senha atualizada com sucesso!", "senha_success")
        return redirect(url_for('site.gerenciar', usuario_id=usuario_id))

    # 👉 POST do formulário de nome
    if nome_form.submit_nome.data and nome_form.validate():
        atualizar_nome(usuario_id)
        flash("Nome alterado com sucesso!", "nome_success")
        return redirect(url_for('site.gerenciar', usuario_id=usuario_id))

    # 👉 POST do formulário de endereço
    if enderecoform.submit_endereco.data and enderecoform.validate():
        editar_endereco(enderecoform.endereco_id.data)
        flash("Endereço atualizado!", "endereco_success")
        return redirect(url_for('site.gerenciar', usuario_id=usuario_id))

    # ---------- CASO 3: GET ----------
    return render_template(
        "gerenciar_conta.html",
        senha_form=senha_form,
        nome_form=nome_form,
        enderecoform=enderecoform,
        enderecos=enderecos,
        **renderizar_header(current_user)
    )


@site_bp.route('/')
def home():
    """
    renderiza a página inicial
    """

    return render_template("index.html", carrossel=acessar_carrossel(), bestsellers=acessar_bestsellers(),
                           novidades=acessar_novidades(), escolha_do_mes=acessar_escolha_do_mes(),
                           **renderizar_header(current_user))


@site_bp.route("/login", methods=["POST", "GET"])
def login():
    """
    Renderiza a página de login
    """
    # Tentar login
    if request.method == "POST":
        # achar usuario no banco de dados
        user = db.session.query(Usuario).filter_by(email=request.form.get('email')).first()
        # Checar se o usuário existe
        if not user:
            flash("Este email não está cadastrado", category='error')
            return redirect(url_for("site.login"))
        # Checar se a senha está correta
        if check_password_hash(pwhash=user.password_hash, password=request.form.get('senha')):
            login_user(user)
            return redirect(url_for("site.home"))
        else:
            flash("Senha incorreta", category='error')
            return render_template("login.html", form=LoginForm(), **renderizar_header(current_user))
    # Renderizar página de login
    else:
        return render_template("login.html", form=LoginForm(), **renderizar_header(current_user))


@site_bp.route("/logout")
def logout():
    """
    Faz logout e redireciona para a página inicial
    """
    logout_user()
    return redirect(url_for("site.home"))


@site_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Registra novo usuário
    """
    # Tentar registro
    if request.method == "POST":
        # procurar usuário no banco de dados
        user = db.session.execute(db.select(Usuario).where(Usuario.email == request.form.get("email"))).scalar()
        # Checa se o usuário já existe
        if user:
            flash("Esse Email já está cadastrado", category='error')
            return redirect(url_for("site.login"))
        # Registra usuário
        else:
            registar()
            return redirect(url_for("site.home"))
    # Renderiza página de registro
    else:
        return render_template("register.html", form=RegisterForm(), **renderizar_header(current_user))


@site_bp.route('/carrinho', methods=["GET", "POST"])
def ir_para_carrinho():
    """
    Renderiza página do carrinho
    """
    # Listar produtos
    produtos_no_carrinho = []
    all_items = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == current_user.id)).scalars()
    for item in all_items:
        if item.produto_id == 0:
            continue
        produto = db.get_or_404(Produto, item.produto_id)
        produtos_no_carrinho.append({"id": produto.id, "name": produto.nome, "img": acessar_capa(produto.id),
                                     "total": round(produto.preco * item.quantidade, 2),
                                     "quantidade": item.quantidade})
    if request.method == 'POST':
        data = request.get_json()
        endereco_id = data["endereco_id"]
        opcoes_envio = produtos_para_envio(current_user.id, endereco_id)
    else:
        opcoes_envio = None
    # Renderizar página do carrinho
    return render_template("cart.html", envio=opcoes_envio, enderecos=acessar_enderecos(current_user.id),
                           products=produtos_no_carrinho, **renderizar_header(current_user))


@site_bp.route("/calcular-frete", methods=["POST"])  # Remova o GET para testar
def calcular_frete_rota():
    data = request.get_json()

    if not data or "endereco_id" not in data:
        return jsonify({"erro": "Dados insuficientes"}), 400

    endereco_id = data["endereco_id"]

    # Adicione um print para ver no console do VS Code se a requisição chegou aqui
    print(f"Calculando frete para o endereço: {endereco_id}")

    try:
        opcoes_envio = produtos_para_envio(current_user.id, endereco_id)
        return jsonify(opcoes_envio)
    except Exception as e:
        print(f"Erro no calculo: {e}")
        return jsonify({"erro": str(e)}), 500


@site_bp.route('/deletar-endereco/<int:id_endereco>')
def deletar_endereco(id_endereco):
    endereco = db.get_or_404(Endereco, id_endereco)

    # Verifica se o endereço pertence ao usuário atual
    if endereco.usuario_id != current_user.id:
        flash("Você não tem permissão para deletar este endereço.", "endereco_error")
        return redirect(url_for('site.gerenciar', usuario_id=current_user.id))

    db.session.delete(endereco)
    db.session.commit()
    flash("Endereço removido com sucesso!", "endereco_success")
    return redirect(url_for('site.gerenciar', usuario_id=current_user.id))

@site_bp.route('/produtos')
def produtos():
    """
    Renderiza página de produtos
    """
    return render_template('produtos.html', lista_produtos=listar_produtos(), **renderizar_header(current_user))


@site_bp.route("/produto/<produto_id>")
def buy_product(produto_id):
    """
    Adiciona produto ao carrinho e redireciona para a página de produtos
    :param produto_id: id do produto
    """
    # id do usuário
    usuario_id = current_user.id
    # Localizar carrinho do usuário
    cart_item = Carrinho.query.filter_by(usuario_id=usuario_id, produto_id=produto_id).first()
    # Aumentar quantidade se o produto já está no carrinho
    if cart_item:
        cart_item.quantidade += 1
    # Adicionar produto ao Carrinho
    else:
        cart_item = Carrinho(usuario_id=usuario_id, produto_id=produto_id, quantidade=1)
        db.session.add(cart_item)
    db.session.commit()

    return redirect(url_for("site.produtos"))


@site_bp.route('/sobre')
def sobre_nos():
    """
    Renderiza a página Sobre Nós
    """
    return render_template('sobre_nos', **renderizar_header(current_user))


@site_bp.route("/pagamento/<int:user_id>", methods=["GET", "POST"])
def ir_para_pagamento(user_id):
    if request.method == "POST":
        # Pega o ID do endereço do <select name="endereco_id">
        endereco_escolhido = request.form.get("endereco_id")

        # Pega o valor do radio button <input name="envio">
        metodo_envio = request.form.get("envio")

        if not metodo_envio:
            # Caso o usuário não tenha selecionado um frete
            flash("Por favor, selecione uma opção de frete.")
            return redirect(url_for('site.carrinho'))
        # Agora você passa esses dados para a função que fecha o pedido
        link_de_pagamento =fechar_pedido(user_id, endereco_id=endereco_escolhido, frete=metodo_envio)
        return redirect(link_de_pagamento)


    # Se for GET, apenas exibe a página (ou redireciona)
    return redirect(url_for('site.carrinho'))

@site_bp.route("/cart/clear", methods=["GET", "POST"])
def clear_checkout():
    """
    Limpar carrinho e redirecionar para o carrinho
    """
    limpar_carrinho(current_user.id)
    return redirect(url_for("site.ir_para_carrinho"))


@site_bp.route("/atualizar/<int:user_id>/<int:product_id>'", methods=["GET", "POST"])
def atualizar_item(user_id, product_id):
    quantidade = request.args.get('quantidade', type=int)
    if quantidade == 0:
        excluir_item_carrinho(user_id, product_id)
    else:
        atualizar_quantia(user_id, product_id, quantidade)
    return redirect(url_for("site.ir_para_carrinho"))


@site_bp.route("/deletar/<int:user_id>/<int:product_id>'", methods=["GET", "POST"])
def deletar_item(user_id, product_id):
    excluir_item_carrinho(user_id, product_id)
    return redirect(url_for("site.ir_para_carrinho"))


@site_bp.route('/produtos/<int:produto_id>')
def pagina_produto(produto_id):
    produto = Produto.query.filter_by(id=produto_id).first()
    fotos = acessar_fotos(produto_id)
    return render_template('produto.html', produto=produto, fotos=fotos, **renderizar_header(current_user))


@site_bp.route('/deletar/<int:id_usuario>')
def deletar_conta(id_usuario):
    logout_user()
    deletar_usuario(id_usuario)
    return redirect(url_for('site.home'))


@site_bp.route('/<int:id_usuario>/endereco', methods=['GET', 'POST'])
def cadastrar_endereco(id_usuario):
    if request.method == 'GET':
        return render_template('novo_endereco.html', form=EnderecoForm())
    else:
        adicionar_endereco(id_usuario)
        return redirect(url_for('site.ir_para_carrinho'))


@site_bp.route("/pagamento/sucesso")
def pagamento_sucesso():
    # O Mercado Pago envia parâmetros via GET (ex: payment_id, status)
    payment_id = request.args.get('payment_id')
    status = request.args.get('status')

    # Aqui você recuperaria os dados que salvou temporariamente no banco de dados
    # ou na sessão antes de enviar o usuário para o Mercado Pago.
    # Exemplo recuperando da sessão (se você salvou lá):
    resumo_pedido = session.get('ultimo_pedido')

    if status == "approved":
        # Lógica para limpar o carrinho do usuário no banco de dados
        # limpar_carrinho(current_user.id)
        return render_template("redirect/sucesso.html", pedido=resumo_pedido, payment_id=payment_id)

    return redirect(url_for('site.home'))