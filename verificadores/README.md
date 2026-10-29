# Verificadores internos

Cada `verificadores/<id>.py` decide, para uma prática, se um evento é `casa` (violação) ou
`nao-casa`. O ID é minúsculo com `_` (`seg_02.py`) e o teste mora em `tests/verificadores/test_<id>.py`.
O contrato completo está no §3 de
[`docs/specs/2026-10-08-curadoria-forca-dura-delta.md`](../docs/specs/2026-10-08-curadoria-forca-dura-delta.md);
a decisão está na [ADR 0012](../docs/adr/0012-verificadores-internos-e-forca-dura.md).

## Regras do script

- Só a biblioteca padrão, Python 3.9 ou superior; sem rede; sem escrever nada no projeto; sem `import`
  de `portal.*`. O pacote copia o script para o projeto e ele roda com `python3 -I`, fora deste repositório.
- Abaixo de 1 segundo nos eventos de harness e de pre-commit.
- Valor sensível (segredo, CPF) nunca aparece na saída: só o tipo e a posição.

## Chamada

```
python3 verificadores/<id>.py --evento <evento> [--base <ref>]
```

| Evento | Entrada |
|---|---|
| `antes-de-ferramenta`, `depois-de-ferramenta` | JSON no stdin: `ferramenta`, `caminho` (relativo à raiz, ou `null`), `conteudo` (texto após a operação, ou `null`), `comando` (ou `null`), `cwd` |
| `pre-commit` | o próprio script lê o índice (`git diff --cached --name-only`, `git show :<caminho>`) na raiz de `git rev-parse --show-toplevel` |
| `ci` | `--base` obrigatório; o script compara `--base` com `HEAD` (`git diff`, `git show`) |

Evento que o script não atende sai com 2 e mensagem em stderr.

## Saída

| Código | Significado | stdout / stderr |
|---|---|---|
| `0` | `nao-casa` | nada a apontar |
| `1` | `casa` | uma linha por achado em stdout: `<caminho>:<linha>: <motivo>` (`<linha>` é `0` quando não se aplica) |
| `2` | erro de uso ou estado indeterminado | mensagem em stderr, sem traceback |

Estado indeterminado inclui stdin vazio ou JSON inválido, `ci` sem `--base` e execução fora de um
repositório Git nos eventos que o exigem.

## Testes

`tests/verificadores/test_contrato_dos_verificadores.py` cobre sozinho todo `verificadores/*.py`
(evento inexistente, entrada inválida, `ci` sem `--base`, só biblioteca padrão). O teste do próprio
verificador traz, para cada evento que ele atende, um caso que pega e um inocente que difere num
ponto só, e roda o script copiado do pacote com `python3 -I`. `tests/verificadores/conftest.py`
oferece `rodar(...)` e a fixture `repo_git`.
