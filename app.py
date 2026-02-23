from flask import Flask
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from flask_babel import Babel
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import mail
from admin import UsuarioAdmin, ProdutoAdmin, CarrosselAdmin, MyAdminIndexView, ConfigAdmin, PedidoAdmin
from db import db
from models import Usuario, Produto, Carrossel, Config, Pedido
from rotas import auth_bp, produtos_bp, carrinho_bp, enderecos_bp, pagamento_bp, geral_bp
from rotas.redefinir_senha import redefinir_bp

app = Flask(__name__)
app.config.from_object('config')

mail.init_app(app)

app.config['SESSION_PERMANENT'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'pt_BR'
babel = Babel(app)
Bootstrap5(app)

# Configurar https test
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(carrinho_bp)
app.register_blueprint(enderecos_bp)
app.register_blueprint(pagamento_bp)
app.register_blueprint(geral_bp)
app.register_blueprint(redefinir_bp)

# Criar interface de Administrador
admin = Admin(app, name='Osean Bags', theme=Bootstrap4Theme(), index_view=MyAdminIndexView())
admin.add_view(UsuarioAdmin(Usuario, db.session))
admin.add_view(ProdutoAdmin(Produto, db.session))
admin.add_view(CarrosselAdmin(Carrossel, db.session))
admin.add_view(ConfigAdmin(Config, db.session))
admin.add_view(PedidoAdmin(Pedido, db.session))

# Config login manager
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'teste'


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Usuario, user_id)


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    # 'adhoc' gera um certificado autoassinado temporário
    app.run(debug=True)