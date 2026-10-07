#!/bin/sh
# Roda o exemplo da IAC-03: o verificador do plano e um deploy que falha e volta de verdade.
# Uso: sh executar.sh   (na pasta exemplos/IAC-03; precisa de Docker e Python 3)
# O script usa o contêiner iac-app, o projeto iac-rollback, as imagens iac-app:1 e iac-app:2 e a
# porta 18090 do host, e remove tudo ao sair. Como o "rmi" do fim apagaria imagens de quem já tem
# essas tags, o script se recusa a rodar se iac-app:1, iac-app:2 ou o contêiner iac-app existirem.
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
cd "$AQUI" || exit 1
for existente in iac-app:1 iac-app:2; do
    if docker image inspect "$existente" >/dev/null 2>&1; then
        echo "a imagem $existente já existe; não a removo. Apague-a você ou use outra máquina."
        exit 1
    fi
done
if docker inspect iac-app >/dev/null 2>&1; then
    echo "o contêiner iac-app já existe; não o toco."
    exit 1
fi
trap 'IMAGEM=x docker compose -f "$AQUI/compose.yml" down -v >/dev/null 2>&1; docker rmi iac-app:1 iac-app:2 >/dev/null 2>&1' EXIT

echo "### A. Antes: o plano não declara rollback"
python3 verificar-rollback.py plano-antes.md
echo "saída: $?"

echo; echo "### B. Depois: rollback declarado e testado"
python3 verificar-rollback.py plano.md
echo "saída: $?"

echo; echo "### C. O rollback executado: deploy que falha na saúde e volta para a imagem anterior"
docker build -q -t iac-app:1 --build-arg VERSAO=1 app >/dev/null || exit 1
docker build -q -t iac-app:2 --build-arg VERSAO=2 --build-arg SAUDE=quebrado app >/dev/null || exit 1

# implantar <imagem>: sobe a imagem e espera ficar saudável, no máximo 30 segundos.
implantar() {
    IMAGEM="$1" docker compose up -d --wait --wait-timeout 30 >/dev/null 2>&1
}

implantar iac-app:1 || { echo "a imagem inicial não ficou saudável"; exit 1; }
anterior="$(docker inspect --format '{{.Config.Image}}' iac-app)"
echo "no ar: $(curl -s http://127.0.0.1:18090/versao) (imagem $anterior, guardada como a anterior)"

echo "--- deploy da iac-app:2"
if implantar iac-app:2; then
    echo "a imagem 2 deveria ter falhado na saúde"
    exit 1
fi
echo "falhou na saúde: $(docker inspect --format '{{.State.Health.Status}}' iac-app)"

echo "--- rollback: redeploy da imagem anterior pelo mesmo compose"
implantar "$anterior" || { echo "o rollback não ficou saudável em 30 segundos"; exit 1; }
echo "saúde: $(docker inspect --format '{{.State.Health.Status}}' iac-app)"
echo "no ar: $(curl -s http://127.0.0.1:18090/versao)"
