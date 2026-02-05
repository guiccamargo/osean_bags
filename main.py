from flask import Flask
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, logout_user

from admin import UsuarioAdmin, ProdutoAdmin, CarrosselAdmin, FotoAdmin
from db import db
from models import Usuario, Produto, Carrossel, Foto
from rotas import site_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
Bootstrap5(app)

db.init_app(app)

app.register_blueprint(site_bp)

# Criar interface de Administrador
admin = Admin(app, name='site', theme=Bootstrap4Theme())
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
