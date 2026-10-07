#!/usr/bin/env bash
# Hook de pré-commit (SEG-02): reprova o commit que leva segredo no que está em stage.
# Instalar: cp pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# O hook mora em .git/hooks e não é versionado: o gate que vale é o job do CI.
set -u
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "SEG-02: gitleaks não está instalado; sem ele o commit não é conferido." >&2
  exit 1
fi
if ! gitleaks git --pre-commit --staged --no-banner --redact --verbose; then
  echo "SEG-02: segredo no que está em stage; tire-o do arquivo e mova para variável de ambiente." >&2
  exit 1
fi
