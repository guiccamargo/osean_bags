from flask import Blueprint, render_template
from flask_login import current_user

from extensions import sitemapper
from funcoes import acessar_carrossel, acessar_bestsellers, acessar_novidades, acessar_escolha_do_mes
from rotas.utils import renderizar_header

geral_bp = Blueprint('geral', __name__, template_folder='templates')


@sitemapper.include()
@geral_bp.route('/')
def home():
    """
    Renderiza a página inicial da aplicação.

    Agrega os dados necessários para a home: imagens do carrossel,
    bestsellers, novidades e a escolha do mês.

    Returns:
        Response: Template index.html com todos os dados da página inicial.
    """
    return render_template(
        'index.html',
        carrossel=acessar_carrossel(),
        bestsellers=acessar_bestsellers(),
        novidades=acessar_novidades(),
        escolha_do_mes=acessar_escolha_do_mes(),
        **renderizar_header(current_user)
    )


@sitemapper.include()
@geral_bp.route('/sobre')
def sobre_nos():
    """
    Renderiza a página Sobre Nós.

    Returns:
        Response: Template sobre_nos.html.
    """
    return render_template('sobre_nos.html', **renderizar_header(current_user))
