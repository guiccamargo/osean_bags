from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    """
    Formulário de registro
    """
    email = StringField("Email", validators=[DataRequired()], render_kw={"class": "contorno"})
    nome = StringField("Nome", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Cadastrar")


class LoginForm(FlaskForm):
    """
    Formulário de login
    """
    email = StringField("Email", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Entrar")

class AtualizarLoginForm(FlaskForm):
    """
    Formulário de atualização login
    """
    senha_atual = PasswordField("Senha Atual", validators=[DataRequired()], render_kw={"class": "contorno"})
    senha_nova = PasswordField("Nova Senha", validators=[DataRequired()], render_kw={"class": "contorno"})
    confirmacao_senha_nova = PasswordField("Confirme a Nova Senha", validators=[DataRequired()], render_kw={"class": "contorno"})

    submit = SubmitField("Mudar Senha")

class AtualizarNomeForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()], render_kw={"class": "contorno"})
    submit = SubmitField("Atualizar")