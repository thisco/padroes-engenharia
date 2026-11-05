"""Sinais de perfil (spec do motor §7.2): o que, no projeto, indica que um domínio se aplica.

O pacote leva a tabela em `perfil/sinais.json` (JSON, porque o CLI só usa a biblioteca padrão), com
os domínios na ordem da espinha. Critérios de cada sinal, lidos pelo CLI (`portal/cli/deteccao.py`):

- `sempre`: o domínio entra em todo perfil;
- `caminhos`: globs sobre caminhos do projeto; terminado em `/` casa pasta, senão arquivo; sem `/`
  casa o nome em qualquer nível, com `/` casa o caminho relativo (`**/` aceita a raiz);
- `dependencias`: nome de pacote nos arquivos de dependência (`pyproject.toml`, `requirements*.txt`,
  `package.json`, `go.mod`, `pom.xml`, `build.gradle*`, `Cargo.toml`);
- `texto`: regex sobre os arquivos de `caminhos`, para sinais de prosa (menção à LGPD).
"""

from __future__ import annotations

from typing import Any

from portal.gerador.espinha import Espinha

VERSAO_FORMATO_SINAIS = 1

SINAIS: tuple[dict[str, Any], ...] = (
    {"dominio": "construir-com-ia", "sempre": True},
    {"dominio": "seguranca", "sempre": True},
    {"dominio": "qualidade-bdd", "sempre": True},
    {
        "dominio": "dados-migrations",
        "caminhos": ["**/migrations/", "**/migration/", "alembic/", "prisma/", "flyway/"],
    },
    {
        "dominio": "infra-iac",
        "caminhos": [
            "Dockerfile",
            "compose*.yml",
            "docker-compose*.yml",
            "*.tf",
            "*.bicep",
            "helm/",
        ],
    },
    {"dominio": "ci-cd", "caminhos": [".gitlab-ci.yml", ".github/workflows/"]},
    {
        "dominio": "contratos-api",
        "caminhos": ["openapi*.yml", "openapi*.yaml", "*.proto", "asyncapi*.yml", "asyncapi*.yaml"],
    },
    {
        "dominio": "ia-no-produto",
        "dependencias": ["anthropic", "openai", "litellm", "google-genai", "langchain"],
    },
    {"dominio": "frontend-ux", "dependencias": ["react", "vue", "angular", "svelte"]},
    {
        "dominio": "privacidade-lgpd",
        "texto": {"caminhos": ["README.md", "docs/**/*.md"], "regex": r"(?i)\blgpd\b"},
    },
    {
        "dominio": "observabilidade",
        "dependencias": ["opentelemetry", "prometheus", "grafana", "sentry"],
        "caminhos": ["otel*.yml", "otel*.yaml", "prometheus*.yml", "prometheus*.yaml"],
    },
    {"dominio": "arquitetura", "caminhos": ["docs/adr/", "docs/arquitetura/"]},
)


def sinais(espinha: Espinha) -> dict[str, Any]:
    return {
        "versao_formato": VERSAO_FORMATO_SINAIS,
        "dominios": list(dict.fromkeys(f.slug for f in espinha.faixas)),
        "sinais": [dict(s) for s in SINAIS],
    }
