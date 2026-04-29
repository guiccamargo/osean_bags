"""
Módulo de integração com o Cloudinary para armazenamento de imagens.

Substitui o salvamento local em static/uploads/, que é incompatível com
ambientes de deploy efêmeros como o Render.com, onde o filesystem é
resetado a cada novo deploy.

Funções principais:
    - fazer_upload: envia uma imagem e retorna a URL pública.
    - deletar_imagem: remove uma imagem pelo seu public_id.
    - public_id_from_url: extrai o public_id de uma URL do Cloudinary.
"""

import os

import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

from PIL import Image
import tempfile


def comprimir_imagem(arquivo):
    img = Image.open(arquivo)

    # Redimensiona (mantém proporção)
    img.thumbnail((1600, 1600))

    temp = tempfile.NamedTemporaryFile(suffix=".webp", delete=False)

    img.save(
        temp.name,
        format="WEBP",
        quality=80,  # ajuste aqui (60–85 ideal)
        optimize=True
    )

    return temp.name


cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

import cloudinary
import cloudinary.uploader
import cloudinary.utils


def fazer_upload(arquivo, pasta='osean', public_id=None):
    arquivo_comprimido = comprimir_imagem(arquivo)

    opcoes = {
        'folder': pasta,
        'resource_type': 'image'
    }

    if public_id:
        opcoes['public_id'] = public_id

    resultado = cloudinary.uploader.upload(arquivo_comprimido, **opcoes)

    url_otimizada, _ = cloudinary.utils.cloudinary_url(
        resultado['public_id'],
        fetch_format='auto',
        quality='auto',
        secure=True
    )

    return url_otimizada

def deletar_imagem(public_id: str) -> dict:
    """Remove uma imagem do Cloudinary pelo seu public_id.

    :param public_id: Identificador público da imagem no Cloudinary,
                      no formato ``'pasta/nome_arquivo'`` (sem extensão).
    :return: Dicionário com a resposta da API do Cloudinary.

    Exemplo::

        public_id = public_id_from_url(foto.arquivo)
        deletar_imagem(public_id)
    """
    return cloudinary.uploader.destroy(public_id)


def public_id_from_url(url: str) -> str:
    """Extrai o public_id de uma URL do Cloudinary.

    Útil para deletar imagens a partir da URL armazenada no banco de dados.

    :param url: URL completa da imagem no Cloudinary.
                Exemplo: ``'https://res.cloudinary.com/cloud/image/upload/v123/osean/42/foto.webp'``
    :return: public_id sem extensão.
             Exemplo: ``'osean/42/foto'``

    Exemplo::

        public_id = public_id_from_url(foto.arquivo)
        deletar_imagem(public_id)
    """
    # Remove protocolo e domínio, isola o caminho após /upload/vXXXXX/
    partes = url.split('/upload/')
    if len(partes) < 2:
        return url
    caminho = partes[1]
    # Remove o prefixo de versão (ex: v1234567890/)
    if caminho.startswith('v') and '/' in caminho:
        caminho = caminho.split('/', 1)[1]
    # Remove a extensão
    return os.path.splitext(caminho)[0]
