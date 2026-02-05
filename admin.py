import os

from PIL import Image
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField
from flask_login import current_user
from flask_wtf.file import FileAllowed
from markupsafe import Markup
from werkzeug.utils import secure_filename

from models import Foto


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return 'Acesso Negado'


# def formatar_imagem(imagem_path, tamanho):
#     def crop_center(img):
#         w, h = img.size
#         min_dim = min(w, h)
#         left = (w - min_dim) // 2
#         top = (h - min_dim) // 2
#         right = left + min_dim
#         bottom = top + min_dim
#         return img.crop((left, top, right, bottom))
#
#     img = Image.open(imagem_path)
#     img = crop_center(img)
#     max_size = tamanho  # Max width and height
#
#     img.thumbnail(max_size, Image.Resampling.LANCZOS)
#
#     img.save(imagem_path)
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


class ProdutoAdmin(ModelView):
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

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    # class ProdutoAdmin(ModelView):
    #     file_path = os.path.join(os.path.dirname(__file__), 'static/uploads/')
    #     def on_model_create(self, form, model, is_created):
    #         if is_created:
    #             produto_id = model.id
    #             self.file_path = os.path.join(self.file_path, produto_id)
    #
    #     form_extra_fields = {
    #         'capa': FileUploadField(
    #             'Capa',
    #             base_path=file_path,
    #             validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Somente imagens!')]
    #         )
    #     }
    #     inline_models = (Foto,)
    #     def on_model_change(self, form, model, is_created):
    #         if form.capa.data:
    #             caminho = os.path.join(self.file_path, model.imagem)
    #             formatar_imagem(caminho, (400, 500))

    column_formatters = {
        'imagem': lambda v, c, m, p: Markup(
            f'<img src="/static/uploads/{m.id}/{m.capa}" style="max-height:100px;">'
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
