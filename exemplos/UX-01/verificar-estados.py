#!/usr/bin/env python3
"""Confere os quatro estados de uma tela (prática UX-01).

Uso: python3 verificar-estados.py --html frontend/lista-chamados.html \
        --dados frontend/dados-exemplo/lista-chamados.json

Usa só a biblioteca padrão. Reprova (saída 1) se:
  1. o HTML não tem exatamente um elemento data-estado para cada um de carregando, vazio, erro
     e sucesso;
  2. o JSON de dados de exemplo não tem os quatro estados, ou falta campo: carregando com
     mensagem e limite_segundos positivo; vazio com titulo, orientacao e acao; erro com titulo,
     descricao e acao; sucesso com ao menos um item;
  3. o texto de orientação do vazio é igual ao de descrição do erro (vazio tratado como erro),
     ou a descrição do erro traz rastro técnico (Traceback, Exception, undefined, null);
  4. o título e a orientação do vazio, o título e a descrição do erro e as ações não aparecem
     no elemento do estado correspondente do HTML.
Sai com 0 se tudo confere.

O verificador lê dois arquivos. Ele não prova que a tela real chama esses estados na hora certa,
nem que o texto é bom: isso é a revisão e o teste da tela.
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser

ESTADOS = ("carregando", "vazio", "erro", "sucesso")
CAMPOS = {
    "vazio": ("titulo", "orientacao", "acao"),
    "erro": ("titulo", "descricao", "acao"),
}
RASTRO = re.compile(r"Traceback|Exception|undefined|\bnull\b|\bat \w+\.\w+\(", re.IGNORECASE)


class Secoes(HTMLParser):
    """Junta o texto de cada elemento com data-estado, na ordem do documento."""

    def __init__(self):
        super().__init__()
        self.textos = {}
        self.contagem = {}
        self._pilha = []

    def handle_starttag(self, tag, attrs):
        estado = dict(attrs).get("data-estado")
        if estado in ESTADOS and tag == "section":
            self.contagem[estado] = self.contagem.get(estado, 0) + 1
            self.textos.setdefault(estado, [])
            self._pilha.append((tag, estado))
        elif self._pilha and tag == self._pilha[-1][0]:
            self._pilha.append((tag, None))

    def handle_endtag(self, tag):
        if self._pilha and self._pilha[-1][0] == tag:
            self._pilha.pop()

    def handle_data(self, dado):
        for _, estado in self._pilha:
            if estado:
                self.textos[estado].append(dado)


def normalizar(texto):
    return " ".join(texto.split())


def ler(caminho, erros, json_=False):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f) if json_ else f.read()
    except (OSError, ValueError) as e:
        erros.append(f"{caminho}: não foi possível ler ({e})")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--dados", required=True)
    args = ap.parse_args()
    erros = []
    html = ler(args.html, erros)
    dados = ler(args.dados, erros, json_=True)
    if erros:
        print("\n".join(erros))
        sys.exit(1)

    secoes = Secoes()
    secoes.feed(html)
    textos = {e: normalizar(" ".join(t)) for e, t in secoes.textos.items()}
    for estado in ESTADOS:
        n = secoes.contagem.get(estado, 0)
        if n != 1:
            erros.append(f"{args.html}: estado '{estado}' aparece {n} vez(es) (esperado 1)")

    if not isinstance(dados, dict):
        erros.append(f"{args.dados}: o JSON precisa ser um objeto")
        dados = {}
    for estado in ESTADOS:
        if not isinstance(dados.get(estado), dict):
            erros.append(f"{args.dados}: estado '{estado}' ausente")
    c = dados.get("carregando")
    if isinstance(c, dict):
        if not str(c.get("mensagem", "")).strip():
            erros.append(f"{args.dados}: carregando sem mensagem")
        limite = c.get("limite_segundos")
        if not isinstance(limite, int | float) or isinstance(limite, bool) or limite <= 0:
            erros.append(f"{args.dados}: carregando sem limite_segundos positivo")
    for estado, campos in CAMPOS.items():
        d = dados.get(estado)
        if not isinstance(d, dict):
            continue
        for campo in campos:
            valor = str(d.get(campo, "")).strip()
            if not valor:
                erros.append(f"{args.dados}: {estado} sem {campo}")
            elif normalizar(valor) not in textos.get(estado, ""):
                erros.append(f"{args.html}: {estado}: texto de {campo} não aparece na tela")
    s = dados.get("sucesso")
    if isinstance(s, dict) and not (isinstance(s.get("itens"), list) and s["itens"]):
        erros.append(f"{args.dados}: sucesso sem itens de exemplo")

    vazio, erro = dados.get("vazio"), dados.get("erro")
    if isinstance(vazio, dict) and isinstance(erro, dict):
        orientacao = normalizar(str(vazio.get("orientacao", "")))
        descricao = normalizar(str(erro.get("descricao", "")))
        if orientacao and orientacao == descricao:
            erros.append(f"{args.dados}: o vazio tem o mesmo texto do erro (vazio não é erro)")
        if RASTRO.search(descricao):
            erros.append(f"{args.dados}: a descrição do erro traz rastro técnico")

    if erros:
        print("\n".join(erros))
        print("UX-01: a tela não tem os quatro estados completos (acima).")
        sys.exit(1)
    print("UX-01: 4 estados presentes; o vazio orienta e é distinto do erro.")


if __name__ == "__main__":
    main()
