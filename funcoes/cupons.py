from typing import Optional
from db import db
from models import Cupom


def checar_cupom(codigo: str) -> Optional[Cupom]:
    """Verifica se um cupom de desconto existe e é válido.
    ...
    """
    return db.session.execute(
        db.select(Cupom).where(Cupom.codigo == codigo.strip().upper())
    ).scalar_one_or_none()


def aplicar_desconto(total: float, cupom: Cupom) -> float:
    """Aplica o percentual de desconto de um cupom ao total do carrinho.
    ...
    """
    desconto = total * (cupom.desconto / 100)
    return round(max(total - desconto, 0.0), 2)