Trecho redigido de código do motor de classificação, no commit fixado no registro de verificação. Lido em 2026-11-03. Os nomes de função, de variável, de tabela e de tipo foram trocados por equivalentes neutros, e o corpo foi reduzido ao que sustenta o caso; a lógica é a do original.

## A cascata determinística (resolvedor)

```python
def resolver_categoria(sessao, fornecedor, categoria_nativa):
    chave = normalizar(categoria_nativa)

    # Etapa 1: de-para direto (associação ativa)
    depara = carregar_depara(sessao, fornecedor)
    if chave in depara:
        return Resultado(depara[chave], origem="depara")

    # Etapa 2: o nome normalizado bate com uma categoria canônica
    taxonomia = carregar_taxonomia(sessao)
    if chave in taxonomia:
        return Resultado(taxonomia[chave], origem="normalizacao")

    # Etapa 3: órfã; o chamador leva ao modelo e, por fim, ao tipo padrão
    return Resultado(None, origem="indefinido")
```

## O núcleo que aplica a resposta do modelo às órfãs

```python
def resolver_orfas_com_modelo(sessao, fornecedor, orfas, taxonomia, sugestoes_orfas):
    limiar = 0.6                                   # padrão quando não há parâmetro
    parametro = carregar_parametro(sessao, "confianca_minima_canal_a", fornecedor)
    if parametro is not None:                      # override por fornecedor vence o global
        limiar = parametro

    try:
        resultados = classificar_com_modelo(sessao, fornecedor, orfas)
    except Exception as exc:
        # Degradação: qualquer falha do lote deixa o lote sem casamento;
        # a execução NÃO levanta.
        log.warning(f"{fornecedor}: falha no lote do modelo, degradando: {exc}")
        resultados = {}

    aplicadas = {}
    for nativa in orfas:
        r = resultados.get(nativa)
        if r is None or r.canal_a.nome is None:
            # Sem canal A usável: a sugestão do canal B, se houver, acompanha
            # a linha provisória na fila de revisão.
            if r is not None and r.canal_b is not None:
                sugestoes_orfas[nativa] = r.canal_b
            continue
        categoria = taxonomia_por_nome(taxonomia).get(r.canal_a.nome)
        if categoria is None:
            continue
        # Canal A aplicado (melhor palpite); o tipo deriva da categoria.
        observacao = None
        if r.canal_a.confianca < limiar and r.canal_b is not None:
            observacao = r.canal_b                  # sugestão registrada para revisão
        registrar_associacao(sessao, fornecedor, nativa, categoria,
                             status="ASSOCIADA", origem="modelo",
                             observacao=observacao)
        aplicadas[nativa] = categoria
    return aplicadas
```

## O que o motor faz com o que não casou

```python
for nativa in orfas:
    if nativa in aplicadas:
        mapa[nativa] = Resolucao(aplicadas[nativa], origem="modelo", status="ASSOCIADA")
        continue
    # Tipo padrão (o de menor valor), provisório: não bloqueia o pipeline e
    # vai para a fila de revisão; a sugestão do canal B, se houver, vai junto.
    origem_da_orfa = "modelo" if nativa in sugestoes_orfas else "tipo_padrao"
    registrar_associacao(sessao, fornecedor, nativa, None,
                         status="PENDENTE", origem=origem_da_orfa,
                         observacao=sugestoes_orfas.get(nativa))
    mapa[nativa] = Resolucao(None, tipo=TIPO_PADRAO, origem="tipo_padrao",
                             status="PENDENTE")
```

A etapa do modelo só roda com a flag de configuração ligada (padrão: ligada); desligada, a cascata é inteiramente determinística.
