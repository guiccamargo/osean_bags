from flask_login import current_user

from funcoes import soma_itens, acessar_inicial


def renderizar_header(usuario) -> dict:
    """
    Gera o dicionário de contexto para renderização do header da aplicação.

    Coleta informações do usuário atual — autenticação, status de administrador,
    total de itens no carrinho e inicial do nome — e as retorna em um dicionário
    para ser desempacotado nos templates via **renderizar_header(current_user).

    Args:
        usuario: Objeto do usuário atual, geralmente current_user do Flask-Login.
                 Pode ser um usuário autenticado ou um AnonymousUser.

    Returns:
        dict: Dicionário com as seguintes chaves:
            - logged_in (bool): True se o usuário estiver autenticado.
            - total_items (int | None): Total de itens no carrinho do usuário
              autenticado, ou None se não estiver logado.
            - admin (bool): True se o usuário for administrador, False caso contrário.
            - id_usuario (int | None): ID do usuário autenticado, ou None se
              não estiver logado.
            - inicial_nome (str | None): Inicial do nome do usuário autenticado
              em maiúsculo, ou None se não estiver logado.

    Note:
        Os blocos try/except tratam AttributeError para compatibilidade com o
        AnonymousUser do Flask-Login, que não possui os atributos is_authenticated
        e is_admin().

    Example:
        return render_template('index.html', **renderizar_header(current_user))
    warning::
        Os blocos try/except capturam AttributeError silenciosamente.
        Se usuario não for uma instância de Usuario ou AnonymousUser
        do Flask-Login, o comportamento pode ser inesperado.

    """
    try:
        logged_in = usuario.is_authenticated
    except AttributeError:
        logged_in = False

    try:
        is_admin = usuario.is_admin()
    except AttributeError:
        is_admin = False

    if usuario.is_authenticated:
        soma = soma_itens(usuario.id)
    else:
        soma = None

    if logged_in:
        id_usuario_atual = current_user.id
    else:
        id_usuario_atual = None

    if logged_in:
        inicial_nome = acessar_inicial(usuario.id)
    else:
        inicial_nome = None

    return {
        'logged_in': logged_in,
        'total_items': soma,
        'admin': is_admin,
        'id_usuario': id_usuario_atual,
        'inicial_nome': inicial_nome,
    }
