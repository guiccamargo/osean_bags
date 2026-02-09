import stripe
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from db import db
from funcoes import soma_itens, acessar_carrossel, registar, listar_produtos, limpar_carrinho, atualizar_quantia, \
    excluir_item_carrinho, acessar_capa, acessar_fotos
from forms import LoginForm, RegisterForm
from models import Usuario, Carrinho, Produto

site_bp = Blueprint('site', __name__, template_folder='templates')

BASE_DOMAIN = "http://127.0.0.1:5000"


@site_bp.route('/')
def home():
    """
    renderiza a página inicial
    """
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None

    return render_template("index.html", logged_in=current_user.is_authenticated,
                           total_items=soma, carrossel=acessar_carrossel())


@site_bp.route("/login", methods=["POST", "GET"])
def login():
    """
    Renderiza a página de login
    """
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None
   # Tentar login
    if request.method == "POST":
        # achar usuario no banco de dados
        user = db.session.query(Usuario).filter_by(email=request.form.get('email')).first()
        # Checar se o usuário existe
        if not user:
            flash("Este email não está cadastrado")
            return redirect(url_for("site.login"))
        # Checar se a senha está correta
        if check_password_hash(pwhash=user.password_hash, password=request.form.get('senha')):
            login_user(user)
            return redirect(url_for("site.home"))
        else:
            flash("Senha incorreta")
            return render_template("login.html", form=LoginForm(), logged_in=current_user.is_authenticated,
                                   total_items=soma
                                   )
    # Renderizar página de login
    else:
        return render_template("login.html", form=LoginForm(), logged_in=current_user.is_authenticated,
                               total_items=soma
                               )


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
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None
    # Tentar registro
    if request.method == "POST":
        # procurar usuário no banco de dados
        user = db.session.execute(db.select(Usuario).where(Usuario.email == request.form.get("email"))).scalar()
        # Checa se o usuário já existe
        if user:
            flash("Esse Email já está cadastrado")
            return redirect(url_for("site.login"))
        # Registra usuário
        else:
            registar()
            return redirect(url_for("site.home"))
    # Renderiza página de registro
    else:
        return render_template("register.html", form=RegisterForm(), logged_in=current_user.is_authenticated,
                               total_items=soma)


@site_bp.route('/carrinho')
def ir_para_carrinho():
    """
    Renderiza página do carrinho
    """
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None
    # Listar produtos
    produtos_no_carrinho = []
    all_items = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == current_user.id)).scalars()
    for item in all_items:
        if item.produto_id == 0:
            continue
        produto = db.get_or_404(Produto, item.produto_id)
        produtos_no_carrinho.append({"id": produto.id, "name": produto.nome, "img": acessar_capa(produto.id), "total": round(produto.preco * item.quantidade, 2),
                         "quantidade": item.quantidade})

    # Renderizar página do carrinho
    return render_template("cart.html", products=produtos_no_carrinho, logged_in=True, total_items=soma)


@site_bp.route('/produtos')
def produtos():
    """
    Renderiza página de produtos
    """
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None

    return render_template('produtos.html', logged_in=current_user.is_authenticated, lista_produtos=listar_produtos(),
                           total_items=soma)


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
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None

    return render_template('sobre_nos', logged_in=current_user.is_authenticated, total_items=soma)


@site_bp.route("/create-checkout-session", methods=["GET", "POST"])
def create_checkout_session():
    """
    Redirect user to a stripe based checkout page
    """
    all_items = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == current_user.id)).scalars()
    line_items = []
    for item in all_items:
        if item.produto_id == 0:
            continue
        db_produto = db.get_or_404(Produto, item.produto_id)
        product = stripe.Product.create(name=db_produto.nome)
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(db_produto.preco * 100),
            currency="brl",
        )
        line_items.append({"price": price.id, "quantity": item.quantity})
    try:
        checkout_session = stripe.checkout.Session.create(mode="payment",
                                                          line_items=line_items,
                                                          success_url=BASE_DOMAIN + "/success",
                                                          cancel_url=BASE_DOMAIN + "/cancel"
                                                          )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


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
    # Autenticação de usuário
    if current_user.is_authenticated:
        soma = soma_itens(current_user.id)
    else:
        soma = None
    produto = Produto.query.filter_by(id=produto_id).first()
    fotos = acessar_fotos(produto_id)
    return render_template('produto.html', produto=produto, fotos=fotos, logged_in=current_user.is_authenticated, total_items=soma)