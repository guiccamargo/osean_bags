from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Classe base para todos os models da aplicação.

    Estende DeclarativeBase do SQLAlchemy, centralizando a configuração
    do sistema declarativo de mapeamento objeto-relacional (ORM).

    Todos os models da aplicação devem herdar desta classe indiretamente
    através de db.Model, que é configurado com esta base.

    Example:
        class Produto(db.Model):
            __tablename__ = 'produtos'
            id = db.Column(db.Integer, primary_key=True)
    """
    pass


db = SQLAlchemy(model_class=Base)
"""
Instância global do SQLAlchemy configurada com a Base declarativa customizada.

Deve ser inicializada com a aplicação Flask via db.init_app(app) antes
de qualquer operação com o banco de dados.

Example:
    # Inicialização com a aplicação:
    from db import db
    db.init_app(app)

    # Uso em models:
    from db import db
    class Usuario(db.Model):
        ...

    # Uso em rotas:
    db.session.add(objeto)
    db.session.commit()
"""