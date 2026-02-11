import os

from PIL import Image
from flask import url_for, redirect
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField
from flask_login import current_user
from flask_wtf.file import FileAllowed
from markupsafe import Markup
from werkzeug.utils import secure_filename

from models import Foto


class BaseAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('site.login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


BASE_UPLOAD = os.path.join(os.path.dirname(__file__), 'static/uploads')


def formatar_imagem(caminho, tamanho=(800, 800)):
    img = Image.open(caminho)
    img.thumbnail(tamanho)
    img.save(caminho)


class FotoAdmin(ModelView):
    form_extra_fields = {
        'arquivo': FileUploadField(
            'Imagem',
            base_path=BASE_UPLOAD,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
        )
    }

    def on_model_change(self, form, model, is_created):
        if form.arquivo.data:
            pasta = os.path.join(BASE_UPLOAD, str(model.produto_id))
            os.makedirs(pasta, exist_ok=True)

            nome = secure_filename(model.arquivo)
            origem = os.path.join(BASE_UPLOAD, nome)
            destino = os.path.join(pasta, nome)

            if origem != destino:
                os.replace(origem, destino)
                model.arquivo = f"{model.produto_id}/{nome}"

            formatar_imagem(destino, (800, 800))

    column_formatters = {
        'arquivo': lambda v, c, m, p: Markup(
            f'<img src="{BASE_UPLOAD}/{m.arquivo}" style="max-height:100px;">'
        )
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class ProdutoAdmin(BaseAdmin):
    column_labels = {
        'preco': 'Preço',
        'descricao': 'Descrição',
        'novidade': 'Novidades',
        'escolha_do_mes': 'Produto do Mês'
    }
    column_descriptions = {'vendas': 'Quantia de vendas deste produto',
                           'preco': 'Inserir valor usando . para separar o valor dos centavos', 'novidade':
                               'Adicionar este produto à seção de novidades',
                           'escolha_do_mes': 'Selecionar este produto como Escolha do Mês'}
    column_searchable_list = ('nome',)
    column_filters = ('novidade', 'escolha_do_mes')
    UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'static/uploads')

    inline_models = [
        (Foto, dict(
            form_extra_fields={
                'arquivo': FileUploadField(
                    'Imagem',
                    base_path=UPLOAD_PATH,
                    validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
                )
            }
        ))
    ]

    column_formatters = {
        'imagem': lambda v, c, m, p: Markup(
            f'<img src="/static/uploads/{m.id}/{m.capa}" style="max-height:100px;">'
        ) if m.imagem else ''
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


class UsuarioAdmin(BaseAdmin):
    can_create = False
    column_list = ('nome', 'email', 'admin')
    column_labels = {'admin': 'Administrador'}
    column_filters = ('admin',)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


class CarrosselAdmin(BaseAdmin):
    column_labels = {'arquivo': 'Imagem'}
    form_extra_fields = {
        'arquivo': FileUploadField(
            'Imagem',
            base_path=BASE_UPLOAD,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
        )
    }

    def on_model_change(self, form, model, is_created):
        if form.arquivo.data:
            pasta = BASE_UPLOAD
            os.makedirs(pasta, exist_ok=True)

            nome = secure_filename(form.arquivo.data.filename)
            caminho = os.path.join(pasta, nome)

            form.arquivo.data.save(caminho)

            formatar_imagem(caminho, (1000, 1000))

            model.arquivo = nome

    column_formatters = {
        'arquivo': lambda v, c, m, p: Markup(
            f'<img src="{url_for("static", filename="uploads/" + m.arquivo)}" style="max-height:100px;">'
        ) if m.arquivo else ''
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
