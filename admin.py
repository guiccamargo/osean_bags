import os

from PIL import Image
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField
from flask_login import current_user
from flask_wtf.file import FileAllowed
from markupsafe import Markup


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


def formatar_imagem(imagem_path, tamanho):
    def crop_center(img):
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        return img.crop((left, top, right, bottom))

    img = Image.open(imagem_path)
    img = crop_center(img)
    max_size = tamanho  # Max width and height

    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    img.save(imagem_path)


class ProdutoAdmin(ModelView):
    file_path = os.path.join(os.path.dirname(__file__), 'static/uploads')
    form_extra_fields = {
        'imagem': FileUploadField(
            'Imagem',
            base_path=file_path,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Somente imagens!')]
        )
    }

    def on_model_change(self, form, model, is_created):
        if form.imagem.data:
            caminho = os.path.join(self.file_path, model.imagem)
            formatar_imagem(caminho, (400, 500))

    column_formatters = {
        'imagem': lambda v, c, m, p: Markup(
            f'<img src="/static/uploads/{m.imagem}" style="max-height:100px;">'
        ) if m.imagem else ''
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


class UsuarioAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


class CarrosselAdmin(ModelView):
    file_path = os.path.join(os.path.dirname(__file__), 'static/uploads/carrossel')
    form_extra_fields = {
        'primeira_imagem': FileUploadField(
            'Imagem',
            base_path=file_path,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Somente imagens!')]
        ),
        'segunda_imagem': FileUploadField(
            'Imagem',
            base_path=file_path,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Somente imagens!')]
        )
    }

    def on_model_change(self, form, model, is_created):
        caminho = os.path.join(self.file_path, model.primeira_imagem)
        formatar_imagem(caminho, (400, 500))
        caminho = os.path.join(self.file_path, model.segunda_imagem)
        formatar_imagem(caminho, (400, 500))

    column_formatters = {
        'primeira_imagem': lambda v, c, m, p: Markup(
            f'<img src="/static/uploads/carrossel/{m.primeira_imagem}" style="max-height:100px;">'
        ) if m.primeira_imagem else '',
        'segunda_imagem': lambda v, c, m, p: Markup(
            f'<img src="/static/uploads/carrossel/{m.segunda_imagem}" style="max-height:100px;">'
        ) if m.segunda_imagem else ''
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'
