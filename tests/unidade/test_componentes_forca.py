from tests import fabrica
from tests.dom import analisar


def macro(nome):
    return getattr(fabrica.site().ambiente.get_template("componentes.html").module, nome)


def test_chip_diz_a_consequencia_e_legenda_tem_as_quatro():
    chip = analisar(str(macro("chip_forca")("bloqueia"))).todos("span", classe="ef")[0]
    assert chip.attrs["title"] == "a verificação automática reprova e a mudança não entra"
    legenda = analisar(str(macro("legenda_forcas")()))
    assert [d.texto for d in legenda.todos("dd")] == [
        "a verificação automática reprova e a mudança não entra",
        "uma pessoa precisa aprovar antes de a mudança entrar",
        "a verificação aponta o problema e não impede",
        "não há verificação automática; depende de você e da revisão",
    ]


def test_barra_um_segmento_por_pratica_e_some_sem_pratica():
    barra = analisar(
        str(macro("barra_forca")({"bloqueia": 1, "pede-aprovacao": 0, "avisa": 0, "orienta": 2}))
    )
    assert [s.attrs["class"] for s in barra.todos("i")] == [
        "seg bloqueia",
        "seg orienta",
        "seg orienta",
    ]
    assert (
        str(
            macro("barra_forca")(
                dict.fromkeys(["bloqueia", "pede-aprovacao", "avisa", "orienta"], 0)
            )
        ).strip()
        == ""
    )


def test_bloco_escuro_com_copiar_e_chips():
    html = analisar(
        str(macro("bloco_escuro")("Para o agente", "## Padrões", [("llms.txt", "llms.txt")]))
    )
    assert html.todos("button", **{"data-copiar": ""})
    assert [a.texto for a in html.todos("a")] == ["llms.txt"]
