"""consultar.py (spec do motor §9.2, item 2): busca léxica com vizinhança, rota e orçamento."""

import ast
import json
import subprocess
import sys
from pathlib import Path

from portal.gerador import consultar
from portal.gerador.pacote import emitir_pacote
from portal.gerador.renderizar import montar_site
from tests import fabrica

NOS = [
    {
        "id": "DAD-01",
        "label": "DAD-01 Migration já aplicada não se edita",
        "file_type": "pratica",
        "rationale": "Migration na branch de destino não muda; a correção é uma migration nova.",
        "forca": "bloqueia",
        "dominio": "dados-migrations",
        "momento": "antes-do-merge",
        "url": "https://p/praticas/DAD-01.md",
    },
    {
        "id": "P1-01",
        "label": "P1-01 Classificar toda mudança em tier antes de codar",
        "file_type": "pratica",
        "rationale": "Classifique antes de codar.",
        "forca": "orienta",
        "dominio": "construir-com-ia",
        "momento": "antes-de-escrever",
        "url": "https://p/praticas/P1-01.md",
    },
    {
        "id": "skill:migrations-reversiveis",
        "label": "skill:migrations-reversiveis",
        "file_type": "skill",
        "rationale": "rollback de schema",
    },
]
LINKS = [{"source": "DAD-01", "target": "skill:migrations-reversiveis", "relation": "aplica"}]


def test_pergunta_em_palavras_traz_a_pratica_certa_primeiro_com_vizinhos():
    saida = consultar.buscar(NOS, LINKS, "posso editar uma migration já aplicada?")
    primeira = saida.splitlines()[0]
    assert primeira.startswith("DAD-01 · Migration já aplicada não se edita · bloqueia")
    assert "https://p/praticas/DAD-01.md" in primeira
    assert "vizinhos: skill:migrations-reversiveis" in saida


def test_id_em_minusculas_vem_primeiro():
    assert consultar.buscar(NOS, LINKS, "o que diz a dad-01").startswith("DAD-01 ")


def test_vizinho_nao_pratica_puxa_a_pratica():
    assert consultar.buscar(NOS, LINKS, "rollback").startswith("DAD-01 ")


def test_sem_termo_conhecido():
    assert consultar.buscar(NOS, LINKS, "xyzzy").startswith("nenhuma prática encontrada")


def test_orcamento_corta_e_diz_quanto():
    saida = consultar.rota(
        NOS + [dict(NOS[1], id="P1-02", url="https://p/praticas/P1-02.md")],
        [],
        "construir-com-ia",
        None,
        orcamento=30,
    )
    assert len(saida) <= 30 * consultar.CARACTERES_POR_TOKEN
    assert "[cortado: 2 de 2" in saida


def test_orcamento_nunca_estoura_com_pergunta_que_casa_tudo():
    muitos = [
        dict(NOS[1], id=f"P1-{i:02d}", label=f"P1-{i:02d} Classificar mudança", rationale="codar")
        for i in range(1, 100)
    ]
    for orcamento in (1, 30, 31, 100, 500, consultar.ORCAMENTO_PADRAO):
        saida = consultar.buscar(muitos, [], "classificar mudança codar", orcamento=orcamento)
        assert len(saida) <= orcamento * consultar.CARACTERES_POR_TOKEN
        saida = consultar.rota(muitos, [], "construir-com-ia", None, orcamento=orcamento)
        assert len(saida) <= orcamento * consultar.CARACTERES_POR_TOKEN


def test_saida_e_deterministica_e_empate_desempata_por_id():
    gemeos = [dict(NOS[1], id=i) for i in ("P1-03", "P1-01", "P1-02")]
    saida = consultar.buscar(gemeos, [], "classificar tier")
    assert [linha.split(" ")[0] for linha in saida.splitlines()] == ["P1-01", "P1-02", "P1-03"]
    assert saida == consultar.buscar(list(reversed(gemeos)), [], "classificar tier")


def test_rota_filtra_dominio_e_momento():
    saida = consultar.rota(NOS, LINKS, "dados-migrations", "antes-do-merge")
    assert saida.startswith("DAD-01 ") and "P1-01" not in saida


def test_main_le_o_grafo_e_sai_com_2_sem_grafo(tmp_path, capsys):
    grafo = tmp_path / "graph.json"
    grafo.write_text(json.dumps({"nodes": NOS, "links": LINKS}), encoding="utf-8")
    assert consultar.main(["migration aplicada", "--grafo", str(grafo)]) == 0
    assert capsys.readouterr().out.startswith("DAD-01 ")
    assert consultar.main(["x", "--grafo", str(tmp_path / "nao.json")]) == 2


def test_so_biblioteca_padrao():
    arvore = ast.parse(Path(consultar.__file__).read_text(encoding="utf-8"))
    modulos = {
        a.name.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.Import) for a in n.names
    }
    modulos |= {
        n.module.split(".")[0]
        for n in ast.walk(arvore)
        if isinstance(n, ast.ImportFrom) and n.module
    }
    assert modulos <= set(sys.stdlib_module_names) | {"__future__"}


def test_copia_do_pacote_roda_isolada_sem_o_portal(tmp_path):
    site = montar_site(
        fabrica.RAIZ,
        versao="0.0.0",
        commit=fabrica.COMMIT,
        data="2026-10-08",
        url_base="https://portal.exemplo",
    )
    emitir_pacote(site, tmp_path)
    resultado = subprocess.run(
        [sys.executable, "-I", str(tmp_path / "consultar.py"), "migration já aplicada"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.startswith("DAD-01 ")


def _main_com(tmp_path, conteudo, *extra):
    grafo = tmp_path / "graph.json"
    grafo.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo), "utf-8")
    return consultar.main(["migration", "--grafo", str(grafo), *extra])


def test_grafo_malformado_sai_com_2_e_mensagem(tmp_path, capsys):
    casos = [
        [],
        "{ nao e json",
        {"nodes": NOS},
        {"nodes": {"a": 1}, "links": []},
        {"nodes": [{"label": "sem id"}], "links": []},
        {"nodes": [{"id": 1}], "links": []},
        {"nodes": NOS, "links": [{"source": "DAD-01", "target": "P1-01"}]},
        {"nodes": NOS, "links": [{"target": "a", "relation": "x"}]},
        {"nodes": NOS, "links": ["x"]},
    ]
    for caso in casos:
        assert _main_com(tmp_path, caso) == 2
        assert "grafo indisponível" in capsys.readouterr().err


def test_sigla_de_duas_letras_casa_e_stopword_curta_nao():
    nos = [dict(NOS[1], id="QLD-03", label="QLD-03 O CI roda antes do push", rationale="")]
    assert consultar.buscar(nos, [], "CI").startswith("QLD-03 ")
    nos_ia = [dict(NOS[1], id="P2-01", label="P2-01 Uso de IA no produto", rationale="")]
    assert consultar.buscar(nos_ia, [], "IA").startswith("P2-01 ")
    assert consultar.buscar(NOS, LINKS, "de da do em no na os as um se ou e o a").startswith(
        "nenhuma prática"
    )


def test_termo_repetido_conta_uma_vez():
    assert consultar.buscar(NOS, LINKS, "migration") == consultar.buscar(
        NOS, LINKS, "migration migration migration"
    )


def test_budget_invalido_sai_com_2(tmp_path, capsys):
    for b in ("0", "-5", str(consultar.ORCAMENTO_MINIMO - 1)):
        assert _main_com(tmp_path, {"nodes": NOS, "links": LINKS}, "--budget", b) == 2
        assert "--budget" in capsys.readouterr().err
    assert _main_com(tmp_path, {"nodes": NOS, "links": LINKS}, "--budget", "100") == 0


def test_pergunta_e_dominio_juntos_sai_com_2(tmp_path, capsys):
    assert _main_com(tmp_path, {"nodes": NOS, "links": LINKS}, "--dominio", "dados-migrations") == 2
    assert "não os dois" in capsys.readouterr().err
