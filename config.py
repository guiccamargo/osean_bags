import os

SECRET_KEY = os.getenv('SECRET_KEY')
database_url = os.getenv('DATABASE_URL', 'sqlite:///database.db')
SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://', 1)
BABEL_DEFAULT_LOCALE = 'pt_BR'
SESSION_PERMANENT = False
MAIL_SERVER = os.getenv('SERVIDOR_DE_EMAIL')
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv('EMAIL_DE_REDEFINICAO')
MAIL_PASSWORD = os.getenv('SENHA_DE_APP')
