"""Configuração da aplicação: lida do ambiente e conferida no boot (SEG-04)."""

import sys
from typing import Literal

from pydantic import SecretStr, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # hide_input_in_errors: a mensagem de erro não repete o valor recebido (a chave, por exemplo).
    model_config = SettingsConfigDict(env_prefix="APP_", hide_input_in_errors=True)

    ambiente: Literal["local", "homologacao", "producao"]  # sem padrão: ausente, o boot falha
    debug: bool = False
    chave_de_sessao: SecretStr  # sem padrão: não existe chave "de desenvolvimento" embutida
    origens_cors: list[str] = []
    docs_publicas: bool = False

    @model_validator(mode="after")
    def segura_em_producao(self) -> "Config":
        if self.ambiente != "producao":
            return self
        problemas = []
        if self.debug:
            problemas.append("APP_DEBUG ligado")
        if len(self.chave_de_sessao.get_secret_value()) < 32:
            problemas.append("APP_CHAVE_DE_SESSAO com menos de 32 caracteres")
        if "*" in self.origens_cors:
            problemas.append("APP_ORIGENS_CORS aceita qualquer origem")
        if self.docs_publicas:
            problemas.append("APP_DOCS_PUBLICAS ligado")
        if problemas:
            raise ValueError("configuração insegura em produção: " + "; ".join(problemas))
        return self


def carregar() -> Config:
    """Lê e confere a configuração; se algo falha, o processo sai com 1 antes de abrir a porta."""
    try:
        return Config()
    except ValidationError as erro:
        for e in erro.errors():
            campo = ".".join(str(p) for p in e["loc"]) or "config"
            print(f"boot abortado: {campo}: {e['msg']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    config = carregar()
    print(f"configuração ok para {config.ambiente}")
