import os

from flask import Flask, send_from_directory
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from flask_sitemapper import Sitemapper
from werkzeug.middleware.proxy_fix import ProxyFix

from admin import HomeMenuLink
from extensions import mail, db, login_manager, bootstrap, babel
from funcoes import acessar_capa
from seo import SEO

sitemapper = Sitemapper()

def create_app():
    app = Flask(__name__)
    sitemapper.init_app(app)
    app.config.from_object('config')
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.jinja_env.globals['META_PIXEL_ID'] = os.getenv('META_PIXEL_ID')
    app.jinja_env.globals['SEO'] = SEO
    app.jinja_env.globals['SITE_NAME'] = 'Osean Bags'
    app.jinja_env.globals['SITE_URL'] = os.getenv('SITE_URL', 'http://127.0.0.1:5000')
    app.jinja_env.filters['preco_br'] = formatar_preco
    app.jinja_env.globals['acessar_capa'] = acessar_capa
    _init_extensions(app)
    _register_blueprints(app)
    _register_admin(app)
    sitemapper.init_app(app)

    # 3. Cria a rota para o XML do sitemap
    @app.route("/sitemap.xml")
    def sitemap():
        return sitemapper.generate()

    with app.app_context():
        db.create_all()

    @app.route("/static/<path:filename>")
    def static_files(filename):
        response = send_from_directory("static", filename)
        response.headers["Cache-Control"] = "public, max-age=31536000"
        return response
    return app


def _init_extensions(app):
    mail.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


def _register_blueprints(app):
    from rotas import auth_bp, produtos_bp, carrinho_bp, enderecos_bp, pagamento_bp, geral_bp, conta_bp
    from rotas.redefinir_senha import redefinir_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(carrinho_bp)
    app.register_blueprint(enderecos_bp)
    app.register_blueprint(pagamento_bp)
    app.register_blueprint(geral_bp)
    app.register_blueprint(redefinir_bp)
    app.register_blueprint(conta_bp)

def formatar_preco(valor):
    """
    Filtro Jinja2 para formatar valores monetários no padrão brasileiro.

    Converte o separador decimal de ponto para vírgula e adiciona o
    prefixo 'R$', seguindo o padrão pt-BR.

    Args:
        valor (float): Valor monetário a ser formatado.

    Returns:
        str: Valor formatado (ex: 'R$ 59,90').
             Retorna '—' se o valor for None.

    Example:
        # No template:
        {{ produto.preco | preco_br }}  →  R$ 59,90
    """
    if valor is None:
        return '—'
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _register_admin(app):
    from admin import UsuarioAdmin, ProdutoAdmin, CarrosselAdmin, MyAdminIndexView, ConfigAdmin, PedidoAdmin
    from models import Usuario, Produto, Carrossel, Config, Pedido

    adm = Admin(app, name='Osean Bags', theme=Bootstrap4Theme(), index_view=MyAdminIndexView())
    adm.add_view(UsuarioAdmin(Usuario, db.session))
    adm.add_view(ProdutoAdmin(Produto, db.session))
    adm.add_view(CarrosselAdmin(Carrossel, db.session))
    adm.add_view(ConfigAdmin(Config, db.session))
    adm.add_view(PedidoAdmin(Pedido, db.session))
    adm.add_link(HomeMenuLink(name='Voltar ao Site'))


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)