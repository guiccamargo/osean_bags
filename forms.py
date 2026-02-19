from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired

estados_brasil = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]


class RegisterForm(FlaskForm):
    """
    Formulário de registro
    """
    email = StringField("Email", validators=[DataRequired()], render_kw={"class": "contorno"})
    nome = StringField("Nome", validators=[DataRequired()], render_kw={"class": "contorno"})
    sobrenome = StringField("Sobrenome", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Cadastrar")


class LoginForm(FlaskForm):
    """
    Formulário de login
    """
    email = StringField("Email", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Entrar")


class AtualizarSenhaForm(FlaskForm):
    """
    Formulário de atualização login
    """
    senha_atual = PasswordField("Senha Atual", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha_nova = PasswordField("Nova Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit_senha = SubmitField("Mudar Senha")


class AtualizarNomeForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()], render_kw={"class": "contorno"})
    sobrenome = StringField("Sobrenome", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit_nome = SubmitField("Atualizar")

    def __init__(self, nome_atual=None, sobrenome_atual=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if nome_atual:
            self.nome.data = nome_atual
            self.sobrenome.data = sobrenome_atual


class EnderecoForm(FlaskForm):
    apelido = StringField("Apelido para o Endereço", validators=[DataRequired()], render_kw={"class": "contorno"})
    cep = StringField("Cep", validators=[DataRequired()], render_kw={"class": "contorno"})
    cidade = StringField("Cidade", validators=[DataRequired()], render_kw={"class": "contorno"})
    estado = SelectField("Estado", choices=estados_brasil, validators=[DataRequired()],
                         render_kw={"class": "contorno texto-estilizado text-center"})
    rua = StringField("Rua", validators=[DataRequired()], render_kw={"class": "contorno"})
    numero = StringField("Número", validators=[DataRequired()], render_kw={"class": "contorno"})
    complemento = StringField("Complemento", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField('Adicionar')


class EditarEnderecoForm(FlaskForm):
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

