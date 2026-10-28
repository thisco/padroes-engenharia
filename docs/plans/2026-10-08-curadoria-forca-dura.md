# Curadoria de força dura: plano de implementação

> **Para agentes:** use superpowers:subagent-driven-development. Passos em checkbox (`- [ ]`).

**Objetivo:** promover sete práticas a força dura, com verificadores internos no pacote e um contrato
único de chamada.

**Arquitetura:** cada verificador é um arquivo isolado em `verificadores/`, só com a biblioteca padrão,
chamado por `--evento` (harness, pre-commit, CI). Um teste de contrato parametrizado garante que todos
se comportam igual. O pacote leva a pasta. Cada prática passa pelo ciclo da skill `curadoria-de-pratica`.

**Stack:** Python 3.12 no repositório (verificadores compatíveis com 3.9+), pytest, ruff, o gerador do
portal.

**Spec:** `docs/specs/2026-10-08-curadoria-forca-dura-delta.md` (delta), ADR 0012, e a spec do motor
`docs/specs/2026-10-06-motor-harness-cli-design.md` §5 e §6.

## Restrições globais

- Português do Brasil. Nenhum comentário, docstring ou commit menciona marca de assistente de IA, e
  nenhum commit leva trailer de assistente.
- Não altere `skills/` nem `constituicao/`. Leia por inteiro todo arquivo antes de editá-lo; `portal/`,
  `scripts/`, `esquemas/` e `.gitlab-ci.yml` são de alto risco.
- Verificador: só biblioteca padrão, Python 3.9+, sem rede, sem escrita no projeto, sem `import` de
  `portal.*`. Contrato do delta §3, sem exceção.
- Toda regra e todo verificador têm caso que pega e caso inocente, diferindo num ponto só.
- A `mensagem` do mecanismo começa com `<ID>:`, tem uma linha, no máximo 400 caracteres, e termina em
  `{URL do portal}/praticas/<ID>.md#como-aplicar`.
- Prática alterada: `revisado_em: 2026-10-08` e `revisar_ate: 2027-04-08`.
- Nunca encerre processos por padrão de texto (`pkill`, `killall`, `kill $(pgrep ...)`): há hook que
  bloqueia. Encerre só pelo PID que você mesmo iniciou.
- O repositório fica em pasta sincronizada pelo iCloud, que cria cópias "arquivo 2.py". Antes de cada
  commit, `git status --short`; nada com " 2" no nome entra.
- Verificação a cada tarefa: `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check .`,
  `.venv/bin/ruff format --check .`, `.venv/bin/python scripts/validar.py`.

## Foco de revisão

1. Falso positivo de `bloqueia`: texto legítimo (documentação sobre segredos, CPF de exemplo inválido,
   e-mail `example.com`) não pode ser barrado.
2. Valor sensível nunca aparece na saída do verificador.
3. `pede-aprovacao` não pode disparar em edição que não muda o que a prática protege (ex.: mudar a
   descrição em `pyproject.toml`).
4. Verificador chamado com evento que não atende, sem stdin, com JSON inválido ou fora de um repositório
   Git sai com 2 e mensagem, sem traceback.
5. O verificador copiado do pacote roda com `python3 -I` fora do repositório.

---

## Tarefa 1: Infraestrutura dos verificadores internos

**Arquivos:** `portal/gerador/pacote.py`, `tests/unidade/test_pacote.py`, `tests/verificadores/conftest.py`
(novo), `tests/verificadores/test_contrato_dos_verificadores.py` (novo), `verificadores/README.md`
(novo), `docs/specs/2026-10-06-motor-harness-cli-design.md` (§5 e §6.5: remissão ao delta),
`docs/specs/2026-10-08-curadoria-forca-dura-delta.md` e `docs/adr/0012-...md` (já escritos; só commitar).

**Produz:**
- `pacote.py`: `montar_pacote` inclui cada `verificadores/*.py` em `verificadores/<nome>` (ordenado,
  sem ocultos, sem `__pycache__`), no manifesto. `README.md` da pasta fica fora do pacote.
- `tests/verificadores/conftest.py`: fixtures e funções reutilizáveis:
  - `rodar(script: Path, evento: str, *, entrada: dict | str | None = None, cwd: Path | None = None,
    base: str | None = None, isolado: bool = False) -> subprocess.CompletedProcess` (roda com
    `sys.executable`, e com `-I` quando `isolado`);
  - fixture `repo_git(tmp_path)` que cria um repositório Git com identidade local e um commit inicial,
    e devolve um objeto com `raiz`, `escrever(caminho, texto)`, `adicionar(*caminhos)` (stage),
    `commitar(msg) -> str` (sha).
- `tests/verificadores/test_contrato_dos_verificadores.py`: parametrizado sobre todo `verificadores/*.py`
  (o teste passa vazio enquanto a pasta só tem o README; use `pytest.mark.parametrize` com a lista, e um
  teste que confirma que a lista é coletada). Para cada script: `--evento evento-inexistente` sai 2 com
  stderr não vazio; evento de harness com stdin vazio ou JSON inválido sai 2 sem `Traceback`; `--evento
  ci` sem `--base` sai 2; o arquivo não importa `portal` nem módulo fora da biblioteca padrão (use
  `sys.stdlib_module_names` sobre os imports do AST).
- `verificadores/README.md`: o contrato do delta §3 em uma página, para quem escreve verificador.
- Teste do pacote: um verificador de fixture no repo_exemplo aparece em `pacote/verificadores/`, com
  sha no manifesto; arquivo oculto e `__pycache__` ficam fora.

- [ ] TDD dos testes do pacote e do contrato; implementar; verificação global; commit
  `feat(gerador): pacote leva verificadores internos e contrato único de chamada` (inclui delta e ADR).

## Tarefas 2 a 8: uma prática por tarefa

Cada tarefa segue o mesmo roteiro. Os valores de cada prática estão na tabela do delta §4.

**Arquivos:** `verificadores/<id>.py`, `tests/verificadores/test_<id>.py`, `praticas/<faixa>/<ID>.md`,
`verificacoes/<ID>.yaml`; `referencias/*.yaml` se uma afirmação nova citar fonte nova.

- [ ] **Passo 1. Verificador e teste (TDD).** Parta do candidato indicado no delta §4 (leia-o inteiro).
  Implemente o contrato do delta §3 para cada evento da tabela. Testes em `tests/verificadores/
  test_<id>.py`, usando `rodar` e `repo_git` do conftest: para cada evento atendido, um caso que pega
  (saída 1, linha `<caminho>:<linha>: <motivo>`) e um inocente (saída 0); os casos do Foco de revisão
  que se aplicam; e uma execução isolada do script copiado do pacote gerado (`python3 -I`).
- [ ] **Passo 2. Frontmatter.** `forca` e `mecanismo` estruturado (`verificador: verificadores/<id>.py`,
  `gatilhos` do delta §4, `mensagem` dentro das restrições globais, dizendo o que fazer em vez do que
  foi barrado).
- [ ] **Passo 3. Texto.** "Como verificar" deixa de dizer que não há mecanismo: descreve o verificador,
  os eventos em que roda, a força e como rodá-lo à mão. O Exemplo continua; se citava o candidato,
  aponta que a versão hospedada é `verificadores/<id>.py`. Ajuste qualquer outra frase que dependa da
  força antiga. Cada afirmação factual nova sobre fonte externa leva `[ref:]`; afirmação sobre o próprio
  verificador do repositório não precisa de referência externa.
- [ ] **Passo 4. Registro de curadoria** em `verificacoes/<ID>.yaml`: `verificado_em: 2026-10-08`;
  afirmações novas ou alteradas (passo 2 da skill, com a fonte aberta na web quando houver); em
  `execucoes`, uma entrada `tipo: arquivo` para `verificadores/<id>.py` com o comando de teste, o
  ambiente e a evidência real da execução. Prompts de exemplo que não mudaram mantêm o registro.
- [ ] **Passo 5. Verificação global e commit** `feat(conteudo): <ID> passa a <força> com verificador
  interno`.

A revisão adversarial da skill (passo 3 dela) é feita pelo revisor da tarefa, em sessão independente;
o registro `revisao_adversarial` é atualizado na rodada de correção que segue a revisão.

| Tarefa | Prática | Observação para o implementador |
|---|---|---|
| 2 | LGPD-02 | Porte direto; os gatilhos de harness só valem em `tests/**`, `logs/**`, `prompts/**`; a saída mostra "CPF" ou "e-mail", nunca o valor. |
| 3 | CICD-02 | Só `ci`; os dois tetos do Exemplo viram padrão, sobrescrevíveis por variável de ambiente documentada. |
| 4 | P2-01 | Porte do `.sh` para Python; atenção a falso positivo em teste, documentação e no próprio cliente do gateway. |
| 5 | P3-06 | Allowlist central conforme o Exemplo; sem allowlist, casa (pede aprovação) com motivo claro. |
| 6 | SEG-03 | Casa só quando o conjunto de nomes de dependência muda; parse sem dependências de cada formato da tabela (TOML só com `tomllib` quando houver, Python 3.11+; abaixo disso, parse mínimo e documentado). |
| 7 | SEG-02 | Verificador novo; lista fechada de padrões com fonte (formatos documentados pelos emissores); nunca imprime o valor; documentação sobre segredos com valores de exemplo óbvios (`AKIAIOSFODNN7EXAMPLE`, `xxxx`) é inocente. |
| 8 | API-02 | Contrato JSON e YAML: YAML só se houver parser na biblioteca padrão; sem parser, saída 2 com mensagem. Decida pelo que o candidato de API-01 já faz e registre. |

## Tarefa 9: Fechamento

- [ ] `CHANGELOG.md` em `[Não publicado]`: verificadores internos no pacote e as sete práticas com a
  força nova.
- [ ] Evidências abaixo: contagem de forças do catálogo, trecho de `regras.json` com as sete práticas,
  árvore de `pacote/verificadores/`, linhas e bytes do núcleo do perfil de três domínios, dois builds
  com `diff -r` vazio, suíte, ruff e validador.
- [ ] Checkpoint: aceite do dono por prática; liberar a versão 1.2.0.
- [ ] Commit `docs: changelog e evidências da curadoria de força dura`.

## Evidências

(preenchido na Tarefa 9)

## Checkpoint humano

(preenchido na Tarefa 9)
