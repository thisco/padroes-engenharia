#!/usr/bin/env python3
"""Exige um protótipo com os quatro estados para cada tela da spec (prática UX-02).

Uso: python3 verificar-prototipos.py [--specs docs/specs] [--prototipos docs/prototipos]

Usa só a biblioteca padrão. A spec lista as telas na seção "## Telas", uma por linha, no formato
"- `slug`: descrição". Cada slug precisa de docs/prototipos/<slug>.md (um título "Carregando",
"Vazio", "Erro" e "Sucesso", de nível 2 a 4, cada um com texto) ou <slug>.html (um elemento
data-estado para cada estado, com texto). Reprova (saída 1) se:
  1. uma tela da spec não tem protótipo;
  2. o protótipo não tem um dos quatro estados, ou tem o estado sem texto;
  3. o texto do vazio é igual ao do erro (o vazio não é erro).
Sai com 0 se tudo confere. Specs com nome iniciado por MODELO são ignoradas, e a spec sem a seção
"## Telas" também reprova, para o erro de digitação no título não virar "nenhuma tela".

O verificador lê arquivos. Ele não prova que a tela implementada segue o protótipo, nem que uma
pessoa o validou: isso é o checkpoint humano.
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ESTADOS = ("carregando", "vazio", "erro", "sucesso")
TELA = re.compile(r"^-\s+`([a-z0-9-]+)`")
TITULO = re.compile(r"^#{2,4}\s+(\w+)\s*$")


class Secoes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.textos = {}
        self._pilha = []

    def handle_starttag(self, tag, attrs):
        estado = dict(attrs).get("data-estado")
        if estado in ESTADOS and tag == "section":
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


def telas_da_spec(caminho, erros):
    telas, dentro, achou = [], False, False
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith("## "):
            dentro = linha.strip().lower() == "## telas"
            achou = achou or dentro
        elif dentro and (m := TELA.match(linha)):
            telas.append(m.group(1))
    if not achou or not telas:
        erros.append(f"{caminho}: a spec não lista telas na seção '## Telas'")
    return telas


def estados_do_markdown(texto):
    textos, atual = {}, None
    for linha in texto.splitlines():
        m = TITULO.match(linha)
        if m:
            nome = m.group(1).lower()
            atual = nome if nome in ESTADOS else None
            if atual:
                textos[atual] = []
        elif atual:
            textos[atual].append(linha)
    return textos


def estados_do_html(texto):
    p = Secoes()
    p.feed(texto)
    return p.textos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", default="docs/specs")
    ap.add_argument("--prototipos", default="docs/prototipos")
    args = ap.parse_args()
    erros, telas = [], []
    for spec in sorted(Path(args.specs).glob("*.md")):
        if not spec.name.startswith("MODELO"):
            telas += [(spec.name, t) for t in telas_da_spec(spec, erros)]
    if not telas and not erros:
        erros.append(f"{args.specs}: nenhuma spec com telas")
    for spec, tela in telas:
        base = Path(args.prototipos) / tela
        if base.with_suffix(".md").is_file():
            arquivo, leitor = base.with_suffix(".md"), estados_do_markdown
        elif base.with_suffix(".html").is_file():
            arquivo, leitor = base.with_suffix(".html"), estados_do_html
        else:
            erros.append(f"{spec}: a tela '{tela}' não tem protótipo em {args.prototipos}/")
            continue
        textos = {
            e: " ".join(" ".join(t).split())
            for e, t in leitor(arquivo.read_text(encoding="utf-8")).items()
        }
        for estado in ESTADOS:
            if not textos.get(estado):
                erros.append(f"{arquivo}: estado '{estado}' ausente ou sem texto")
        if textos.get("vazio") and textos.get("vazio") == textos.get("erro"):
            erros.append(f"{arquivo}: o vazio tem o mesmo texto do erro")
    if erros:
        print("\n".join(erros))
        print("UX-02: tela da spec sem protótipo completo (acima).")
        sys.exit(1)
    print(f"UX-02: {len(telas)} telas da spec, cada uma com protótipo dos quatro estados.")


if __name__ == "__main__":
    main()
