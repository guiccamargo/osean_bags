from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from db import db
from extensions import sitemapper
from forms import EnderecoForm
from funcoes import adicionar_endereco, deletar_endereco
from models import Endereco
from rotas.utils import renderizar_header

enderecos_bp = Blueprint('enderecos', __name__, template_folder='templates')


@sitemapper.include()
@enderecos_bp.route('/<int:id_usuario>/endereco', methods=['GET', 'POST'])
def cadastrar_endereco(id_usuario):
    """
    Renderiza o formulário de cadastro de novo endereço e salva o registro.

    No metodo GET, exibe o formulário vazio. No metodo POST, coleta os dados
    do formulário, cria o endereço no banco de dados e redireciona para o carrinho.

    Args:
        id_usuario (int): ID do usuário ao qual o endereço será vinculado.

    Returns:
        GET: Template novo_endereco.html com o formulário de cadastro.
        POST: Redirecionamento para carrinho.ir_para_carrinho.
    """
    if request.method == 'GET':
        return render_template('novo_endereco.html', form=EnderecoForm(), **renderizar_header(current_user))
    else:
        adicionar_endereco(id_usuario)
        return redirect(url_for('carrinho.ir_para_carrinho'))


@sitemapper.include()
@enderecos_bp.route('/deletar-endereco/<int:id_endereco>')
def deletar_endereco_form(id_endereco):
    """
    Remove um endereço cadastrado pelo usuário autenticado.

    Verifica se o endereço pertence ao usuário atual antes de deletar,
    impedindo que um usuário remova endereços de outro usuário.

    Args:
        id_endereco (int): ID do endereço a ser removido.

    Returns:
        Response: Redirecionamento para auth.gerenciar com mensagem flash
                  de sucesso ou erro dependendo da autorização.
    """
    deletar_endereco(id_endereco)
    flash('Endereço removido com sucesso!', 'endereco_success')
    return redirect(url_for('conta.gerenciar', usuario_id=current_user.id))
