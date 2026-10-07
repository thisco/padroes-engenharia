"""LGPD-01: todo campo de schema SQL precisa de classe em dados.md. Sai com 0 ou 1."""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

CLASSES = {"publico", "interno", "pessoal", "sensivel"}
COM_FINALIDADE = {"pessoal", "sensivel"}
IDENT = r'(?:"[^"]+"|`[^`]+`|[\w.]+)'
CREATE = re.compile(rf"create\s+table\s+(?:if\s+not\s+exists\s+)?({IDENT})\s*\(", re.I)
ALTER = re.compile(
    rf"alter\s+table\s+(?:only\s+)?(?:if\s+exists\s+)?({IDENT})\s+(.*?)(?:;|\Z)", re.I | re.S
)
# Cláusula de constraint ou de índice se reconhece pela sintaxe, e nunca pelo nome: `key text` e
# `"index" integer` são colunas; `PRIMARY KEY (id)` e `INDEX ix (nome)` não são.
CONSTRAINT = re.compile(
    r"(?:constraint\s+\S+"
    r"|primary\s+key\b"
    r"|foreign\s+key\b"
    r"|(?:unique|check|exclude)\s*(?:\(|using\b)"
    r"|(?:(?:unique|fulltext|spatial)\s+)?(?:index|key)\s+(?:\w+\s*)?\(\s*(?:[^\W\d]|[\"`]))",
    re.I,
)


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").strip()


def nome(identificador: str) -> str:
    return identificador.strip('"`').split(".")[-1].strip('"`').lower()


def corpo_do_create(sql: str, abre: int) -> str:
    """O texto entre o parêntese que abre em `abre` e o que o fecha (aspas e literais à parte)."""
    nivel, aspa = 0, ""
    for i in range(abre, len(sql)):
        c = sql[i]
        if aspa:
            aspa = "" if c == aspa else aspa
        elif c in "'\"`":
            aspa = c
        elif c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
            if nivel == 0:
                return sql[abre + 1 : i]
    return sql[abre + 1 :]


def itens(texto: str) -> list[str]:
    """Quebra por vírgula no nível de cima, sem olhar vírgula entre parênteses ou aspas."""
    achados, nivel, aspa, atual = [], 0, "", ""
    for c in texto:
        if aspa:
            aspa = "" if c == aspa else aspa
        elif c in "'\"`":
            aspa = c
        else:
            nivel += (c == "(") - (c == ")")
            if c == "," and nivel == 0:
                achados.append(atual)
                atual = ""
                continue
        atual += c
    achados.append(atual)
    return [i.strip() for i in achados if i.strip()]


def coluna_do_item(item: str) -> str | None:
    """Nome da coluna que o item declara, ou None se o item é constraint ou índice."""
    if CONSTRAINT.match(item):
        return None
    primeiro = re.match(IDENT, item)
    return nome(primeiro.group(0)) if primeiro else None


def colunas(corpo: str) -> list[str]:
    achados = [coluna_do_item(item) for item in itens(corpo)]
    return [c for c in achados if c]


def colunas_do_alter(clausulas: str) -> list[str]:
    """Uma coluna por cláusula `ADD [COLUMN]`; as de constraint e de índice ficam de fora."""
    achados = []
    for clausula in itens(clausulas):
        m = re.match(r"add\s+(column\s+)?(?:if\s+not\s+exists\s+)?(.*)", clausula, re.I | re.S)
        if not m:
            continue
        resto = m.group(2)
        if m.group(1):
            primeiro = re.match(IDENT, resto)
            coluna = nome(primeiro.group(0)) if primeiro else None
        else:
            coluna = coluna_do_item(resto)
        if coluna:
            achados.append(coluna)
    return achados


def campos_do_schema(caminho: Path) -> list[tuple[str, str]]:
    """Pares (arquivo, tabela.coluna) dos CREATE TABLE e de cada ADD COLUMN dos ALTER TABLE."""
    arquivos = [caminho] if caminho.is_file() else sorted(caminho.rglob("*.sql"))
    campos = []
    for arquivo in arquivos:
        sql = re.sub(r"--[^\n]*", "", arquivo.read_text(encoding="utf-8"))
        for m in CREATE.finditer(sql):
            tabela = nome(m.group(1))
            corpo = corpo_do_create(sql, m.end() - 1)
            campos += [(arquivo.name, f"{tabela}.{c}") for c in colunas(corpo)]
        for m in ALTER.finditer(sql):
            tabela = nome(m.group(1))
            campos += [(arquivo.name, f"{tabela}.{c}") for c in colunas_do_alter(m.group(2))]
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
