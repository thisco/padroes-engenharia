// Filtro por coleção da página da trilha (spec da trilha, R9). Sem script, todos os cartões
// aparecem e os botões ficam ocultos; o script mostra os botões e liga o filtro.
(function () {
  const botoes = document.querySelectorAll("[data-colecao-filtro]");
  if (!botoes.length) return;
  const ativas = new Set(Array.from(botoes, (b) => b.dataset.colecaoFiltro));
  function aplicar() {
    document.querySelectorAll(".tr-opcoes").forEach((caixa) => {
      let visiveis = 0;
      caixa.querySelectorAll("[data-colecao]").forEach((cartao) => {
        const mostrar = ativas.has(cartao.dataset.colecao);
        cartao.hidden = !mostrar;
        if (mostrar) visiveis += 1;
      });
      const vazio = caixa.querySelector(".tr-vazio");
      if (vazio) vazio.hidden = visiveis > 0;
    });
  }
  botoes.forEach((botao) => {
    botao.hidden = false;
    botao.addEventListener("click", () => {
      const colecao = botao.dataset.colecaoFiltro;
      if (ativas.has(colecao)) ativas.delete(colecao);
      else ativas.add(colecao);
      botao.setAttribute("aria-pressed", String(ativas.has(colecao)));
      aplicar();
    });
  });
})();
