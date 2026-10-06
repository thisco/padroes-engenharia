"""LGPD-01: todo campo de schema SQL precisa de classe em dados.md. Sai com 0 ou 1."""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

CLASSES = {"publico", "interno", "pessoal", "sensivel"}
COM_FINALIDADE = {"pessoal", "sensivel"}
INICIO_CONSTRAINT = ("constraint", "primary", "foreign", "unique", "check", "key", "index")
CREATE = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([\w.\"]+)\s*\(", re.I)
ALTER = re.compile(
    r"alter\s+table\s+([\w.\"]+)\s+add\s+(?:column\s+)?(?:if\s+not\s+exists\s+)?([\w\"]+)", re.I
)


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").strip()


def nome(identificador: str) -> str:
    return identificador.strip('"').split(".")[-1].lower()


def corpo_do_create(sql: str, abre: int) -> str:
    """O texto entre o parêntese que abre em `abre` e o que o fecha."""
    nivel = 0
    for i in range(abre, len(sql)):
        if sql[i] == "(":
            nivel += 1
        elif sql[i] == ")":
            nivel -= 1
            if nivel == 0:
                return sql[abre + 1 : i]
    return sql[abre + 1 :]


def colunas(corpo: str) -> list[str]:
    """Primeiro token de cada item do corpo, no nível de cima, sem as constraints de tabela."""
    itens, nivel, atual = [], 0, ""
    for c in corpo:
        nivel += (c == "(") - (c == ")")
        if c == "," and nivel == 0:
            itens.append(atual)
            atual = ""
        else:
            atual += c
    itens.append(atual)
    achados = []
    for item in itens:
        partes = item.split()
        if partes and partes[0].lower().strip('"') not in INICIO_CONSTRAINT:
            achados.append(nome(partes[0]))
    return achados


def campos_do_schema(caminho: Path) -> list[tuple[str, str]]:
    """Pares (arquivo, tabela.coluna) dos CREATE TABLE e dos ADD COLUMN."""
    arquivos = [caminho] if caminho.is_file() else sorted(caminho.rglob("*.sql"))
    campos = []
    for arquivo in arquivos:
        sql = re.sub(r"--[^\n]*", "", arquivo.read_text(encoding="utf-8"))
        for m in CREATE.finditer(sql):
            tabela = nome(m.group(1))
            corpo = corpo_do_create(sql, m.end() - 1)
            campos += [(arquivo.name, f"{tabela}.{c}") for c in colunas(corpo)]
        for m in ALTER.finditer(sql):
            campos.append((arquivo.name, f"{nome(m.group(1))}.{nome(m.group(2))}"))
    return campos


def tabela_de_classes(dados: Path) -> dict[str, tuple[str, str]]:
    """campo -> (classe normalizada, finalidade), das linhas `| campo | classe | finalidade |`."""
    linhas = {}
    for linha in dados.read_text(encoding="utf-8").splitlines():
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        if linha.lstrip().startswith("|") and len(celulas) >= 2 and "." in celulas[0]:
            finalidade = celulas[2] if len(celulas) > 2 else ""
            linhas[celulas[0].lower()] = (normalizar(celulas[1]), finalidade)
    return linhas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schema", required=True, help="arquivo .sql ou pasta de migrations")
    ap.add_argument("--dados", required=True, help="docs/steering/dados.md")
    args = ap.parse_args()
    schema, dados = Path(args.schema), Path(args.dados)
    for caminho in (schema, dados):
        if not caminho.exists():
            print(f"{caminho}: arquivo ou pasta ausente")
            return 1
    campos = campos_do_schema(schema)
    if not campos:
        print(f"{schema}: nenhum campo encontrado (CREATE TABLE ou ADD COLUMN)")
        return 1
    classes = tabela_de_classes(dados)
    erros = []
    for arquivo, campo in campos:
        classe, finalidade = classes.get(campo, (None, ""))
        if classe is None:
            erros.append(f"{arquivo}: {campo}: sem classificação em {dados.name}")
        elif classe not in CLASSES:
            erros.append(f"{dados.name}: {campo}: classe inválida ({classe})")
        elif classe in COM_FINALIDADE and finalidade.strip(" -") == "":
            erros.append(f"{dados.name}: {campo}: dado {classe} sem finalidade")
    for erro in erros:
        print(erro)
    if erros:
        print("LGPD-01: campo sem classe, com classe inválida ou sem finalidade (acima).")
        return 1
    print(f"LGPD-01: {len(campos)} campos de schema, todos classificados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
