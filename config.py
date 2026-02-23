# config.py
import os

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv('email_de_redefinicao')
MAIL_PASSWORD = os.getenv('senha_email')