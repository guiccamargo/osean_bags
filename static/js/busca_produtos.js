/**
 * @fileoverview Módulo de busca dinâmica de produtos.
 *
 * Realiza requisições à rota `/produtos/buscar` enquanto o usuário digita,
 * atualizando a listagem de produtos sem recarregar a página.
 *
 * Dependências:
 * - Elemento `<div id="lista-produtos">` presente no DOM.
 * - Rota Flask `/produtos/buscar?busca=<termo>` retornando JSON.
 *
 * Uso no HTML:
 * @example
 * <input type="text" oninput="buscarProdutos(this.value)">
 * <script src="static/js/busca_produtos.js"></script>
 */

let timeout = null;

/**
 * Dispara a busca de produtos com debounce de 300ms.
 *
 * Aguarda o usuário parar de digitar antes de realizar a requisição,
 * evitando chamadas desnecessárias à API a cada tecla pressionada.
 *
 * @param {string} termo - Texto digitado pelo usuário no campo de busca.
 */
function buscarProdutos(termo) {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        fetch(`/produtos/buscar?busca=${encodeURIComponent(termo)}`)
            .then(res => res.json())
            .then(produtos => renderizarProdutos(produtos))
            .catch(err => console.error('Erro na busca:', err));
    }, 300);
}

/**
 * Renderiza a lista de produtos no DOM.
 *
 * Substitui o conteúdo de `#lista-produtos` com os cards dos produtos
 * retornados pela API. Exibe uma mensagem caso nenhum produto seja encontrado.
 *
 * @param {Array<{id: number, nome: string, preco: number, imagem: string}>} produtos
 *        Lista de produtos retornada pela rota `/produtos/buscar`.
 */
function renderizarProdutos(produtos) {
    const lista = document.getElementById('lista-produtos');

    if (produtos.length === 0) {
        lista.innerHTML = `
            <div class="col-12 text-center py-5">
                <p class="text-muted">Nenhum produto encontrado.</p>
            </div>`;
        return;
    }

    lista.innerHTML = produtos.map(p => `
    <div class="col-lg-5 col-sm-5 me-3">
        <a href="/produtos/${p.id}" class="text-decoration-none text-dark">
            <div class="card shadow-sm">
                <img class="card-img-top produto-img"
                     src="${p.imagem}"/>
                <hr/>
                <div class="card-body text-center">
                    <h3 class="card-text texto-estilizado">${p.nome}</h3>
                    <h5 class="text-muted">${formatarPreco(p.preco)}</h5>
                </div>
            </div>
        </a>
    </div>
`).join('');
}

/**
 * Formata um valor numérico como moeda brasileira (BRL).
 *
 * @param {number} preco - Valor a ser formatado.
 * @returns {string} Valor formatado, ex: `R$ 99,90`.
 */
function formatarPreco(preco) {
    return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
/**
 * Inicializa a listagem ao carregar a página.
 * Chama buscarProdutos com termo vazio para exibir todos os produtos.
 */
document.addEventListener('DOMContentLoaded', () => {
    buscarProdutos('');
});