"""
Pacote de rotas da aplicação.

Organiza as rotas em blueprints temáticos para facilitar a manutenção
e separação de responsabilidades. Todos os blueprints devem ser registrados
na aplicação Flask via app.register_blueprint().

Blueprints disponíveis:
    auth_bp: Autenticação e gerenciamento de conta (login, registro, perfil).
    produtos_bp: Listagem e detalhes de produtos.
    carrinho_bp: Gerenciamento do carrinho de compras.
    enderecos_bp: Cadastro e remoção de endereços de entrega.
    pagamento_bp: Cálculo de frete e processamento de pagamento.
    geral_bp: Páginas gerais da aplicação (home, sobre nós).

Example:
    # Em app.py:
    from rotas import auth_bp, produtos_bp, carrinho_bp, enderecos_bp, pagamento_bp, geral_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(carrinho_bp)
    app.register_blueprint(enderecos_bp)
    app.register_blueprint(pagamento_bp)
    app.register_blueprint(geral_bp)
"""

from rotas.auth import auth_bp
from rotas.produtos import produtos_bp
from rotas.carrinho import carrinho_bp
from rotas.enderecos import enderecos_bp
from rotas.pagamento import pagamento_bp
from rotas.geral import geral_bp
