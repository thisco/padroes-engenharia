"""Confere o plano de mudança de infra (saída de `tofu show -json <plano>`) antes do merge.

Uso: python3 verificar-plano.py <plano.json> [aprovacoes.txt]

Reprova (saída 1): arquivo ausente, vazio ou que não é um plano em JSON, e recurso que o plano
destrói (ação delete, inclusive a substituição) sem estar listado em aprovacoes.txt, que traz um
endereço de recurso por linha, registrado na revisão do PR. Saída 0: o plano só cria, altera
no lugar ou não muda nada, ou toda destruição tem aprovação.
"""

import json
import sys
from pathlib import Path


def ler_json(caminho):
    arq = Path(caminho)
    if not arq.is_file() or not arq.read_text(encoding="utf-8").strip():
        print(f"{caminho}: ausente ou vazio")
        sys.exit(1)
    try:
        dado = json.loads(arq.read_text(encoding="utf-8"))
    except ValueError:
        print(f"{caminho}: não é JSON")
        sys.exit(1)
    if not isinstance(dado, dict) or "format_version" not in dado:
        print(f"{caminho}: não é um plano de `tofu show -json`")
        sys.exit(1)
    return dado


def aprovados(caminho):
    if caminho is None:
        return set()
    arq = Path(caminho)
    if not arq.is_file():
        print(f"{caminho}: arquivo de aprovações ausente")
        sys.exit(1)
    linhas = arq.read_text(encoding="utf-8").splitlines()
    return {linha.strip() for linha in linhas if linha.strip() and not linha.startswith("#")}


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 1
    plano = ler_json(sys.argv[1])
    liberados = aprovados(sys.argv[2] if len(sys.argv) == 3 else None)
    contagem = {}
    erros = []
    for mudanca in plano.get("resource_changes", []):
        acoes = mudanca.get("change", {}).get("actions", [])
        rotulo = "+".join(acoes) if acoes else "?"
        contagem[rotulo] = contagem.get(rotulo, 0) + 1
        if "delete" in acoes and mudanca.get("address") not in liberados:
            erros.append(f"{mudanca.get('address')}: será destruído ({rotulo}) sem aprovação")
    for erro in erros:
        print(erro)
    resumo = ", ".join(f"{n} {a}" for a, n in sorted(contagem.items())) or "nenhuma mudança"
    if erros:
        print(f"IAC-02: {len(erros)} destruição(ões) sem aprovação ({resumo}).")
        return 1
    print(f"IAC-02: plano sem destruição não aprovada ({resumo}).")
    return 0


sys.exit(main())
