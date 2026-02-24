from flask_babel import Babel
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_mail import Mail
from flask_sitemapper import Sitemapper

from db import db

mail = Mail()
bootstrap = Bootstrap5()
babel = Babel()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from models import Usuario
    return db.get_or_404(Usuario, user_id)

sitemapper = Sitemapper(https=True)