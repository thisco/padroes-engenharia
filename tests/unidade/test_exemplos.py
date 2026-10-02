from portal.gerador.exemplos import (
    Bloco,
    blocos,
    caminho_seguro,
    checar_sintaxe,
    expandir_inclusoes,
    inclusoes,
    secoes,
)

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


def test_expandir_inclusoes_vira_bloco_com_linguagem(tmp_path):
    (tmp_path / "exemplos/x").mkdir(parents=True)
    (tmp_path / "exemplos/x/a.sh").write_text("echo ```\n", encoding="utf-8")
    texto = expandir_inclusoes("A\n<!-- incluir: exemplos/x/a.sh -->\nB\n", tmp_path)
    assert texto == "A\n````bash\necho ```\n````\nB\n"
    assert expandir_inclusoes("<!-- incluir: ../x -->\n", tmp_path) == "<!-- incluir: ../x -->\n"


def test_caminho_seguro_so_dentro_de_exemplos(tmp_path):
    (tmp_path / "exemplos/x").mkdir(parents=True)
    (tmp_path / "exemplos/x/a.yml").write_text("a: 1\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("segredo\n", encoding="utf-8")
    (tmp_path / "exemplos/x/link.md").symlink_to(tmp_path / "AGENTS.md")
    assert caminho_seguro(tmp_path, "exemplos/x/a.yml") == (tmp_path / "exemplos/x/a.yml").resolve()
    for hostil in (
        "../../etc/passwd",
        "/etc/passwd",
        "exemplos/../AGENTS.md",
        "AGENTS.md",
        "exemplos",
        "exemplos/x/link.md",
    ):
        assert caminho_seguro(tmp_path, hostil) is None, hostil


def test_sintaxe_com_crlf_e_fora_de_utf8_vira_problema_e_nao_excecao(tmp_path):
    (tmp_path / "a.yml").write_bytes(b"a: 1\r\nb: [2]\r\n")
    (tmp_path / "b.json").write_bytes(b"\xff\xfe{}")
    (tmp_path / "c.sh").write_bytes(b"echo ok\r\nif true; then\r\n  echo x\r\nfi\r\n")
    assert checar_sintaxe(tmp_path / "a.yml") == ""
    assert checar_sintaxe(tmp_path / "b.json") == "não está em UTF-8"
    assert checar_sintaxe(tmp_path / "c.sh") != ""
