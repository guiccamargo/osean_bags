from typing import Optional

from db import db
from models import Cupom, CupomUso, Pedido


def checar_cupom(codigo: str) -> Optional[Cupom]:
    """Verifica se um cupom de desconto existe e é válido.

    Realiza uma consulta case-insensitive pelo código informado.
    Retorna o objeto :class:`Cupom` caso encontrado, ou ``None`` se o
    código não existir na base de dados.

    :param codigo: Código do cupom digitado pelo usuário.
    :return: Instância de :class:`Cupom` se válido, ``None`` caso contrário.

    Example::

        cupom = checar_cupom('OSEAN10')
        if cupom:
            total = aplicar_desconto(total_carrinho, cupom)
    """
    return db.session.execute(
        db.select(Cupom).where(Cupom.codigo == codigo.strip().upper())
    ).scalar_one_or_none()


def cupom_ja_usado(cupom_id: int, usuario_id: int) -> bool:
    """Verifica se um usuário já utilizou um cupom em algum pedido pago.

    Consulta a tabela ``cupom_usos`` buscando um registro com a combinação
    de ``cupom_id`` e ``usuario_id`` informados.

    :param cupom_id: ID do cupom a ser verificado.
    :param usuario_id: ID do usuário que está tentando aplicar o cupom.
    :return: ``True`` se o cupom já foi utilizado pelo usuário, ``False``
             caso contrário.

    Example::

        if cupom_ja_usado(cupom.id, current_user.id):
            return jsonify({'erro': 'Você já utilizou este cupom.'}), 409
    """
    uso = db.session.execute(
        db.select(CupomUso).where(
            CupomUso.cupom_id == cupom_id,
            CupomUso.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    return uso is not None


def usuario_tem_pedido_pago(usuario_id: int) -> bool:
    """Verifica se um usuário já possui pelo menos um pedido com status 'pago'.

    Utilizado para validar cupons do tipo ``primeira_compra``, que só podem
    ser aplicados por clientes que ainda não finalizaram nenhuma compra.

    :param usuario_id: ID do usuário a ser verificado.
    :return: ``True`` se existir ao menos um pedido pago, ``False`` caso contrário.

    Example::

        if cupom.primeira_compra and usuario_tem_pedido_pago(current_user.id):
            return jsonify({'erro': 'Este cupom é válido apenas na primeira compra.'}), 409
    """
    pedido = db.session.execute(
        db.select(Pedido).where(
            Pedido.usuario_id == usuario_id,
            Pedido.status == 'pago',
        )
    ).first()
    return pedido is not None


def registrar_uso_cupom(cupom_id: int, usuario_id: int, pedido_id: int) -> None:
    """Registra que um usuário utilizou um cupom em um pedido confirmado.

    Deve ser chamado exclusivamente após a confirmação do pagamento
    (status ``approved`` do Mercado Pago), nunca no momento da aplicação
    do cupom no carrinho.

    :param cupom_id: ID do cupom utilizado.
    :param usuario_id: ID do usuário que utilizou o cupom.
    :param pedido_id: ID do pedido em que o cupom foi aplicado.
    :return: None

    .. warning::
        Esta função não verifica se o cupom já foi usado antes de inserir.
        A constraint ``UniqueConstraint`` do banco de dados impedirá
        duplicatas em nível de infraestrutura, mas para melhor tratamento
        de erros prefira chamar :func:`cupom_ja_usado` antes.

    Example::

        registrar_uso_cupom(cupom_id=1, usuario_id=3, pedido_id=42)
    """
    uso = CupomUso(cupom_id=cupom_id, usuario_id=usuario_id, pedido_id=pedido_id)
    db.session.add(uso)
    db.session.commit()


def aplicar_desconto(total: float, cupom: Cupom) -> float:
    """Aplica o percentual de desconto de um cupom ao total do carrinho.

    Subtrai do ``total`` o valor correspondente ao percentual de desconto
    definido no cupom. O resultado é arredondado para duas casas decimais
    e nunca retorna valor negativo.

    :param total: Valor total do carrinho em reais, sem desconto.
    :param cupom: Instância de :class:`Cupom` com o percentual de desconto.
    :return: Novo total após a aplicação do desconto (mínimo 0.0).

    Example::

        cupom = checar_cupom('OSEAN10')
        total_com_desconto = aplicar_desconto(250.00, cupom)
        # Desconto de 10% → retorna 225.00
    """
    desconto = total * (cupom.desconto / 100)
    return round(max(total - desconto, 0.0), 2)