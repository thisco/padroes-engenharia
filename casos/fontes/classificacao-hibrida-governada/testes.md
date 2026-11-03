Contagem e nomes de testes do projeto de origem, no commit fixado no registro de verificação. Lidos em 2026-11-03. O comando fica no registro de verificação; nomes de fornecedor retirados dos nomes de arquivo.

| O que | Valor |
|---|---|
| Arquivos de teste do módulo de classificação | 48 |
| Funções de teste do módulo de classificação | 391 |
| Arquivos de teste do serviço de publicação | 8 |
| Funções de teste do serviço de publicação | 88 |

Testes que sustentam os padrões do caso (nomes originais, em português no código):

- **Modelo não bloqueia:** `test_degradacao_falha_lote_nao_levanta` (o modelo simulado levanta "timeout simulado"; as categorias saem com o tipo padrão, origem "tipo padrão" e status pendente) e `test_lote_que_falha_nao_derruba_os_demais`.
- **Cache de decisão:** `test_caching_segundo_run_nao_chama_llm` (a primeira execução chama o modelo uma vez; a segunda, com a mesma categoria, não chama de novo: a contagem de chamadas continua 1, e a categoria sai associada pelo de-para) e `test_idempotencia_input_estavel`.
- **Limiar de confiança:** `test_canal_a_confiavel_aplica_categoria`, `test_canal_a_fraco_com_canal_b_grava_observacao`, `test_limiar_governado_global`, `test_limiar_subido_inverte_caso` e `test_override_provedor_prevalece`.
- **Guardrail e invariante do tipo:** `test_guardrail_canal_a_fora_taxonomia_vai_<tipo padrão>` (nome fora da taxonomia vai ao tipo padrão; o sufixo original, que nomeia o tipo, foi retirado) e `test_invariante_tipo_deriva_da_categoria`.
- **Contrato selado com contexto governável:** `test_esqueleto_selado_carrega_workflow_always_emit`, `test_contexto_canal_a_do_banco_entra_no_slot_de_classificacao` e `test_contexto_canal_b_do_banco_entra_no_slot_de_sugestao`.
- **Lote e reserva:** `test_lote_grande_e_particionado_em_varias_chamadas`, `test_fallback_habilitado_resolve_so_o_subconjunto_vazio` e `test_fallback_nao_chamado_quando_primario_resolve_tudo`.
- **Saída imutável:** `test_objeto_ja_publicado_nunca_sobrescreve`, `test_destino_existente_e_registrado_bloqueia`, `test_orfao_identico_pode_ser_regravado`, `test_orfao_divergente_bloqueia` e `test_falha_no_disparo_de_webhook_nao_derruba_a_publicacao`.

Os testes do motor simulam o modelo (substituem a chamada por um objeto de teste). Na busca por "eval", "golden" e "acurácia" nas specs, nos planos e nos testes da classificação, nenhum conjunto de avaliação da qualidade do modelo foi encontrado.
