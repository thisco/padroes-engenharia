"""Tema: azul só significa "impede" (delta §9.3). Status do radar e quadro "Como combinar tudo"
não usam o azul do governo como cor de fundo, de borda ou de texto."""

import re

import pytest

from tests import fabrica

CSS = (fabrica.RAIZ / "portal" / "tema" / "tema.css").read_text(encoding="utf-8")
AZUIS = re.compile(r"var\(--gov(-claro)?\)")


def declaracoes(seletor: str) -> str:
    """Junta o corpo de todas as regras cujo seletor é exatamente `seletor`."""
    corpos = []
    for sel, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", CSS):
        if seletor in [s.strip() for s in sel.split(",")]:
            corpos.append(corpo)
    return " ".join(corpos)


@pytest.mark.parametrize(
    "seletor",
    [
        ".st.adotar",
        ".st.experimentar",
        ".st.avaliar",
        ".st.evitar",
        ".combinar",
        ".combinar .momento-caixa",
    ],
)
def test_status_e_quadro_combinar_sem_azul(seletor):
    corpo = declaracoes(seletor)
    assert corpo, f"o CSS não tem regra para {seletor}"
    assert not AZUIS.search(corpo), f"{seletor} usa azul: {corpo.strip()}"


def test_adotar_e_experimentar_se_distinguem_sem_cor():
    adotar, experimentar = declaracoes(".st.adotar"), declaracoes(".st.experimentar")
    assert "dashed" in experimentar and "dashed" not in adotar
    assert "var(--tinta)" in adotar
