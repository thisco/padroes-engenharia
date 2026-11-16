# Memória do projeto

Aprendizados operacionais duráveis, lidos no início de cada sessão (AGENTS.md, regra 7). Cada
entrada é um fato verificável, sem narrativa de sessão. Origem entre parênteses.

## Exportação semântica (RDF/OWL)

- A exportação só roda com `--base-rdf <URL https terminada em />`; sem a opção o build não muda.
  A identidade das entidades depende só dessa base (piloto RDF, ADR 0016).
- `rdflib` é dependência só de desenvolvimento e teste; o gerador usa apenas a biblioteca padrão.
- Contexto JSON-LD exige IRIs absolutas: IRI relativa em mapeamento de termo é "invalid IRI
  mapping" (JSON-LD 1.1), e o Turtle com IRI relativa resolve para `file://` ao ser lido. Exemplos
  na página usam a base ilustrativa `https://example.org/padroes/` quando a exportação está inativa.
- `rdfs:domain` em propriedade compartilhada vaza tipo: `arquivoFonte` é usada em entidade e em
  `rdf:Statement`, então não pode ter domínio `pe:Entidade`, ou as afirmações viram entidades sob
  entailment RDFS. Há teste que cobre isso.

## Avaliação visual com WebVOWL

- OWL2VOWL 0.3.7 precisa de Java 17 e de `--add-opens java.base/java.lang=ALL-UNNAMED`.
- O domínio antigo visualdataweb.org não é do projeto; usar `https://service.tib.eu/webvowl/`.
- Conversor, Java e serviço externo ficam fora do build e da CI. A visualização não valida a
  verdade dos dados, a inferência nem a completude.

## Testes e ferramentas

- Sem `__init__.py` em `tests/`, o nome-base de cada arquivo de teste deve ser único entre as
  pastas (ex.: `test_semantica.py` e `test_semantica_integracao.py`).
- `scripts/task-brief` espera cabeçalhos no formato "Task N" (aqui o plano usa "Tarefa N").
- A suíte completa leva cerca de 5 a 6 minutos; rode em segundo plano.
- Sem o alias `python` no shell, use `python3` ou o Python do ambiente virtual.

## Processo

- A revisão adversarial de curadoria e a final do Tier 2 precisam de sessão nova, sem o histórico
  do rascunho; autorrevisão não vale (`skills/curadoria-de-pratica`, passo 3).
- `scripts/gerar.py` sem `--saida` grava em `public/` e regrava `README.md` e `ROTEAMENTO.md`;
  nunca edite esses arquivos à mão. Mudou a versão, regere e rode `scripts/validar.py`.
- Integração na `main` exige as duas aprovações de risco alto (`portal/`, `scripts/`) da pessoa
  responsável; a aprovação da spec não vale como aprovação do merge.
