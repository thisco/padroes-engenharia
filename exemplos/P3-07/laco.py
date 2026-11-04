"""Laço do agente com interruptor, tetos de passos e custo, e traço por execução (P3-07)."""
from opentelemetry import trace

tracer = trace.get_tracer("agente-triagem")
AGENTE, VERSAO = "triagem", "3"
MAX_PASSOS, MAX_CUSTO_USD = 20, 0.50


class Interrompido(Exception):
    """O laço parou por interruptor ou por teto; o motivo vai para o traço."""


def executar(tarefa_id, tipo, entrada, modelo, ferramentas, interruptor, preco, ao_interromper):
    with tracer.start_as_current_span(f"invoke_agent {AGENTE}") as span:
        span.set_attributes({"gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": AGENTE,
                             "gen_ai.conversation.id": tarefa_id, "agente.config_versao": VERSAO,
                             "tarefa.tipo": tipo})
        historico, custo, entrada_tok, saida_tok = [entrada], 0.0, 0, 0
        try:
            for _ in range(MAX_PASSOS):
                if interruptor.desligado(AGENTE):
                    raise Interrompido("interruptor")
                passo = modelo.proximo_passo(historico)
                entrada_tok += passo.tokens_entrada
                saida_tok += passo.tokens_saida
                custo += preco(passo.tokens_entrada, passo.tokens_saida)
                if custo > MAX_CUSTO_USD:
                    raise Interrompido("teto-de-custo")
                if passo.fim:
                    span.set_attribute("tarefa.resultado", "sucesso")
                    return passo.resultado
                with tracer.start_as_current_span(f"execute_tool {passo.ferramenta}") as ferramenta:
                    ferramenta.set_attributes({"gen_ai.operation.name": "execute_tool",
                                               "gen_ai.tool.name": passo.ferramenta})
                    historico.append(ferramentas[passo.ferramenta](**passo.argumentos))
            raise Interrompido("teto-de-passos")
        except Interrompido as motivo:
            span.set_attributes({"tarefa.resultado": "interrompida", "error.type": str(motivo)})
            ao_interromper(tarefa_id, historico)
            raise
        except Exception as erro:  # ferramenta ou modelo que falha: mesmo registro e mesma saída
            span.set_attributes({"tarefa.resultado": "falhou", "error.type": type(erro).__name__})
            ao_interromper(tarefa_id, historico)
            raise
        finally:
            span.set_attributes({"gen_ai.usage.input_tokens": entrada_tok,
                                 "gen_ai.usage.output_tokens": saida_tok,
                                 "tarefa.custo_usd": custo})
