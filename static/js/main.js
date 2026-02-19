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
                    <label>
                        <input type="radio" name="envio" value="${opcao.nome}">
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

document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("select-endereco-editar");

    if (!select) return;

    const userId = select.dataset.userId;

    function carregarEndereco(enderecoId) {
        fetch(`/gerenciar/${userId}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ endereco_id: enderecoId })
        })
        .then(r => r.json())
        .then(data => {
            document.getElementById("apelido").value = data.apelido;
            document.getElementById("cep").value = data.cep;
            document.getElementById("cidade").value = data.cidade;
            document.getElementById("estado").value = data.estado;
            document.getElementById("rua").value = data.rua;
            document.getElementById("numero").value = data.numero;
            document.getElementById("complemento").value = data.complemento;
        });
    }

    // 🔹 ao mudar manualmente
    select.addEventListener("change", function () {
        carregarEndereco(this.value);
    });

    // 🔹 ao carregar a página
    if (select.options.length > 0) {
        select.selectedIndex = 0;
        carregarEndereco(select.value);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const selectEditar = document.getElementById("select-endereco-editar");
    const btnDeletar = document.getElementById("btn-deletar-endereco");

    if (!selectEditar || !btnDeletar) return;

    function atualizarLinkDeletar() {
        const enderecoId = selectEditar.value;
        // Aqui você monta a URL manualmente ou usa uma variável global do Flask
        // Exemplo: /deletar-endereco/5
        btnDeletar.href = `/deletar-endereco/${enderecoId}`;
    }

    // Atualiza ao mudar a seleção
    selectEditar.addEventListener("change", atualizarLinkDeletar);

    // Atualiza ao carregar a página para o primeiro item da lista
    atualizarLinkDeletar();
});