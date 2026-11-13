# Plano de implementação: piloto RDF

> Execução por subagentes autorizada por Thiago; aplicar `subagent-driven-development` ou
> `executing-plans` tarefa a tarefa. Este plano é o único rastreamento de progresso.

**Objetivo:** publicar opcionalmente RDF determinístico e descoberta por agentes, explicados
por uma página visual curada, mantendo a consulta e o build estático atuais.
**Arquitetura:** o grafo de catálogo alimenta um contrato compartilhado de classes/relações,
um exportador puro e os diagramas. O pacote incorpora os arquivos antes de calcular seu
manifesto; a emissão permanece dentro da transação atômica existente.
**Stack:** Python 3.11+, biblioteca padrão na produção/consulta, Jinja2, HTML/SVG/CSS;
`rdflib==7.1.4` somente em `requirements-dev.txt` para leitura independente nos testes.
**Tier:** 2. **Branch:** `feat/2026-11-12-piloto-rdf`, worktree isolado `3d77`.
**Contrato:** [spec aprovada](../specs/2026-11-12-piloto-rdf-delta.md),
[PRD aprovado](../prd/2026-11-12-piloto-rdf.md), [ADR aceita](../adr/0016-exportacao-semantica-do-catalogo.md).
**Checkpoint inicial:** Thiago aprovou os três documentos em 2026-11-12 e autorizou execução.

## Impacto Arquitetural

- Compose local será alterado? Não; nenhum serviço de produção é acrescentado.
- Algum módulo IaC será criado ou alterado? Não; publicação permanece estática.
- Diagrama e manifesto de infraestrutura precisam de atualização? N/A; não há mapa aplicável
  ao piloto. Os diagramas novos são conteúdo do portal, não governança.
- Schema editorial, contratos JSON existentes e consulta não mudam. Mudança aditiva minor.
- `portal/` e `scripts/` exigem duas aprovações para integração. A autorização para implementar
  não substitui essas aprovações; preparar entrega verificável antes do gate de merge.

## Fronteiras e arquivos exatos

Executar exportador/integração antes de conteúdo/visual: ambos tocam `renderizar.py` e
`saidas.py`. Avaliação WebVOWL usa o vocabulário produzido, sem modificar produção.

| Frente | Criar | Alterar |
| --- | --- | --- |
| Contrato e exportação | `portal/gerador/modelo_semantico.py`, `portal/gerador/semantica.py`, `tests/unidade/test_semantica.py` | `requirements-dev.txt` |
| Integração | `tests/integracao/test_semantica.py` | `portal/gerador/build.py`, `portal/gerador/renderizar.py`, `portal/gerador/pacote.py`, `portal/gerador/saidas.py`, `scripts/gerar.py`, `tests/unidade/test_build_atomico.py` |
| Conteúdo e visual | `paginas/modelo-de-conhecimento.md`, `verificacoes/modelo-de-conhecimento.yaml`, `portal/gerador/modelo_conhecimento.py`, `portal/templates/modelo-conhecimento.html`, `tests/unidade/test_modelo_conhecimento.py` | `portal/gerador/renderizar.py`, `portal/gerador/saidas.py`, `portal/tema/tema.css` |
| Fontes curadas | `referencias/w3c-rdf11.yaml`, `referencias/w3c-rdfs.yaml`, `referencias/w3c-owl2-primer.yaml`, `referencias/w3c-jsonld11.yaml`, `referencias/w3c-turtle.yaml`, `referencias/w3c-skos-primer.yaml`, `referencias/w3c-shacl.yaml`, `referencias/webvowl.yaml`, `referencias/owl2vowl.yaml` | somente reutilizar referência existente se URL/id já catalogados; registrar essa resolução neste plano |
| Evidências e release | `docs/PROJECT_MEMORY.md` apenas ao encerrar sessão complexa | este plano, `CHANGELOG.md`, `portal/config.yml`, spec ao arquivar |

Saídas como `public/`, `README.md` e `ROTEAMENTO.md` são geradas exclusivamente pelo comando.
Artefatos temporários da avaliação ficam em `/tmp/piloto-rdf-webvowl/`; o registro durável
comandos/versões/resultados fica neste plano, sem arquivo paralelo de tarefas.

### Interfaces entre frentes

```python
# modelo_semantico.py: nenhum import de Site/renderizar, para evitar ciclo.
CLASSES: dict[str, str]  # tipo original -> nome de classe; fallback RecursoAplicavel
RELACOES: tuple[dict[str, str], ...]  # origem, relacao, destino, propriedade, descricao

# semantica.py: somente biblioteca padrão, resultado sem escrita em disco.
def validar_base_rdf(base: str) -> str: ...  # ValueError diagnosticado

def iri_entidade(base: str, id_: str) -> str: ...

def montar_semantica(
    grafo: dict, *, base_rdf: str, versao: str, commit: str
) -> dict[str, bytes]: ...  # chaves semantica/manifesto.json etc. relativas ao pacote

# modelo_conhecimento.py: obtém exemplos do grafo e relações do contrato comum.
def contexto_modelo(grafo: dict, *, base_rdf: str | None) -> dict: ...
```

Acrescentar `base_rdf: str | None = None` a `Site`, `montar_site` e `construir`, mantendo
os parâmetros atuais. `scripts/gerar.py` valida `--base-rdf` imediatamente após parse_args,
antes de limpeza/escrita. `montar_pacote` chama `montar_semantica` somente quando ativa.
`llms_txt` publica caminho relativo `pacote/semantica/manifesto.json` somente quando ativa.
O componente visual recebe `contexto_modelo(montar_grafo(site), base_rdf=site.base_rdf)` por
import local quando necessário para evitar ciclo com `grafo_catalogo`.

## Tarefa 1 — Contrato, identidades e exportador puro

- [x] Escrever `test_semantica.py` com fixture cobrindo os 12 pares concretos da tabela da
  spec, tipos genéricos de aplica e caracteres especiais em ID/literais; cada teste cita R<n>.
  Incluir casos negativos para duplicata, destino ausente e combinação incompatível. (R2, R3, R7, R8)
- [x] Executar `python -m pytest tests/unidade/test_semantica.py -q`; registrar falha inicial
  por módulo/função ainda ausente, e depois falhas de comportamento específicas. (R2, R3, R7)
- [x] Implementar contrato compartilhado e `validar_base_rdf`, `iri_entidade`, `montar_semantica`.
  Base exige HTTPS absoluto, hostname, `/` final e ausência de credenciais/query/fragmento.
  IRI usa `quote(id_, safe='-._~')`; hash da afirmação usa JSON UTF-8 compacto de
  `[source,target,relation]`, `ensure_ascii=False`, `separators=(',', ':')`. (R2, R3, R7)
- [x] Exportar vocabulário sem instâncias, dados Turtle e JSON-LD com contexto embutido;
  classes recebem Entidade e classe específica, rótulos/descrições pt-BR, URL como IRI,
  campos opcionais ausentes não são inventados. Serializar a partir de uma estrutura comum
  ordenada, escapando literais sem avaliar marcação ou seguir URLs. (R3, R4, R8)
- [x] Exportar manifesto versão 1, índice por ID e recorte por hash do ID; recorte tem entidade,
  vizinhos mínimos, arestas incidentes e registros rdf:Statement sem expansão recursiva.
  Manifesto aponta `../grafo/graph.json` e `../consultar.py`, lista mídia/capacidades/limites,
  mudança de identidade ao trocar base e aproximação de quatro caracteres por token. (R5, R6)
- [x] Fixar parser independente de teste e provar isomorfismo, reconstrução exata dos IDs e
  tuplas com fontes, igualdade byte a byte com entrada invertida e identidade estável ao
  variar commit/URL/pasta; dados não têm contextos remotos/importações. (R2, R3, R4, R8)
- [x] Rodar testes completos e `python -m ruff check .`, colar resultados e criar commit
  `feat(semantica): exportar contrato RDF deterministico`. (R2, R3, R4, R7, R8)

Exemplo de teste contratual mínimo, a ampliar com a fixture completa acima:

```python
def test_r2_id_inteiro_sem_normalizacao():
    from portal.gerador.semantica import iri_entidade
    base = 'https://example.org/padroes/'
    assert iri_entidade(base, 'A/á:%') == base + 'id/A%2F%C3%A1%3A%25'
    assert iri_entidade(base, 'á') != iri_entidade(base, 'a')
```

## Tarefa 2 — CLI, pacote e consumo independente

- [x] Criar testes de ativação/desativação e base inválida na CLI. Sem opção, ausência de
  semantica/ e anúncio; com opção, arquivos cobertos pelos hashes do manifesto do pacote.
  Rodar testes antes de alterar integração e registrar o vermelho. (R1, R5)
- [x] Propagar parâmetro opcional pelas interfaces acima e incluir artefatos no pacote;
  preservar ordenação, contratos e defaults existentes. Anunciar manifesto em llms.txt. (R1, R5)
- [x] Injetar erro de exportação em teste de build atômico com sentinela na saída anterior:
  verificar sentinela intacta e ausência de `.tmp` após erro; erro inclui ID/campo/fonte.
  Testar base inválida antes de qualquer escrita e erro de entrada real além da injeção. (R1, R7)
- [x] Criar consumidor de teste somente com biblioteca padrão, sem importar gerador;
  descobrir manifesto via llms.txt, índice e referência pelo recorte, em diretório local
  e servidor HTTP loopback. Registrar arquivos e bytes lidos e caracteres devolvidos;
  comprovar que catálogo completo não foi lido. (R5, R6)
- [x] Demonstrar com fixture conhecida prática→referência, conceito→prática→ferramenta e
  prática→célula→domínio/momento; afirmar direção, IDs, fonte e ausência de relação.
  Comparar com consulta atual e executar seus testes de orçamento sem mudar a consulta. (R6)
- [x] Desabilitar conexões externas nos testes de build/parser/consulta, permitindo loopback
  apenas no teste HTTP; garantir strings hostis preservadas como dados. (R8)
- [x] Executar `python -m pytest tests/integracao/test_semantica.py tests/unidade/test_build_atomico.py -q`
  (o arquivo ficou `tests/integracao/test_semantica_integracao.py`: o nome do plano colide com
  `tests/unidade/test_semantica.py` na coleta, pois `tests/` não tem `__init__.py`),
  suíte completa e lint; registrar evidências e commit `feat(portal): integrar piloto RDF opcional`. (R1, R5, R6, R7, R8)

Checkpoint de fase: apresentar resultados intermediários a Thiago. A execução está autorizada;
retorno à aprovação só é necessário se o contrato se mostrar inviável ou mudar.

## Tarefa 3 — Curadoria e referência visual

- [x] Ler `skills/curadoria-de-pratica/SKILL.md`, conferir na web as nove fontes primárias
  listadas na spec e preencher referências/registros com data, afirmações e trechos de suporte.
  Corpo editorial em português com citações `[ref:<id>]` em cada afirmação factual. (R11)
- [x] Criar testes que exigem página/navegação Entender, três diagramas, legenda/alternativa
  textual, links válidos nos modos ativo/inativo, escape de HTML e mapeamento compartilhado.
  Rodar os testes e registrar falha antes de criar componente. (R10, R11, R8)
- [x] Criar página curada, componente de contexto, template e CSS; renderizar relações da
  tabela comum e selecionar exemplos reais por ordem de ID. Relação sem ocorrência mostra
  ausência; nunca inventa exemplo. Cada relação pode ser focada/expandida por teclado
  via HTML nativo, exibindo significado, origem e exemplo. (R10, R11)
- [x] Painel 1 diferencia classe/instância e todos os vínculos. Painel 2 apresenta tripla RDF,
  JSON-LD/Turtle paralelos, OWL sem raciocinador e SKOS/SHACL explicitamente futuros.
  Painel 3 mostra descoberta e fontes, limite de consulta e estado RDF indisponível quando
  desativado; não renderizar links sem artefato. Texto distingue vínculo de verdade factual. (R10, R11)
- [x] Inspecionar navegador a 375 e 1280 px, Tab/Enter, foco, legendas, contraste e ausência
  de significado apenas por cor; registrar capturas e resultado no plano. Reexecutar
  testes completos/lint e commit `feat(portal): explicar modelo de conhecimento em diagramas`. (R8, R10, R11)

## Tarefa 4 — Avaliação WebVOWL separada

- [ ] Obter versão/commit exatos de OWL2VOWL e WebVOWL e registrar sua procedência aqui.
  Produzir vocabulário com a CLI usando base ilustrativa; converter esse arquivo pelo
  conversor real, registrando comando completo, versões Java/conversor, entrada e saída. (R9)
- [ ] Abrir JSON convertido no WebVOWL local ou serviço disponível, inspecionar visualmente
  classes e propriedades; guardar captura, hash da entrada/saída e resultado neste plano.
  Se conversão incompatível, parar esta entrega e voltar à spec; Turtle válido não encerra R9. (R9)
- [ ] Confirmar build/CI sem conversor ou serviço externo e registrar que visualização
  não valida verdade factual, inferência ou completude dos dados. (R8, R9)

## Tarefa 5 — Verificação, revisão e entrega

- [ ] Rodar `python -m pytest -q`, `python -m ruff check .`, `python scripts/validar.py`,
  `python scripts/gerar.py` e build ativo com `--base-rdf https://example.org/padroes/`.
  Colar saídas/status reais nesta seção; os quatro comandos obrigatórios devem retornar 0. (R1, R4, R8, R11)
- [ ] Solicitar revisão adversarial independente partindo de R1–R11; preencher tabela abaixo
  com arquivo:linha ou saída de teste, tratar achados e repetir apenas verificações afetadas. (R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11)
- [ ] Atualizar `CHANGELOG.md` em Keep a Changelog e minor em `portal/config.yml`, conferir
  versão mais recente antes da integração; arquivar spec somente ao concluir requisitos.
  Destilar aprendizados operacionais em `docs/PROJECT_MEMORY.md`. (R1, R11)
- [ ] Preparar MR com evidências, limites e duas aprovações de risco alto antes de merge;
  não confundir aprovação da spec com revisão de implementação. (R1, R11)

## Evidências

Registro inicial: constituição/skill/spec/PRD/ADR e módulos de build, grafo, emissão e pacote
lidos. `docs/PROJECT_MEMORY.md` não existe nesta base. Testes de implementação ainda não
executados por esta etapa de planejamento; não há declaração de suíte verde.
A execução local usa `python3` ou o Python do ambiente virtual, pois o alias `python` não
está instalado no shell; comandos acima usam `python` após ativação do ambiente.

### Tarefa 1 (2026-11-13)

Vermelho inicial, antes de existir `portal/gerador/semantica.py`:

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_semantica.py -q
E   ModuleNotFoundError: No module named 'portal.gerador.semantica'
ERROR tests/unidade/test_semantica.py
1 error in 0.20s
```

Primeira execução com o exportador: `2 failed, 36 passed`. As duas falhas eram expectativas
erradas do próprio teste (trecho "duplicada" contra a mensagem "vínculo duplicado", e idioma
`pt-br` contra `pt-BR`, que o rdflib preserva); corrigidas no teste, sem mudar o contrato.

Verde:

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_semantica.py -q
38 passed in 0.11s
$ /tmp/piloto-rdf-venv/bin/python -m pytest -q -p no:cacheprovider tests/unidade
978 passed in 23.80s
$ /tmp/piloto-rdf-venv/bin/ruff check .
All checks passed!
$ /tmp/piloto-rdf-venv/bin/ruff format --check portal/gerador/semantica.py portal/gerador/modelo_semantico.py tests/unidade/test_semantica.py
3 files already formatted
```

Suíte completa, rodada pela coordenação. Linha de base em `3ad4fd1` e depois em `76b9d32`
(os 38 testes novos; nenhuma falha):

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest -q -p no:cacheprovider   # 3ad4fd1
3200 passed in 306.07s (0:05:06)
$ /tmp/piloto-rdf-venv/bin/python -m pytest -q -p no:cacheprovider   # 76b9d32
3238 passed in 315.02s (0:05:15)
```

Revisão da tarefa e correção (`939943a`): `indice.json` passou a ser a lista ordenada por ID,
classes e propriedades ganharam rótulo legível em pt-BR, campo obrigatório ausente virou
`ValueError` diagnosticado e a base exige o prefixo literal `https://`.

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_semantica.py -q   # 939943a
47 passed in 0.11s
$ /tmp/piloto-rdf-venv/bin/ruff check .
All checks passed!
```

A suíte completa sobre `939943a` roda de novo ao fim da Tarefa 2.

### Tarefa 2 (2026-11-13)

Vermelho, antes de tocar a integração (testes novos em
`tests/integracao/test_semantica_integracao.py` e em `tests/unidade/test_build_atomico.py`):

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/integracao/test_semantica_integracao.py tests/unidade/test_build_atomico.py -q -p no:cacheprovider
E   TypeError: construir() got an unexpected keyword argument 'base_rdf'
E   AttributeError: <module 'portal.gerador.pacote' ...> has no attribute 'montar_semantica'
18 failed, 19 passed
```

Segundo vermelho, com a propagação feita mas `montar_site` ainda sem repassar `base_rdf` ao `Site`
(o build devolvia `[]` onde se esperava `R-SEMANTICA`): `10 failed, 27 passed`.

Verde, ruff e suíte completa:

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/integracao/test_semantica_integracao.py tests/unidade/test_build_atomico.py -q -p no:cacheprovider
37 passed in 5.73s
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_consultar.py tests/integracao/test_tokens_catalogo.py -q -p no:cacheprovider
19 passed in 2.86s        # consultar.py intacto (git diff vazio)
$ /tmp/piloto-rdf-venv/bin/ruff check .
All checks passed!
$ /tmp/piloto-rdf-venv/bin/ruff format --check <arquivos alterados>
8 files already formatted
$ /tmp/piloto-rdf-venv/bin/python -m pytest -q -p no:cacheprovider
3273 passed in 312.62s (0:05:12)
```

Catálogo real, em pasta temporária (nada gravado em `public/` nem na raiz):

```
$ /tmp/piloto-rdf-venv/bin/python scripts/gerar.py --saida /tmp/t2-real/site --previa \
    --base-rdf https://example.org/padroes/ --url-base https://exemplo.pages.exemplo/padroes
PRÉVIA, não publicada: portal gerado em /private/tmp/t2-real/site (versão 1.3.0, commit 0123456, 2026-11-13).
```

496 entidades exportadas sem erro; `varrer_externos` sobre o site inteiro devolve `[]` (R-EXTERNO só
inspeciona `.html` e `.css`, então `.ttl`, `.jsonld` e `.json` não são alvo).
Os caminhos `../grafo/graph.json` e `../consultar.py` do manifesto semântico resolvem para
`pacote/grafo/graph.json` e `pacote/consultar.py`; `consultar.py "migration já aplicada" --budget 300`
roda e responde.

Medição do percurso prática → referência no catálogo real (DAD-01 cita referências), por
`Consumidor` (só biblioteca padrão) sobre a pasta gerada:

| Leitura | Arquivos | Bytes lidos | Caracteres devolvidos |
| --- | --- | --- | --- |
| Semântica: llms.txt, manifesto, índice, entidade DAD-01 e recorte da referência | 5 | 214137 (llms 39473, manifesto 2450, índice 147052, entidades 21716 e 3446) | 990 |
| Consulta atual: `consultar.py "migration já aplicada"` | 1 (`graph.json`) | 476586 | 1046 |

Catálogo completo, não lido pelo consumidor: `catalogo.ttl` 617142 bytes, `catalogo.jsonld` 710017
e `graph.json` 476586. Sem promessa de redução: o índice (147052 bytes) domina a leitura e os
dois percursos respondem a perguntas diferentes (a consulta ranqueia por texto; o recorte segue
vínculos declarados, com direção e fonte).

### Tarefa 3 (2026-11-13)

Vermelho 1, antes de existir o componente:

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_modelo_conhecimento.py -q -p no:cacheprovider
E   ImportError: cannot import name 'modelo_conhecimento' from 'portal.gerador'
1 error in 0.08s
```

Vermelho 2, com `modelo_conhecimento.py` pronto e a página ainda no template genérico (sem
navegação, template nem `.md` próprio): `15 failed, 6 passed`. Passavam só os testes do
contexto puro (contrato, propriedade inventada, relação sem desenho, exemplo por ordem de ID).

Verde, lint, validação e suíte:

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_modelo_conhecimento.py -q -p no:cacheprovider
21 passed
$ /tmp/piloto-rdf-venv/bin/ruff check .
All checks passed!
$ /tmp/piloto-rdf-venv/bin/ruff format --check portal/gerador/modelo_conhecimento.py portal/gerador/renderizar.py portal/gerador/saidas.py tests/unidade/test_modelo_conhecimento.py
4 files already formatted
$ /tmp/piloto-rdf-venv/bin/python scripts/validar.py
aviso: praticas/construir-com-ia/P1-12.md: Exemplo recomendado ausente (status experimentar ou avaliar)
validação ok: nenhum erro.
$ /tmp/piloto-rdf-venv/bin/python -m pytest -q -p no:cacheprovider
3294 passed in 310.74s (0:05:10)
```

`README.md` mudou só na contagem de referências (431 → 440): regravado por
`scripts/gerar.py --saida /tmp/piloto-rdf-visual/oficial` (sem `--previa`), não à mão; sem isso
`validar.py` reprovava com `R-GERADO-DIVERGENTE`. `ROTEAMENTO.md` não mudou.

Resolução de referências: nenhuma das nove URLs nem IDs estava catalogada em `referencias/`;
as nove são novas.

Fontes conferidas na web em 2026-11-13:

| id | URL | trecho de suporte |
| --- | --- | --- |
| w3c-rdf11 | https://www.w3.org/TR/rdf11-concepts/ | §1.1 e §3/§3.1: tripla de sujeito, predicado e objeto; "An RDF graph is a set of RDF triples" (Rec. 2014-02-25) |
| w3c-rdfs | https://www.w3.org/TR/rdf-schema/ | §1: "data-modelling vocabulary for RDF data"; §2: recursos em classes; §3.3: `R rdf:type C`; §3.6/§3.7: label e comment (Rec. 2014-02-25) |
| w3c-owl2-primer | https://www.w3.org/TR/owl2-primer/ | Abstract: classes, propriedades, indivíduos; §3: "reasoners – that can automatically compute consequences" (Rec. 2012-12-11) |
| w3c-jsonld11 | https://www.w3.org/TR/json-ld11/ | Abstract: formato baseado em JSON para Linked Data; §1.5: sempre JSON válido; §3.1: contexto mapeia termos para IRIs (Rec. 2020-07-16) |
| w3c-turtle | https://www.w3.org/TR/turtle/ | Abstract: sintaxe textual RDF; grafo inteiro em forma de texto compacta (Rec. 2014-02-25) |
| w3c-skos-primer | https://www.w3.org/TR/skos-primer/ | Abstract e §2.1–2.3: modelo de esquemas de conceitos, prefLabel/altLabel, broader/narrower/related (Note 2009-08-18) |
| w3c-shacl | https://www.w3.org/TR/shacl/ | Abstract: linguagem para validar grafos RDF contra condições (shapes) (Rec. 2017-07-20) |
| webvowl | https://github.com/VisualDataWeb/WebVOWL | descrição "Visualizing ontologies on the Web"; README aponta https://service.tib.eu/webvowl/ e avisa que o domínio antigo não é mais do projeto (não citado) |
| owl2vowl | https://github.com/VisualDataWeb/OWL2VOWL | descrição "Converting ontologies for WebVOWL"; README: saída em `.json`, uso `-file` |

Inspeção de navegador (Chrome headless via Playwright, `http.server` em 127.0.0.1, sites em
`/tmp/piloto-rdf-visual/inativo` e `/tmp/piloto-rdf-visual/ativo`, este com
`--base-rdf https://example.org/padroes/`; os dois com `--previa`):

| modo | largura | HTTP | scrollWidth ≤ clientWidth | console | Tab → relação → Enter | foco | links locais (todos 200) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inativo | 375 | 200 | 375 ≤ 375 | sem erro | `rel-1` abriu | contorno sólido 3px | 11 |
| inativo | 1280 | 200 | 1280 ≤ 1280 | sem erro | `rel-1` abriu | contorno sólido 3px | 11 |
| ativo | 375 | 200 | 375 ≤ 375 | sem erro | `rel-1` abriu | contorno sólido 3px | 17 |
| ativo | 1280 | 200 | 1280 ≤ 1280 | sem erro | `rel-1` abriu | contorno sólido 3px | 17 |

O tema não tem modo escuro; os pares de cor novos usam só tokens já conferidos em
`contraste.yml`. Futuro e indisponível são marcados por texto, traço pontilhado e hachura.
Correções feitas depois de olhar as capturas: caixa "Documento de conceito" estourava a largura
(caixas de 170 → 184 px, passo de 280 → 300), rótulo `temMomento` encostava nas caixas, números de
dois dígitos apertados no círculo, fontes `[n]` quebrando linha nos nós, número da etapa esticado
em toda a largura no painel 3 e falta de indicação "abrir/fechar" nos `summary` em flex.
Capturas finais em `/tmp/piloto-rdf-visual/capturas/` (página inteira `<modo>-<largura>.png`,
foco por teclado `<modo>-<largura>-teclado.png` e por painel `secao-<modo>-<largura>-*.png`).

## Revisão adversarial: 2026-11-12 — achados

Revisão ainda não realizada; preencher vereditos após inspecionar implementação contra spec.

| R | veredito | evidência |
| --- | --- | --- |
| R1 | não avaliado | implementação pendente |
| R2 | não avaliado | implementação pendente |
| R3 | não avaliado | implementação pendente |
| R4 | não avaliado | implementação pendente |
| R5 | não avaliado | implementação pendente |
| R6 | não avaliado | implementação pendente |
| R7 | não avaliado | implementação pendente |
| R8 | não avaliado | implementação pendente |
| R9 | não avaliado | avaliação real pendente |
| R10 | não avaliado | inspeção responsiva pendente |
| R11 | não avaliado | curadoria/implementação pendentes |
