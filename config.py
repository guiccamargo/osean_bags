# config.py
import os


SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
BABEL_DEFAULT_LOCALE = 'pt_BR'
SESSION_PERMANENT = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv('email_de_redefinicao')
MAIL_PASSWORD = os.getenv('senha_email')