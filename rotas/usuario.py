from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from flask_login import current_user, logout_user, login_required

from db import db
from extensions import sitemapper
from forms import AtualizarSenhaForm, AtualizarNomeForm, EditarEnderecoForm, EnderecoForm
from funcoes import acessar_enderecos, atualizar_senha, atualizar_nome, editar_endereco, deletar_usuario, \
    adicionar_endereco
from models import Usuario, Endereco, Pedido
from rotas.utils import renderizar_header

conta_bp = Blueprint('conta', __name__, template_folder='templates')


@sitemapper.include()
@login_required
@conta_bp.route('/gerenciar/<int:usuario_id>', methods=['GET', 'POST'])
def gerenciar(usuario_id):
    """
    Renderiza a página de gerenciamento de conta do usuário.

    Suporta três fluxos distintos em uma mesma rota:

    POST JSON: Retorna os dados de um endereço específico em formato JSON,
    utilizado pelo frontend para preencher o formulário de edição via fetch.

    POST formulário (senha): Atualiza a senha do usuário se o formulário
    AtualizarSenhaForm for submetido e válido.

    POST formulário (nome): Atualiza o nome do usuário se o formulário
    AtualizarNomeForm for submetido e válido.

    POST formulário (endereço): Edita um endereço existente se o formulário
    EditarEnderecoForm for submetido e válido.

    GET: Exibe a página com os três formulários e a lista de endereços.

    Args:
        usuario_id (int): ID do usuário a ser gerenciado.

    Returns:
        POST JSON: JSON com os dados do endereço solicitado.
        POST formulário: Redirecionamento para gerenciar com mensagem flash.
        GET: Template gerenciar_conta.html com os formulários e endereços.
    """
    usuario = db.get_or_404(Usuario, usuario_id)
    senha_form = AtualizarSenhaForm()
    nome_form = AtualizarNomeForm(nome_atual=usuario.nome, sobrenome_atual=usuario.sobrenome)
    editarenderecoform = EditarEnderecoForm()
    criarenderecoform = EnderecoForm()
    lista_enderecos = acessar_enderecos(usuario_id)

    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        endereco_id = data.get('endereco_id')
        endereco = db.get_or_404(Endereco, endereco_id)
        return jsonify({
            'status': 'ok',
            'apelido': endereco.apelido,
            'cep': endereco.cep,
            'cidade': endereco.cidade,
            'estado': endereco.estado,
            'rua': endereco.rua,
            'numero': endereco.numero,
            'complemento': endereco.complemento
        })

    if senha_form.submit_senha.data and senha_form.validate():
        atualizar_senha(usuario_id)
        flash('Senha atualizada com sucesso!', 'senha_success')
        return redirect(url_for('conta.gerenciar', usuario_id=usuario_id))

    if nome_form.submit_nome.data and nome_form.validate():
        atualizar_nome(usuario_id)
        flash('Nome alterado com sucesso!', 'nome_success')
        return redirect(url_for('conta.gerenciar', usuario_id=usuario_id))

    if editarenderecoform.submit_endereco.data and editarenderecoform.validate():
        editar_endereco(editarenderecoform.endereco_id.data)
        flash('Endereço atualizado!', 'endereco_success')
        return redirect(url_for('conta.gerenciar', usuario_id=usuario_id))

    if criarenderecoform.submit_criar_endereco.data and criarenderecoform.validate():
        adicionar_endereco(usuario_id)
        flash('Endereço Registrado!', 'endereco_success')
        return redirect(url_for('conta.gerenciar', usuario_id=usuario_id))

    return render_template(
        'gerenciar_conta.html',
        senha_form=senha_form,
        nome_form=nome_form,
        editarenderecoform=editarenderecoform,
        criarenderecoform=criarenderecoform,
        lista_enderecos=lista_enderecos,
        **renderizar_header(current_user)
    )


@sitemapper.include()
@login_required
@conta_bp.route('/pedidos/<int:usuario_id>')
def meus_pedidos(usuario_id):
    pedidos = Pedido.query.filter_by(usuario_id=usuario_id, status='pago').all()
    return render_template('meus_pedidos.html', pedidos=pedidos, **renderizar_header(current_user))


@sitemapper.include()
@login_required
@conta_bp.route('/deletar/<int:id_usuario>')
def deletar_conta(id_usuario):
    """
    Encerra a sessão e deleta permanentemente a conta do usuário.

    Realiza logout antes de deletar para evitar referências a um usuário
    inexistente na sessão após a exclusão.

    Args:
        id_usuario (int): ID do usuário a ser deletado.

    Returns:
        Response: Redirecionamento para geral.home após a exclusão.
    """
    logout_user()
    deletar_usuario(id_usuario)
    return redirect(url_for('geral.home'))
