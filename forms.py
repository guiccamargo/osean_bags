from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    """
    Formulário de registro
    """
    email = StringField("Email", validators=[DataRequired()])
    nome = StringField("Nome", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Cadastrar")


class LoginForm(FlaskForm):
    """
    Formulário de login
    """
    email = StringField("Email", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")
