"""LGPD-02: reprova CPF ou e-mail em claro em tests/, logs/ e prompts/. Sai com 0 ou 1."""

import argparse
import re
import sys
from pathlib import Path

PASTAS = ("tests", "logs", "prompts")
# Aceita ponto, hífen ou espaço (ou nada) entre os grupos, em qualquer combinação (como na P2-04).
CPF = re.compile(r"(?<!\d)(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{3})[.\s-]?(\d{2})(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
# Escolha do Exemplo: domínios que o time reserva para e-mail de teste.
DOMINIOS_DE_TESTE = {"example.com", "example.org", "example.net"}
IGNORADOS = {".pyc", ".png", ".jpg", ".gif", ".pdf", ".zip", ".gz", ".sqlite"}


def cpf_valido(digitos: str) -> bool:
    """Confere os dois dígitos verificadores, para não acusar qualquer número de 11 dígitos."""
    if len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(
            int(d) * p for d, p in zip(digitos[:tamanho], range(tamanho + 1, 1, -1), strict=True)
        )
        if int(digitos[tamanho]) != (soma * 10 % 11) % 10:
            return False
    return True


def achados_da_linha(linha: str) -> list[str]:
    achados = []
    if any(cpf_valido("".join(m.groups())) for m in CPF.finditer(linha)):
        achados.append("CPF em claro")
    if any(m.group(1).lower() not in DOMINIOS_DE_TESTE for m in EMAIL.finditer(linha)):
        achados.append("e-mail em claro")
    return achados


def arquivos(raiz: Path) -> list[Path]:
    achados = []
    for pasta in PASTAS:
        base = raiz / pasta
        if base.is_dir():
            achados += [
                f
                for f in sorted(base.rglob("*"))
                if f.is_file() and f.suffix not in IGNORADOS and "__pycache__" not in f.parts
            ]
    return achados


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raiz", default=".", help="raiz do projeto, com tests/, logs/ e prompts/")
    raiz = Path(ap.parse_args().raiz)
    if not any((raiz / p).is_dir() for p in PASTAS):
        print(f"{raiz}: nenhuma das pastas {', '.join(PASTAS)} existe (raiz errada?)")
        return 1
    varridos, erros = 0, []
    for arquivo in arquivos(raiz):
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        varridos += 1
        for n, linha in enumerate(texto.splitlines(), start=1):
            # Nunca imprime o dado achado: o relatório do verificador também vai para o CI.
            erros += [f"{arquivo.relative_to(raiz)}:{n}: {a}" for a in achados_da_linha(linha)]
    for erro in erros:
        print(erro)
    if erros:
        print("LGPD-02: dado pessoal em claro em teste, log ou prompt (acima).")
        return 1
    print(f"LGPD-02: {varridos} arquivos varridos, nenhum CPF ou e-mail em claro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
