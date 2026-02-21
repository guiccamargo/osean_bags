from typing import List

from flask import request

from db import db
from models import Endereco


def acessar_enderecos(id_usuario: int) -> List[Endereco] | None:
    """Lista os endereços cadastrados por um usuário.

    Acessa os endereços no banco de dados associados ao usuário atual.

    :param id_usuario: id do usuário atual
    :return: lista de endereços se a busca retornar algum valor, caso contrário, None
    """
    return Endereco.query.filter_by(usuario_id=id_usuario).all() if id_usuario else None


def adicionar_endereco(id_usuario: int) -> None:
    """Adiciona novo endereço.

    Cria um novo registro na tabela de endereços usando as informções passadas através do formulário.

    :param id_usuario: id do usuário atual/
    :return: None
    """

    apelido = request.form.get('apelido')
    cep = request.form.get('cep')
    if '-' in cep:  # Formatar cep
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


def editar_endereco(id_endereco: int) -> None:
    """Edita um endereço.

    Altera informações de um endereço já existente no banco de dados.

    :param id_endereco: id do endereço a ser alterado
    :return: None
    """

    apelido = request.form.get('apelido')
    cep = request.form.get('cep')
    if '-' in cep:  # Formatar cep
        cep.replace('-', '')
    cidade = request.form.get('cidade')
    estado = request.form.get('estado')
    rua = request.form.get('rua')
    numero = request.form.get('numero')
    complemento = request.form.get('complemento')

    endereco = db.get_or_404(Endereco, id_endereco)

    endereco.apelido = apelido
    endereco.cep = cep
    endereco.cidade = cidade
    endereco.estado = estado
    endereco.rua = rua
    endereco.numero = numero
    endereco.complemento = complemento

    db.session.commit()
