#!/usr/bin/env python3
"""Compara dois contratos OpenAPI e classifica a mudança em compatível ou incompatível (API-01).

Uso: python3 comparar-contratos.py BASE REVISAO [--adr docs/adr/0001-algo.md]

BASE e REVISAO são arquivos OpenAPI em YAML (precisa do PyYAML) ou JSON. Reprova (saída 1) se:
  1. a revisão tem mudança incompatível e `info.version` não subiu a versão major;
  2. a revisão tem mudança incompatível com major nova, mas sem `--adr` apontando um arquivo
     que exista (a mudança destrutiva exige o registro da decisão);
  3. um dos arquivos não existe, não é válido ou não traz `info.version` no formato X.Y.Z.
Sai com 0 se a revisão é compatível, ou se é incompatível com major nova e ADR.

Regras de incompatibilidade, para cada operação (método e caminho) e para cada schema, seguindo
os $ref internos de `#/components/`:
  - endpoint, operação ou código de resposta removido;
  - parâmetro removido, novo e obrigatório, ou que passou a obrigatório; tipo de parâmetro mudado;
  - corpo da requisição que passou a obrigatório;
  - campo removido, com tipo mudado ou que deixou de ser obrigatório na resposta;
  - campo removido, com tipo mudado, que passou a obrigatório ou novo e obrigatório, na requisição.
É compatível: endpoint, operação ou código de resposta novo, campo ou parâmetro novo e opcional.

Limites: o verificador lê só os dois arquivos. Não confere enum, formato, limites de tamanho,
oneOf, allOf, a semântica dos campos, nem se a implementação segue o contrato (isso é o teste
de contrato, API-02). A regra de versão é a do SemVer: mudança incompatível pede a major.
"""

import argparse
import json
import re
import sys
from pathlib import Path

METODOS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
INCOMPATIVEL, COMPATIVEL = "incompativel", "compativel"
PROFUNDIDADE_MAXIMA = 20


def carregar(caminho):
    texto = Path(caminho).read_text(encoding="utf-8")
    if str(caminho).lower().endswith(".json"):
        return json.loads(texto)
    try:
        import yaml
    except ImportError as erro:
        raise ValueError("YAML exige o PyYAML (pip install pyyaml); ou use um .json") from erro
    return yaml.safe_load(texto)


def resolver(doc, no):
    """Segue um $ref interno ('#/components/...'); devolve o próprio nó se não for $ref."""
    for _ in range(PROFUNDIDADE_MAXIMA):
        if not isinstance(no, dict) or "$ref" not in no:
            return no or {}
        ref = no["$ref"]
        if not ref.startswith("#/"):
            raise ValueError(f"$ref externo não suportado: {ref}")
        no = doc
        for parte in ref[2:].split("/"):
            no = no[parte.replace("~1", "/").replace("~0", "~")]
    raise ValueError("$ref circular ou fundo demais")


def versao_major(doc, rotulo):
    versao = str((doc.get("info") or {}).get("version", ""))
    achado = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", versao)
    if not achado:
        raise ValueError(f"{rotulo}: info.version precisa ser X.Y.Z (veio {versao!r})")
    return versao, int(achado.group(1))


class Comparador:
    def __init__(self, base, revisao):
        self.base, self.revisao = base, revisao
        self.achados = []

    def registrar(self, tipo, texto):
        self.achados.append((tipo, texto))

    def schema(self, b, r, onde, modo, nivel=0):
        b, r = resolver(self.base, b), resolver(self.revisao, r)
        if nivel > PROFUNDIDADE_MAXIMA:
            return
        if b.get("type") != r.get("type"):
            self.registrar(
                INCOMPATIVEL,
                f"tipo mudou de {b.get('type')} para {r.get('type')}: {onde}",
            )
            return
        if b.get("type") == "array":
            self.schema(b.get("items", {}), r.get("items", {}), f"{onde}[]", modo, nivel + 1)
        if b.get("type") != "object":
            return
        pb, pr = b.get("properties") or {}, r.get("properties") or {}
        obrigatorios_b, obrigatorios_r = set(b.get("required") or []), set(r.get("required") or [])
        for nome in pb:
            if nome not in pr:
                lado = "da resposta" if modo == "resposta" else "da requisição"
                self.registrar(INCOMPATIVEL, f"campo {lado} removido: {onde}.{nome}")
            else:
                self.schema(pb[nome], pr[nome], f"{onde}.{nome}", modo, nivel + 1)
        for nome in pr:
            if nome in pb:
                continue
            if modo == "requisicao" and nome in obrigatorios_r:
                self.registrar(
                    INCOMPATIVEL, f"campo novo e obrigatório na requisição: {onde}.{nome}"
                )
            else:
                self.registrar(COMPATIVEL, f"campo novo e opcional: {onde}.{nome}")
        if modo == "requisicao":
            for nome in (obrigatorios_r - obrigatorios_b) & set(pb):
                self.registrar(
                    INCOMPATIVEL, f"campo passou a obrigatório na requisição: {onde}.{nome}"
                )
        else:
            for nome in (obrigatorios_b - obrigatorios_r) & set(pr):
                self.registrar(
                    INCOMPATIVEL, f"campo da resposta deixou de ser obrigatório: {onde}.{nome}"
                )

    def parametros(self, b, r, onde):
        def indexar(doc, op):
            itens = [resolver(doc, p) for p in op.get("parameters") or []]
            return {(p.get("in"), p.get("name")): p for p in itens}

        pb, pr = indexar(self.base, b), indexar(self.revisao, r)
        for chave, p in pb.items():
            if chave not in pr:
                self.registrar(INCOMPATIVEL, f"parâmetro removido: {onde} {chave[1]}")
                continue
            if not p.get("required") and pr[chave].get("required"):
                self.registrar(INCOMPATIVEL, f"parâmetro passou a obrigatório: {onde} {chave[1]}")
            self.schema(
                p.get("schema", {}), pr[chave].get("schema", {}), f"{onde} {chave[1]}", "requisicao"
            )
        for chave, p in pr.items():
            if chave in pb:
                continue
            if p.get("required"):
                self.registrar(INCOMPATIVEL, f"parâmetro novo e obrigatório: {onde} {chave[1]}")
            else:
                self.registrar(COMPATIVEL, f"parâmetro novo e opcional: {onde} {chave[1]}")

    def conteudo_json(self, doc, no):
        no = resolver(doc, no)
        midia = (no.get("content") or {}).get("application/json") or {}
        return midia.get("schema")

    def operacao(self, b, r, onde):
        self.parametros(b, r, onde)
        corpo_b, corpo_r = (
            resolver(self.base, b.get("requestBody")),
            resolver(self.revisao, r.get("requestBody")),
        )
        if not corpo_b.get("required") and corpo_r.get("required"):
            self.registrar(INCOMPATIVEL, f"corpo da requisição passou a obrigatório: {onde}")
        sb, sr = self.conteudo_json(self.base, corpo_b), self.conteudo_json(self.revisao, corpo_r)
        if sb is not None and sr is not None:
            self.schema(sb, sr, f"{onde} corpo", "requisicao")
        resp_b, resp_r = b.get("responses") or {}, r.get("responses") or {}
        for codigo in resp_b:
            if codigo not in resp_r:
                self.registrar(INCOMPATIVEL, f"resposta removida: {onde} {codigo}")
                continue
            sb = self.conteudo_json(self.base, resp_b[codigo])
            sr = self.conteudo_json(self.revisao, resp_r[codigo])
            if sb is not None and sr is not None:
                self.schema(sb, sr, f"{onde} {codigo}", "resposta")
        for codigo in resp_r:
            if codigo not in resp_b:
                self.registrar(COMPATIVEL, f"resposta nova: {onde} {codigo}")

    def comparar(self):
        pb, pr = self.base.get("paths") or {}, self.revisao.get("paths") or {}
        for caminho, item_b in pb.items():
            if caminho not in pr:
                self.registrar(INCOMPATIVEL, f"endpoint removido: {caminho}")
                continue
            for metodo in METODOS:
                onde = f"{metodo.upper()} {caminho}"
                if metodo in item_b and metodo not in pr[caminho]:
                    self.registrar(INCOMPATIVEL, f"operação removida: {onde}")
                elif metodo in item_b:
                    self.operacao(item_b[metodo], pr[caminho][metodo], onde)
                elif metodo in pr[caminho]:
                    self.registrar(COMPATIVEL, f"operação nova: {onde}")
        for caminho in pr:
            if caminho not in pb:
                self.registrar(COMPATIVEL, f"endpoint novo: {caminho}")
        return self.achados


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("base")
    ap.add_argument("revisao")
    ap.add_argument("--adr", help="arquivo da ADR que registra a mudança incompatível")
    args = ap.parse_args(argv)
    try:
        base, revisao = carregar(args.base), carregar(args.revisao)
        v_base, major_base = versao_major(base, args.base)
        v_rev, major_rev = versao_major(revisao, args.revisao)
        achados = Comparador(base, revisao).comparar()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as erro:
        print(f"API-01: não foi possível comparar: {erro}")
        return 1
    incompativeis = [t for k, t in achados if k == INCOMPATIVEL]
    for tipo, texto in achados:
        print(("INCOMPATÍVEL: " if tipo == INCOMPATIVEL else "compatível: ") + texto)
    if not incompativeis:
        print(f"API-01: {len(achados)} mudança(s), todas compatíveis (versão {v_base} -> {v_rev}).")
        return 0
    if major_rev <= major_base:
        print(
            f"API-01: {len(incompativeis)} mudança(s) incompatível(is) sem versão major nova "
            f"({v_base} -> {v_rev}). Suba a major e registre a ADR, ou torne a mudança compatível."
        )
        return 1
    if not args.adr or not Path(args.adr).is_file():
        print(
            f"API-01: mudança incompatível com major nova ({v_base} -> {v_rev}), mas sem ADR: "
            "passe --adr com o arquivo que registra a decisão."
        )
        return 1
    print(f"API-01: mudança incompatível com major nova ({v_base} -> {v_rev}) e ADR {args.adr}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
