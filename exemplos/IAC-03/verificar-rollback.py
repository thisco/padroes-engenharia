"""Confere que o plano declara e testou o rollback antes do deploy.

Uso: python3 verificar-rollback.py <plano.md>

O plano precisa ter a seção "## Rollback" com três linhas e a seção "## Evidências" preenchida:
  - Tipo: schema | deploy | dados
  - Volta: o que desfaz (schema: a migration de volta, V<n>__ ou downgrade; deploy: a imagem
    anterior com tag ou digest; dados: o backup e o tempo de restauração)
  - Testado: sim, e onde (ou não, e por quê)

Reprova (saída 1): arquivo ausente ou vazio, seção ausente, tipo desconhecido, volta que não
cita o que o tipo pede, e "Testado" que não começa por "sim".
"""

import re
import sys
from pathlib import Path

PEDIDO = {
    "schema": (r"V\d+__|downgrade", "a migration de volta (V<n>__ ou downgrade)"),
    "deploy": (r"[\w./-]+:[\w.-]+|@sha256:", "a imagem anterior com tag ou digest"),
    "dados": (r"backup[\s\S]*tempo|tempo[\s\S]*backup", "o backup e o tempo de restauração"),
}


def secao(texto, titulo):
    achado = re.search(rf"^## {titulo}\s*$(.*?)(?=^## |\Z)", texto, re.M | re.S)
    return achado.group(1) if achado else None


def campo(bloco, nome):
    achado = re.search(rf"^- {nome}:\s*(.+)$", bloco, re.M)
    return achado.group(1).strip() if achado else None


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    arq = Path(sys.argv[1])
    if not arq.is_file() or not arq.read_text(encoding="utf-8").strip():
        print(f"{arq}: ausente ou vazio")
        return 1
    texto = arq.read_text(encoding="utf-8")
    erros = []
    rollback = secao(texto, "Rollback")
    if rollback is None:
        erros.append(f"{arq}: falta a seção '## Rollback'")
    else:
        tipo = (campo(rollback, "Tipo") or "").lower()
        volta = campo(rollback, "Volta")
        testado = campo(rollback, "Testado")
        if tipo not in PEDIDO:
            erros.append(f"{arq}: Tipo ausente ou fora de schema, deploy e dados: {tipo!r}")
        if not volta:
            erros.append(f"{arq}: falta a linha 'Volta:'")
        elif tipo in PEDIDO and not re.search(PEDIDO[tipo][0], volta, re.I):
            erros.append(f"{arq}: a Volta de {tipo} precisa citar {PEDIDO[tipo][1]}")
        if not testado or not testado.lower().startswith("sim"):
            erros.append(f"{arq}: o rollback não consta como testado ('Testado: sim, ...')")
    evidencias = secao(texto, "Evidências")
    if evidencias is None or not evidencias.strip():
        erros.append(f"{arq}: falta a seção '## Evidências' preenchida")
    for erro in erros:
        print(erro)
    if erros:
        print(f"IAC-03: {len(erros)} problema(s) no rollback do plano (acima).")
        return 1
    print("IAC-03: rollback declarado, com a volta nomeada e testado.")
    return 0


sys.exit(main())
