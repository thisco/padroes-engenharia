#!/bin/sh
# Percorre a receita "Entregar uma tela com os quatro estados" num repositório de teste temporário.
# Uso: sh executar.sh   (na pasta exemplos/entregar-tela-com-quatro-estados; precisa de git e
# Python 3, sem dependência externa). Tudo mora em /tmp/b5-tela-XXXXXX e é apagado ao sair.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
UX01="$AQUI/../UX-01"
UX02="$AQUI/../UX-02"
RAIZ="$(mktemp -d /tmp/b5-tela-XXXXXX)"
trap 'rm -rf "$RAIZ"' EXIT

cd "$RAIZ" || exit 1
git init -q -b main
git config user.email t@exemplo.test
git config user.name Teste
mkdir -p scripts docs/specs docs/prototipos frontend/dados-exemplo
cp "$UX01/verificar-estados.py" "$UX02/verificar-prototipos.py" scripts/
cp "$UX02/spec-chamados.md" docs/specs/2026-10-07-chamados.md
git add -A && git commit -q -m "chore: spec com duas telas e os verificadores"

echo "### Passo 1. A spec lista as telas"
sed -n '/^## Telas/,/^## Fora/p' docs/specs/2026-10-07-chamados.md

echo; echo "### Passos 2 e 3. Protótipos: só um, e sem o estado vazio (errado)"
python3 - "$UX02" <<'PY'
import re
import sys
origem = sys.argv[1] + "/prototipo-lista-chamados.md"
t = open(origem, encoding="utf-8").read()
semvazio = re.sub(r"### Vazio.*?(?=### Erro)", "", t, flags=re.S)
open("docs/prototipos/lista-chamados.md", "w", encoding="utf-8").write(semvazio)
PY
python3 scripts/verificar-prototipos.py; echo "saida=$?"

echo; echo "### Passos 2 e 3. Protótipos completos: lista em texto, detalhe em HTML estático"
cp "$UX02/prototipo-lista-chamados.md" docs/prototipos/lista-chamados.md
cp "$UX02/prototipo-detalhe-chamado.html" docs/prototipos/detalhe-chamado.html
python3 scripts/verificar-prototipos.py; echo "saida=$?"
git add -A && git commit -q -m "docs(prototipos): protótipos dos quatro estados das telas da spec (UX-02)"

echo; echo "### Passos 5 e 6. Tela implementada sem o estado vazio (errado)"
python3 - "$UX01" <<'PY'
import json
import re
import sys
pasta = sys.argv[1]
h = open(pasta + "/lista-chamados.html", encoding="utf-8").read()
h = re.sub(r'<section data-estado="vazio".*?</section>\n\n', "", h, flags=re.S)
h = re.sub(r'\s*<button data-vai="vazio">Vazio</button>', "", h)
open("frontend/lista-chamados.html", "w", encoding="utf-8").write(h)
d = json.load(open(pasta + "/dados-exemplo.json", encoding="utf-8"))
del d["vazio"]
json.dump(d, open("frontend/dados-exemplo/lista-chamados.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
PY
python3 scripts/verificar-estados.py --html frontend/lista-chamados.html \
    --dados frontend/dados-exemplo/lista-chamados.json; echo "saida=$?"

echo; echo "### Passos 5 e 6. Tela com os quatro estados"
cp "$UX01/lista-chamados.html" frontend/lista-chamados.html
cp "$UX01/dados-exemplo.json" frontend/dados-exemplo/lista-chamados.json
python3 scripts/verificar-estados.py --html frontend/lista-chamados.html \
    --dados frontend/dados-exemplo/lista-chamados.json; echo "saida=$?"
git add -A && git commit -q -m "feat(frontend): tela lista-chamados com os quatro estados (UX-01)"
git log --oneline
