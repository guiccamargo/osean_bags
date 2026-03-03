document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("select-endereco");
    const divOpcoes = document.getElementById("opcoes-envio");

    if (!select || !divOpcoes) return;

    function carregarFrete(enderecoId) {
        if (!enderecoId) return;

        divOpcoes.innerHTML = "<em>Calculando frete...</em>";

        fetch(URL_CALCULAR_FRETE, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ endereco_id: enderecoId })
        })
        .then(r => r.ok ? r.json() : Promise.reject("Erro no servidor"))
        .then(opcoes => {
            divOpcoes.innerHTML = "";

            if (opcoes.length === 0) {
                divOpcoes.textContent = "Nenhuma opção de envio disponível.";
                return;
            }

            opcoes.forEach(opcao => {
                const linha = document.createElement("div");
                linha.className = "opcao-item";

                // Usando template string mas com cuidado ou criando elementos
                linha.innerHTML = `
                    <label class="texto-estilizado">
                        <input type="radio" name="envio" value="${opcao.nome}|${opcao.preco}|${opcao.prazo}" required>
                        <strong></strong> – R$ ${parseFloat(opcao.preco).toFixed(2)} – ${opcao.prazo} dias
                    </label>
                `;
                // Insere o nome como texto puro para evitar XSS
                linha.querySelector("strong").textContent = opcao.nome;
                divOpcoes.appendChild(linha);
            });
        })
        .catch(err => {
            divOpcoes.innerHTML = "<span style='color:red'>Erro ao buscar frete. Tente novamente.</span>";
        });
    }

    select.addEventListener("change", (e) => carregarFrete(e.target.value));

    if (select.value) carregarFrete(select.value);
});
