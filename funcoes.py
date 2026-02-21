from typing import List

import sqlalchemy.exc
from flask import request, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash

from apis.envio import calcular_frete
from apis.pagamento import gerar_link_pagamento
from db import db
from models import Produto, Usuario, Carrinho, Carrossel, Foto, Endereco, Config


def soma_itens(id_usuario: int) -> int:
    """
    Soma os itens do Carrinho
    :argument id_usuario: id do usuário atual
    :return: Total de itens
    """
    soma = 0
    todos_itens = db.session.execute(db.select(Carrinho).where(Carrinho.usuario_id == id_usuario)).scalars()
    for item in todos_itens:
        soma += item.quantidade
    return soma


def listar_produtos():
    """
    Acessa os produtos do Banco de Dados
    :return: lista de produtos
    """
    busca = request.args.get("busca")

    if busca:
        produtos = Produto.query.filter(Produto.nome.ilike(f"%{busca}%")).all()
    else:
        produtos = Produto.query.all()

    lista_produtos = []

    for produto in produtos:
        lista_produtos.append({
            "id": produto.id,
            "imagem": acessar_capa(produto.id),
            "nome": produto.nome,
            "preco": produto.preco,
        })
    return lista_produtos


def limpar_carrinho(id_usuario: int):
    """
    Deleta produtos do carrinho
    :argument id_usuario: id dousuário atual
    """
    items = Carrinho.query.filter_by(usuario_id=id_usuario).delete()
    db.session.commit()


def acessar_carrossel() -> List[str]:
    """
    Acessa os itens do carrossel
    :return: lista com o caminho das imagens do carrossel
    """
    try:
        banners = []
        return Carrossel.query.all()
    except sqlalchemy.exc.OperationalError:
        return None


def registar():
    """
    Registra um novo usuário
    """
    nome = request.form.get("nome")
    sobrenome = request.form.get("sobrenome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    new_user = Usuario(email=email, name=nome, last_name=sobrenome,
                       password=generate_password_hash(senha, method="pbkdf2:sha256",
                                                       salt_length=8))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)


def atualizar_quantia(id_usuario, id_produto, nova_quantidade):
    cart_item = Carrinho.query.filter_by(usuario_id=id_usuario, produto_id=id_produto).first()
    cart_item.quantidade = nova_quantidade
    db.session.commit()


def excluir_item_carrinho(id_usuario, id_produto):
    produto = Carrinho.query.filter_by(usuario_id=id_usuario, produto_id=id_produto).first()
    db.session.delete(produto)
    db.session.commit()


def acessar_fotos(produto_id):
    return db.session.execute(db.select(Foto).where(Foto.produto_id == produto_id)).scalars()


def acessar_capa(produto_id):
    capa = Foto.query.filter_by(produto_id=produto_id).first()
    return capa.arquivo


def acessar_bestsellers():
    lista_produtos = []
    todos_produtos = Produto.query.order_by(Produto.vendas).limit(5).all()
    for produto in todos_produtos:
        lista_produtos.append({
            "id": produto.id,
            "imagem": acessar_capa(produto.id),
            "nome": produto.nome,
            "preco": produto.preco,
        })
    return lista_produtos


def acessar_novidades():
    lista_produtos = []
    novidades = Produto.query.filter_by(novidade=True).all()
    for produto in novidades:
        lista_produtos.append({
            "id": produto.id,
            "imagem": acessar_capa(produto.id),
            "nome": produto.nome,
            "preco": produto.preco,
        })
    return lista_produtos


def acessar_escolha_do_mes():
    escolha = Produto.query.filter_by(escolha_do_mes=True).first()
    if not escolha:
        return None
    return {
        "id": escolha.id,
        "imagem": acessar_capa(escolha.id),
        "nome": escolha.nome,
    }


def acessar_inicial(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    return usuario.get_inicial()


def atualizar_senha(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    senha = request.form.get("senha_nova")
    usuario.password_hash = generate_password_hash(senha, method="pbkdf2:sha256",
                                                   salt_length=8)
    db.session.commit()


def atualizar_nome(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    nome = request.form.get('nome')
    sobrebnome = request.form.get('sobrenome')
    usuario.nome = nome
    usuario.sobrenome = sobrebnome
    db.session.commit()


def deletar_usuario(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    db.session.delete(usuario)
    db.session.commit()


def produtos_para_envio(id_usuario, endereco_id):
    items = Carrinho.query.filter_by(usuario_id=id_usuario).all()
    lista_de_produtos = []
    endereco = db.get_or_404(Endereco, endereco_id)
    for item in items:
        produto = db.get_or_404(Produto, item.produto_id)
        lista_de_produtos.append({
            "id": produto.id,
            "width": produto.largura,
            "height": produto.altura,
            "length": produto.comprimento,
            "weight": produto.peso,
            "quantity": item.quantidade
        })
    config_info = Config.query.first().__dict__
    return calcular_frete(produtos=lista_de_produtos, cep_destino=endereco.cep, cep_origem=config_info['cep_origem'],
                          email_contato=config_info['email'])


def acessar_enderecos(id_usuario):
    return Endereco.query.filter_by(usuario_id=id_usuario).all() if id_usuario else None


def adicionar_endereco(id_usuario):
    apelido = request.form.get('apelido')
    cep = request.form.get('cep')
    if '-' in cep:
        cep.replace('-', '')
    cidade = request.form.get('cidade')
    estado = request.form.get('estado')
    rua = request.form.get('rua')
    numero = request.form.get('numero')
    complemento = request.form.get('complemento')
    novo_endereco = Endereco(usuario_id=id_usuario, apelido=apelido, cep=cep, cidade=cidade, estado=estado, rua=rua,
                             numero=numero, complemento=complemento)
    db.session.add(novo_endereco)
    db.session.commit()


def editar_endereco(id_endereco):
    cidade = request.form.get('cidade')
    estado = request.form.get('estado')
    rua = request.form.get('rua')
    numero = request.form.get('numero')
    complemento = request.form.get('complemento')

    endereco = db.get_or_404(Endereco, id_endereco)
    endereco.cidade = cidade
    endereco.estado = estado
    endereco.rua = rua
    endereco.numero = numero
    endereco.complemento = complemento
    db.session.commit()


def fechar_pedido(id_usuario, endereco_id, frete):
    usuario = db.get_or_404(Usuario, id_usuario)
    itens = Carrinho.query.filter_by(usuario_id=id_usuario).all()
    endereco = db.get_or_404(Endereco, endereco_id)

    # 1. Tratamento robusto do frete
    try:
        if frete and "|" in frete:
            nome_frete, preco_frete, prazo_frete = frete.split("|")
            custo_envio = float(preco_frete)
        else:
            custo_envio = 0.0
    except (ValueError, TypeError):
        custo_envio = 0.0

    # 2. Lista de produtos (unit_price deve ser float)
    lista_de_produtos = []
    for item in itens:
        produto = db.get_or_404(Produto, item.produto_id)
        lista_de_produtos.append({
            "id": str(produto.id),
            "title": produto.nome,
            "quantity": int(item.quantidade),
            "currency_id": "BRL",
            "unit_price": float(produto.preco),  # Garante que é float
        })

    # 3. Estrutura correta para o Mercado Pago
    preference_data = {
        "items": lista_de_produtos,
        "shipments": {
            "cost": custo_envio,
            "mode": "not_specified",  # 'custom' exige configurações extras no painel
        },
        # URLs de retorno
        "back_urls": {
            "success": url_for('site.pagamento_sucesso', _external=True),
            "failure": url_for('site.home', _external=True),
            "pending": url_for('site.home', _external=True)
        },
        "auto_return": "approved",
    }

    return gerar_link_pagamento(preference_data)