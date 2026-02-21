from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired

estados_brasil = [("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"), ("BA", "Bahia"),
    ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"), ("GO", "Goiás"), ("MA", "Maranhão"),
    ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"), ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"),
    ("PR", "Paraná"), ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"), ("SP", "São Paulo"),
    ("SE", "Sergipe"), ("TO", "Tocantins"), ]
"""
Lista de tuplas (sigla, nome) com todos os 27 estados brasileiros,
incluindo o Distrito Federal. Utilizada como choices nos formulários
que contêm o campo de seleção de estado.
"""


class RegisterForm(FlaskForm):
    """
    Formulário de registro de novo usuário.

    Attributes:
        email (StringField): Email do usuário. Obrigatório.
        nome (StringField): Primeiro nome do usuário. Obrigatório.
        sobrenome (StringField): Sobrenome do usuário. Obrigatório.
        senha (PasswordField): Senha do usuário. Obrigatório.
        submit (SubmitField): Botão de envio do formulário.

    Example:
        form = RegisterForm()
        if form.validate_on_submit():
            usuario = Usuario(
                email=form.email.data,
                name=form.nome.data,
                last_name=form.sobrenome.data,
                password=gerar_hash(form.senha.data)
            )
    """

    email = StringField("Email", validators=[DataRequired()], render_kw={"class": "contorno"})
    nome = StringField("Nome", validators=[DataRequired()], render_kw={"class": "contorno"})
    sobrenome = StringField("Sobrenome", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Cadastrar")


class LoginForm(FlaskForm):
    """
    Formulário de autenticação de usuário.

    Attributes:
        email (StringField): Email do usuário. Obrigatório.
        senha (PasswordField): Senha do usuário. Obrigatório.
        submit (SubmitField): Botão de envio do formulário.

    Example:
        form = LoginForm()
        if form.validate_on_submit():
            usuario = Usuario.query.filter_by(email=form.email.data).first()
    """

    email = StringField("Email", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Entrar")


class AtualizarSenhaForm(FlaskForm):
    """
    Formulário de atualização de senha do usuário autenticado.

    Requer a senha atual para confirmar a identidade do usuário
    antes de permitir a alteração.

    Attributes:
        senha_atual (PasswordField): Senha atual do usuário. Obrigatório.
        senha_nova (PasswordField): Nova senha desejada. Obrigatório.
        submit_senha (SubmitField): Botão de envio do formulário.

    Note:
        O nome do submit é submit_senha (em vez de submit) para permitir
        que múltiplos formulários coexistam na mesma página sem conflito
        na identificação do formulário submetido.
    """

    senha_atual = PasswordField("Senha Atual", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha_nova = PasswordField("Nova Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit_senha = SubmitField("Mudar Senha")


class AtualizarNomeForm(FlaskForm):
    """
    Formulário de atualização do nome do usuário autenticado.

    Suporta pré-preenchimento com os dados atuais do usuário,
    facilitando a edição sem necessidade de redigitar as informações.

    Attributes:
        nome (StringField): Primeiro nome do usuário. Obrigatório.
        sobrenome (StringField): Sobrenome do usuário. Obrigatório.
        submit_nome (SubmitField): Botão de envio do formulário.

    Note:
        O nome do submit é submit_nome (em vez de submit) para permitir
        que múltiplos formulários coexistam na mesma página sem conflito
        na identificação do formulário submetido.

    Example:
        form = AtualizarNomeForm(
            nome_atual=current_user.nome,
            sobrenome_atual=current_user.sobrenome
        )
    """

    nome = StringField("Nome", validators=[DataRequired()], render_kw={"class": "contorno"})
    sobrenome = StringField("Sobrenome", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit_nome = SubmitField("Atualizar")

    def __init__(self, nome_atual=None, sobrenome_atual=None, *args, **kwargs):
        """
        Inicializa o formulário com os dados atuais do usuário.

        Args:
            nome_atual (str, optional): Nome atual do usuário para pré-preenchimento.
            sobrenome_atual (str, optional): Sobrenome atual para pré-preenchimento.
            *args: Argumentos posicionais repassados ao FlaskForm.
            **kwargs: Argumentos nomeados repassados ao FlaskForm.

        Note:
            O pré-preenchimento só ocorre se nome_atual for fornecido.
            Caso contrário, os campos são inicializados vazios.
        """
        super().__init__(*args, **kwargs)
        if nome_atual:
            self.nome.data = nome_atual
            self.sobrenome.data = sobrenome_atual


class EnderecoForm(FlaskForm):
    """
    Formulário de cadastro de novo endereço de entrega.

    Attributes:
        apelido (StringField): Nome de identificação do endereço
            (ex: 'Casa', 'Trabalho'). Obrigatório.
        cep (StringField): CEP do endereço. Obrigatório.
        cidade (StringField): Cidade do endereço. Obrigatório.
        estado (SelectField): Estado selecionado a partir da lista
            de todos os estados brasileiros. Obrigatório.
        rua (StringField): Logradouro do endereço. Obrigatório.
        numero (StringField): Número do imóvel. Obrigatório.
        complemento (StringField): Complemento do endereço
            (ex: 'Apto 42'). Obrigatório.
        submit (SubmitField): Botão de envio do formulário.

    Note:
        O campo complemento é obrigatório neste formulário. Considere
        torná-lo opcional para maior flexibilidade, assim como em
        EditarEnderecoForm.
    """

    apelido = StringField("Apelido para o Endereço", validators=[DataRequired()], render_kw={"class": "contorno"})
    cep = StringField("Cep", validators=[DataRequired()], render_kw={"class": "contorno"})
    cidade = StringField("Cidade", validators=[DataRequired()], render_kw={"class": "contorno"})
    estado = SelectField("Estado", choices=estados_brasil, validators=[DataRequired()],
                         render_kw={"class": "contorno texto-estilizado text-center"})
    rua = StringField("Rua", validators=[DataRequired()], render_kw={"class": "contorno"})
    numero = StringField("Número", validators=[DataRequired()], render_kw={"class": "contorno"})
    complemento = StringField("Complemento", render_kw={"class": "contorno"})
    submit = SubmitField('Adicionar')


class EditarEnderecoForm(FlaskForm):
    """
    Formulário de edição de endereço de entrega existente.

    Estende as funcionalidades de EnderecoForm com um campo oculto
    para identificar o endereço sendo editado, e torna o complemento
    opcional.

    Attributes:
        endereco_id (HiddenField): ID do endereço sendo editado,
            enviado de forma oculta para identificação no backend.
        apelido (StringField): Nome de identificação do endereço. Obrigatório.
        cep (StringField): CEP do endereço. Obrigatório.
        cidade (StringField): Cidade do endereço. Obrigatório.
        estado (SelectField): Estado selecionado a partir da lista
            de todos os estados brasileiros. Obrigatório.
        rua (StringField): Logradouro do endereço. Obrigatório.
        numero (StringField): Número do imóvel. Obrigatório.
        complemento (StringField): Complemento do endereço. Opcional.
        submit_endereco (SubmitField): Botão de envio do formulário.

    Note:
        O nome do submit é submit_endereco (em vez de submit) para permitir
        que EnderecoForm e EditarEnderecoForm coexistam na mesma página
        sem conflito na identificação do formulário submetido.
    """

    endereco_id = HiddenField()
    apelido = StringField("Apelido para o Endereço", validators=[DataRequired()], render_kw={"class": "contorno"})
    cep = StringField("Cep", validators=[DataRequired()], render_kw={"class": "contorno"})
    cidade = StringField("Cidade", validators=[DataRequired()], render_kw={"class": "contorno"})
    estado = SelectField("Estado", choices=estados_brasil, validators=[DataRequired()],
                         render_kw={"class": "contorno texto-estilizado text-center"})
    rua = StringField("Rua", validators=[DataRequired()], render_kw={"class": "contorno"})
    numero = StringField("Número", validators=[DataRequired()], render_kw={"class": "contorno"})
    complemento = StringField("Complemento", render_kw={"class": "contorno"})
    submit_endereco = SubmitField('Editar')
