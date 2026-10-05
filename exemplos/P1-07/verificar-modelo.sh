#!/bin/sh
# Confere o registro do modelo: campos preenchidos, guia em URL https e as duas listas com item.
f="${1:-docs/steering/modelo.md}"
[ -f "$f" ] || { echo "ERRO: falta $f"; exit 1; }
for campo in 'Modelo' 'Versão' 'Guia consultado' 'Consultado em'; do
  grep -qE "^- \*\*$campo:\*\* *[^ ]" "$f" || { echo "ERRO: campo ausente ou vazio: $campo"; exit 1; }
done
grep -qE '^- \*\*Guia consultado:\*\* *https://' "$f" || { echo "ERRO: o guia deve ser uma URL https"; exit 1; }
for secao in 'Aplicadas' 'Não aplicadas'; do
  awk -v s="## $secao" '$0==s{d=1;next} /^## /{d=0} d&&/^- /{n++} END{exit n?0:1}' "$f" \
    || { echo "ERRO: a seção '$secao' não tem item"; exit 1; }
done
echo "OK: $f"
