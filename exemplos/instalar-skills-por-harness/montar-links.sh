#!/usr/bin/env bash
# Monta os quatro pontos de montagem de skills como links para skills/.
# Receita: "Instalar as skills por harness" (portal de padrões de engenharia).
# Rode na raiz do repositório, onde está a pasta skills/.
set -euo pipefail

[ -d skills ] || { echo "ERRO: não há pasta skills/ aqui" >&2; exit 1; }

for ponto in .claude .codex .kiro .agents; do
  mkdir -p "$ponto"
  if [ -e "$ponto/skills" ] && [ ! -L "$ponto/skills" ]; then
    echo "ERRO: $ponto/skills existe e não é um link; mova-a antes" >&2
    exit 1
  fi
  ln -sfn ../skills "$ponto/skills"
  echo "$ponto/skills -> $(readlink "$ponto/skills")"
done
