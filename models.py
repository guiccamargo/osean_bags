from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from db import db


class Usuario(UserMixin, db.Model):
    """Representa um usuário da aplicação.

    Combina ``UserMixin`` do Flask-Login para gerenciamento de sessão com
    ``db.Model`` do SQLAlchemy para persistência no banco de dados.

    :param email: E-mail do usuário. Deve ser único na base de dados.
    :param name: Primeiro nome do usuário.
    :param last_name: Sobrenome do usuário.
    :param password: Senha já hasheada do usuário. Nunca armazene em texto puro.

    :ivar id: Identificador único do usuário (chave primária).
    :ivar nome: Primeiro nome do usuário. Máximo de 80 caracteres.
    :ivar sobrenome: Sobrenome do usuário. Máximo de 80 caracteres.
    :ivar email: E-mail único do usuário. Máximo de 120 caracteres.
    :ivar password_hash: Hash da senha do usuário. Máximo de 128 caracteres.
    :ivar admin: Indica se o usuário possui privilégios de administrador. Padrão: ``False``.
    :ivar items_carrinho: Relação dinâmica com os itens do carrinho do usuário.
                          Carregada sob demanda via query (``lazy='dynamic'``).
    :ivar enderecos: Lista de endereços vinculados ao usuário.

    Exemplo de uso::

        usuario = Usuario(
            email='joao@email.com',
            name='João',
            last_name='Silva',
            password=generate_password_hash('senha123')
        )
        db.session.add(usuario)
        db.session.commit()
    """

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)
    sobrenome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, default=False)

    items_carrinho = db.relationship('Carrinho', lazy='dynamic')
    enderecos = db.relationship('Endereco', backref='usuario', lazy=True)

    def __init__(self, email, name, last_name, password):
        self.email = email
        self.nome = name
        self.sobrenome = last_name
        self.password_hash = password

    def set_password(self, senha):
        """Atualiza a senha do usuário aplicando hash antes de armazenar.

        :param senha: Nova senha em texto puro. Será hasheada internamente
                      via ``werkzeug.security.generate_password_hash``.

        .. warning::
            Nunca armazene ou passe senhas em texto puro para o banco de dados.
        """
        self.password_hash = generate_password_hash(senha)

    def check_password(self, senha):
        """Verifica se a senha fornecida corresponde ao hash armazenado.

        :param senha: Senha em texto puro a ser verificada.
        :return: ``True`` se a senha estiver correta, ``False`` caso contrário.
        """
        return check_password_hash(self.password_hash, senha)

    def is_admin(self):
        """Verifica se o usuário possui privilégios de administrador.

        :return: ``True`` se o usuário for administrador, ``False`` caso contrário.
        """
        return self.admin

    def get_inicial(self):
        """Retorna a inicial do primeiro nome do usuário em maiúsculo.

        Utilizado para exibição de avatar ou identificação visual na interface.

        :return: Primeira letra do nome em maiúsculo.

        Exemplo::

            usuario.nome = 'joão'
            usuario.get_inicial()  # retorna 'J'
        """
        return str(self.nome[0]).upper()

class Produto(db.Model):
    """
    Model que representa um produto da loja.

    Armazena informações de exibição, precificação e dimensões físicas
    necessárias para cálculo de frete.

    Attributes:
        id (int): Identificador único do produto.
        nome (str): Nome do produto. Máximo de 100 caracteres.
        preco (float): Preço do produto.
        descricao (str): Descrição completa do produto. Sem limite de caracteres.
        peso (float): Peso do produto em quilogramas.
        altura (int): Altura do pacote em centímetros.
        largura (int): Largura do pacote em centímetros.
        comprimento (int): Comprimento do pacote em centímetros.
        vendas (int): Contador de vendas realizadas. Padrão: 0.
        novidade (bool): Indica se o produto aparece na seção de novidades.
            Padrão: False.
        escolha_do_mes (bool): Indica se o produto é a escolha do mês.
            Padrão: False.
        fotos (list[Foto]): Lista de fotos vinculadas ao produto.
            Deleção em cascata: ao remover o produto, todas as fotos
            associadas são removidas automaticamente.

    Example:
        produto = Produto()
        produto.nome = 'Camiseta'
        produto.preco = 59.90
        produto.peso = 0.3
    """

    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text(), nullable=False)
    peso = db.Column(db.Float, nullable=False)
    altura = db.Column(db.Integer, nullable=False)
    largura = db.Column(db.Integer, nullable=False)
    comprimento = db.Column(db.Integer, nullable=False)
    vendas = db.Column(db.Integer, nullable=False, default=0)
    novidade = db.Column(db.Boolean, default=False)
    escolha_do_mes = db.Column(db.Boolean, default=False)

    fotos = db.relationship(
        'Foto',
        backref='produto',
        cascade='all, delete-orphan',
        lazy=True
    )


class Foto(db.Model):
    """
    Model que representa uma foto de um produto.

    Cada foto pertence a um único produto. Ao deletar o produto,
    todas as fotos associadas são removidas automaticamente via cascade.

    Attributes:
        id (int): Identificador único da foto.
        arquivo (str): Caminho relativo da imagem dentro de static/uploads,
            no formato '{produto_id}/nome_arquivo.jpg'.
            Máximo de 200 caracteres.
        produto_id (int): Chave estrangeira referenciando o produto ao qual
            a foto pertence.

    Example:
        foto = Foto()
        foto.arquivo = '42/camiseta.jpg'
        foto.produto_id = 42
    """

    __tablename__ = 'fotos'

    id = db.Column(db.Integer, primary_key=True)
    arquivo = db.Column(db.String(200), nullable=False)
    produto_id = db.Column(
        db.Integer,
        db.ForeignKey('produtos.id'),
        nullable=False
    )


class Carrossel(db.Model):
    """
    Model que representa uma imagem do carrossel da página inicial.

    As imagens são salvas diretamente em BASE_UPLOAD, sem organização
    em subpastas, pois não estão vinculadas a nenhum produto.

    Attributes:
        id (int): Identificador único da imagem.
        arquivo (str): Nome do arquivo de imagem dentro de static/uploads.
            Máximo de 200 caracteres.

    Example:
        slide = Carrossel()
        slide.arquivo = 'banner_verao.jpg'
    """

    __tablename__ = 'carrossel'

    id = db.Column(db.Integer, primary_key=True)
    arquivo = db.Column(db.String(200), nullable=False)


class Carrinho(db.Model):
    """
    Model que representa um item no carrinho de compras de um usuário.

    Cada registro corresponde a um produto adicionado ao carrinho,
    com sua respectiva quantidade.

    Attributes:
        id (int): Identificador único do item no carrinho.
        usuario_id (int): Chave estrangeira referenciando o usuário dono
            do carrinho.
        produto_id (int): Chave estrangeira referenciando o produto
            adicionado. Nullable para preservar o histórico caso o
            produto seja removido.
        quantidade (int): Quantidade do produto no carrinho. Padrão: 1.
        produto (Produto): Relação com o model Produto para acesso
            direto aos dados do produto.

    Example:
        item = Carrinho()
        item.usuario_id = 1
        item.produto_id = 42
        item.quantidade = 2
    """

    __tablename__ = 'carrinho'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=True)
    quantidade = db.Column(db.Integer, default=1)
    produto = db.relationship('Produto')


class Config(db.Model):
    """
    Model que representa as configurações globais da aplicação.

    Armazena informações operacionais da empresa utilizadas em
    funcionalidades como cálculo de frete e contato.

    Attributes:
        id (int): Identificador único da configuração.
        cep_origem (str): CEP de origem para cálculo de frete,
            no formato XXXXX-XXX. Máximo de 9 caracteres.
        email (str): Email único da empresa. Máximo de 120 caracteres.

    Note:
        Espera-se que exista apenas um registro desta tabela.
        Considere adicionar uma validação ou restrição para garantir
        isso em nível de banco de dados.

    Example:
        config = Config()
        config.cep_origem = '01310-100'
        config.email = 'contato@empresa.com'
    """

    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True)
    cep_origem = db.Column(db.String(9), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Endereco(db.Model):
    """
    Model que representa um endereço de entrega de um usuário.

    Um usuário pode ter múltiplos endereços cadastrados, identificados
    por um apelido único por usuário (ex: 'Casa', 'Trabalho').

    Attributes:
        id (int): Identificador único do endereço.
        apelido (str): Nome de identificação do endereço. Único e
            obrigatório. Máximo de 200 caracteres.
        cep (str): CEP do endereço no formato XXXXX-XXX.
            Máximo de 9 caracteres.
        cidade (str): Cidade do endereço. Máximo de 200 caracteres.
        estado (str): Sigla do estado com 2 caracteres (ex: 'SP').
        rua (str): Logradouro do endereço. Máximo de 200 caracteres.
        numero (int): Número do imóvel. Opcional.
        complemento (str): Complemento do endereço (ex: 'Apto 42').
            Opcional. Máximo de 200 caracteres.
        usuario_id (int): Chave estrangeira referenciando o usuário
            dono do endereço.

    Example:
        endereco = Endereco()
        endereco.apelido = 'Casa'
        endereco.cep = '01310-100'
        endereco.cidade = 'São Paulo'
        endereco.estado = 'SP'
        endereco.rua = 'Avenida Paulista'
        endereco.numero = 1000
        endereco.usuario_id = 1
    """

    __tablename__ = 'endereco'

    id = db.Column(db.Integer, primary_key=True)
    apelido = db.Column(db.String(200), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    cidade = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    rua = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.Integer)
    complemento = db.Column(db.String(200))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


class Pedido(db.Model):
    """Representa um pedido realizado por um usuário na aplicação.

    Armazena os dados completos do pedido no momento da compra, incluindo
    endereço de entrega e informações de frete como snapshot, garantindo
    que o histórico não seja afetado por alterações futuras no cadastro
    do usuário.

    :ivar id: Identificador único do pedido (chave primária).
    :ivar usuario_id: Chave estrangeira referenciando o usuário que realizou o pedido.
    :ivar data_criacao: Data e hora de criação do pedido. Preenchida automaticamente.
    :ivar status: Status atual do pedido. Valores possíveis: ``pendente``, ``pago``, ``cancelado``.
                  Padrão: ``pendente``.
    :ivar metodo_envio: Nome ou código do metodo de envio escolhido.
    :ivar valor_frete: Valor do frete em reais no momento da compra.
    :ivar prazo_envio: Prazo estimado de entrega em dias úteis.
    :ivar rua: Rua do endereço de entrega no momento da compra.
    :ivar numero: Número do endereço de entrega.
    :ivar cidade: Cidade do endereço de entrega.
    :ivar cep: CEP do endereço de entrega.
    :ivar total_pedido: Valor total do pedido em reais, incluindo frete.
    :ivar payment_id_mercadopago: ID do pagamento gerado pelo Mercado Pago.
                                   Utilizado para rastreio e conciliação financeira.
    :ivar itens: Lista de :class:`ItemPedido` vinculados a este pedido.

    .. note::
        Os dados de endereço e frete são armazenados diretamente no pedido
        (snapshot), e não como referência ao cadastro do usuário. Isso preserva
        o histórico mesmo que o usuário altere seus dados posteriormente.
    """

    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now())

    status = db.Column(db.String(20), default='pendente')  # pendente, pago, cancelado
    metodo_envio = db.Column(db.String(50))
    valor_frete = db.Column(db.Float)
    prazo_envio = db.Column(db.Integer)

    rua = db.Column(db.String(100))
    numero = db.Column(db.String(10))
    cidade = db.Column(db.String(50))
    cep = db.Column(db.String(10))

    total_pedido = db.Column(db.Float)
    payment_id_mercadopago = db.Column(db.String(100))

    itens = db.relationship('ItemPedido', backref='pedidos', lazy=True)


class ItemPedido(db.Model):
    """Representa um item individual dentro de um pedido.

    Cada instância corresponde a um produto adicionado ao pedido, com
    o preço e nome fixados no momento da compra como snapshot, garantindo
    que alterações futuras no cadastro do produto não afetem o histórico.

    :ivar id: Identificador único do item (chave primária).
    :ivar pedido_id: Chave estrangeira referenciando o :class:`Pedido` ao qual
                     este item pertence.
    :ivar produto_id: Chave estrangeira referenciando o produto correspondente
                      na tabela ``produtos``.
    :ivar nome: Nome do produto fixado no momento da compra.
    :ivar quantidade: Quantidade do produto adicionada ao pedido.
    :ivar preco_unitario: Preço unitário do produto fixado no momento da compra,
                          em reais. Não reflete alterações posteriores no cadastro
                          do produto.

    .. note::
        O ``preco_unitario`` e o ``nome`` são armazenados como snapshot para
        preservar a integridade do histórico de compras. O valor total do item
        pode ser calculado como ``quantidade * preco_unitario``.
    """

    __tablename__ = 'itens_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    nome = db.Column(db.String(250), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
