"""Guardrail de PII do gateway (P2-04): mascara CPF e e-mail antes de chegar ao modelo."""

import logging
import re

from litellm.integrations.custom_guardrail import CustomGuardrail

log = logging.getLogger("mascara_pii")

CPF = re.compile(r"(?<!\d)(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def cpf_valido(digitos: str) -> bool:
    """Confere os dois dígitos verificadores, para não mascarar qualquer número de 11 dígitos."""
    if len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(
            int(d) * p for d, p in zip(digitos[:tamanho], range(tamanho + 1, 1, -1), strict=True)
        )
        if int(digitos[tamanho]) != (soma * 10 % 11) % 10:
            return False
    return True


def mascarar(texto: str) -> str:
    def troca_cpf(m: re.Match) -> str:
        return "[CPF]" if cpf_valido("".join(m.groups())) else m.group(0)

    return EMAIL.sub("[EMAIL]", CPF.sub(troca_cpf, texto))


class MascaraPII(CustomGuardrail):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        for mensagem in data.get("messages") or []:
            conteudo = mensagem.get("content")
            if isinstance(conteudo, str):
                mensagem["content"] = mascarar(conteudo)
            elif isinstance(conteudo, list):
                for parte in conteudo:
                    if isinstance(parte, dict) and isinstance(parte.get("text"), str):
                        parte["text"] = mascarar(parte["text"])
        return data

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        # Registra o que de fato seguiu para o modelo, depois do guardrail.
        log.warning("MENSAGENS ENVIADAS AO MODELO: %s", kwargs.get("messages"))
