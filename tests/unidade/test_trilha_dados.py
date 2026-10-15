"""R8, R9 e a ordem de R7 da spec da trilha: os dados da página, sem template."""

from portal.gerador import trilha
from tests import fabrica


def pratica(id_, momento, forca="orienta", status="experimentar"):
    meta = fabrica.meta_pratica(id=id_, momento=momento, forca=forca, status=status)
    if forca != "orienta":
        meta["mecanismo"] = "scripts/validar.py"
    return fabrica.pratica(meta)


def test_marcos_com_mecanismo_primeiro_e_completa_com_orienta():
    site = fabrica.site(
        pratica("P1-01", "antes-do-merge", "avisa"),
        pratica("P1-02", "antes-do-merge", status="adotar"),
        pratica("P1-03", "antes-do-merge"),
        pratica("P1-04", "antes-do-merge"),
    )
    dados = trilha.marcos_do_diagrama(site, "antes-do-merge")
    assert [(m["id"], m["mecanismo"]) for m in dados["marcos"]] == [
        ("P1-01", True),
        ("P1-02", False),
        ("P1-03", False),
    ]
    assert dados["sem_mecanismo"] is False


def test_etapa_sem_mecanismo_tem_a_nota_e_nao_fica_vazia():
    site = fabrica.site(pratica("P1-01", "enquanto-escreve"))
    dados = trilha.marcos_do_diagrama(site, "enquanto-escreve")
    assert [m["id"] for m in dados["marcos"]] == ["P1-01"]
    assert dados["sem_mecanismo"] is True


def test_ciclo_tem_tres_caixas_e_o_laco():
    dados = trilha.ciclo(fabrica.site())
    assert [c["etapa"] for c in dados["caixas"]] == ["Especificar", "Codar", "Revisar"]
    assert dados["laco"]["etapa"] == "Aprender"


def test_mapa_sem_skill_mostra_todos_os_passos_vazios():
    mapa = trilha.mapa(fabrica.site())
    codar = next(e for e in mapa if e["etapa"] == "Codar")
    assert [p["slug"] for p in codar["passos"]][:2] == ["planejar", "isolar"]
    assert all(p["caminhos"] == [] for p in codar["passos"])


def test_mapa_poe_o_caminho_no_passo_certo():
    site = fabrica.site(fabrica.ferramenta(fabrica.meta_ferramenta_skill()))
    codar = next(e for e in trilha.mapa(site) if e["etapa"] == "Codar")
    planejar = next(p for p in codar["passos"] if p["slug"] == "planejar")
    assert planejar["caminhos"][0]["ferramenta"] == "sp-writing-plans"
    assert planejar["caminhos"][0]["href"] == "ferramentas/sp-writing-plans.html"


def test_trilhas_ordenadas_por_status_caso_e_id():
    skill = fabrica.ferramenta(
        fabrica.meta_ferramenta_skill(status="adotar", casos=["origem-do-modelo"])
    )
    t = [
        fabrica.trilha(fabrica.meta_trilha(id="enxuta", status="avaliar")),
        fabrica.trilha(fabrica.meta_trilha(id="guiada", status="adotar")),
        fabrica.trilha(
            fabrica.meta_trilha(id="de-origem", status="adotar", casos=["origem-do-modelo"])
        ),
    ]
    site = fabrica.site(skill, fabrica.caso("origem-do-modelo"), *t)
    assert [x["id"] for x in trilha.trilhas(site)] == ["de-origem", "guiada", "enxuta"]


def test_mapa_inclui_ferramenta_que_nao_e_skill():
    caminho = {
        "momento": "antes-do-merge",
        "passo": "evidencia",
        "papel": "caminho",
        "bom_quando": "x",
    }
    pw = fabrica.ferramenta(
        fabrica.meta_ferramenta(
            id="pw",
            titulo="Playwright MCP",
            categoria="teste",
            colecao="superpowers",
            caminhos=[caminho],
        )
    )
    revisar = next(e for e in trilha.mapa(fabrica.site(pw)) if e["slug"] == "antes-do-merge")
    evid = next(p for p in revisar["passos"] if p["slug"] == "evidencia")
    assert [c["ferramenta"] for c in evid["caminhos"]] == ["pw"]
