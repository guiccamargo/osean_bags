from typing import List

import sqlalchemy

from models import Carrossel


def acessar_carrossel() -> List[str]:
    """Acessa os itens do carrossel.

    Acessa as imagens armazenadas no banco de dados para exibi-las no carossel da página inicial.

    :return: lista com o caminho das imagens do carrossel ou None.
    """
    try:
        return Carrossel.query.all()
    except sqlalchemy.exc.OperationalError:
        return None
