"""
Configuração do servidor Gunicorn para produção no Render.com.

O timeout padrão de 30s é insuficiente para operações bloqueantes como
envio de e-mail via SMTP. Aumentamos para 120s para cobrir esses casos.
"""

bind = "0.0.0.0:10000"
workers = 1
timeout = 120  # segundos — cobre envio de e-mail via SMTP