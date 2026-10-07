#!/usr/bin/env bash
# Escreve app/config.py com uma chave AWS sintética dentro do diretório informado.
# A chave é montada em duas partes de propósito: o repositório do portal roda o gitleaks e não
# pode conter o valor inteiro. O valor é uma sequência de letras do alfabeto, sem conta nem
# credencial por trás; só tem o formato que a regra aws-access-token do gitleaks detecta.
# ATENÇÃO: escreve (e sobrescreve) app/config.py no diretório informado. Use só num repositório de
# teste; o script se recusa a rodar se app/config.py já existir.
set -eu
if [ "$#" -ne 1 ] || [ ! -d "$1" ]; then
  echo "uso: plantar-segredo.sh <diretório existente>" >&2
  exit 1
fi
parte_a="AKIA"
parte_b="ABCDEFGHIJKLMNOP"
if [ -e "$1/app/config.py" ]; then
  echo "SEG-02: $1/app/config.py já existe; não sobrescrevo. Use um diretório de teste." >&2
  exit 1
fi
mkdir -p "$1/app"
printf 'AWS_ACCESS_KEY_ID = "%s%s"\n' "$parte_a" "$parte_b" > "$1/app/config.py"
echo "SEG-02: app/config.py escrito em $1 com chave sintética."
