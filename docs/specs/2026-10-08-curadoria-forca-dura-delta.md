# Motor de harness: delta da curadoria de força dura (verificadores internos)

**Data:** 2026-10-08 · **Status:** aprovada pelo dono em 2026-10-08 (lista e forças); contrato do
verificador decidido pelo controlador, sujeito ao aceite final do dono
**Tier:** 2 (fixa a interface dos verificadores internos que a F2 e a F4 consomem)
**Altera:** §5 (o pacote passa a levar `verificadores/`), §6.1 e §6.5 da
[spec do motor](2026-10-06-motor-harness-cli-design.md) (contrato concreto do verificador). O resto vale.
**Origem:** checkpoint da F1 enxuta. O dono aprovou em 2026-10-08: versão 1.2.0, F4 antes da F2 e uma
rodada curta de curadoria que promove práticas a força dura antes da F2.

---

## 1. Por que

Na `main` em 3e37b8c, 1 prática bloqueia, 5 avisam e 42 orientam. Uma F2 construída agora teria um
motor de hooks com uma regra de harness. Das 42 que orientam, 40 já trazem no Exemplo um verificador
candidato. O que falta para promovê-las é um lugar para o verificador morar (`verificadores/`), um
contrato de chamada que sirva ao hook, ao pre-commit e ao CI, e o pacote levar o script ao projeto.

## 2. Decisões

| ID | Decisão |
|---|---|
| CFD-D1 | Verificador interno mora em `verificadores/<id>.py` (ID em minúsculas com `_`, ex.: `seg_02.py`), com teste em `tests/verificadores/test_<id>.py` (regra já existente no validador). |
| CFD-D2 | Verificador interno usa só a biblioteca padrão do Python 3.9 ou superior, não acessa a rede e não escreve nada no projeto. Roda na máquina do usuário, como o `consultar.py`. |
| CFD-D3 | O pacote leva `verificadores/*.py` em `pacote/verificadores/`, no manifesto e conferido por `R-PACOTE`. |
| CFD-D4 | Contrato de chamada no §3 abaixo. É o contrato que o runtime da F2 e o pre-commit da F4 usam. |
| CFD-D5 | `pede-aprovacao` tem só gatilho de harness (`antes-de-ferramenta`); Git e CI não têm "perguntar". O verificador candidato de CI dessas práticas fica no Exemplo como opcional. |
| CFD-D6 | Força e gatilhos das sete práticas, na tabela do §4. |
| CFD-D7 | A versão 1.2.0 sai depois desta rodada, com F1 enxuta e as sete práticas. |

## 3. Contrato do verificador interno

```
python3 verificadores/<id>.py --evento <evento> [--base <ref>]
```

- `--evento` é um dos eventos do gatilho (`antes-de-ferramenta`, `depois-de-ferramenta`, `pre-commit`,
  `ci`). Evento que o verificador não atende → saída 2 com mensagem em stderr.
- **Harness** (`antes-de-ferramenta`, `depois-de-ferramenta`): JSON normalizado no stdin, um objeto com
  `ferramenta` (vocabulário neutro), `caminho` (relativo à raiz do projeto, ou `null`), `conteudo` (o
  texto que o arquivo terá depois da operação, ou `null`), `comando` (para `shell`, ou `null`) e `cwd`
  (raiz do projeto). Montar `conteudo` a partir do dialeto de cada harness (Write, Edit, apply_patch) é
  tarefa do runtime da F2, não do verificador. O verificador pode ler o estado atual do arquivo em disco.
- **`pre-commit`**: o verificador lê sozinho o que está no índice (`git diff --cached --name-only` e
  `git show :<caminho>`), na raiz dada por `git rev-parse --show-toplevel`.
- **`ci`**: o verificador compara `--base` (obrigatório; ex.: `$CI_MERGE_REQUEST_DIFF_BASE_SHA`) com
  `HEAD`, lendo com `git diff` e `git show`.
- **Saída:** `0` = `nao-casa` (nada a apontar); `1` = `casa` (violação), com uma linha por achado em
  stdout no formato `<caminho>:<linha>: <motivo>` (`<linha>` pode ser `0` quando não se aplica);
  `2` = erro de uso ou estado indeterminado, com mensagem em stderr. O runtime trata `2` como manda o
  §6.5 (regra dura casada ou indeterminada → negar; sem regra dura → permitir e registrar).
- **Tempo:** abaixo de 1 segundo nos eventos de harness e de pre-commit, num repositório típico.
- **Achado não vaza segredo:** quando o achado é um valor sensível (segredo, CPF), a linha de saída
  mostra só o tipo e a posição, nunca o valor.

## 4. As sete práticas

| Prática | Força | Gatilhos | Verificador (origem) |
|---|---|---|---|
| SEG-02 segredo no repositório | `bloqueia` | `antes-de-ferramenta` (`editar`, `escrever`); `pre-commit`; `ci` | `seg_02.py`, novo: padrões de formato conhecido (chave privada PEM, chave AWS, token GitHub/GitLab, chave de provedor de modelo) e atribuição explícita a nome de segredo; sem entropia genérica |
| LGPD-02 dado pessoal em claro em teste, log ou prompt | `bloqueia` | `antes-de-ferramenta` (`editar`, `escrever`) em `tests/**`, `logs/**`, `prompts/**`; `pre-commit`; `ci` | `lgpd_02.py`, de `exemplos/LGPD-02/verificar-dado-em-claro.py` (CPF com dígito verificador, e-mail fora dos domínios de teste) |
| SEG-03 dependência nova | `pede-aprovacao` | `antes-de-ferramenta` (`editar`, `escrever`) nos arquivos de dependência (`pyproject.toml`, `requirements*.txt`, `package.json`, `go.mod`, `pom.xml`, `build.gradle*`, `Cargo.toml`) | `seg_03.py`: casa só quando o conjunto de dependências declaradas muda (nome novo ou removido), não em qualquer edição do arquivo; o candidato de CI do Exemplo segue como opcional |
| P3-06 MCP e conectores | `pede-aprovacao` | `antes-de-ferramenta` (`editar`, `escrever`) na configuração de MCP (`.mcp.json`, `**/mcp.json`, `**/mcp_config.json`, `.codex/config.toml`, `.gemini/settings.json`, `.kiro/settings/mcp.json`) | `p3_06.py`, de `exemplos/P3-06/verificar-allowlist.py`: casa quando surge servidor fora da allowlist central do projeto, ou quando não há allowlist |
| P2-01 chamada direta ao provedor | `avisa` | `antes-de-ferramenta` (`editar`, `escrever`) em código; `ci` | `p2_01.py`, porte para Python de `exemplos/P2-01/verificar-chamada-direta.sh` |
| CICD-02 MR pequena | `avisa` | `ci` | `cicd_02.py`, de `exemplos/CICD-02/verificar-tamanho-mr.py` |
| API-02 quebra de contrato | `avisa` | `ci` | `api_02.py`, a partir de `exemplos/API-01/comparar-contratos.py`: contrato de `--base` contra `HEAD`; casa com mudança incompatível sem versão maior nova e ADR no diff |

Resultado esperado no catálogo: 3 `bloqueia`, 2 `pede-aprovacao`, 8 `avisa`, 35 `orienta`.

## 5. Curadoria

Cada prática passa pelo ciclo da skill `curadoria-de-pratica`: texto de "Como verificar" reescrito
(sai "não há mecanismo, por isso orienta"), `mecanismo` estruturado com `mensagem`, afirmações novas
verificadas, execução do verificador registrada em `verificacoes/<ID>.yaml` (`execucoes`), revisão
adversarial independente e aceite do dono antes da integração. Prompt de exemplo que não mudar mantém a
execução registrada; prompt alterado é executado de novo.

## 6. Critérios de aceite

1. `scripts/validar.py` sai com 0 e o catálogo tem a contagem do §4.
2. Cada verificador tem caso que pega e caso inocente para cada evento que atende, e um teste que o
   roda isolado (`python3 -I`) a partir do pacote gerado.
3. O pacote gerado traz `verificadores/` e passa em `R-PACOTE`; dois builds dão os mesmos bytes.
4. `regras.json` traz as sete práticas com os gatilhos do §4.
5. O núcleo continua dentro de 100 linhas e 8 KB no perfil de três domínios.
6. Revisão final da branch sem Critical nem Important em aberto, e aceite do dono por prática.
