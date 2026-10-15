# Trilha SDD, versão 3: plano de implementação

> **Para workers agênticos:** SUB-SKILL OBRIGATÓRIA: use `superpowers:subagent-driven-development`
> (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa a tarefa. Os
> passos usam checkbox (`- [ ]`). O rastreamento vive só aqui (AGENTS.md, princípio 2).

**Objetivo:** levar ao portal a v3 da Trilha:
- o ciclo com portões em destaque e as trilhas como camada opcional;
- as cores da legenda de força;
- o campo `marco` na prática;
- "etapa" como nome do eixo no portal inteiro;
- a Início com três portas e o ciclo compacto;
- cinco coleções na versão mais nova, com o conteúdo curado da primeira leva.

**Arquitetura:**
- O motor das fases 1 e 2 continua: a espinha com etapa e passos, as ferramentas com caminhos, as
  trilhas, as regras, `trilha.py` e as saídas.
- Esta fase troca os dados que `trilha.py` entrega ao template (o ciclo por portão, até seis
  marcos, o agrupamento por etapa e os cartões compactos).
- O template e o tema são portados do mockup v3.
- A Início e a navegação mudam.
- `Momento.rotulo` passa a nomear o eixo em todo rótulo gerado.

**Stack:** Python 3.11+, PyYAML, Jinja2, jsonschema, pytest, ruff. HTML, CSS e um script local, sem
dependência externa.

**Specs:**
- [`2026-10-14-trilha-sdd-design.md`](../specs/2026-10-14-trilha-sdd-design.md), aprovada em
  2026-10-14;
- alterada por [`2026-10-15-trilha-sdd-v3-delta.md`](../specs/2026-10-15-trilha-sdd-v3-delta.md),
  aprovada em 2026-10-15.

**Mockup de aceite:**
[`2026-10-14-trilha-sdd-mockups/trilha-v3.html`](../specs/2026-10-14-trilha-sdd-mockups/trilha-v3.html).

**Plano anterior:** [`2026-10-14-trilha-sdd.md`](2026-10-14-trilha-sdd.md). As tarefas 1 a 12
estão feitas e valem. As tarefas 13 a 21 dele são **substituídas** pela Fase 5 deste plano.

**Tier:** 2. **Branch:** `feat/2026-10-14-trilha-sdd`, a mesma.

## Restrições globais

- Todas as do plano anterior continuam:
  - PT-BR;
  - nenhuma marca de assistente em artefato de autoria ou em commit, e commits sem linha de
    coautoria;
  - nada do projeto de origem que identifique organização, sistema, pessoa ou host;
  - mudança de schema só por acréscimo;
  - `public/`, `README.md` e `ROTEAMENTO.md` não se editam à mão;
  - as classes CSS novas usam os prefixos `ciclo-` e `tr-`, e nunca `.trilha` nem `.ciclo` sozinho;
  - conteúdo passa pela skill `curadoria-de-pratica`;
  - antes do PR, `validar.py` e `gerar.py` saem com 0, a suíte e o ruff ficam verdes, e roda-se
    `graphify update .`.
- Ambiente: `.venv/bin/python -m pytest` e `.venv/bin/ruff check .`.
- **Cor = força, nunca enfeite:**
  - azul só para `bloqueia` e `pede-aprovacao`;
  - âmbar sólido para `avisa`;
  - âmbar tracejado para `orienta`;
  - skill, ferramenta e trilha são neutras (a tinta e o selo `.st` do tema).
- **Aceite visual:** a página e a Início reproduzem `trilha-v3.html`, em estrutura, hierarquia e
  regra de cor. Quando a página real e o mockup divergirem, vale o mockup, exceto onde a spec diz
  outra coisa.
- Nomear a ferramenta de um fornecedor, por exemplo um repositório com marca no nome, é permitido
  como em `ferramentas/claude-code.yml`. O que é proibido é a marca como autoria.

## Foco de revisão

1. **Prática que avisa pintada de azul.** Em qualquer chip, portão ou cartão, `avisa` é âmbar
   sólido. O teste está na V4 e na V5.
2. **Espinha antiga e catálogo sem skill.** A página e a Início geram sem ferramenta com caminhos,
   sem trilha e sem `marco`, e mostram o título no lugar do rótulo curto. Os testes estão na V4 e
   na V5.
3. **A largura de 400 px.** Nem a Trilha nem a Início rolam na horizontal. O aceite visual é no
   checkpoint 3.
4. **"Fase" e o título do momento como rótulo.** Depois da V7, nenhuma página gerada usa "fase N"
   nem o título antigo do momento como nome de coluna. O teste está na V7.
5. **Versão da coleção diferente da versão do caso.** O `limites` diz a versão do caso e o
   registro diz a versão lida. A revisão é na C11.

## Impacto Arquitetural

Não se aplica (site estático): nenhum compose, IaC ou diagrama de arquitetura.

---

## Fase 4 · Motor v3

### Tarefa V1: Coleções na versão mais nova (R4')

**Arquivos:**
- Alterar: `componentes.yml`;
- Alterar: `tests/unidade/test_trilha_componentes.py`, `tests/unidade/test_carregar.py` (o teste
  que compara o dicionário de componentes) e `tests/test_bootstrap.py` (`EXTERNOS`).

- [ ] **Passo 1: reconferir na origem**, só com leitura:

```bash
git ls-remote https://github.com/obra/superpowers 'refs/tags/v7.0.0*'
git ls-remote https://github.com/addyosmani/agent-skills HEAD 'refs/tags/0.6.9*'
git ls-remote https://github.com/anthropics/claude-plugins-official HEAD
git ls-remote https://github.com/microsoft/playwright-mcp 'refs/tags/v0.0.83*'
git ls-remote https://github.com/mattpocock/skills HEAD
```

Esperado:

| Repositório | Valor esperado |
|---|---|
| superpowers | `bb92a77741419a4ab5f06e711a283343f1ada0c3` (se a tag for anotada, vale a linha `^{}`) |
| agent-skills | `aeac41d4d005999432bb7312f7ff06383a91d59d` |
| claude-plugins-official | `8f814f49002ff824e8a9ba43cf96112dc7f5948d` |
| playwright-mcp | `f183dad4a52965583e3cc1d59b88cdc279e2e57d` (se a tag for anotada, a linha `^{}`) |
| mattpocock/skills | `49dd158d1076134a641b33efb035946536778336` |

Se algum ramo andou depois de 2026-10-15, use o valor da tabela, que é o curado, e registre a
diferença no relatório. Se algum valor não existir, **pare** (princípio 4).

- [ ] **Passo 2: teste que falha.** Substitua o corpo de `test_colecoes_fixadas` por:

```python
ESPERADO = {
    "superpowers": ("https://github.com/obra/superpowers", "7.0.0",
                    "bb92a77741419a4ab5f06e711a283343f1ada0c3"),
    "mattpocock-skills": ("https://github.com/mattpocock/skills", "1.3.1",
                          "49dd158d1076134a641b33efb035946536778336"),
    "agent-skills": ("https://github.com/addyosmani/agent-skills", "0.6.9",
                     "aeac41d4d005999432bb7312f7ff06383a91d59d"),
    "claude-plugins-official": ("https://github.com/anthropics/claude-plugins-official",
                                "2026.10.15", "8f814f49002ff824e8a9ba43cf96112dc7f5948d"),
    "playwright-mcp": ("https://github.com/microsoft/playwright-mcp", "0.0.83",
                       "f183dad4a52965583e3cc1d59b88cdc279e2e57d"),
}


def test_colecoes_fixadas():
    componentes = carregar_componentes(fabrica.RAIZ)
    for nome, (repo, versao, commit) in ESPERADO.items():
        c = componentes[nome]
        assert (c.repo, c.versao, c.commit) == (repo, versao, commit), nome
```

Comando: `.venv/bin/python -m pytest tests/unidade/test_trilha_componentes.py -v`.
Esperado: FAIL.

- [ ] **Passo 3: `componentes.yml`.** Troque o bloco `superpowers` e acrescente os três novos, no
  formato dos existentes, com os valores de `ESPERADO`. No comentário de cada um, diga de onde vem
  a versão:
  - agent-skills: "última tag; o commit está à frente dela";
  - claude-plugins-official: "o repositório não publica versão: a versão é a data do commit".
- [ ] **Passo 4: testes antigos.**
  - Em `test_carregar.py`, acrescente os três componentes ao dicionário esperado e troque o commit
    do superpowers.
  - Em `tests/test_bootstrap.py`, acrescente ao `EXTERNOS`:
    `"agent-skills": "addyosmani/agent-skills"`,
    `"claude-plugins-official": "anthropics/claude-plugins-official"` e
    `"playwright-mcp": "microsoft/playwright-mcp"`.
- [ ] **Passo 5:** rode `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check .` e
  `.venv/bin/python scripts/validar.py`. Esperado: todos verdes. As referências da tarefa 12 que
  apontam para o commit antigo continuam válidas até a C1.
- [ ] **Passo 6:** faça o commit `feat(componentes): coleções na versão mais nova (superpowers 7.0.0, agent-skills, plugins oficiais, playwright-mcp)`.

Entrega: (R4')

### Tarefa V2: Caminhos em qualquer ferramenta (R2', TV3-D7)

**Arquivos:**
- Alterar: `portal/gerador/regras.py` (`regra_caminhos` e `regra_trilhas`);
- Alterar: `portal/gerador/trilha.py` (`_skills` vira `_com_caminhos`);
- Teste: `tests/unidade/test_trilha_ferramenta_skill.py` (acréscimos).

**Interfaces:** produz `trilha._com_caminhos(site) -> list[Conteudo]`, que devolve toda ferramenta
com `caminhos`. Ele substitui `_skills` em `mapa`, `html_trilha` e no filtro de coleções.

- [ ] **Passo 1: testes que falham**, acrescentados a `test_trilha_ferramenta_skill.py`:

```python
def test_ferramenta_teste_com_caminho_exige_colecao(tmp_path):
    caminho = {"momento": "antes-do-merge", "passo": "evidencia", "papel": "caminho", "bom_quando": "x"}
    meta = fabrica.meta_ferramenta(id="pw", categoria="teste", caminhos=[caminho])
    arq = "ferramentas/pw.yml"
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [Erro(arq, "colecao", "R-COLECAO", "ausente")]
    meta["colecao"] = "superpowers"
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == []


def test_ferramenta_teste_com_passo_inexistente(tmp_path):
    caminho = {"momento": "antes-do-merge", "passo": "nao-existe", "papel": "caminho", "bom_quando": "x"}
    meta = fabrica.meta_ferramenta(id="pw", categoria="teste", colecao="superpowers", caminhos=[caminho])
    assert rodar(fabrica.ferramenta(meta), raiz=tmp_path) == [
        Erro("ferramentas/pw.yml", "caminhos.0", "R-CAMINHO", "antes-do-merge/nao-existe")
    ]
```

e, em `tests/unidade/test_trilha_dados.py`:

```python
def test_mapa_inclui_ferramenta_que_nao_e_skill():
    caminho = {"momento": "antes-do-merge", "passo": "evidencia", "papel": "caminho", "bom_quando": "x"}
    pw = fabrica.ferramenta(fabrica.meta_ferramenta(id="pw", titulo="Playwright MCP", categoria="teste",
                                                    colecao="superpowers", caminhos=[caminho]))
    revisar = next(e for e in trilha.mapa(fabrica.site(pw)) if e["slug"] == "antes-do-merge")
    evid = next(p for p in revisar["passos"] if p["slug"] == "evidencia")
    assert [c["ferramenta"] for c in evid["caminhos"]] == ["pw"]
```

- [ ] **Passo 2:** rode e veja falhar.
- [ ] **Passo 3: implementar.**
  - Em `regra_caminhos`, troque a condição `if _texto(f.meta, "categoria") != "skill": continue`
    por:

```python
        eh_skill = _texto(f.meta, "categoria") == "skill"
        caminhos = _itens(f, "caminhos")
        if not eh_skill and not caminhos:
            continue
```

    Mantenha as checagens seguintes: a de `colecao` e a de passo valem para quem tem caminhos; o
    "skill sem caminho" vale só quando `eh_skill`. Remova a linha duplicada
    `caminhos = _itens(f, "caminhos")` que vinha depois.
  - Em `regra_trilhas`, um item vale quando a ferramenta tem `caminhos`, seja skill ou não. Troque
    `meta.get("categoria") != "skill"` por `not meta.get("caminhos")` e a mensagem por
    `f"{fid} não tem caminhos"`. Atualize a docstring e renomeie `test_item_que_nao_e_skill` (em
    `test_trilha_tipo.py`) para `test_item_sem_caminhos`, esperando a mensagem nova. A ferramenta
    `flyway` da fábrica não tem caminhos, então o teste continua cobrindo o caso.
  - Em `trilha.py`, renomeie `_skills` para `_com_caminhos`, com
    `return [f for f in site.repo.ferramentas if f.meta.get("caminhos")]`, e atualize os usos.
    Atualize as docstrings ("ferramentas com caminhos").
- [ ] **Passo 4:** rode os dois arquivos e a suíte.
- [ ] **Passo 5:** faça o commit `feat(trilha): ferramenta que não é skill também pode ser caminho`.

Entrega: (R2')

### Tarefa V3: Campo `marco` na prática (R19)

**Arquivos:** `esquemas/pratica.schema.json`; `portal/gerador/trilha.py` (`_marco`); teste novo
`tests/unidade/test_trilha_marco.py`.

**Interfaces:** `_marco(p)` passa a incluir `rotulo` (o `marco`, ou o `titulo` quando não há
`marco`), `forca_rotulo` (`ROTULO_FORCA[forca]`, de `vocabulario.py`) e `status`.

- [ ] **Passo 1: testes que falham.**

```python
"""R19 da delta v3: rótulo curto do marco."""

from portal.gerador import trilha
from portal.gerador.esquemas import carregar_validador, validar_instancia
from tests import fabrica

ARQ = "praticas/construir-com-ia/P1-01.md"


def test_marco_opcional_ate_40():
    v = carregar_validador(fabrica.RAIZ / "esquemas", "pratica")
    assert validar_instancia(fabrica.meta_pratica(marco="tier classificado"), v, ARQ) == []
    erros = validar_instancia(fabrica.meta_pratica(marco="x" * 41), v, ARQ)
    assert [(e.regra, e.campo) for e in erros] == [("R-ESQUEMA", "marco")]


def test_rotulo_usa_marco_ou_titulo():
    com = fabrica.pratica(fabrica.meta_pratica(marco="tier classificado"))
    sem = fabrica.pratica(fabrica.meta_pratica(id="P1-02"))
    assert trilha._marco(com)["rotulo"] == "tier classificado"
    assert trilha._marco(sem)["rotulo"] == sem.meta["titulo"]
    assert trilha._marco(com)["forca_rotulo"] == "só orienta"
```

- [ ] **Passo 2:** rode e veja falhar.
- [ ] **Passo 3: implementar.**
  - No schema, acrescente `"marco": {"type": "string", "minLength": 1, "maxLength": 40}` e cite a
    R19 na descrição.
  - Em `_marco`:

```python
from portal.gerador.vocabulario import ROTULO_FORCA


def _marco(p: Conteudo) -> dict[str, Any]:
    forca = p.meta["forca"]
    return {
        "id": p.chave,
        "titulo": p.meta["titulo"],
        "rotulo": p.meta.get("marco") or p.meta["titulo"],
        "forca": forca,
        "forca_rotulo": ROTULO_FORCA[forca],
        "status": p.meta.get("status", ""),
        "href": caminho_de(p),
        "mecanismo": forca != "orienta",
    }
```

- [ ] **Passo 4:** rode o arquivo e a suíte. Se um teste de "todos os campos da prática" listar o
  schema, acrescente `marco` a ele.
- [ ] **Passo 5:** faça o commit `feat(praticas): campo marco com o rótulo curto do ciclo`.

Entrega: (R19)

### Tarefa V4: Dados do ciclo v3 (R8', R9', R7' trilhas agrupadas)

**Arquivos:** `portal/gerador/trilha.py`; `tests/unidade/test_trilha_dados.py`, cujos testes de
`ciclo` e `marcos_do_diagrama` são reescritos.

**Interfaces** (a V5 e a V6 consomem):
- `marcos_da_etapa(site, momento, limite=6) -> {"marcos": list, "total": int}`. Ordena primeiro as
  práticas com força acima de "orienta", na ordem de `ORDEM_FORCA` e depois por ID; em seguida as
  que só orientam, `adotar` primeiro e depois por ID. Corta em `limite`.
- `portao(site, momento) -> {"forca": str | None, "marcos": list, "total": int, "mais": int}`.
  Tem só as práticas com força acima de "orienta". `forca` é a mais alta delas, ou `None`. `mais`
  é `total` menos o número de marcos do portão.
- `ciclo(site) -> {"etapas": [...], "laco": {...}}`.
  - Cada etapa é `{"slug", "etapa", "titulo", "passos": [{"slug", "titulo"}], "portao": portao(...)}`,
    para todos os momentos menos o último.
  - O laço é `{"slug", "etapa", "titulo", "passos", "marcos": marcos_da_etapa(..., limite=3)["marcos"]}`.
- `mapa(site)`: cada etapa ganha `"saida": marcos_da_etapa(site, slug)`, que substitui `marcos`.
  Cada caminho ganha `"compacto": bool`, verdadeiro quando a mesma ferramenta já apareceu num passo
  anterior (na ordem dos momentos e dos passos).
- `trilhas(site)`: cada trilha ganha `"grupos": [{"etapa", "itens": [{"ferramenta", "href",
  "passos": [títulos]}]}]`, um grupo por etapa na ordem da espinha, juntando os passos da mesma
  ferramenta na etapa. `itens` continua, por compatibilidade com o Markdown.

- [ ] **Passo 1: testes que falham.** Substitua os testes de `marcos_do_diagrama` e de `ciclo` por:

```python
def test_portao_so_tem_mecanismo_e_a_forca_mais_alta():
    site = fabrica.site(
        pratica("P1-01", "antes-do-merge", "avisa"),
        pratica("P1-02", "antes-do-merge", "bloqueia"),
        pratica("P1-03", "antes-do-merge"),
    )
    p = trilha.portao(site, "antes-do-merge")
    assert [m["id"] for m in p["marcos"]] == ["P1-02", "P1-01"]
    assert (p["forca"], p["total"], p["mais"]) == ("bloqueia", 3, 1)


def test_portao_vazio_sem_mecanismo():
    p = trilha.portao(fabrica.site(pratica("P1-01", "enquanto-escreve")), "enquanto-escreve")
    assert (p["forca"], p["marcos"], p["mais"]) == (None, [], 1)


def test_saida_ate_seis_com_adotar_primeiro_entre_as_que_orientam():
    praticas = [pratica(f"P1-0{i}", "antes-de-escrever") for i in range(1, 8)]
    praticas[6] = pratica("P1-07", "antes-de-escrever", status="adotar")
    dados = trilha.marcos_da_etapa(fabrica.site(*praticas), "antes-de-escrever")
    assert [m["id"] for m in dados["marcos"]][:2] == ["P1-07", "P1-01"]
    assert (len(dados["marcos"]), dados["total"]) == (6, 7)


def test_ciclo_tem_tres_etapas_com_portao_e_o_laco():
    dados = trilha.ciclo(fabrica.site())
    assert [e["etapa"] for e in dados["etapas"]] == ["Especificar", "Codar", "Revisar"]
    assert all("portao" in e and e["passos"] for e in dados["etapas"])
    assert dados["laco"]["etapa"] == "Aprender"


def test_caminho_repetido_vira_compacto():
    caminhos = [
        {"momento": "antes-de-escrever", "passo": "escrever-spec", "papel": "caminho", "bom_quando": "x"},
        {"momento": "enquanto-escreve", "passo": "planejar", "papel": "caminho", "bom_quando": "x"},
    ]
    site = fabrica.site(fabrica.ferramenta(fabrica.meta_ferramenta_skill(caminhos=caminhos)))
    vistos = [c["compacto"] for e in trilha.mapa(site) for p in e["passos"] for c in p["caminhos"]]
    assert vistos == [False, True]


def test_trilha_agrupada_por_etapa():
    caminhos = [
        {"momento": "antes-de-escrever", "passo": "entrevistar", "papel": "caminho", "bom_quando": "x"},
        {"momento": "antes-de-escrever", "passo": "escrever-spec", "papel": "caminho", "bom_quando": "x"},
    ]
    skill = fabrica.ferramenta(fabrica.meta_ferramenta_skill(caminhos=caminhos))
    seq = [{"ferramenta": "sp-writing-plans", "momento": "antes-de-escrever", "passo": p}
           for p in ("entrevistar", "escrever-spec")]
    t = trilha.trilhas(fabrica.site(skill, fabrica.trilha(fabrica.meta_trilha(sequencia=seq))))[0]
    assert t["grupos"] == [{"etapa": "Especificar", "itens": [
        {"ferramenta": "writing-plans", "href": "ferramentas/sp-writing-plans.html",
         "passos": ["Entrevistar", "Escrever a spec"]}]}]
```

  Ajuste a função `pratica` do teste para aceitar `forca="bloqueia"`, com `mecanismo` preenchido
  como hoje.
- [ ] **Passo 2:** rode e veja falhar.
- [ ] **Passo 3: implementar** em `trilha.py`:

```python
from portal.gerador.vocabulario import ORDEM_FORCA, ROTULO_FORCA


def _ordem_saida(p: Conteudo) -> tuple:
    forca = p.meta["forca"]
    if forca != "orienta":
        return (0, ORDEM_FORCA.index(forca), p.chave)
    return (1, p.meta.get("status") != "adotar", p.chave)


def marcos_da_etapa(site: Site, momento: str, limite: int = 6) -> dict[str, Any]:
    """R9': até `limite` marcos; os com mecanismo pela força, depois os que orientam
    (`adotar` primeiro), com o ID como desempate."""
    praticas = sorted(_do_momento(site, momento), key=_ordem_saida)
    return {"marcos": [_marco(p) for p in praticas[:limite]], "total": len(praticas)}


def portao(site: Site, momento: str) -> dict[str, Any]:
    """R8': as práticas com mecanismo do momento; o portão toma a força mais alta."""
    praticas = _do_momento(site, momento)
    fortes = sorted((p for p in praticas if p.meta["forca"] != "orienta"), key=_ordem_saida)
    return {
        "forca": fortes[0].meta["forca"] if fortes else None,
        "marcos": [_marco(p) for p in fortes],
        "total": len(praticas),
        "mais": len(praticas) - len(fortes),
    }


def _etapa_base(m: Any) -> dict[str, Any]:
    return {
        "slug": m.slug,
        "etapa": m.rotulo,
        "titulo": m.titulo,
        "passos": [{"slug": p.slug, "titulo": p.titulo} for p in m.passos],
    }


def ciclo(site: Site) -> dict[str, Any]:
    """R8': as etapas com o portão de saída (todos os momentos menos o último) e o laço."""
    momentos = site.espinha.momentos
    etapas = [{**_etapa_base(m), "portao": portao(site, m.slug)} for m in momentos[:-1]]
    ultimo = momentos[-1]
    laco = {**_etapa_base(ultimo), "marcos": marcos_da_etapa(site, ultimo.slug, limite=3)["marcos"]}
    return {"etapas": etapas, "laco": laco}
```

  - `_etapa_base` usa `m.etapa or m.titulo`; a V7 troca por `m.rotulo`. No código acima, leia
    `m.rotulo` como `m.etapa or m.titulo` até a V7.
  - Remova `marcos_do_diagrama`; a Início passa a usar `ciclo` (V6).
  - Em `mapa`:
    - troque `"marcos": marcos_da_etapa(site, m.slug)` por `"saida": marcos_da_etapa(site, m.slug)`;
    - mantenha um `vistos: set[str]` fora dos laços e, para cada caminho na ordem final de cada
      passo, faça `c["compacto"] = c["ferramenta"] in vistos` e depois `vistos.add(c["ferramenta"])`.
  - Em `trilhas`, monte `grupos` a partir de `itens`, na ordem dos momentos da espinha, juntando
    pelo título da ferramenta. Guarde o slug do momento em cada item (`"momento"`), para agrupar
    sem ambiguidade.
- [ ] **Passo 4:** rode `tests/unidade/test_trilha_dados.py` e a suíte. Os testes de página da
  fase 2 que dependiam de `marcos` ou de `caixas` quebram aqui de propósito; eles são reescritos
  na V5 e na V6. Para a suíte ficar verde neste commit, marque esses testes com
  `@pytest.mark.skip(reason="reescrito na V5/V6")`, e a V5 e a V6 tiram a marca.
- [ ] **Passo 5:** faça o commit `feat(trilha): dados do ciclo v3: portões, saída da etapa, caminhos compactos e trilhas agrupadas`.

Entrega: (R8', R9', R7')

### Tarefa V5: Página da Trilha portada do mockup v3 (R7', R8', R9')

**Arquivos:**
- Reescrever: `portal/templates/trilha.html`;
- Reescrever: a macro `ciclo` em `portal/templates/componentes.html`, mais uma macro nova
  `ciclo_compacto(dados, raiz)`;
- Reescrever: `portal/tema/trilha.js`;
- Substituir: o bloco "Trilha" no fim de `portal/tema/tema.css`;
- Alterar: `portal/tema/contraste.yml`, `md_trilha` em `trilha.py` e
  `tests/unidade/test_trilha_pagina.py`.

**Fonte:** `docs/specs/2026-10-14-trilha-sdd-mockups/trilha-v3.html`. O HTML e o CSS são portados
dele. O que o mockup monta em JavaScript a partir das constantes `ETAPAS`, `SKILLS` e `TRILHAS`,
o template monta em Jinja a partir de `ciclo`, `trilhas`, `mapa` e `colecoes`.

| Mockup (seletor) | Destino no portal |
|---|---|
| `.topo` com `h1`, `.lead` e `.como-usar` | `trilha.html`, cabeçalho; o `h1` vem do `titulo`, que passa a "Uma trilha, não um trilho" em `paginas/trilha.md` (C8) |
| `#ciclo` (`.et-col`, `.portao`, `.laco`) e `.mapa-pe` | macro `ciclo`; a camada de trilha (`.trilho-svg`) é criada pelo `trilha.js` |
| `details.tabela` | `trilha.html`; tabela gerada no servidor, com etapa, passo e uma coluna por trilha |
| `#trilhas` (`.trilha`, `.paradas` agrupadas e "Ver no ciclo") | `trilha.html` a partir de `trilhas[].grupos`; o botão "Ver no ciclo" nasce `hidden`, e o script o mostra |
| `#filtro` fixo, com coleções e "Mostrar complementos" | `trilha.html`; botões `hidden` sem script, como hoje |
| `.etapa` (`.saida`, `.passo`, `.caminho`, `.caminho.compacto`) | `trilha.html` a partir de `mapa` |
| `.atritos` | `corpo` de `paginas/trilha.md` (já existe), dentro de `<section id="atritos">` |

- **Classes do mockup:** troque `.et-col`, `.portao`, `.laco`, `.mapa`, `.etapa`, `.passo`,
  `.caminho`, `.filtro` e `.trilhas` pelos prefixos `ciclo-` e `tr-`, por exemplo
  `.ciclo-col`, `.ciclo-portao`, `.ciclo-laco`, `.tr-etapa`, `.tr-passo`, `.tr-caminho`,
  `.tr-filtro` e `.tr-trilhas`. As do tema, `.ef` e `.st`, são **reaproveitadas** e não copiadas.
- **Tokens:** os tokens do mockup que já existem no `tema.css` (`--papel` e os demais) não se
  repetem. O mockup só tem as cores do tema; não crie cor nova.
- **Script:** `trilha.js` junta o filtro atual (`data-colecao-filtro`), o "Mostrar complementos"
  (`data-papel`) e a camada de trilha. Os botões das trilhas trazem `data-trilha` e a lista de
  passos cobertos em `data-passos="momento/passo …"`; cada `li` do ciclo traz
  `data-passo="momento/passo"`, e o nome do caminho para a camada vem de `data-skill-<trilha>`.
  Nada faz requisição de rede, e o traço é desenhado só dentro de cada etapa, nunca no laço, como
  no mockup.

- [ ] **Passo 1: testes que falham.** Reescreva `test_trilha_pagina.py`:

```python
"""R7', R8' e R9' da delta v3: a página da trilha."""

import re

from portal.gerador.trilha import html_trilha, md_trilha
from tests import fabrica


def pratica(id_, momento, forca="orienta", status="experimentar", marco=None):
    meta = fabrica.meta_pratica(id=id_, momento=momento, forca=forca, status=status)
    if marco:
        meta["marco"] = marco
    if forca != "orienta":
        meta["mecanismo"] = "scripts/validar.py"
    return fabrica.pratica(meta)


def site_completo():
    return fabrica.site(
        fabrica.pagina_trilha(), fabrica.referencia(),
        pratica("P1-05", "antes-de-escrever", "avisa", marco="ambiguidade resolvida"),
        pratica("DAD-01", "antes-do-merge", "bloqueia", marco="migration intocada"),
        fabrica.ferramenta(fabrica.meta_ferramenta_skill()), fabrica.trilha(),
    )


def test_ordem_das_secoes():
    html = html_trilha(site_completo(), site_completo().pagina("trilha"))
    posicoes = [html.index(x) for x in ('class="ciclo-', 'id="trilhas"', 'id="etapas"', 'id="atritos"')]
    assert posicoes == sorted(posicoes)


def test_portao_na_cor_da_forca():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert re.search(r'class="ciclo-portao avisa"', html)
    assert re.search(r'class="ciclo-portao bloqueia"', html)
    assert re.search(r'class="ciclo-portao sem"', html)
    assert 'class="ef avisa"' in html and 'class="ef bloqueia"' in html
    assert "ambiguidade resolvida" in html


def test_avisa_nunca_em_azul():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert not re.search(r'class="[^"]*(gov|azul)[^"]*"[^>]*>[^<]*P1-05', html)


def test_trilha_pronta_monte_a_sua_e_ver_no_ciclo():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert html.count('class="tr-trilha') == 2  # a trilha da fábrica mais o "Monte a sua"
    assert re.search(r'<button[^>]*data-trilha="de-origem"[^>]*hidden', html)


def test_sem_javascript_todos_os_cartoes_visiveis():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    cartoes = re.findall(r'<article class="tr-caminho[^"]*"[^>]*>', html)
    assert cartoes and all("hidden" not in c for c in cartoes)
    assert "tema/trilha.js" in html


def test_tabela_alternativa_do_ciclo():
    site = site_completo()
    html = html_trilha(site, site.pagina("trilha"))
    assert "<summary>Ver o ciclo como tabela</summary>" in html


def test_texto_do_caminho_e_escapado():
    meta = fabrica.meta_ferramenta_skill()
    meta["caminhos"][0]["bom_quando"] = "<script>alert(1)</script>"
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia(), fabrica.ferramenta(meta))
    html = html_trilha(site, site.pagina("trilha"))
    assert "&lt;script&gt;" in html and "<script>alert(1)</script>" not in html


def test_markdown_tem_portoes_e_trilhas_agrupadas():
    site = site_completo()
    md = md_trilha(site, site.pagina("trilha"))
    assert "Para sair de Revisar: DAD-01 migration intocada (bloqueia)" in md
    assert "## Trilhas prontas" in md
```

  No caso de um site sem nenhuma prática com mecanismo em Codar, a classe `ciclo-portao sem`
  aparece porque `fabrica.site` usa a espinha real.
- [ ] **Passo 2:** rode e veja falhar.
- [ ] **Passo 3: implementar o template, a macro, o CSS e o script.**
  - **Template, macro, CSS e JS:** porte do mockup conforme a tabela acima.
  - **`md_trilha`:** para cada etapa do ciclo, uma linha
    `Para sair de <etapa>: <ID> <rótulo> (<força>); …`, ou
    `Para sair de <etapa>: ainda sem marco com mecanismo.`; depois os passos com os caminhos; e as
    trilhas pelos `grupos`.
  - **`contraste.yml`:** os pares de texto novos, se houver, por exemplo `tinta` sobre `branco`
    nos cartões.
  - **Testes de contraste:** rode com `-k contraste`.
- [ ] **Passo 4:** rode o arquivo e a suíte. Tire a marca de `skip` que a V4 pôs nos testes de
  página. Depois rode `.venv/bin/python scripts/gerar.py` e confira que `public/trilha.html`
  existe.
- [ ] **Passo 5:** faça o commit `feat(portal): página da trilha v3 portada do mockup`.

Entrega: (R7', R8', R9')

### Tarefa V6: Início com três portas e ciclo compacto, mais a navegação (R10', R11')

**Arquivos:**
- `portal/gerador/renderizar.py` (`NAV`);
- `portal/templates/inicio.html` (seção "Comece aqui" e bloco "Para quem desenvolve");
- `portal/gerador/paginas.py` (`html_inicio` e `md_inicio`);
- `paginas/inicio.md` (destinos de `caminhos`);
- testes `tests/unidade/test_trilha_inicio_nav.py` e `tests/unidade/test_pagina_inicio.py`.

- [ ] **Passo 1: testes que falham**, substituindo os de `test_trilha_inicio_nav.py`:

```python
def test_trilha_e_item_de_primeiro_nivel():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    grupos = navegacao(site, "index.html")
    titulos = [g["titulo"] for g in grupos]
    assert titulos.index("Trilha") == titulos.index("Comece aqui") + 1
    padroes = next(g for g in grupos if g["titulo"] == "Padrões")
    assert all(i["titulo"] != "IA no produto" for i in padroes["itens"])


def test_inicio_ciclo_compacto_com_portoes():
    site = fabrica.site(fabrica.pagina_trilha(), fabrica.referencia())
    html = html_inicio(site)
    assert 'class="ciclo-mini"' in html
    assert html.count('class="ciclo-mini-portao') == 3
    assert 'href="trilha.html"' in html


def test_portas_da_inicio():
    meta = fabrica.meta_pagina(titulo="Início", caminhos=[
        {"titulo": "Projeto novo", "texto": "x", "destino": "guias/do-zero-a-primeira-mr"},
        {"titulo": "Projeto existente", "texto": "x", "destino": "guias/brownfield-em-5-passos"},
        {"titulo": "No meio de uma mudança", "texto": "x", "destino": "trilha"},
    ])
    inicio = fabrica.Conteudo("pagina", "paginas/inicio.md", meta, "")
    guias = [fabrica.Conteudo("guia", f"guias/{s}.md", fabrica.meta_guia(), "x\n")
             for s in ("do-zero-a-primeira-mr", "brownfield-em-5-passos")]
    site = fabrica.site(inicio, fabrica.pagina_trilha(), fabrica.referencia(), *guias)
    html = html_inicio(site)
    for destino in ("guias/do-zero-a-primeira-mr.html", "guias/brownfield-em-5-passos.html", "trilha.html"):
        assert f'href="{destino}"' in html
```

  Ajuste as chamadas de fábrica ao formato real (`fabrica.Conteudo` é o `Conteudo` de
  `carregar`; `meta_guia` pode exigir campos). Confira em `_caminhos_da_inicio` que um destino
  `trilha`, sem pasta, vira `trilha.html`; se não virar, ajuste a função para aceitar a página na
  raiz.
- [ ] **Passo 2:** rode e veja falhar.
- [ ] **Passo 3: implementar.**
  - **`NAV`:** depois de "Comece aqui", entra `("Trilha", (("Trilha", "trilha.html"),))`. Em
    "Padrões", saem "Trilha" e "IA no produto".
  - **Macro `ciclo_compacto(dados, raiz)`:** porte de `.mini` do mockup, com as classes
    `ciclo-mini`, `ciclo-mini-col` e `ciclo-mini-portao <força|sem>`. Cada etapa traz os IDs
    (`.ef <força>`) com `title` "<rótulo> (<força>)", mais o laço e o link.
  - **`inicio.html`:**
    - a seção "Comece aqui" vira a grade de portas do mockup (`.portas`/`.porta`, com a classe
      `tr-porta`);
    - "Para quem desenvolve" vira "O ciclo de toda mudança", com `ciclo_compacto(ciclo, raiz)`;
    - o `aria-label` do bloco descreve as etapas e os portões, como no mockup;
    - "Para o agente" não muda.
  - **`paginas/inicio.md`:** troque os `caminhos` pelos três destinos do teste. O texto das portas
    é o do mockup; a revisão de curadoria do texto fica na C8.
  - **`md_inicio`:** lista as portas, as etapas e os IDs dos portões.
- [ ] **Passo 4:** rode os dois arquivos, `test_pagina_inicio.py` e a suíte.
- [ ] **Passo 5:** faça o commit `feat(portal): Início com três portas, ciclo compacto e Trilha no primeiro nível`.

Entrega: (R10', R11')

### Tarefa V7: "Etapa" como nome do eixo (R20)

**Arquivos:**
- `portal/gerador/espinha.py` (`Momento.rotulo`);
- `portal/templates/espinha.html`, `pratica.html`, `dominio.html` e `inicio.html` (minimatriz);
- `portal/gerador/paginas.py` (linhas que usam `momento.titulo`: ~122, ~557, ~590, ~618 e ~653),
  `renderizar.py` (~516 e ~783), `saidas.py` (~291, ~356, ~393, ~477 e ~815) e
  `grafo_catalogo.py` (~70);
- `trilha.py` (troca de `m.etapa or m.titulo` por `m.rotulo`);
- teste novo `tests/unidade/test_trilha_vocabulario.py`.

**Interfaces:** `Momento.rotulo -> str` devolve `etapa or titulo`.

- [ ] **Passo 1: testes que falham.**

```python
"""R20 da delta v3: o eixo se chama etapa nas páginas geradas."""

import re

from portal.gerador.espinha import Momento
from portal.gerador.paginas import html_inicio
from portal.gerador.renderizar import html_espinha
from tests import fabrica


def test_rotulo_do_momento():
    assert Momento("x", "Antes de escrever", (0,), etapa="Especificar").rotulo == "Especificar"
    assert Momento("x", "Antes de escrever", (0,)).rotulo == "Antes de escrever"


def test_espinha_usa_etapa_e_nao_fase():
    html = html_espinha(fabrica.site(fabrica.pratica()))
    cab = re.findall(r'<th scope="col" id="momento-[^"]+">(.*?)</th>', html)
    assert [re.sub(r"<.*", "", c).strip() for c in cab] == ["Especificar", "Codar", "Revisar", "Aprender"]
    assert not re.search(r"\bfases? \d", html)


def test_minimatriz_da_inicio_usa_etapa():
    html = html_inicio(fabrica.site(fabrica.pratica()))
    assert "coluna = momento" not in html
    assert re.search(r'<abbr title="Especificar">', html) or ">Especificar<" in html
```

  Confira o nome real de `html_espinha` (em `renderizar.py`, linha ~464) e ajuste o import.
- [ ] **Passo 2:** rode e veja falhar.
- [ ] **Passo 3: implementar.**
  - **`Momento`:** a propriedade `rotulo`.
  - **Espinha:** o cabeçalho das colunas mostra `m.rotulo` com `<small>{{ m.titulo }}</small>`, o
    nome antigo, como descrição secundária, sem "fase". O texto "naquele momento" vira "naquela
    etapa", e "momentos cobertos" vira "etapas cobertas".
  - **`pratica.html`:** o caminho de navegação usa `momento.rotulo`.
  - **`dominio.html`:** o `h2` da seção usa `m.rotulo`.
  - **Minimatriz da Início:** a coluna vira `<abbr title="{{ m.titulo }}">{{ m.rotulo }}</abbr>`,
    e o texto vira "Linha = domínio, coluna = etapa, célula = práticas."
  - **Python:** troque cada `momento.titulo` ou `m.titulo` usado como **rótulo de exibição** por
    `.rotulo`, e "Momento:" por "Etapa:" nos textos gerados. As saídas para máquina
    (`roteamento.json`, linha ~778 de `saidas.py`, e os campos `momento` do catálogo) **não
    mudam**, porque são contrato. O bloco do agente (`renderizar.py:416`) não muda nesta entrega.
  - **`grafo_catalogo.py`:** o rótulo da célula passa a usar `.rotulo`.
- [ ] **Passo 4:** rode o arquivo e a suíte. Os testes que esperavam "Antes de escrever" como
  rótulo, ou "fase", mudam a expectativa para a etapa, sem afrouxar o resto. Rode
  `.venv/bin/python scripts/gerar.py` e
  `grep -rn "fases\? [0-9]" public/*.html public/*/*.html | grep -v "para-agentes"`.
  Esperado: nenhuma linha, além do bloco do agente.
- [ ] **Passo 5:** faça o commit `feat(portal): o eixo do ciclo se chama etapa nas páginas geradas`.

Entrega: (R20)

### Checkpoint humano 3

- [ ] Gerar uma prévia como na fase 2: o catálogo real, mais skills de exemplo enquanto a Fase 5
  não traz as reais. Tirar capturas de `trilha.html` e `index.html` em 1280 px e em 400 px, lado a
  lado com `trilha-v3.html`. Colar a evidência aqui.
- [ ] **PAUSA.** O dono confere o aceite visual antes da Fase 5.

---

## Fase 5 · Conteúdo (substitui as tarefas 13 a 21 do plano anterior)

Toda tarefa desta fase segue a skill `curadoria-de-pratica`. As fontes são lidas só com leitura
(o clone raso no commit fixado ou o `raw` do GitHub), nunca executadas. Os textos "bom quando" e
"cuidado" partem do mockup v3 e são conferidos contra o `SKILL.md` no commit fixado.

### Tarefa C1: Reconferir a tarefa 12 na versão nova e ajustar a precisão

- [ ] **Referências do superpowers:** troque as 4 referências `superpowers-*` da tarefa 12 para o
  commit `bb92a77` (7.0.0), com `versao: "7.0.0"`, e reconfira cada afirmação na 7.0.0. O
  `brainstorming` foi reescrito: confira se ele ainda grava o desenho em `docs/superpowers/specs/`
  e em qual caminho. Ajuste o texto ao que a fonte sustenta.
- [ ] **Precisão:** aplique os seis ajustes da revisão da tarefa 12:
  - a `code-review` busca a spec em quatro origens;
  - o `brainstorming` só grava a spec no caminho arquitetural (reconferido na 7.0.0);
  - "PR para a origem" fica restrito a skill nova;
  - o idioma do superpowers ganha `[ref:]`;
  - as versões e o `revisar_ate` ganham `[ref:]`;
  - o registro diz que os ids de repositório com nome de pessoa são identificadores de fonte.
- [ ] **Título da página:** o `titulo` de `paginas/trilha.md` passa a ser "Uma trilha, não um
  trilho", e o `lead` fica como está.
- [ ] **Verificação:** atualize `verificacoes/trilha.yaml`. `validar.py` e `gerar.py` saem com 0.
  Faça o commit `docs(paginas): trilha reconferida no superpowers 7.0.0`.

### Tarefa C2: Caso de origem ampliado (R14, R14')

É a tarefa 13 do plano anterior, com os artefatos a mais da R14'. Todos os passos daquela tarefa
valem, inclusive **a pausa para o dono**: o relato e a lista de termos fora do repositório. O
`relato.md` passa a dizer:
- que o dono usou todas as skills do superpowers da série 6.x;
- que usou as skills do agent-skills que preenchem as lacunas e as do gatekeeper;
- que usou a `frontend-design` em toda tela e o Playwright na evidência;
- e que o modelo nasceu ali.

Os trechos sanitizados incluem:
- o gatekeeper de 2026-06-10;
- dois planos com a passada de `frontend-design`;
- um plano com Playwright;
- a lista de permissões de skill e MCP, sem caminhos pessoais;
- as datas de instalação das coleções.

Commit: `docs(casos): caso de origem do modelo, sanitizado`.

### Tarefa C3: Ferramentas do superpowers 7.0.0

É a tarefa 14 do plano anterior, com estas trocas:
- `versao_minima: "7.0.0"` e URLs no commit `bb92a77`;
- `sp-systematic-debugging` ganha também `antes-de-escrever/investigar`;
- o `limites` de cada uma diz: "o caso de origem usou a série 6.x; o portal fixa a 7.0.0".

As 13 ficam em `adotar` com `casos: [origem-do-modelo]`. Commit:
`docs(ferramentas): skills do superpowers 7.0.0 como caminhos da trilha`.

### Tarefa C4: Ferramentas do agent-skills

**Arquivos:**
- 14 arquivos `ferramentas/ao-<nome>.yml`, com `colecao: agent-skills` e `versao_minima: "0.6.9"`;
- as referências `referencias/agent-skills-<nome>.yaml`, tipo `comunidade`, com URL
  `https://github.com/addyosmani/agent-skills/blob/aeac41d4d005999432bb7312f7ff06383a91d59d/skills/<nome>/SKILL.md`;
- os registros correspondentes.

| Arquivo | `caminhos` (momento/passo, papel) | Status |
|---|---|---|
| `ao-doubt-driven-development` | antes-de-escrever/decidir (caminho) | adotar |
| `ao-documentation-and-adrs` | antes-de-escrever/decidir (caminho) | adotar |
| `ao-debugging-and-error-recovery` | antes-de-escrever/investigar (caminho); enquanto-escreve/bug (caminho) | adotar |
| `ao-source-driven-development` | antes-de-escrever/investigar (caminho) | adotar |
| `ao-security-and-hardening` | antes-de-escrever/seguranca (caminho) | adotar |
| `ao-test-driven-development` | enquanto-escreve/tdd (caminho) | adotar |
| `ao-frontend-ui-engineering` | enquanto-escreve/dominio (caminho) | adotar |
| `ao-api-and-interface-design` | enquanto-escreve/dominio (caminho) | adotar |
| `ao-deprecation-and-migration` | enquanto-escreve/dominio (caminho) | adotar |
| `ao-ci-cd-and-automation` | enquanto-escreve/dominio (caminho) | adotar |
| `ao-performance-optimization` | enquanto-escreve/dominio (complemento) | adotar |
| `ao-code-review-and-quality` | antes-do-merge/revisar (caminho) | adotar |
| `ao-context-engineering` | depois-da-entrega/continuar (caminho) | adotar |
| `ao-observability-and-instrumentation` | enquanto-escreve/dominio (complemento) | avaliar, sem caso |

- As 13 em `adotar` levam `casos: [origem-do-modelo]`, e o `limites` delas diz: "o caso de origem
  usou a versão de junho de 2026 (commit 5e262b2); o portal fixa a de outubro (aeac41d)".
- `praticas` liga cada uma à prática da faixa que ela ajuda, quando houver. Exemplos: `ao-security-and-hardening` → SEG-01;
  `ao-frontend-ui-engineering` → UX-01; `ao-deprecation-and-migration` → DAD-02;
  `ao-ci-cd-and-automation` → CICD-01; `ao-doubt-driven-development` → P1-09;
  `ao-documentation-and-adrs` → ARQ-01.
- Commit: `docs(ferramentas): skills do agent-skills como caminhos da trilha`.

### Tarefa C5: `frontend-design` e Playwright MCP

- **`ferramentas/an-frontend-design.yml`:**
  - `categoria: skill`, `colecao: claude-plugins-official` e `versao_minima: "2026.10.15"`;
  - caminho `enquanto-escreve/dominio`, papel caminho;
  - `adotar`, com o caso; `praticas: [UX-01, UX-02]`;
  - referência ao `SKILL.md` em `plugins/frontend-design/skills/frontend-design/SKILL.md` no
    commit `8f814f4`;
  - o "cuidado" diz que, sem o tema do projeto, ela cria uma identidade nova.
- **`ferramentas/pw-playwright-mcp.yml`:**
  - `categoria: teste`, `colecao: playwright-mcp` e `versao_minima: "0.0.83"`;
  - caminhos `antes-do-merge/evidencia` (caminho) e `enquanto-escreve/tdd` (complemento);
  - `adotar`, com o caso; `praticas: [UX-01, QLD-03]`;
  - referência ao README no commit `f183dad`;
  - o `como_instalar` traz a configuração do servidor MCP (`npx @playwright/mcp@0.0.83`), e o
    "cuidado" diz "é ferramenta, não skill".
- **Commit:** `docs(ferramentas): frontend-design e Playwright MCP como caminhos`.

### Tarefa C6: Ferramentas do mattpocock

É a tarefa 15 do plano anterior, sem mudança: 8 ferramentas `mp-*` em `avaliar`, no commit
`49dd158`.

### Tarefa C7: `sdd-lifecycle` como caminho

É a tarefa 16 do plano anterior, sem mudança.

### Tarefa C8: Rótulos dos marcos, glossário e textos da Início

- [ ] **Rótulos dos marcos:** campo `marco` nas práticas que aparecem nos portões e em "Para sair
  desta etapa" (até seis por etapa, pela regra da V4). Os valores de partida são os do mockup v3
  ("ambiguidade resolvida", "aprovação registrada", "threat-model do agente", "migration
  intocada", "veredito por requisito", "pipeline com gates", "spec como delta", "constituição
  curta", "tier classificado", "agente só lê por padrão", "teste falhou antes", "expandir e
  contrair", "sem drift spec e código", "CI roda antes do push", "segredo fora do repo", "spec
  arquivada e destilada", "bug vira regra", "changelog e tag"), cada um conferido contra o corpo
  da prática. O `revisado_em` muda junto, e o registro de verificação da prática ganha a
  afirmação do rótulo.
- [ ] **Glossário:** cinco termos em `glossario.yml` (etapa, passo, marco, caminho e trilha pronta),
  com definição de até 200 caracteres e referência à página `trilha` (tipo `portal`).
- [ ] **Início:** em `paginas/inicio.md`, o `lead` é reescrito a partir da tese ("Práticas de
  engenharia para times que desenvolvem com agentes de código. Cada prática diz o que fazer, com
  que força e de onde vem a evidência."), e o texto das portas vem do mockup. A curadoria confere
  as afirmações.
- [ ] **Validação e commit:** `validar.py` e `gerar.py` saem com 0. Commit:
  `docs(praticas): rótulos dos marcos, glossário da trilha e textos da Início`.

### Tarefa C9: As três trilhas

É a tarefa 17 do plano anterior, com a `de-origem` da R16':

```yaml
id: de-origem
titulo: De origem
origem: superpowers, agent-skills, frontend-design e Playwright, com os gates do portal
status: adotar
casos: [origem-do-modelo]
sequencia:
  - {ferramenta: sp-brainstorming, momento: antes-de-escrever, passo: entrevistar}
  - {ferramenta: sp-brainstorming, momento: antes-de-escrever, passo: escrever-spec}
  - {ferramenta: ao-doubt-driven-development, momento: antes-de-escrever, passo: decidir}
  - {ferramenta: sp-systematic-debugging, momento: antes-de-escrever, passo: investigar}
  - {ferramenta: ao-security-and-hardening, momento: antes-de-escrever, passo: seguranca}
  - {ferramenta: sp-writing-plans, momento: enquanto-escreve, passo: planejar}
  - {ferramenta: sp-using-git-worktrees, momento: enquanto-escreve, passo: isolar}
  - {ferramenta: sp-subagent-driven-development, momento: enquanto-escreve, passo: executar}
  - {ferramenta: sp-test-driven-development, momento: enquanto-escreve, passo: tdd}
  - {ferramenta: sp-systematic-debugging, momento: enquanto-escreve, passo: bug}
  - {ferramenta: an-frontend-design, momento: enquanto-escreve, passo: dominio}
  - {ferramenta: sp-requesting-code-review, momento: antes-do-merge, passo: revisar}
  - {ferramenta: sp-receiving-code-review, momento: antes-do-merge, passo: responder}
  - {ferramenta: pw-playwright-mcp, momento: antes-do-merge, passo: evidencia}
  - {ferramenta: sp-finishing-a-development-branch, momento: antes-do-merge, passo: pr-e-merge}
  - {ferramenta: sdd-lifecycle, momento: depois-da-entrega, passo: retro}
  - {ferramenta: sp-writing-skills, momento: depois-da-entrega, passo: instrucoes}
  - {ferramenta: ao-context-engineering, momento: depois-da-entrega, passo: continuar}
bom_quando: "a mudança é grande, com subagentes, revisão por tarefa e tela para conferir. É a combinação em que o modelo nasceu: o gate destrutivo era o doubt-driven-development."
cuidado: "o plugin do superpowers traz um bootstrap que obriga a acionar skills, e o brainstorming só aceita writing-plans depois. Sem subagente, troque subagent-driven-development por executing-plans."
```

A `guiada` e a `enxuta` são como no plano anterior. A `R-TRILHA` já aceita o Playwright desde a
V2.

Commit do conteúdo: `docs(trilhas): de origem, guiada e enxuta`.

### Tarefa C10: ADRs e a regra da versão mais nova

É a tarefa 18 do plano anterior, ampliada pela R17':
- a ADR 0010 registra também TV3-D1, TV3-D2, TV3-D4, TV3-D6 e TV3-D7, com as alternativas
  descartadas;
- a ADR 0011 registra o caso ampliado;
- a ADR 0006 ganha só a linha "Substituída em parte por";
- na skill `curadoria-de-pratica` (`skills/curadoria-de-pratica/SKILL.md`, que é risco alto),
  entra, onde o texto fala de componente externo, um parágrafo curto: "Coleção externa de skills
  ou ferramentas: fixe em `componentes.yml` a versão mais nova na data da curadoria e revalide a
  cada `revisar_ate`. Se a evidência de uso veio de uma versão anterior, o `limites` da ferramenta
  diz qual."

Commit: `docs(adr): 0010 trilha e versões, 0011 caso de origem; curadoria fixa a versão mais nova`.

### Tarefa C11: Revisão independente do lote de conteúdo

É a tarefa 19 do plano anterior, com mais duas perguntas:
4. alguma prática que avisa aparece em azul na página gerada?
5. o `limites` de cada ferramenta cujo caso usou versão anterior diz qual versão?

### Tarefa C12: CHANGELOG

É a tarefa 20 do plano anterior, com os itens da v3:
- o ciclo por portões;
- a legenda de força;
- o campo `marco`;
- a etapa no portal inteiro;
- a Trilha no primeiro nível;
- as três portas;
- cinco coleções;
- 37 ferramentas novas: 13 sp-, 14 ao-, 2 de plugins e 8 mp-, mais a `sdd-lifecycle` convertida;
- o caso ampliado;
- ADRs.

O aumento continua **minor**.

### Tarefa C13: Verificação final, aceite visual e revisão adversarial

É a tarefa 21 do plano anterior, mais:
- capturas da página e da Início reais em 1280 px e 400 px, comparadas com `trilha-v3.html`;
- o `grep` da V7 contra "fase";
- a revisão adversarial cobrindo R1 a R18 da spec de 2026-10-14 e R2', R4', R7' a R11', R14' a
  R17', R19 e R20 do delta, numa tabela única.

### Revisão adversarial (Tier 2)

| R | veredito | evidência |
|---|---|---|

---

## Evidências

(colar aqui as saídas do checkpoint 3 e da C13)
