/**
 * @fileoverview Módulo de atualização dinâmica do carrinho de compras.
 *
 * Realiza requisições à rota `/carrinho/atualizar` ao alterar a quantidade
 * de um item, atualizando o subtotal do item e o total geral do carrinho
 * sem recarregar a página.
 *
 * Dependências:
 * - Elementos `<p id="total-{productId}">` para o subtotal de cada item.
 * - Elemento `<p id="total-carrinho">` para o total geral.
 * - Rota Flask `/carrinho/atualizar/<user_id>/<product_id>?quantidade=<n>`
 *   retornando `{ novo_total, total_carrinho }`.
 */

/**
 * Atualiza a quantidade de um item do carrinho via requisição GET.
 *
 * @param {number} userId - ID do usuário atual.
 * @param {number} productId - ID do produto a ser atualizado.
 * @param {number} quantidade - Nova quantidade informada pelo usuário.
 *
 * @example
 * onchange="atualizarQuantidade({{ current_user['id'] }}, {{ product['id'] }}, this.value)"
 */
function atualizarQuantidade(userId, productId, quantidade) {
    const url = `/carrinho/atualizar/${userId}/${productId}?quantidade=${quantidade}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const totalItem = document.getElementById(`total-${productId}`);
            if (totalItem) {
                totalItem.textContent = `Total ${formatarPreco(data.novo_total)}`;
            }

            const totalCarrinho = document.getElementById('total-carrinho');
            if (totalCarrinho) {
                totalCarrinho.textContent = formatarPreco(data.total_carrinho);
            }
        })
        .catch(err => console.error('Erro ao atualizar quantidade:', err));
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