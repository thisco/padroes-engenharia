// Busca offline do portal (spec §7.2): carrega busca.json e filtra por trecho, sem acento e sem
// caixa. Também liga os filtros da página de referências. JS puro, sem dependência externa;
// o texto vindo do índice entra no DOM só por textContent.
(function () {
  "use strict";

  function normalizar(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  function iniciarBusca() {
    var campo = document.getElementById("busca");
    var lista = document.getElementById("busca-resultados");
    if (!campo || !lista) {
      return;
    }
    var raiz = campo.getAttribute("data-raiz") || "";
    var indice = null;

    function carregar() {
      if (indice) {
        return Promise.resolve(indice);
      }
      return fetch(campo.getAttribute("data-indice"))
        .then(function (resposta) {
          return resposta.json();
        })
        .then(function (itens) {
          indice = itens.map(function (item) {
            item.chave = normalizar([item.titulo, item.descricao, item.secao, item.palavras || ""].join(" "));
            return item;
          });
          return indice;
        });
    }

    function mostrar(itens) {
      lista.textContent = "";
      itens.slice(0, 20).forEach(function (item) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        var detalhe = document.createElement("small");
        a.href = raiz + item.url;
        a.textContent = item.titulo;
        detalhe.textContent = item.secao + (item.descricao ? " · " + item.descricao : "");
        a.appendChild(detalhe);
        li.appendChild(a);
        lista.appendChild(li);
      });
    }

    function avisar(texto) {
      var li = document.createElement("li");
      li.textContent = texto;
      lista.textContent = "";
      lista.appendChild(li);
    }

    campo.addEventListener("input", function () {
      var termo = normalizar(campo.value.trim());
      if (termo.length < 2) {
        lista.textContent = "";
        return;
      }
      carregar()
        .then(function (itens) {
          var achados = itens.filter(function (item) {
            return item.chave.indexOf(termo) !== -1;
          });
          if (achados.length) {
            mostrar(achados);
          } else {
            avisar("Nada encontrado.");
          }
        })
        .catch(function () {
          avisar("Busca indisponível fora de um servidor: rode python -m http.server -d public.");
        });
    });

    campo.addEventListener("keydown", function (evento) {
      if (evento.key === "Escape") {
        campo.value = "";
        lista.textContent = "";
      }
    });
  }

  // Filtros de tabela: `.filtros[data-alvo]` diz quais linhas filtrar; cada select diz o atributo
  // `data-<filtro>` da linha a comparar (valor vazio = todos).
  function iniciarFiltros() {
    var caixas = Array.prototype.slice.call(document.querySelectorAll(".filtros[data-alvo]"));
    var antiga = document.getElementById("filtros-referencias");
    if (antiga) {
      caixas.push(antiga);
    }
    caixas.forEach(ligarFiltros);
  }

  function ligarFiltros(caixa) {
    var alvo = caixa.getAttribute("data-alvo") || "tr[data-tipo]";
    caixa.hidden = false;
    var seletores = Array.prototype.slice.call(caixa.querySelectorAll("select[data-filtro]"));

    function aplicar() {
      document.querySelectorAll(alvo).forEach(function (linha) {
        linha.hidden = !seletores.every(function (seletor) {
          var valor = seletor.value;
          var dado = linha.getAttribute("data-" + seletor.getAttribute("data-filtro")) || "";
          return !valor || dado.split(" ").indexOf(valor) !== -1;
        });
      });
    }

    seletores.forEach(function (seletor) {
      seletor.addEventListener("change", aplicar);
    });
  }

  // Atalho "/" foca a busca; abaixo de 900px o menu começa fechado.
  function iniciarMenu() {
    var campo = document.getElementById("busca");
    var menu = document.querySelector("details.menu");
    if (menu && window.matchMedia("(max-width: 900px)").matches) {
      menu.open = false;
    }
    document.addEventListener("keydown", function (evento) {
      var alvo = evento.target;
      var digitando = alvo && (alvo.tagName === "INPUT" || alvo.tagName === "TEXTAREA" || alvo.tagName === "SELECT");
      if (evento.key === "/" && campo && !digitando && !evento.ctrlKey && !evento.metaKey) {
        evento.preventDefault();
        campo.focus();
      }
    });
  }

  // Escreve `texto` na área de transferência: Clipboard API quando existe e, senão (página fora de
  // contexto seguro, navegador antigo), um textarea temporário com `execCommand("copy")`.
  function copiarTexto(texto, feito) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(feito, function () {
        copiarPorSelecao(texto, feito);
      });
      return;
    }
    copiarPorSelecao(texto, feito);
  }

  function copiarPorSelecao(texto, feito) {
    var area = document.createElement("textarea");
    area.value = texto;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.top = "-1000px";
    document.body.appendChild(area);
    area.select();
    var deu = false;
    try {
      deu = document.execCommand("copy");
    } catch (erro) {
      deu = false;
    }
    document.body.removeChild(area);
    if (deu) {
      feito();
    }
  }

  // Botão Copiar (bloco de código e prompt): só escreve na área de transferência, nunca lê.
  function iniciarCopiar() {
    document.querySelectorAll("[data-copiar]").forEach(function (botao) {
      var texto = botao.textContent;
      botao.addEventListener("click", function () {
        var raiz = botao.closest("figure") || botao.closest(".bloco") || botao.parentElement;
        var codigo = raiz ? raiz.querySelector("pre") : null;
        if (!codigo) {
          return;
        }
        copiarTexto(codigo.textContent, function () {
          botao.textContent = "Copiado";
          setTimeout(function () {
            botao.textContent = texto;
          }, 2000);
        });
      });
    });
  }

  // Abas por harness: `[data-abas]` é um tablist dentro de `section.passo`; os painéis são
  // `.painel[data-harness]` da mesma seção. A escolha vale para todos os grupos da página e fica
  // guardada no navegador (se ele deixar).
  function iniciarAbas() {
    var grupos = Array.prototype.slice.call(document.querySelectorAll("[data-abas]"));
    if (!grupos.length) {
      return;
    }

    function aplicar(id) {
      grupos.forEach(function (grupo) {
        var passo = grupo.closest("section.passo") || grupo.parentElement;
        grupo.querySelectorAll('[role="tab"][data-harness]').forEach(function (aba) {
          var ativa = aba.getAttribute("data-harness") === id;
          aba.setAttribute("aria-selected", ativa ? "true" : "false");
          aba.tabIndex = ativa ? 0 : -1;
        });
        passo.querySelectorAll('.painel[role="tabpanel"][data-harness]').forEach(function (painel) {
          painel.hidden = painel.getAttribute("data-harness") !== id;
        });
      });
    }

    function existe(id) {
      return !!id && grupos.some(function (grupo) {
        return !!grupo.querySelector('[role="tab"][data-harness="' + id + '"]');
      });
    }

    grupos.forEach(function (grupo) {
      grupo.querySelectorAll('[role="tab"][data-harness]').forEach(function (aba) {
        aba.addEventListener("click", function () {
          var id = aba.getAttribute("data-harness");
          aplicar(id);
          try {
            localStorage.setItem("harness", id);
          } catch (erro) {
            /* navegação privada ou armazenamento bloqueado: a escolha só não persiste */
          }
        });
      });
    });

    var guardado = null;
    try {
      guardado = localStorage.getItem("harness");
    } catch (erro) {
      guardado = null;
    }
    if (existe(guardado)) {
      aplicar(guardado);
      return;
    }
    grupos.forEach(function (grupo) {
      var primeira = grupo.querySelector('[role="tab"][data-harness]');
      if (primeira) {
        aplicar(primeira.getAttribute("data-harness"));
      }
    });
  }

  // Passar o mouse ou o foco numa linha de peça acende a peça no desenho do ninho.
  function iniciarPecas() {
    document.querySelectorAll("li[data-peca]").forEach(function (linha) {
      var peca = linha.getAttribute("data-peca");
      function marcar(ligar) {
        document.querySelectorAll('.ninho [data-peca="' + peca + '"]').forEach(function (caixa) {
          caixa.classList.toggle("alvo-hover", ligar);
        });
      }
      linha.addEventListener("mouseenter", function () { marcar(true); });
      linha.addEventListener("mouseleave", function () { marcar(false); });
      linha.addEventListener("focusin", function () { marcar(true); });
      linha.addEventListener("focusout", function () { marcar(false); });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    iniciarPecas();
    iniciarBusca();
    iniciarFiltros();
    iniciarMenu();
    iniciarCopiar();
    iniciarAbas();
  });
})();
