// Página da trilha (delta v3, R8' e R9'; mockup trilha-v3.html). Sem script, a página fica
// completa: todos os cartões aparecem, a camada de trilha fica desligada e os botões nascem com
// `hidden`. O script só lê os `data-*` gerados no servidor e não faz requisição de rede.
(function () {
  "use strict";

  // 1. O que só funciona com script aparece.
  document.querySelectorAll("[data-tr-js], [data-tr-js] button, [data-trilha]").forEach((el) => {
    el.hidden = false;
  });

  // 2. Filtro por coleção e "Mostrar complementos". Cartão de coleção sem botão nunca some.
  const botoesColecao = Array.from(document.querySelectorAll("[data-colecao-filtro]"));
  const conhecidas = new Set(botoesColecao.map((b) => b.dataset.colecaoFiltro));
  const ativas = new Set(conhecidas);
  let comComplementos = true;

  function filtrar() {
    document.querySelectorAll(".tr-caminhos").forEach((caixa) => {
      let visiveis = 0;
      caixa.querySelectorAll(".tr-caminho").forEach((cartao) => {
        const colecao = cartao.dataset.colecao;
        const mostrar =
          (!conhecidas.has(colecao) || ativas.has(colecao)) &&
          (comComplementos || cartao.dataset.papel !== "complemento");
        cartao.hidden = !mostrar;
        if (mostrar) visiveis += 1;
      });
      const vazio = caixa.querySelector('.tr-vazio-passo[data-vazio="filtro"]');
      if (vazio) vazio.hidden = visiveis > 0;
    });
  }

  botoesColecao.forEach((botao) => {
    botao.addEventListener("click", () => {
      const colecao = botao.dataset.colecaoFiltro;
      if (ativas.has(colecao)) ativas.delete(colecao);
      else ativas.add(colecao);
      botao.setAttribute("aria-pressed", String(ativas.has(colecao)));
      filtrar();
    });
  });
  const botaoComplementos = document.querySelector("[data-complementos]");
  if (botaoComplementos) {
    botaoComplementos.addEventListener("click", () => {
      comComplementos = !comComplementos;
      botaoComplementos.setAttribute("aria-pressed", String(comComplementos));
      filtrar();
    });
  }

  // 3. A camada de trilha no ciclo: pontos cobertos, nome do caminho em cada passo e um traço
  // por etapa ligando os passos cobertos (nunca no laço, como no mockup).
  const grade = document.getElementById("ciclo");
  if (!grade) return;
  const escolha = Array.from(document.querySelectorAll(".ciclo-escolha [data-trilha]"));
  const resumo = document.querySelector(".ciclo-resumo");
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("class", "ciclo-trilho");
  svg.setAttribute("aria-hidden", "true");
  grade.append(svg);
  let atual = "";

  function desenhar() {
    svg.replaceChildren();
    if (!atual) return;
    const base = grade.getBoundingClientRect();
    svg.setAttribute("viewBox", `0 0 ${base.width} ${base.height}`);
    grade.querySelectorAll(".ciclo-col").forEach((coluna) => {
      const pontos = Array.from(coluna.querySelectorAll("li.coberto .ciclo-pt")).map((pt) => {
        const r = pt.getBoundingClientRect();
        return `${r.left - base.left + r.width / 2},${r.top - base.top + r.height / 2}`;
      });
      if (pontos.length > 1) {
        const linha = document.createElementNS(NS, "polyline");
        linha.setAttribute("points", pontos.join(" "));
        svg.append(linha);
      }
    });
  }

  function mostrar(id) {
    atual = id || "";
    const botao = escolha.find((b) => b.dataset.trilha === atual);
    const cobertos = new Set(atual && botao ? botao.dataset.passos.split(" ") : []);
    grade.classList.toggle("com-trilha", Boolean(atual));
    grade.querySelectorAll("li[data-passo]").forEach((li) => {
      const coberto = cobertos.has(li.dataset.passo);
      li.classList.toggle("coberto", coberto);
      li.querySelector(".ciclo-sk").textContent = coberto
        ? li.getAttribute("data-skill-" + atual) || ""
        : "";
    });
    escolha.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.trilha === atual)));
    if (resumo) resumo.textContent = atual && botao ? botao.dataset.resumo : "";
    desenhar();
  }

  escolha.forEach((b) => b.addEventListener("click", () => mostrar(b.dataset.trilha)));
  document.querySelectorAll(".tr-ver-ciclo[data-trilha]").forEach((b) => {
    b.addEventListener("click", () => {
      mostrar(b.dataset.trilha);
      const calmo = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      document.getElementById("mapa").scrollIntoView({ behavior: calmo ? "auto" : "smooth" });
    });
  });
  window.addEventListener("resize", desenhar);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(desenhar);
})();
