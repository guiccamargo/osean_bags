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