from flask import Flask
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from flask_babel import Babel
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

from admin import UsuarioAdmin, ProdutoAdmin, CarrosselAdmin, MyAdminIndexView
from db import db
from models import Usuario, Produto, Carrossel
from rotas import site_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'pt_BR'
babel = Babel(app)
Bootstrap5(app)

db.init_app(app)

app.register_blueprint(site_bp)

# Criar interface de Administrador
admin = Admin(app, name='Osean Bags', theme=Bootstrap4Theme(), index_view=MyAdminIndexView())
admin.add_view(UsuarioAdmin(Usuario, db.session))
admin.add_view(ProdutoAdmin(Produto, db.session))
admin.add_view(CarrosselAdmin(Carrossel, db.session))

# Config login manager
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SECRET_KEY"] = "teste"


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Usuario, user_id)


with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True)
