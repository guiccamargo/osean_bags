import os

from PIL import Image
from flask import url_for, redirect, abort
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField
from flask_login import current_user
from flask_wtf.file import FileAllowed
from markupsafe import Markup
from werkzeug.utils import secure_filename
from wtforms.validators import Regexp

from models import Foto

BASE_UPLOAD = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

def formatar_imagem(caminho, tamanho=(800, 800)):
    """
    Valida, redimensiona e salva uma imagem no caminho especificado.

    Abre o arquivo, verifica se é uma imagem válida, redimensiona respeitando
    a proporção original (thumbnail) e sobrescreve o arquivo. Caso o arquivo
    não seja uma imagem válida, ele é removido e uma exceção é lançada.

    Args:
        caminho (str): Caminho absoluto ou relativo do arquivo de imagem.
        tamanho (tuple[int, int]): Dimensão máxima (largura, altura) em pixels.
                                   O redimensionamento preserva a proporção.
                                   Padrão: (800, 800).

    Raises:
        ValueError: Se o arquivo não for uma imagem válida. O arquivo é
                    removido do disco antes da exceção ser lançada.

    Note:
        O arquivo é aberto duas vezes intencionalmente: Image.verify() invalida
        o objeto após a verificação, exigindo uma nova abertura para manipulação.

    Example:
        formatar_imagem('/uploads/foto.jpg')
        formatar_imagem('/uploads/banner.png', tamanho=(1200, 600))
    """
    try:
        img = Image.open(caminho)
        img.verify()  # verifica se é imagem válida
        img = Image.open(caminho)  # reabre após verify
        img.thumbnail(tamanho)
        img.save(caminho)
    except Exception:
        os.remove(caminho)
        raise ValueError("Arquivo enviado não é uma imagem válida.")
class BaseAdmin(ModelView):
    """
    View base para o painel administrativo.

    Estende ModelView do Flask-Admin, adicionando controle de acesso
    baseado em autenticação e privilégios de administrador.

    Methods:
        is_accessible(): Verifica se o usuário pode acessar a view.
        inaccessible_callback(): Redireciona para login caso o acesso seja negado.

    Example:
        class UserAdmin(BaseAdmin):
            column_list = ('id', 'name', 'email')
    """

    def is_accessible(self):
        """
        Verifica se o usuário atual tem permissão de acesso.

        Returns:
            bool: True se o usuário estiver autenticado e for administrador,
                  False caso contrário.
        """
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        """
        Callback executado quando o acesso é negado pelo is_accessible().

        Args:
            name (str): Nome da view que foi negada.
            **kwargs: Argumentos adicionais da view.

        Returns:
            Response: Redirecionamento para a rota 'site.login'.
        """
        return redirect(url_for('site.login'))


class MyAdminIndexView(AdminIndexView):
    """
    View customizada para a página inicial do painel administrativo.

    Estende AdminIndexView do Flask-Admin, adicionando controle de acesso
    baseado em autenticação e privilégios de administrador.

    Methods:
        is_accessible(): Verifica se o usuário pode acessar o index admin.
        inaccessible_callback(): Redireciona para login caso o acesso seja negado.

    Example:
        admin = Admin(app, index_view=MyAdminIndexView())
    """

    def is_accessible(self):
        """
        Verifica se o usuário atual tem permissão de acesso ao index.

        Returns:
            bool: True se o usuário estiver autenticado e for administrador,
                  False caso contrário.
        """
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        """
        Callback executado quando o acesso é negado pelo is_accessible().

        Args:
            name (str): Nome da view que foi negada.
            **kwargs: Argumentos adicionais da view.

        Returns:
            Response: Redirecionamento para a rota 'site.login'.
        """
        return redirect(url_for('site.login'))


class FotoAdmin(BaseAdmin):
    """
    View administrativa para gerenciamento de fotos de produtos.

    Estende BaseAdmin com suporte a upload de imagens, organização
    automática por produto e renderização de preview na listagem.

    Attributes:
        form_extra_fields (dict): Adiciona o campo 'arquivo' ao formulário,
            permitindo upload de imagens nos formatos jpg, jpeg, png e webp.
        column_formatters (dict): Renderiza o campo 'arquivo' como uma tag
            <img> na listagem, com altura máxima de 100px.

    Methods:
        on_model_change(): Processa e organiza o arquivo enviado após salvar.

    Example:
        admin.add_view(FotoAdmin(Foto, db.session, name='Fotos'))
    """

    form_extra_fields = {
        'arquivo': FileUploadField(
            'Imagem',
            base_path=BASE_UPLOAD,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
        )
    }

    def on_model_change(self, form, model, is_created):
        """
        Executado automaticamente após criação ou edição de uma Foto.

        Se um arquivo foi enviado, move-o para uma subpasta nomeada com o
        produto_id (ex: static/uploads/42/foto.jpg), atualiza o campo arquivo
        do model com o caminho relativo e aplica redimensionamento.

        Args:
            form (Form): Formulário submetido contendo os dados do upload.
            model (Foto): Instância do model sendo criado ou editado.
            is_created (bool): True se o model está sendo criado, False se editado.

        Raises:
            ValueError: Propagado de formatar_imagem() se o arquivo enviado
                        não for uma imagem válida. O arquivo é removido do disco.

        Note:
            A verificação `if origem != destino` evita mover o arquivo quando
            ele já se encontra no destino correto, o que ocorre em edições
            onde nenhum novo arquivo foi enviado.

        Example:
            # Arquivo enviado: static/uploads/foto.jpg
            # Após on_model_change: static/uploads/42/foto.jpg
            # model.arquivo: '42/foto.jpg'
        """
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
            f'<img src="{ url_for("static", filename="uploads/" + m.arquivo) }" style="max-height:100px;">'
        ) if m.arquivo else ''
    }


class ProdutoAdmin(BaseAdmin):
    """
    View administrativa para gerenciamento de produtos.

    Estende BaseAdmin com configurações específicas para o model Produto,
    incluindo labels traduzidos, descrições de apoio, busca, filtros,
    upload de imagens inline e renderização de capa na listagem.

    Attributes:
        column_labels (dict): Traduz os nomes das colunas para português.
        column_descriptions (dict): Exibe textos de ajuda abaixo de cada campo
            no formulário, orientando o preenchimento correto.
        column_searchable_list (tuple): Habilita busca textual pelo campo 'nome'.
        column_filters (tuple): Habilita filtros por 'novidade' e 'escolha_do_mes'.
        inline_models (list): Permite gerenciar fotos diretamente na página do
            Produto, com campo de upload validado por extensão.
        column_formatters (dict): Renderiza o campo 'imagem' como uma tag <img>
            na listagem, exibindo a capa com altura máxima de 100px.
            Retorna string vazia se não houver imagem cadastrada.

    Example:
        admin.add_view(ProdutoAdmin(Produto, db.session, name='Produtos'))
    """

    column_labels = {
        'preco': 'Preço',
        'descricao': 'Descrição',
        'novidade': 'Novidades',
        'escolha_do_mes': 'Produto do Mês'
    }

    column_descriptions = {
        'vendas': 'Quantia de vendas deste produto',
        'preco': 'Inserir valor usando . para separar o valor dos centavos',
        'novidade': 'Adicionar este produto à seção de novidades',
        'escolha_do_mes': 'Selecionar este produto como Escolha do Mês',
        'peso': 'Peso do produto em quilogramas',
        'altura': 'Altura do pacote em centímetros',
        'largura': 'Largura do pacote em centímetros',
        'comprimento': 'Comprimento do pacote em centímetros'
    }

    column_searchable_list = ('nome',)
    column_filters = ('novidade', 'escolha_do_mes')

    inline_models = [
        (Foto, dict(
            form_extra_fields={
                'arquivo': FileUploadField(
                    'Imagem',
                    base_path=BASE_UPLOAD,
                    validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
                )
            }
        ))
    ]

    column_formatters = {
        'imagem': lambda v, c, m, p: Markup(
            f'<img src="{ url_for("static", filename=f"uploads/{m.id}/{m.capa}") }" style="max-height:100px;">'
        ) if m.imagem else ''
    }

class UsuarioAdmin(BaseAdmin):
    """
    View administrativa para gerenciamento de usuários.

    Estende BaseAdmin com configurações específicas para o model Usuario.
    A criação de usuários é desabilitada, restringindo o admin ao gerenciamento
    de registros existentes.

    Attributes:
        can_create (bool): Desabilita a criação de novos usuários pelo admin.
            Usuários devem ser criados exclusivamente pelo fluxo de cadastro.
        column_list (tuple): Define as colunas exibidas na listagem:
            nome, email e status de administrador.
        column_labels (dict): Traduz o campo 'admin' para 'Administrador'.
        column_filters (tuple): Habilita filtro lateral pelo campo 'admin',
            permitindo listar apenas administradores ou usuários comuns.

    Example:
        admin.add_view(UsuarioAdmin(Usuario, db.session, name='Usuários'))
    """

    can_create = False
    column_list = ('nome', 'email', 'admin')
    column_labels = {'admin': 'Administrador'}
    column_filters = ('admin',)


class CarrosselAdmin(BaseAdmin):
    """
    View administrativa para gerenciamento de imagens do carrossel.

    Estende BaseAdmin com suporte a upload de imagens, redimensionamento
    automático e renderização de preview na listagem.

    Diferente de FotoAdmin, as imagens do carrossel são salvas diretamente
    em BASE_UPLOAD sem organização em subpastas, pois não estão vinculadas
    a um produto específico.

    Attributes:
        column_labels (dict): Traduz o campo 'arquivo' para 'Imagem'.
        form_extra_fields (dict): Adiciona o campo 'arquivo' ao formulário,
            permitindo upload de imagens nos formatos jpg, jpeg, png e webp.
        column_formatters (dict): Renderiza o campo 'arquivo' como uma tag
            <img> na listagem, com altura máxima de 100px. Retorna string
            vazia se não houver imagem cadastrada.

    Methods:
        on_model_change(): Processa e salva o arquivo enviado após salvar.

    Example:
        admin.add_view(CarrosselAdmin(Carrossel, db.session, name='Carrossel'))
    """

    column_labels = {'arquivo': 'Imagem'}

    form_extra_fields = {
        'arquivo': FileUploadField(
            'Imagem',
            base_path=BASE_UPLOAD,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
        )
    }

    def on_model_change(self, form, model, is_created):
        """
        Executado automaticamente após criação ou edição de um item do Carrossel.

        Se um arquivo foi enviado, salva-o diretamente em BASE_UPLOAD,
        aplica redimensionamento máximo de 1000x1000px e atualiza o campo
        arquivo do model com o nome do arquivo.

        Args:
            form (Form): Formulário submetido contendo os dados do upload.
            model (Carrossel): Instância do model sendo criado ou editado.
            is_created (bool): True se o model está sendo criado, False se editado.

        Raises:
            Exception: Qualquer exceção lançada por formatar_imagem() é
                       propagada após a remoção do arquivo do disco.

        Note:
            O stream do arquivo é reposicionado com seek(0) antes de salvar,
            garantindo que o arquivo seja gravado corretamente mesmo que o
            stream tenha sido lido anteriormente durante a validação.

        Example:
            # Arquivo enviado: foto.jpg
            # Após on_model_change: static/uploads/foto.jpg
            # model.arquivo: 'foto.jpg'
        """
        if form.arquivo.data:
            pasta = BASE_UPLOAD
            os.makedirs(pasta, exist_ok=True)

            file = form.arquivo.data
            file.stream.seek(0)

            nome = secure_filename(file.filename)
            caminho = os.path.join(pasta, nome)

            file.save(caminho)

            try:
                formatar_imagem(caminho, (1000, 1000))
            except Exception:
                os.remove(caminho)
                raise

            model.arquivo = nome

    column_formatters = {
        'arquivo': lambda v, c, m, p: Markup(
            f'<img src="{url_for("static", filename="uploads/" + m.arquivo)}" style="max-height:100px;">'
        ) if m.arquivo else ''
    }

class ConfigAdmin(BaseAdmin):
    """
    View administrativa para gerenciamento das configurações da aplicação.

    Estende BaseAdmin com validações de formulário e descrições de apoio
    para os campos de configuração da empresa.

    Attributes:
        form_args (dict): Define validadores para os campos do formulário.
            O campo 'cep_origem' aceita apenas CEPs no formato XXXXX-XXX
            ou XXXXXXXX.
        column_descriptions (dict): Exibe textos de ajuda abaixo de cada
            campo no formulário, orientando o preenchimento correto.

    Example:
        admin.add_view(ConfigAdmin(Config, db.session, name='Configurações'))
    """

    form_args = {
        'cep_origem': {
            'validators': [
                Regexp(r'^\d{5}-?\d{3}$', message="CEP inválido")
            ]
        }
    }

    column_descriptions = {
        'cep_origem': 'CEP de onde o produto será enviado.',
        'email': 'Email da empresa'
    }