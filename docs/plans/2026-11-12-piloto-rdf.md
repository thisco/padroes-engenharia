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
| Integração | `tests/integracao/test_semantica_integracao.py` | `portal/gerador/build.py`, `portal/gerador/renderizar.py`, `portal/gerador/pacote.py`, `portal/gerador/saidas.py`, `scripts/gerar.py`, `tests/unidade/test_build_atomico.py` |
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
- [x] Executar `python -m pytest tests/integracao/test_semantica_integracao.py tests/unidade/test_build_atomico.py -q`
  (o nome `tests/integracao/test_semantica.py`, previsto no rascunho, colidiria com
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

- [x] Obter versão/commit exatos de OWL2VOWL e WebVOWL e registrar sua procedência aqui.
  Produzir vocabulário com a CLI usando base ilustrativa; converter esse arquivo pelo
  conversor real, registrando comando completo, versões Java/conversor, entrada e saída. (R9)
- [x] Abrir JSON convertido no WebVOWL local ou serviço disponível, inspecionar visualmente
  classes e propriedades; guardar captura, hash da entrada/saída e resultado neste plano.
  Se conversão incompatível, parar esta entrega e voltar à spec; Turtle válido não encerra R9. (R9)
- [x] Confirmar build/CI sem conversor ou serviço externo e registrar que visualização
  não valida verdade factual, inferência ou completude dos dados. (R8, R9)

## Tarefa 5 — Verificação, revisão e entrega

- [x] Rodar `python -m pytest -q`, `python -m ruff check .`, `python scripts/validar.py`,
  `python scripts/gerar.py` e build ativo com `--base-rdf https://example.org/padroes/`.
  Colar saídas/status reais nesta seção; os quatro comandos obrigatórios devem retornar 0. (R1, R4, R8, R11)
- [x] Solicitar revisão adversarial independente partindo de R1–R11; preencher tabela abaixo
  com arquivo:linha ou saída de teste, tratar achados e repetir apenas verificações afetadas. (R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11)
- [x] Atualizar `CHANGELOG.md` em Keep a Changelog e minor em `portal/config.yml`, conferir
  versão mais recente antes da integração; arquivar spec somente ao concluir requisitos.
  Destilar aprendizados operacionais em `docs/PROJECT_MEMORY.md`. (R1, R11)
- [x] Preparar MR com evidências, limites e duas aprovações de risco alto antes de merge;
  não confundir aprovação da spec com revisão de implementação. (R1, R11)
  Texto preparado em `.superpowers/sdd/2026-11-12-piloto-rdf/mr.md`; nenhum MR foi aberto e as duas
  aprovações de risco alto seguem pendentes com o dono (Thiago).

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

### Tarefa 4 (2026-11-13)

Avaliação feita fora do repositório; nenhum arquivo versionado mudou. Artefatos em
`/tmp/piloto-rdf-webvowl/`.

Procedência:

| item | valor |
| --- | --- |
| OWL2VOWL | 0.3.7, tag `0.3.7` = commit `2833ead00122ca252a0fd0e18c5e5b696d711d2c`; o tarball desse commit, comparado por `diff -rq` com a cópia compilada, difere só em `target/` |
| WebVOWL | 1.1.7, tag `v1.1.7` = commit `28e7dd9540622e8cb723dc000824b5eef5ae775f` |
| JAR | `OWL2VOWL-0.3.7-shaded.jar`, sha256 `dc505307ccc1bcf984b76c59662da671750781ac0f74cce32b382180a83086ff` (Maven 3.9.11) |
| Java | Temurin 17.0.18+8 com `--add-opens java.base/java.lang=ALL-UNNAMED` |
| Navegador | Chrome 157 headless via Playwright 1.58.2 |
| Portal | HEAD `709b8a3`, versão 1.3.0 |

Entrada, gerada pela CLI com base ilustrativa:

```
python scripts/gerar.py --saida /tmp/piloto-rdf-webvowl/site --base-rdf https://example.org/padroes/
```

`pacote/semantica/vocabulario.ttl`: 210 linhas, sha256
`161b4c0e111e36af8f88eca713c8c62497923b09e3972fe54a8710be300528e7`. Contém 12 classes (11
subclasses de `Entidade`), 10 propriedades de objeto relacionais, 7 de dados, `url`, `recorte` e
`relacaoOrigem`, com rótulos e comentários `@pt-BR`.

Conversão (rc=0; único aviso é o do log4j2 sem configuração):

```
JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home \
$JAVA_HOME/bin/java --add-opens java.base/java.lang=ALL-UNNAMED \
  -jar OWL2VOWL-0.3.7-shaded.jar \
  -file /tmp/piloto-rdf-webvowl/vocabulario.ttl \
  -output /tmp/piloto-rdf-webvowl/conv/vocabulario.json
```

Sem `--add-opens`, com Java 17 ou 25, o conversor falha em `OWLManager.createOWLOntologyManager`
(`InaccessibleObjectException` do Guice embutido). A falha acontece antes de ler o vocabulário,
então não é incompatibilidade do Turtle. Os logs estão em `conv/tentativa-*.log`.

Saída: `vocabulario.json` com 18630 bytes, sha256
`042420331086e6e89d2a9a9e8ae32613050ff00d6c0594ccea0d1104df712306`. Ela traz as 12 classes, as 10
propriedades relacionais e as 7 de dados, com domínio e alcance idênticos aos do Turtle e
rótulos pt-br.

Inspeção visual: WebVOWL 1.1.7 local (`http.server` em 127.0.0.1) a 1280×900. Renderizou 26 nós
sem erro no console nem requisição falha. Classes e propriedades estão visíveis, e `Entidade`
fica ao centro com as subclasses. Capturas:

- `webvowl-01-grafo.png`: carga inicial;
- `webvowl-02-pt-br-selecionado.png`: depois de escolher o idioma pt-br;
- `webvowl-03-pratica-selecionada.png`: com o nó Prática selecionado.

Limitações e distorções:

- Propriedades de dados sem `rdfs:range` viram nós sintéticos `Literal`.
- `url` e `recorte` apontam para `owl:Thing`.
- `relacaoOrigem` aparece isolada, porque `rdf:Statement` não é desenhado.
- O cabeçalho mostra "No title available", pois a ontologia não declara título.
- Os rótulos pt-BR só aparecem depois de escolher pt-br no seletor.
- Há nós sobrepostos e "Documento de conceito" aparece truncado no layout de forças.

A inspeção confere a estrutura do vocabulário. Não prova a verdade factual dos dados, nem
inferência, nem completude.

Build e CI independentes: a busca por `owl2vowl|webvowl|java|jdk` em `.github/`, `.gitlab-ci.yml`,
`requirements*.txt`, `Makefile`, `portal/gerador/` e `scripts/` não acha nenhuma dependência do
conversor, de Java ou de serviço externo. As únicas ocorrências são a extensão `.java` em listas
de verificadores e as menções em documentos. Do serviço público https://service.tib.eu/webvowl/
só foi registrada a disponibilidade (HTTP 200); nada foi enviado a ele.

### Correções da revisão final (2026-11-14)

A revisão final independente (base `279b064..a32e9c6`) pediu uma onda única de correções. Itens
corrigidos, em `6a9ea80`, `62e81f9` e `125d0e1`:

| item | correção |
| --- | --- |
| I1 | `arquivoFonte` ficou sem `rdfs:domain` (`PROPRIEDADES_SEM_DOMINIO` em `modelo_semantico.py`), com `rdfs:comment` dizendo que vale para a entidade e para a afirmação; `relacaoOrigem` segue com domínio `rdf:Statement` |
| I2 | sem `--base-rdf`, a tripla de exemplo do painel 2 usa `BASE_ILUSTRATIVA` (`https://example.org/padroes/`), rotulada na página como base ilustrativa; com `--base-rdf`, a base real |
| I3 | `revisao_adversarial` de `verificacoes/modelo-de-conhecimento.yaml` registra a revisão independente de 2026-11-14: 18 afirmações confirmadas, a afirmação 4 imprecisa e os achados I1 e I2 |
| C4 | afirmação 4 reescrita na página e no registro ("que podem ser usados para dar nome e descrição legíveis a um recurso"), conferida de novo contra RDFS §3.6 e §3.7 em 2026-11-14 |
| M1 | texto alternativo do painel 2 descreve só o que está desenhado (setas monta, publica e avaliação fora do build; caixas futuras sem seta); a legenda não diz mais "de baixo" |
| M2 | abaixo de 900 px o rótulo da caixa OWL e RDFS vira "descreve o grafo validado", sem seta |
| M3 | grupo JSON-LD/Turtle recebe `mc-indisponivel` (hachura, borda pontilhada e o texto "indisponíveis neste build") no modo inativo |
| M4 | link do painel 3 rotulado "recorte JSON-LD de <ID>" |
| R-Mn2 | nota na legenda do painel 1 (e no `.md` gêmeo): `aplica` também liga a Recurso aplicável (`pe:RecursoAplicavel`), com a contagem tirada do grafo (20 neste catálogo) |
| R-Mn3 | legenda diz "um número que corresponde à mesma relação na lista" |
| M7 | o teste do `.md` gêmeo afirma que a marcação hostil fica em item de lista, sem linha iniciada por `<`, e que os títulos não mudam |
| P1 | o plano cita `tests/integracao/test_semantica_integracao.py` |

Desvio registrado (R-Mn2): a spec §5 desenha `aplica` → "Recurso aplicável" no painel 1, mas
`CAIXAS` não tem caixa para `RecursoAplicavel`; a seta `aplica` chega a `Entidade`, como no
contrato. Por decisão da coordenação, sem caixa nova: a legenda do painel 1 explica que `aplica`
também liga a Recurso aplicável (skills e steering), com o termo `pe:RecursoAplicavel`.

Vermelho → verde de I1 (`test_r4_afirmacao_nao_vira_entidade_pelo_dominio_das_propriedades`):

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_semantica.py -k afirmacao_nao_vira -q
E   AssertionError: (rdflib.term.URIRef('https://example.org/padroes/vocab#arquivoFonte'), [rdflib.term.URIRef('https://example.org/padroes/vocab#Entidade')])
1 failed, 47 deselected in 0.09s
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_semantica.py -q
48 passed in 0.12s
```

Vermelho → verde de I2 (`test_r10_painel_2_exemplos_sao_rdf_valido_e_isomorfos`, ativo e
inativo; no vermelho, o caso inativo usou a base esperada literal, porque a constante ainda não
existia):

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_modelo_conhecimento.py -q -k exemplos
E         Extra items in the left set:
E         (rdflib.term.URIRef('file:///Users/thiago/.codex/worktrees/3d77/padroes-engenharia/id/P1-01'), ...
1 failed, 1 passed, 20 deselected in 0.17s
$ /tmp/piloto-rdf-venv/bin/python -m pytest tests/unidade/test_modelo_conhecimento.py -q
22 passed in 8.02s
```

O IRI relativo do modo inativo virava `file://` da pasta de trabalho ao ser lido: o exemplo não
era RDF autônomo. Com os testes dos itens de página, o arquivo ficou com 25 testes.

Inspeção de navegador (Chrome headless via Playwright, `http.server` em 127.0.0.1, sites
`--previa` em `/tmp/piloto-rdf-visual/correcoes/{inativo,ativo}`, este com
`--base-rdf https://example.org/padroes/`; servidores encerrados pelo PID):

| modo | largura | HTTP | sem rolagem horizontal | grupo JSON-LD/Turtle | rótulo OWL e RDFS | link do recorte | console | links locais (todos 200) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inativo | 375 | 200 | 375 ≤ 375 | hachurado, pontilhado | "descreve o grafo validado" | "recorte JSON-LD de API-01: indisponível" | sem erro | 11 |
| inativo | 1280 | 200 | 1280 ≤ 1280 | hachurado, pontilhado | "↑ descreve o grafo" | "recorte JSON-LD de API-01: indisponível" | sem erro | 11 |
| ativo | 375 | 200 | 375 ≤ 375 | sólido | "descreve o grafo validado" | "recorte JSON-LD de API-01" | sem erro | 17 |
| ativo | 1280 | 200 | 1280 ≤ 1280 | sólido | "↑ descreve o grafo" | "recorte JSON-LD de API-01" | sem erro | 17 |

Capturas em `/tmp/piloto-rdf-visual/capturas-correcoes/` (página inteira `<modo>-<largura>.png`
e recortes `secao-<modo>-<largura>-{legenda-1,painel-2,painel-3}.png`).

Verificação final:

```
$ /tmp/piloto-rdf-venv/bin/python -m pytest -q -p no:cacheprovider
3299 passed in 318.19s (0:05:18)
$ /tmp/piloto-rdf-venv/bin/python -m ruff check .
All checks passed!
$ /tmp/piloto-rdf-venv/bin/python -m ruff format --check .
534 files already formatted
$ /tmp/piloto-rdf-venv/bin/python scripts/validar.py
aviso: praticas/construir-com-ia/P1-12.md: Exemplo recomendado ausente (status experimentar ou avaliar)
validação ok: nenhum erro.
```

### Tarefa 5 (2026-11-16)

Verificação na raiz do worktree, com `/tmp/piloto-rdf-venv/bin/python`, sobre `e709ecd`
(antes do bump) e de novo com a versão 1.4.0 aplicada.

```
$ python -m pytest -q          # sobre e709ecd
3299 passed in 357.77s (0:05:57)            exit 0
$ python -m ruff check .
All checks passed!                          exit 0
$ python -m ruff format --check .
534 files already formatted                 exit 0
$ python scripts/validar.py
aviso: praticas/construir-com-ia/P1-12.md: Exemplo recomendado ausente (status experimentar ou avaliar)
validação ok: nenhum erro.                  exit 0
$ python scripts/gerar.py       # padrão grava em public/ (ignorado pelo git) e regrava README.md/ROTEAMENTO.md
portal gerado em .../padroes-engenharia/public (versão 1.4.0, commit e709ecd, 2026-11-14).   exit 0
$ python scripts/gerar.py --saida /tmp/t5/ativo --base-rdf https://example.org/padroes/
portal gerado em /private/tmp/t5/ativo (versão 1.4.0, commit e709ecd, 2026-11-14).           exit 0
```

O build ativo produziu 499 arquivos `.ttl`/`.jsonld` (vocabulário, dados, recortes). Depois do
`gerar.py` padrão, `git status` mostrou só `README.md` e `ROTEAMENTO.md` regravados (versão
1.3.0 → 1.4.0 na primeira linha de cada um); `public/` está no `.gitignore`. A rodada final
completa, com a 1.4.0, está em "Rodada final" abaixo.

Decisões da entrega:

- Versão: `versao` de `portal/config.yml` 1.3.0 → 1.4.0 (minor, ADR 0007: conteúdo novo e
  exportação opcional, sem mudança de schema nem ID retirado). Dois testes que fixavam a versão
  foram atualizados (`tests/test_bootstrap.py::test_config_do_portal` e
  `tests/unidade/test_governanca.py::test_versao_1_4_0_no_config_e_no_changelog`, que agora exige
  a seção `## [1.4.0] - 2026-11-16`).
- `CHANGELOG.md`: seção `## [1.4.0] - 2026-11-16` (Adicionado e Alterado), como a da 1.3.0.
- Arquivamento da spec: a `sdd-lifecycle` (fase 8, passo 1) manda mudar o `Status` da spec Tier 2
  para `arquivada`, e a trilha SDD v3 já seguiu isso. O `Status` de
  `docs/specs/2026-11-12-piloto-rdf-delta.md` passou de "aprovada" para "arquivada (R1–R11
  atendidos; histórico do delta)". As linhas de aprovação da spec ficaram como estavam; nenhuma
  aprovação foi registrada por agente.
- `docs/PROJECT_MEMORY.md` criado (primeira destilação, AGENTS.md:62).
- Dogfooding (`.padroes/`, `padroes.lock.json`) não foi reinstalado: a reinstalação da 1.3.0
  (`279b064`) foi um passo de release do dono, fora desta tarefa. Fica como pendência do release.
- Pendência do dono: antes de integrar, conferir se a `main` avançou além de `279b064` e se a
  versão 1.4.0 ainda é a próxima.

Limites conhecidos (menores deixados de propósito por decisão da coordenação, sem correção
nesta entrega):

- T1: fallback sem `file_type`, custo O(N·E), `_recorte` duplicado, `url` não ASCII, testes de NFC,
  de `or` e de `filterwarnings`/lambdas, tamanho de `semantica.py`, `match="id"`.
- T2: `except ValueError` amplo, `ErroDeExportacao` em `pacote.py`, teste de medição de R6,
  arquivo de integração longo, link relativo no `llms.txt`.
- T4: título da ontologia, `Thing`, idioma no WebVOWL.
- M5, M6, M8 e M9 da revisão final.
- A legenda do painel 1 ficou mais longa com a nota de `RecursoAplicavel`, e o registro de
  curadoria guarda "18 afirmações confirmadas" como achado de problema "nenhum", porque o schema
  não tem campo próprio.
- A avaliação WebVOWL fica fora do build e da CI; a visualização não valida a verdade dos dados,
  a inferência nem a completude.

Rodada final, com a 1.4.0, o `CHANGELOG.md`, a spec arquivada e `docs/PROJECT_MEMORY.md`:

```
$ python -m pytest -q -p no:cacheprovider
3299 passed in 359.19s (0:05:59)            exit 0
$ python -m ruff check .                    exit 0
$ python -m ruff format --check .           exit 0
$ python scripts/validar.py                 exit 0 (validação ok; só o aviso antigo de P1-12)
$ python scripts/gerar.py                   exit 0 (versão 1.4.0)
$ python scripts/gerar.py --saida /tmp/t5/ativo --base-rdf https://example.org/padroes/   exit 0
```

### Correções de texto da revisão do modelo (2026-11-16)

Lista fechada de `.superpowers/sdd/2026-11-12-piloto-rdf/model-review-text-fixes.md`, tirada das
seções B e D da revisão especialista do modelo de conhecimento. Só texto: nenhuma classe,
propriedade, tripla, reificação, índice ou nome de arquivo mudou.

- T1 (B.4): o roteiro do manifesto manda citar o ID original e, quando existir, a `url` da página
  da entidade no portal; uma capacidade nova explica que `arquivoFonte` é o caminho no repositório
  de origem, para procedência, e não endereço para o usuário (`semantica.py`).
- T2 (B.5/D.3): sai `EXTRACTED` do manifesto e da faixa final; o texto passa a ser "todo vínculo
  foi declarado por um arquivo editorial do catálogo; nenhum foi inferido nem verificado"
  (`semantica.py`, `modelo_conhecimento.py`). O termo segue existindo no `graph.json` de entrada
  (campo `confidence`), que não é dado RDF e ficou fora da lista.
- T3 (D.1): página, painel 1 e descrição textual dizem que a prática, identificada pelo IRI
  `…/id/<ID>`, é a instância, e que o ID fica como texto em `pe:identificador`.
- T4 (D.2): legenda, `<desc>` do SVG e descrição textual dizem que `Entidade` é a superclasse
  comum e que toda classe é subclasse dela; o comentário de `pe:Entidade` no vocabulário diz o
  mesmo. O SVG não foi redesenhado.
- T5 (D.4): "as ligações que o grafo do catálogo registra viram vínculos", e exemplos,
  mecanismos, datas de revisão e URL e verificação das referências não entram no piloto.
- T6 (D.5): uma frase na página, uma nota no painel 2 e uma linha da descrição textual explicam a
  afirmação `rdf:Statement` de proveniência.
- T7 (D.6): o comentário de `pe:Ferramenta` deixa de dizer "como uma skill" e diz que é o registro
  em `ferramentas/` (inclusive categoria skill), e que skills e steering só citados em `aplica` são
  Recurso aplicável. O exemplo da relação 5 continua o primeiro por ordem de ID; quando o rótulo
  de um registro é o nome de outra classe, a página acrescenta "“Domínio” é o rótulo de
  passo:enquanto-escreve/dominio, da classe Passo, e não a classe Domínio".
- Curadoria: `verificacoes/modelo-de-conhecimento.yaml` ganhou nota na afirmação de RDFS (o texto
  citado não mudou) e seis achados com tratamento; o revisor registrado nomeia a revisão de
  2026-11-14 e a revisão especialista de 2026-11-16, com a re-revisão das alterações a cargo da
  coordenação. `revisado_em` da página ficou em 2026-11-14 (nenhuma afirmação citada mudou, e
  subir a data exigiria declarar nova conferência das fontes). `CHANGELOG.md`: um item em
  "Alterado" da 1.4.0.

Vermelho → verde (TDD): nove testes novos, todos vermelhos antes da mudança
(`9 failed, 73 passed` em `tests/unidade/test_semantica.py` e
`tests/unidade/test_modelo_conhecimento.py`) e verdes depois (`82 passed`):
`test_roteiro_manda_citar_id_e_url_e_explica_arquivo_fonte_como_procedencia`,
`test_manifesto_e_vocabulario_sem_termo_que_nao_existe_nos_dados`,
`test_comentario_de_ferramenta_nao_contradiz_recurso_aplicavel`,
`test_pagina_md_e_html_sem_termo_que_nao_existe_nos_dados`,
`test_pagina_curada_distingue_iri_de_literal_e_nao_exagera_a_cobertura`,
`test_painel_1_instancia_e_identificada_pelo_iri_e_id_e_literal`,
`test_painel_1_diz_que_entidade_e_a_superclasse_comum`,
`test_painel_2_explica_a_afirmacao_de_proveniencia` e
`test_exemplo_com_rotulo_igual_a_nome_de_classe_e_esclarecido`.

```
$ python -m pytest -q -p no:cacheprovider
3308 passed in 318.11s (0:05:18)            exit 0
$ python -m ruff check .
All checks passed!                          exit 0
$ python -m ruff format --check .
534 files already formatted                 exit 0
$ python scripts/validar.py
validação ok: nenhum erro.                  exit 0 (só o aviso antigo de P1-12)
$ python scripts/gerar.py --saida <tmp>/sem --previa                                       exit 0
$ python scripts/gerar.py --saida <tmp>/com --previa --base-rdf https://example.org/padroes/   exit 0
```

Inspeção visual (Playwright headless, Chromium, prévias com e sem `--base-rdf`): a 1280 e 375 px,
com os `<details>` fechados, `scrollWidth` igual à largura da janela nos dois modos; as regiões
alteradas (instância do painel 1, legenda, nota do painel 2) quebram linha sem transbordar. Com
"Diagrama 3 em texto" aberto a 375 px no modo ativo, a linha 4 transborda (745 px) pelo caminho
sha256 do recorte; a linha é anterior a esta correção (igual em `1e3e51d`) e fica registrada.

Transbordo corrigido a pedido da coordenação (R10): `.mc-alternativa ul` ganhou
`overflow-wrap: anywhere` em `portal/tema/tema.css`, sem mudar texto; teste
`test_r10_alternativa_textual_quebra_caminho_longo_em_tela_estreita`. Com os 18 `<details>` abertos,
a 375 e 1280 px, nos modos ativo e inativo: `scrollWidth` = `clientWidth` (375/375, 1280/1280), sem
erro de console. `tests/unidade/test_modelo_conhecimento.py`: 32 passed; `ruff check` e
`ruff format --check`: ok.

Próxima spec (itens 2 a 5 das cinco mudanças de maior valor da revisão; não feitos aqui):

1. Fechar a cadeia de citação: exportar `url`, `verificacao` (V/S) e `verificado_em` das
   referências e mover `organizacao` de `rdfs:comment` para `dcterms:publisher`.
2. Trocar a reificação `rdf:Statement` por proveniência por entidade (`prov:wasDerivedFrom`) ou
   grafos nomeados por arquivo quando houver divergência.
3. Índice e recortes feitos para LLM: índice de práticas com força, status, célula e `url`;
   nomes de arquivo legíveis em vez de sha256; vizinhos com tipo e força; `@context` fora do
   recorte.
4. Namespace do vocabulário fixo, fora de `--base-rdf`, com `owl:versionInfo`/`versionIRI`,
   política de deprecação, `rdfs:subPropertyOf`/`subClassOf` para Dublin Core, schema.org e
   PROV, e sem `rdfs:domain rdf:Statement`, para o vocabulário ficar em OWL 2 DL.

## Revisão adversarial: 2026-11-14 — achados

Revisão independente em sessão nova, sem o histórico da implementação, sobre `279b064..a32e9c6`
(2026-11-14). Veredito: pronto para merge com correções; R1–R9 atendem, R4, R10 e R11 com
ressalva. Achados e decisões em `.superpowers/sdd/2026-11-12-piloto-rdf/final-review-findings.md`.
Correções em `6a9ea80`, `62e81f9`, `125d0e1` e `e709ecd`, reconferidas em re-revisão escopada
em 2026-11-16: os 12 itens tratados, sem quebra nova. As ressalvas de R4, R10 e R11 deixaram de
existir; a coluna "evidência" aponta o que as sustenta.

| R | veredito | evidência |
| --- | --- | --- |
| R1 | atende | revisão de 2026-11-14; ativação só com `--base-rdf`, build padrão sem artefatos semânticos (Tarefas 1 e 2); suíte completa verde |
| R2 | atende | revisão de 2026-11-14; identidade só de ID e base, testes de invariância a URL, ordem e commit (Tarefa 1) |
| R3 | atende | revisão de 2026-11-14; fidelidade ao grafo do catálogo, 910 afirmações com fonte (Tarefa 1) |
| R4 | atende (ressalva I1 resolvida em `6a9ea80`) | `arquivoFonte` sem `rdfs:domain` (`modelo_semantico.py:159-174`, `semantica.py:283-291`); teste `tests/unidade/test_semantica.py:329`; isomorfismo Turtle x JSON-LD e determinismo da Tarefa 1 |
| R5 | atende | revisão de 2026-11-14; manifesto, índice e recortes e anúncio no `llms.txt` (Tarefa 2) |
| R6 | atende | revisão de 2026-11-14; consumidor de teste só com biblioteca padrão e consultas prática→referência e conceito→prática→ferramenta (Tarefa 2) |
| R7 | atende | revisão de 2026-11-14; diagnóstico de base inválida e falha de exportação com build atômico (Tarefa 2) |
| R8 | atende | revisão de 2026-11-14; sem rede nos testes, sem conversor ou serviço externo no build e na CI (Tarefas 1 e 4) |
| R9 | atende | revisão de 2026-11-14; avaliação real no WebVOWL registrada na Tarefa 4, fora do build |
| R10 | atende (ressalvas I2, M1–M4 resolvidas em `62e81f9`) | testes `tests/unidade/test_modelo_conhecimento.py:269`, `:389`, `:402`, `:415`; inspeção a 375 e 1280 px, ativo e inativo, sem rolagem horizontal e sem erro de console (Correções da revisão final) |
| R11 | atende (ressalvas I3, C4 resolvidas em `125d0e1`) | `verificacoes/modelo-de-conhecimento.yaml` com a revisão independente de 2026-11-14; afirmação 4 de RDFS reescrita e conferida em RDFS §3.6 e §3.7; `validar.py` ok |
