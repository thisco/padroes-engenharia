#!/bin/sh
# Validação do projeto. O mesmo script roda na máquina de quem desenvolve e no job do CI.
# Roda todos os passos e só então sai: uma execução mostra tudo que está errado.
set -u
falhas=0

passo() {
  nome=$1
  shift
  echo "== $nome: $*"
  if "$@"; then
    echo "   ok: $nome"
  else
    echo "   FALHOU: $nome"
    falhas=$((falhas + 1))
  fi
}

passo "linter" python3 -m ruff check .
passo "formatador" python3 -m ruff format --check .
passo "testes e cobertura" python3 -m pytest -q --cov=calculo --cov-fail-under=90

if [ "$falhas" -ne 0 ]; then
  echo "validar: $falhas passo(s) falharam."
  exit 1
fi
echo "validar: tudo certo."
