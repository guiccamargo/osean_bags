import os

from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
database_url = os.getenv('DATABASE_URL', 'sqlite:///database.db')
SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://', 1)
BABEL_DEFAULT_LOCALE = 'pt_BR'


import os

# Reconexão automática com Neon (evita SSL errors por conexões mortas no pool)
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,  # Testa a conexão antes de usar
    'pool_recycle': 300,  # Recicla conexões após 5 minutos
    'connect_args': {
        'sslmode': 'require',
        'connect_timeout': 10,
    }
}
