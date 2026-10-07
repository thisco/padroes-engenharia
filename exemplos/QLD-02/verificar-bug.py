#!/usr/bin/env python3
"""QLD-02: confere que o teste reproduz o defeito e que o gotcha foi registrado.

Uso: python3 verificar-bug.py --teste T --com-bug A --corrigido B --modulo M --memoria MEM

Copia o teste e cada versão do módulo para um diretório temporário e roda o pytest em cada
uma. Sai com 0 só se o teste falha (saída 1 do pytest) no código com o defeito, passa no
corrigido e a memória tem uma entrada com sintoma, causa-raiz, correção, regra e o id do teste.
Sai com 1 em qualquer outro caso, inclusive arquivo ausente ou vazio, pytest ausente e execução
que passe de 120 s.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAMPOS = ("Sintoma", "Causa-raiz", "Correção", "Teste", "Regra")
LIMITE_S = 120


def ler(caminho: str) -> Path:
    arquivo = Path(caminho)
    if not arquivo.is_file() or not arquivo.read_text(encoding="utf-8").strip():
        raise SystemExit(f"QLD-02: {caminho} não existe ou está vazio.")
    return arquivo


def rodar_pytest(teste: Path, versao: Path, modulo: str) -> int:
    with tempfile.TemporaryDirectory(prefix="qld02-") as pasta:
        shutil.copy(teste, Path(pasta) / teste.name)
        shutil.copy(versao, Path(pasta) / f"{modulo}.py")
        try:
            resultado = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", teste.name],
                cwd=pasta,
                capture_output=True,
                text=True,
                timeout=LIMITE_S,
            )
        except subprocess.TimeoutExpired:
            raise SystemExit(f"QLD-02: o pytest passou de {LIMITE_S} s em {versao}.") from None
    if "No module named pytest" in resultado.stderr + resultado.stdout:
        raise SystemExit("QLD-02: o pytest não está instalado neste interpretador.")
    return resultado.returncode


def entrada_da_memoria(memoria: Path, id_do_teste: str) -> list[str]:
    """Devolve os campos que faltam na entrada que cita o id do teste."""
    texto = memoria.read_text(encoding="utf-8")
    entradas = re.split(r"^### ", texto, flags=re.M)[1:]
    citam = [e for e in entradas if id_do_teste in e]
    if not citam:
        return [f"nenhuma entrada da memória cita o teste {id_do_teste}"]
    return [f"falta o campo {c} na entrada" for c in CAMPOS if f"**{c}:**" not in citam[0]]


def main() -> int:
    ap = argparse.ArgumentParser()
    for nome in ("teste", "com-bug", "corrigido", "modulo", "memoria"):
        ap.add_argument(f"--{nome}", required=True)
    args = ap.parse_args()
    teste, com_bug = ler(args.teste), ler(args.com_bug)
    corrigido, memoria = ler(args.corrigido), ler(args.memoria)

    achados = []
    saida_com_bug = rodar_pytest(teste, com_bug, args.modulo)
    if saida_com_bug == 0:
        achados.append("o teste passa no código com o defeito: ele não reproduz o bug")
    elif saida_com_bug != 1:
        achados.append(
            f"no código com o defeito o pytest saiu com {saida_com_bug}, e não 1 (falha)"
        )
    if rodar_pytest(teste, corrigido, args.modulo) != 0:
        achados.append("o teste não passa no código corrigido")
    id_do_teste = re.search(r"^def (test_\w+)", teste.read_text(encoding="utf-8"), re.M)
    if not id_do_teste:
        achados.append(f"{teste} não tem função test_*")
    else:
        achados += entrada_da_memoria(memoria, id_do_teste.group(1))

    for achado in achados:
        print(f"QLD-02: {achado}")
    if achados:
        print(f"QLD-02: {len(achados)} problema(s) (acima).")
        return 1
    print("QLD-02: o teste falha com o defeito, passa na correção e o gotcha está registrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
