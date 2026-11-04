// Testes de comportamento de portal/tema/busca.js com um DOM falso mínimo (sem dependência).
// Uso: node teste_busca.js <caminho do busca.js> <caso>
"use strict";
const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

const [, , caminho, caso] = process.argv;

class No {
  constructor(tag, attrs, doc) {
    this.tag = tag;
    this.attrs = Object.assign({}, attrs || {});
    this.filhos = [];
    this.pai = null;
    this.doc = doc;
    this.ouvintes = {};
    this.hidden = false;
    this.style = {};
    this.tabIndex = 0;
    this.value = "";
    this._texto = "";
  }
  add(...filhos) {
    filhos.forEach((f) => { f.pai = this; this.filhos.push(f); });
    return this;
  }
  get textContent() {
    return this._texto + this.filhos.map((f) => f.textContent).join("");
  }
  set textContent(v) { this._texto = String(v); this.filhos = []; }
  getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; }
  setAttribute(n, v) { this.attrs[n] = String(v); }
  addEventListener(t, f) { (this.ouvintes[t] = this.ouvintes[t] || []).push(f); }
  disparar(t) { (this.ouvintes[t] || []).forEach((f) => f({ target: this })); }
  clicar() { this.disparar("click"); }
  focus() { this.doc.activeElement = this; }
  select() { this.selecionado = true; this.doc.activeElement = this; }
  appendChild(f) { this.add(f); return f; }
  removeChild(f) { this.filhos = this.filhos.filter((x) => x !== f); f.pai = null; return f; }
  casa(seletor) {
    const m = seletor.match(/^([a-z0-9]*)((?:[.#][\w-]+|\[[\w-]+(?:="[^"]*")?\])*)$/i);
    if (!m) throw new Error("seletor não suportado: " + seletor);
    if (m[1] && m[1] !== this.tag) return false;
    const partes = m[2].match(/[.#][\w-]+|\[[^\]]+\]/g) || [];
    return partes.every((p) => {
      if (p[0] === ".") return (this.attrs.class || "").split(" ").includes(p.slice(1));
      if (p[0] === "#") return this.attrs.id === p.slice(1);
      const [n, v] = p.slice(1, -1).split("=");
      if (!(n in this.attrs)) return false;
      return v === undefined || this.attrs[n] === v.replace(/"/g, "");
    });
  }
  descendentes() {
    return this.filhos.reduce((a, f) => a.concat([f], f.descendentes()), []);
  }
  querySelectorAll(seletor) { return this.descendentes().filter((n) => n.casa(seletor)); }
  querySelector(seletor) { return this.querySelectorAll(seletor)[0] || null; }
  closest(seletor) {
    for (let n = this; n; n = n.pai) if (n.casa(seletor)) return n;
    return null;
  }
  get parentElement() { return this.pai; }
}

function criarAmbiente(opcoes) {
  const doc = { activeElement: null, execucoes: [] };
  const raiz = new No("html", {}, doc);
  const corpo = new No("body", {}, doc);
  raiz.add(corpo);
  doc.body = corpo;
  doc.createElement = (tag) => new No(tag, {}, doc);
  doc.querySelectorAll = (s) => raiz.querySelectorAll(s);
  doc.querySelector = (s) => raiz.querySelector(s);
  doc.getElementById = (id) => raiz.querySelector("#" + id);
  doc.addEventListener = () => {};
  doc.execCommand = (cmd) => {
    doc.execucoes.push({ cmd, areaPresente: corpo.querySelector("textarea") !== null });
    return opcoes.execCommand !== false;
  };
  const armazem = {};
  const localStorage = {
    getItem(k) { if (opcoes.storageLanca) throw new Error("bloqueado"); return k in armazem ? armazem[k] : null; },
    setItem(k, v) { if (opcoes.storageLanca) throw new Error("bloqueado"); armazem[k] = String(v); },
  };
  const temporizadores = [];
  const contexto = {
    document: doc,
    navigator: {},
    localStorage,
    setTimeout: (f) => temporizadores.push(f),
    console,
    __portalTeste: true,
  };
  contexto.window = contexto;
  const sel = { faixas: opcoes.faixa ? [opcoes.faixa] : [], rangeCount: opcoes.faixa ? 1 : 0 };
  sel.getRangeAt = (i) => sel.faixas[i];
  sel.removeAllRanges = () => { sel.faixas = []; sel.rangeCount = 0; };
  sel.addRange = (f) => { sel.faixas.push(f); sel.rangeCount = sel.faixas.length; };
  contexto.getSelection = () => sel;
  vm.createContext(contexto);
  vm.runInContext(fs.readFileSync(caminho, "utf8"), contexto);
  return { sel, doc, corpo, contexto, armazem, temporizadores, portal: contexto.__portal, No };
}

const casos = {
  copiar_sem_clipboard_usa_execCommand_e_devolve_foco() {
    const e = criarAmbiente({});
    const botao = new No("button", { "data-copiar": "" }, e.doc);
    e.corpo.add(botao);
    botao.focus();
    let feito = false;
    e.portal.copiarTexto("ls -la", () => { feito = true; });
    assert.deepStrictEqual(e.doc.execucoes, [{ cmd: "copy", areaPresente: true }]);
    assert.strictEqual(e.corpo.querySelector("textarea"), null, "a textarea some");
    assert.strictEqual(e.doc.activeElement, botao, "o foco volta ao botão");
    assert.ok(feito);
  },
  copiar_devolve_a_selecao_da_pessoa() {
    const faixa = { id: "trecho" };
    const e = criarAmbiente({ faixa });
    const botao = new No("button", {}, e.doc);
    e.corpo.add(botao);
    botao.focus();
    e.sel.removeAllRanges();
    e.sel.addRange(faixa);
    e.portal.copiarTexto("x", () => {});
    assert.strictEqual(e.sel.rangeCount, 1);
    assert.strictEqual(e.sel.getRangeAt(0), faixa, "a seleção original volta");
    assert.strictEqual(e.doc.activeElement, botao);
  },
  copiar_que_falha_avisa_no_botao() {
    const e = criarAmbiente({ execCommand: false });
    const figura = new No("figure", {}, e.doc);
    const pre = new No("pre", {}, e.doc);
    pre.textContent = "x";
    const botao = new No("button", { "data-copiar": "" }, e.doc);
    botao.textContent = "Copiar";
    figura.add(pre, botao);
    e.corpo.add(figura);
    e.portal.iniciarCopiar();
    botao.clicar();
    assert.strictEqual(botao.textContent, "Não copiou");
    e.temporizadores.forEach((f) => f());
    assert.strictEqual(botao.textContent, "Copiar");
  },
  abas_com_dois_grupos() {
    const e = criarAmbiente({});
    function passo(harnesses) {
      const sec = new No("section", { class: "passo" }, e.doc);
      const lista = new No("div", { "data-abas": "", role: "tablist" }, e.doc);
      const abas = harnesses.map((h) => new No("button", { role: "tab", "data-harness": h }, e.doc));
      const paineis = harnesses.map((h) => new No("div", { class: "painel", role: "tabpanel", "data-harness": h }, e.doc));
      lista.add(...abas);
      sec.add(lista, ...paineis);
      e.corpo.add(sec);
      return { abas, paineis };
    }
    const a = passo(["claude", "kiro"]);
    const b = passo(["claude", "kiro", "codex"]);
    e.portal.iniciarAbas();
    assert.deepStrictEqual(a.paineis.map((p) => p.hidden), [false, true], "sem guardado: primeira aba");
    a.abas[1].clicar();
    assert.deepStrictEqual(a.paineis.map((p) => p.hidden), [true, false]);
    assert.deepStrictEqual(b.paineis.map((p) => p.hidden), [true, false, true], "vale para todos os grupos");
    assert.strictEqual(a.abas[1].getAttribute("aria-selected"), "true");
    assert.strictEqual(e.armazem.harness, "kiro");
    // grupo misto: só o segundo tem "codex"; o primeiro cai na própria primeira aba
    b.abas[2].clicar();
    assert.deepStrictEqual(b.paineis.map((p) => p.hidden), [true, true, false]);
    assert.deepStrictEqual(a.paineis.map((p) => p.hidden), [false, true]);
  },
  abas_com_harness_guardado_sem_aba_cai_na_primeira() {
    const e = criarAmbiente({});
    e.armazem.harness = "inexistente";
    const sec = new No("section", { class: "passo" }, e.doc);
    const lista = new No("div", { "data-abas": "" }, e.doc);
    const abas = ["claude", "kiro"].map((h) => new No("button", { role: "tab", "data-harness": h }, e.doc));
    const paineis = ["claude", "kiro"].map((h) => new No("div", { class: "painel", role: "tabpanel", "data-harness": h }, e.doc));
    lista.add(...abas);
    sec.add(lista, ...paineis);
    e.corpo.add(sec);
    e.portal.iniciarAbas();
    assert.deepStrictEqual(paineis.map((p) => p.hidden), [false, true]);
  },
  abas_com_localStorage_que_lanca_nao_quebram() {
    const e = criarAmbiente({ storageLanca: true });
    const sec = new No("section", { class: "passo" }, e.doc);
    const lista = new No("div", { "data-abas": "" }, e.doc);
    const abas = ["claude", "kiro"].map((h) => new No("button", { role: "tab", "data-harness": h }, e.doc));
    const paineis = ["claude", "kiro"].map((h) => new No("div", { class: "painel", role: "tabpanel", "data-harness": h }, e.doc));
    lista.add(...abas);
    sec.add(lista, ...paineis);
    e.corpo.add(sec);
    e.portal.iniciarAbas();
    abas[1].clicar();
    assert.deepStrictEqual(paineis.map((p) => p.hidden), [true, false]);
  },
  contagem_conta_so_cartoes_visiveis() {
    const e = criarAmbiente({});
    const caixa = new No("div", { class: "filtros", "data-alvo": ".cartao-prompt" }, e.doc);
    const select = new No("select", { "data-filtro": "origem" }, e.doc);
    const contagem = new No("span", { "data-contagem": "" }, e.doc);
    caixa.add(select, contagem);
    e.corpo.add(caixa);
    ["pratica", "receita", "receita"].forEach((o) => {
      e.corpo.add(new No("figure", { class: "cartao-prompt", "data-origem": o }, e.doc));
    });
    e.portal.ligarFiltros(caixa);
    select.value = "receita";
    select.disparar("change");
    assert.strictEqual(contagem.textContent, "2 de 3 prompts");
    select.value = "";
    select.disparar("change");
    assert.strictEqual(contagem.textContent, "3 de 3 prompts");
  },
};

assert.ok(casos[caso], "caso desconhecido: " + caso);
casos[caso]();
