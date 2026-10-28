"""R8, R9 e a ordem de R7 da spec da trilha: os dados da página, sem template."""

from portal.gerador import trilha
from tests import fabrica


def pratica(id_, momento, forca="orienta", status="experimentar"):
    meta = fabrica.meta_pratica(id=id_, momento=momento, forca=forca, status=status)
    if forca != "orienta":
        meta["mecanismo"] = "scripts/validar.py"
    return fabrica.pratica(meta)


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
        {
            "momento": "antes-de-escrever",
            "passo": "escrever-spec",
            "papel": "caminho",
            "bom_quando": "x",
        },
        {"momento": "enquanto-escreve", "passo": "planejar", "papel": "caminho", "bom_quando": "x"},
    ]
    site = fabrica.site(fabrica.ferramenta(fabrica.meta_ferramenta_skill(caminhos=caminhos)))
    vistos = [c["compacto"] for e in trilha.mapa(site) for p in e["passos"] for c in p["caminhos"]]
    assert vistos == [False, True]


def test_trilha_agrupada_por_etapa():
    caminhos = [
        {
            "momento": "antes-de-escrever",
            "passo": "entrevistar",
            "papel": "caminho",
            "bom_quando": "x",
        },
        {
            "momento": "antes-de-escrever",
            "passo": "escrever-spec",
            "papel": "caminho",
            "bom_quando": "x",
        },
    ]
    skill = fabrica.ferramenta(fabrica.meta_ferramenta_skill(caminhos=caminhos))
    seq = [
        {"ferramenta": "sp-writing-plans", "momento": "antes-de-escrever", "passo": p}
        for p in ("entrevistar", "escrever-spec")
    ]
    t = trilha.trilhas(fabrica.site(skill, fabrica.trilha(fabrica.meta_trilha(sequencia=seq))))[0]
    assert t["grupos"] == [
        {
            "etapa": "Especificar",
            "itens": [
                {
                    "ferramenta": "writing-plans",
                    "href": "ferramentas/sp-writing-plans.html",
                    "passos": ["Entrevistar", "Escrever a spec"],
                }
            ],
        }
    ]


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
