import os
from apis.storage import fazer_upload, deletar_imagem, public_id_from_url
from PIL import Image
from flask import url_for, redirect
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField
from flask_admin.menu import MenuLink
from flask_login import current_user
from flask_wtf.file import FileAllowed
from markupsafe import Markup
from werkzeug.utils import secure_filename
from wtforms.validators import Regexp

from db import db
from models import Foto

BASE_UPLOAD = os.path.join(os.path.dirname(__file__))



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

    Armazena imagens no Cloudinary em vez do filesystem local,
    garantindo persistência entre deploys no Render.

    Attributes:
        form_extra_fields (dict): Campo de upload de imagem no formulário admin.
        column_formatters (dict): Renderiza preview da imagem na listagem.
    """

    form_extra_fields = {
        'arquivo': FileUploadField(
            'Imagem',
            base_path=BASE_UPLOAD,
            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])]
        )
    }

    def on_model_change(self, form, model, is_created):
        """Faz upload da imagem para o Cloudinary após salvar a Foto.

        Substitui o arquivo local por uma URL do Cloudinary no campo
        ``model.arquivo``. O arquivo temporário local é removido após o upload.

        :param form: Formulário submetido com os dados do upload.
        :param model: Instância de Foto sendo criada ou editada.
        :param is_created: True se o model está sendo criado.
        """
        if form.arquivo.data:
            caminho_temp = os.path.join(BASE_UPLOAD, secure_filename(model.arquivo))
            try:
                url = fazer_upload(
                    caminho_temp,
                    pasta=f'osean/produtos/{model.produto_id}'
                )
                model.arquivo = url
            finally:
                if os.path.exists(caminho_temp):
                    os.remove(caminho_temp)

    column_formatters = {
        'arquivo': lambda v, c, m, p: Markup(
            f'<img src="{m.arquivo}" style="max-height:100px;">'
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
    form_excluded_columns = ('vendas',)  # remove do formulário de edição
    column_list = ('nome', 'preco', 'vendas', 'novidade', 'escolha_do_mes')  # exibe como leitura
    column_labels = {
        'preco': 'Preço',
        'descricao': 'Descrição',
        'novidade': 'Novidades',
        'escolha_do_mes': 'Produto do Mês',
        'producao': 'Tempo de Produção'
    }

    column_descriptions = {
        'vendas': 'Quantia de vendas deste produto',
        'preco': 'Inserir valor usando . para separar o valor dos centavos',
        'novidade': 'Adicionar este produto à seção de novidades',
        'escolha_do_mes': 'Selecionar este produto como Escolha do Mês',
        'peso': 'Peso do produto em quilogramas',
        'altura': 'Altura do pacote em centímetros',
        'largura': 'Largura do pacote em centímetros',
        'comprimento': 'Comprimento do pacote em centímetros',
        'producao': 'Prazo para que o item seja enviado'
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
            f'<img src="{url_for("static", filename=f"uploads/{m.id}/{m.capa}")}" style="max-height:100px;">'
        ) if m.imagem else ''
    }

    def after_model_change(self, form, model, is_created):
        """Processa e envia para o Cloudinary as fotos inline do Produto.

        Executado após o commit, quando ``model.id`` já está disponível.
        Percorre as fotos do produto, faz upload das que ainda são caminhos
        locais (não começam com 'http') e atualiza o campo ``foto.arquivo``
        com a URL retornada pelo Cloudinary.

        :param form: Formulário submetido.
        :param model: Instância de Produto salva.
        :param is_created: True se o produto está sendo criado.
        """
        for foto in model.fotos:
            # Já é uma URL do Cloudinary, não precisa processar
            if foto.arquivo.startswith('http'):
                continue

            caminho_temp = os.path.join(BASE_UPLOAD, foto.arquivo)
            if not os.path.exists(caminho_temp):
                continue

            try:
                url = fazer_upload(
                    caminho_temp,
                    pasta=f'osean/produtos/{model.id}'
                )
                foto.arquivo = url
            finally:
                if os.path.exists(caminho_temp):
                    os.remove(caminho_temp)

        db.session.commit()


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
    automático, conversão para WebP e renderização de preview na listagem.

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
        """Faz upload do banner para o Cloudinary após salvar o Carrossel.

        :param form: Formulário submetido com os dados do upload.
        :param model: Instância de Carrossel sendo criada ou editada.
        :param is_created: True se o model está sendo criado.
        """
        if form.arquivo.data:
            file = form.arquivo.data
            file.stream.seek(0)
            nome = secure_filename(file.filename)
            caminho_temp = os.path.join(BASE_UPLOAD, nome)
            file.save(caminho_temp)

            try:
                url = fazer_upload(caminho_temp, pasta='osean/carrossel')
                model.arquivo = url
            finally:
                if os.path.exists(caminho_temp):
                    os.remove(caminho_temp)

    column_formatters = {
        'arquivo': lambda v, c, m, p: Markup(
            f'<img src="{m.arquivo}" style="max-height:100px;">'
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


class PedidoAdmin(BaseAdmin):
    can_create = False
    can_edit = True

    column_list = (
        'id',
        'data_criacao',
        'status',
        'nome_usuario',
        'email_usuario',
        'metodo_envio',
        'valor_frete',
        'prazo_envio',
        'endereco',
        'total_pedido',
        'itens_comprados',
    )

    column_labels = {
        'id': 'Pedido',
        'data_criacao': 'Data',
        'status': 'Status',
        'nome_usuario': 'Cliente',
        'email_usuario': 'Email',
        'metodo_envio': 'Envio',
        'valor_frete': 'Frete (R$)',
        'prazo_envio': 'Prazo (dias)',
        'endereco': 'Endereço',
        'total_pedido': 'Total (R$)',
        'itens_comprados': 'Itens',
    }

    # Largura máxima das colunas em pixels
    column_display_pk = True
    column_filters = ('status', 'data_criacao')
    column_searchable_list = ('id',)

    column_formatters = {
        'nome_usuario': lambda v, c, m, p: (
            m.usuario.nome + ' ' + m.usuario.sobrenome if m.usuario else 'Removido'
        ),

        'email_usuario': lambda v, c, m, p: (
            m.usuario.email if m.usuario else '—'
        ),

        # Data formatada: 23/02/2026 14:30
        'data_criacao': lambda v, c, m, p: (
            m.data_criacao.strftime('%d/%m/%Y')
            if m.data_criacao else '—'
        ),

        # Status com badge colorido
        'status': lambda v, c, m, p: Markup(
            f'<span style="'
            f'background:{"#28a745" if m.status == "pago" else "#ffc107" if m.status == "pendente" else "#dc3545"};'
            f'color:white; padding:2px 8px; border-radius:4px; font-size:0.85em;">'
            f'{m.status}</span>'
        ),

        # Endereço compacto em duas linhas
        'endereco': lambda v, c, m, p: Markup(
            f'<small>{m.rua}, {m.numero}<br>{m.cidade} — {m.cep}</small>'
            if m.rua else '—'
        ),

        # Frete formatado
        'valor_frete': lambda v, c, m, p: (
            f'R$ {m.valor_frete:.2f}' if m.valor_frete else '—'
        ),

        # Total formatado
        'total_pedido': lambda v, c, m, p: (
            f'R$ {m.total_pedido:.2f}' if m.total_pedido else '—'
        ),

        # Itens em lista compacta
        'itens_comprados': lambda v, c, m, p: Markup(
            '<div style="min-width:300px; white-space:normal;">'
            '<small>' + '<br>'.join(
                f'{item.quantidade}x {item.nome} (ID: {item.produto_id})'
                for item in m.itens
            ) + '</small>'
                '</div>'
            if m.itens else '—'
        ),
    }


class HomeMenuLink(MenuLink):
    """Link de navegação para a página inicial exibido no painel do Flask-Admin.

    Estende :class:`flask_admin.menu.MenuLink` para gerar dinamicamente
    a URL da página inicial usando ``url_for``, evitando URLs fixas e
    mantendo compatibilidade com qualquer prefixo de rota configurado
    na aplicação.

    Registrado no painel com::

        admin.add_link(HomeMenuLink(name='Voltar ao Site'))

    O link aparecerá na barra de navegação superior do painel administrativo.

    .. note::
        Substitua ``'geral.home'`` pelo nome correto da rota
        da página inicial da sua aplicação.
    """

    def get_url(self):
        """Retorna a URL da página inicial da aplicação.

        Sobrescreve :meth:`MenuLink.get_url` para resolver a URL
        dinamicamente via ``url_for`` no momento da requisição.

        :return: URL absoluta da rota ``geral.home``.
        """
        return url_for('geral.home')


class CupomAdmin(BaseAdmin):
    """
    View administrativa para gerenciamento de cupons de desconto.

    Estende BaseAdmin com configurações específicas para o model Cupom.
    Exibe código, percentual de desconto e flag de primeira compra na
    listagem, com suporte a busca pelo código e filtro por tipo.

    Attributes:
        column_list (tuple): Colunas exibidas: código, desconto e primeira_compra.
        column_labels (dict): Traduz os campos para português.
        column_searchable_list (tuple): Habilita busca pelo campo 'codigo'.
        column_filters (tuple): Habilita filtro pelos campos 'desconto' e
            'primeira_compra'.
        form_columns (tuple): Campos disponíveis no formulário de criação/edição.

    Example:
        admin.add_view(CupomAdmin(Cupom, db.session, name='Cupons'))
    """

    column_list = ('codigo', 'desconto', 'primeira_compra')
    column_labels = {
        'codigo': 'Código',
        'desconto': 'Desconto (%)',
        'primeira_compra': 'Apenas 1ª Compra',
    }
    column_searchable_list = ('codigo',)
    column_filters = ('desconto', 'primeira_compra')
    form_columns = ('codigo', 'desconto', 'primeira_compra')