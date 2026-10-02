from portal.gerador.exemplos import Bloco, blocos, inclusoes, secoes

CORPO = """## Como aplicar

1. Faça.

## Exemplo

### Antes e depois

```sql
ALTER TABLE x;
```

### Para o agente

```prompt
Faça a migration corretiva.
```

<!-- incluir: exemplos/DAD-01/ci.yml -->

## Como verificar

Rode.
"""


def test_blocos_secoes_e_inclusoes():
    assert blocos(CORPO) == [
        Bloco("sql", "ALTER TABLE x;\n", 9, "Exemplo", "Antes e depois"),
        Bloco("prompt", "Faça a migration corretiva.\n", 15, "Exemplo", "Para o agente"),
    ]
    assert [t for t, _ in secoes(CORPO)] == ["Como aplicar", "Exemplo", "Como verificar"]
    assert dict(secoes(CORPO))["Exemplo"].startswith("### Antes e depois")
    assert inclusoes(CORPO) == ["exemplos/DAD-01/ci.yml"]
