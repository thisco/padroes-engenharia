"""Confere um ambiente local de Docker Compose e a ordem de rebuild escrita.

Uso: python3 verificar-ambiente.py <compose.yml> <ambiente-local.md>

Reprova (saída 1): arquivo ausente ou vazio, Docker indisponível, serviço sem healthcheck (ou com
healthcheck vazio, `disable: true` ou `test: ["NONE"]`), dependência sem condition
service_healthy, serviço do compose fora da seção "Serviços" do documento (ou o inverso) e ordem
de rebuild sem os quatro passos na sequência migrations, build, up, saúde.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

PASSOS = [
    ("migrations", r"migration"),
    ("rebuild das imagens", r"build"),
    ("recriar os serviços", r"\bup\b"),
    ("verificar a saúde", r"sa[uú]de|health"),
]


def ler(caminho):
    arq = Path(caminho)
    if not arq.is_file() or not arq.read_text(encoding="utf-8").strip():
        print(f"{caminho}: ausente ou vazio")
        sys.exit(1)
    return arq.read_text(encoding="utf-8")


def configuracao(compose):
    try:
        saida = subprocess.run(
            ["docker", "compose", "-f", compose, "config", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as erro:
        print(f"não consegui rodar o docker compose: {erro}")
        sys.exit(1)
    if saida.returncode != 0:
        print(f"{compose}: compose inválido: {saida.stderr.strip()}")
        sys.exit(1)
    return json.loads(saida.stdout).get("services", {})


def healthcheck_ativo(spec):
    """True se o serviço tem um healthcheck que não está desligado nem vazio."""
    hc = spec.get("healthcheck")
    if not isinstance(hc, dict) or not hc or hc.get("disable"):
        return False
    teste = hc.get("test")
    if teste is not None and (not teste or str(teste[0]).upper() == "NONE" or teste == "NONE"):
        return False
    return True


def secao(texto, titulo):
    achado = re.search(rf"^## {titulo}\s*$(.*?)(?=^## |\Z)", texto, re.M | re.S)
    return achado.group(1) if achado else None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    compose, doc = sys.argv[1], sys.argv[2]
    ler(compose)
    texto = ler(doc)
    servicos = configuracao(compose)
    erros = []
    if not servicos:
        erros.append(f"{compose}: nenhum serviço declarado")
    for nome, spec in servicos.items():
        if not healthcheck_ativo(spec):
            erros.append(f"{compose}: serviço sem healthcheck (ausente ou desligado): {nome}")
        for dep, cond in (spec.get("depends_on") or {}).items():
            if cond.get("condition") != "service_healthy":
                erros.append(f"{compose}: {nome} depende de {dep} sem condition service_healthy")
    listados = secao(texto, "Serviços")
    if listados is None:
        erros.append(f"{doc}: falta a seção '## Serviços'")
    else:
        nomes = set(re.findall(r"^- `([\w.-]+)`", listados, re.M))
        for nome in sorted(set(servicos) - nomes):
            erros.append(f"{doc}: serviço do compose fora da seção Serviços: {nome}")
        for nome in sorted(nomes - set(servicos)):
            erros.append(f"{doc}: cita serviço que o compose não declara: {nome}")
    ordem = secao(texto, "Ordem de rebuild")
    if ordem is None:
        erros.append(f"{doc}: falta a seção '## Ordem de rebuild'")
    else:
        passos = re.findall(r"^\d+\.\s+(.*?)(?=^\d+\.\s|\Z)", ordem, re.M | re.S)
        if len(passos) < len(PASSOS):
            erros.append(f"{doc}: a ordem de rebuild tem {len(passos)} passos, esperados 4")
        for i, (rotulo, padrao) in enumerate(PASSOS):
            if i >= len(passos) or not re.search(padrao, passos[i], re.I):
                erros.append(f"{doc}: passo {i + 1} da ordem deveria tratar de: {rotulo}")
    for erro in erros:
        print(erro)
    if erros:
        print(f"IAC-01: {len(erros)} problema(s) no ambiente local (acima).")
        return 1
    print(f"IAC-01: {len(servicos)} serviços com healthcheck e a ordem de rebuild escrita.")
    return 0


sys.exit(main())
