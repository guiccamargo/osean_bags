"""
Módulo centralizado de configurações SEO da aplicação.

Define metadados (título, descrição, Open Graph) para cada página,
utilizados nos templates via variável global do Jinja2.
"""

SEO = {
    'home': {
        'title': 'Osean Bags | Bolsas Artesanais',
        'description': 'Descubra bolsas artesanais únicas da Osean Bags. Qualidade e estilo em cada peça.',
        'og_image': '/static/logo.png',
    },
    'produtos': {
        'title': 'Produtos | Osean Bags',
        'description': 'Explore nossa coleção completa de bolsas artesanais.',
        'og_image': '/static/uploads/banner_2.PNG',
    },
    'sobre': {
        'title': 'Sobre Nós | Osean Bags',
        'description': 'Conheça a história da Osean Bags e nossa paixão por bolsas artesanais.',
        'og_image': '/static/uploads/banner_1.jpeg',
    },
}