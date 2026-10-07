#!/bin/sh
# Roda o exemplo da IAC-02: um módulo OpenTofu mínimo, o plano de duas mudanças e o verificador.
# Uso: sh executar.sh   (na pasta exemplos/IAC-02; precisa de tofu e Python 3; o init baixa o
# provider hashicorp/local do registro do OpenTofu). Trabalha numa pasta temporária.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

plano() { # $1 = módulo com a mudança, $2 = aprovações (opcional)
    cp "$AQUI/$1/main.tf" "$TMP/trabalho/main.tf"
    (cd "$TMP/trabalho" && tofu plan -input=false -no-color -out=plano.bin >/dev/null) || exit 1
    (cd "$TMP/trabalho" && tofu show -no-color plano.bin > plano.txt) || exit 1
    (cd "$TMP/trabalho" && tofu show -json plano.bin > plano.json) || exit 1
    echo "--- plano.txt, o que vai para a descrição do PR:"
    grep -E '^(  #|Plan:)' "$TMP/trabalho/plano.txt"
    python3 "$AQUI/verificar-plano.py" "$TMP/trabalho/plano.json" ${2:+"$2"}
    echo "saída: $?"
}

mkdir "$TMP/trabalho" && cp -R "$AQUI/modulo-base/." "$TMP/trabalho/" || exit 1
cd "$TMP/trabalho" || exit 1
echo "### Preparo: init, validate, fmt e o estado atual (apply só neste diretório temporário)"
tofu init -input=false -no-color | grep -E 'Installing|Installed|successfully initialized'
tofu validate -no-color
tofu fmt -check -diff && echo "fmt: ok"
tofu apply -input=false -no-color -auto-approve | grep -E 'Apply complete'

echo; echo "### A. Antes: a mudança renomeia o arquivo de config"
plano modulo-antes

echo; echo "### B. A mesma mudança, com a destruição aprovada na revisão do PR"
echo "local_file.config" > "$TMP/aprovacoes.txt"
plano modulo-antes "$TMP/aprovacoes.txt"

echo; echo "### C. Depois: a mudança só acrescenta um recurso"
plano modulo-depois
