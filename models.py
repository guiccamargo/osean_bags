from flask_login import UserMixin
from db import db


class Usuario(UserMixin, db.Model):
    """
    Model que representa um usuário da aplicação.

    Combina UserMixin do Flask-Login para gerenciamento de sessão com
    db.Model do SQLAlchemy para persistência no banco de dados.

    Attributes:
        id (int): Identificador único do usuário.
        nome (str): Primeiro nome do usuário. Máximo de 80 caracteres.
        sobrenome (str): Sobrenome do usuário. Máximo de 80 caracteres.
        email (str): Email único do usuário. Máximo de 120 caracteres.
        password_hash (str): Hash da senha do usuário. Máximo de 128 caracteres.
        admin (bool): Indica se o usuário possui privilégios de administrador.
            Padrão: False.
        items_carrinho (dynamic): Relação dinâmica com os itens do Carrinho
            do usuário. Carregamento sob demanda via query.
        enderecos (list[Endereco]): Lista de endereços vinculados ao usuário.

    Example:
        usuario = Usuario(
            email='joao@email.com',
            name='João',
            last_name='Silva',
            password=hash_senha
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
        """
        Inicializa um novo usuário.

        Args:
            email (str): Email do usuário.
            name (str): Primeiro nome do usuário.
            last_name (str): Sobrenome do usuário.
            password (str): Hash da senha do usuário.

        Note:
            O parâmetro password deve receber a senha já hasheada.
            Nunca armazene senhas em texto puro.
        """
        self.email = email
        self.nome = name
        self.sobrenome = last_name
        self.password_hash = password

    def is_admin(self):
        """
        Verifica se o usuário possui privilégios de administrador.

        Returns:
            bool: True se o usuário for administrador, False caso contrário.
        """
        return self.admin

    def get_inicial(self):
        """
        Retorna a inicial do primeiro nome do usuário em maiúsculo.

        Utilizado para exibição de avatar ou identificação visual do usuário
        na interface.

        Returns:
            str: Primeira letra do nome em maiúsculo.

        Example:
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