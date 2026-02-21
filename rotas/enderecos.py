from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from db import db
from forms import EnderecoForm
from funcoes import acessar_enderecos, adicionar_endereco
from models import Endereco
from rotas.utils import renderizar_header

enderecos_bp = Blueprint('enderecos', __name__, template_folder='templates')


@enderecos_bp.route('/<int:id_usuario>/endereco', methods=['GET', 'POST'])
def cadastrar_endereco(id_usuario):
    """
    Renderiza o formulário de cadastro de novo endereço e salva o registro.

    No método GET, exibe o formulário vazio. No método POST, coleta os dados
    do formulário, cria o endereço no banco de dados e redireciona para o carrinho.

    Args:
        id_usuario (int): ID do usuário ao qual o endereço será vinculado.

    Returns:
        GET: Template novo_endereco.html com o formulário de cadastro.
        POST: Redirecionamento para carrinho.ir_para_carrinho.
    """
    if request.method == 'GET':
        return render_template('novo_endereco.html', form=EnderecoForm())
    else:
        adicionar_endereco(id_usuario)
        return redirect(url_for('carrinho.ir_para_carrinho'))


@enderecos_bp.route('/deletar-endereco/<int:id_endereco>')
def deletar_endereco(id_endereco):
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
    endereco = db.get_or_404(Endereco, id_endereco)

    if endereco.usuario_id != current_user.id:
        flash("Você não tem permissão para deletar este endereço.", "endereco_error")
        return redirect(url_for('auth.gerenciar', usuario_id=current_user.id))

    db.session.delete(endereco)
    db.session.commit()
    flash("Endereço removido com sucesso!", "endereco_success")
    return redirect(url_for('auth.gerenciar', usuario_id=current_user.id))
