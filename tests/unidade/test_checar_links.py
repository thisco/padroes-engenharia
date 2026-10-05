"""checar_links.py: os seis avisos do job agendado, com fetch falso, e a saída que nunca é 1."""

import datetime
import urllib.error

import pytest

from portal.gerador.carregar import Componente, Repositorio
from scripts import checar_links as cl
from tests import fabrica

HOJE = datetime.date(2026, 10, 1)
SCAFFOLD = Componente(
    "sdd-scaffold",
    "https://github.com/thisco/sdd-scaffold",
    "1.7.0",
    "06a382b938af66230ce6299c1638b0ad055804f0",
)
RAW = "https://raw.githubusercontent.com/thisco/sdd-scaffold"


def falso(respostas=None):
    """fetch falso: devolve a resposta (ou levanta a exceção) mapeada por (url, método)."""
    respostas = respostas or {}
    chamadas = []

    def fetch(url, metodo):
        chamadas.append((url, metodo))
        resposta = respostas.get((url, metodo), cl.Resposta(200))
        if isinstance(resposta, Exception):
            raise resposta
        return resposta

    fetch.chamadas = chamadas
    return fetch


def test_url_que_responde_ao_head_nao_avisa_e_nao_faz_get():
    fetch = falso()
    assert cl.checar_url("https://exemplo.org/a", fetch) is None
    assert fetch.chamadas == [("https://exemplo.org/a", "HEAD")]


def test_head_recusado_cai_para_get():
    fetch = falso({("https://exemplo.org/a", "HEAD"): cl.Resposta(405)})
    assert cl.checar_url("https://exemplo.org/a", fetch) is None
    assert [m for _, m in fetch.chamadas] == ["HEAD", "GET"]


@pytest.mark.parametrize(
    ("status", "problema"),
    [
        (404, "HTTP 404"),
        (500, "HTTP 500"),
        (403, "HTTP 403: bloqueado a robôs; confira à mão e registre em verificacoes/"),
    ],
)
def test_erro_http_vira_aviso(status, problema):
    url = "https://exemplo.org/a"
    fetch = falso({(url, "HEAD"): cl.Resposta(status), (url, "GET"): cl.Resposta(status)})
    assert cl.checar_url(url, fetch) == problema


def test_falha_de_rede_avisa_e_nao_quebra():
    fetch = falso({("https://exemplo.org/a", "HEAD"): urllib.error.URLError("sem rede")})
    assert cl.checar_url("https://exemplo.org/a", fetch) == "sem resposta (URLError); confira à mão"


def test_so_busca_https():
    fetch = falso()
    assert cl.checar_url("file:///etc/passwd", fetch) == "não é https; não foi buscada"
    assert fetch.chamadas == []


def test_aviso_de_link_por_referencia():
    repo = Repositorio.de([fabrica.referencia()])
    url = "https://exemplo.org/doc"
    fetch = falso({(url, "HEAD"): cl.Resposta(404), (url, "GET"): cl.Resposta(404)})
    assert cl.avisos_links(repo, fetch) == [
        cl.Aviso("link", "referencias/ref-forte.yaml", f"{url}: HTTP 404")
    ]
    assert cl.avisos_links(repo, falso()) == []


def test_revisao_vencida_so_depois_do_prazo():
    repo = Repositorio.de([fabrica.pratica()])
    assert cl.avisos_revisao(repo, datetime.date(2027, 4, 1)) == []
    assert cl.avisos_revisao(repo, datetime.date(2027, 4, 2)) == [
        cl.Aviso(
            "revisao",
            "praticas/construir-com-ia/P1-01.md",
            "P1-01: revisar_ate 2027-04-01 venceu; volta ao passo 2 da curadoria",
        )
    ]


def test_experimentar_so_com_referencias_s():
    so_s = fabrica.referencia(fabrica.meta_referencia(verificacao="S"))
    assert cl.avisos_experimentar(Repositorio.de([fabrica.pratica(), so_s])) == [
        cl.Aviso(
            "experimentar",
            "praticas/construir-com-ia/P1-01.md",
            "P1-01: todas as referências são [S]; procure a fonte primária",
        )
    ]
    assert cl.avisos_experimentar(Repositorio.de([fabrica.pratica(), fabrica.referencia()])) == []
    avaliar = fabrica.pratica(fabrica.meta_pratica(status="avaliar"))
    assert cl.avisos_experimentar(Repositorio.de([avaliar, so_s])) == []


def test_mecanismo_externo_conferido_no_commit_fixado():
    mecanismo = "sdd-scaffold:template/scripts/verificar_pr.py@1.7.0"
    p = fabrica.pratica(fabrica.meta_pratica(forca="bloqueia", mecanismo=mecanismo))
    repo = Repositorio.de([p])
    url = f"{RAW}/{SCAFFOLD.commit}/template/scripts/verificar_pr.py"
    assert cl.url_no_commit(SCAFFOLD, "template/scripts/verificar_pr.py") == url
    assert cl.avisos_mecanismos(repo, {"sdd-scaffold": SCAFFOLD}, falso()) == []
    ausente = falso({(url, "HEAD"): cl.Resposta(404), (url, "GET"): cl.Resposta(404)})
    assert cl.avisos_mecanismos(repo, {"sdd-scaffold": SCAFFOLD}, ausente) == [
        cl.Aviso(
            "mecanismo",
            "praticas/construir-com-ia/P1-01.md",
            f"P1-01: {mecanismo}: caminho ausente no commit fixado 06a382b938af",
        )
    ]


def test_mecanismo_interno_nao_e_conferido_aqui():
    p = fabrica.pratica(fabrica.meta_pratica(forca="bloqueia", mecanismo="scripts/validar.py"))
    fetch = falso()
    assert cl.avisos_mecanismos(Repositorio.de([p]), {"sdd-scaffold": SCAFFOLD}, fetch) == []
    assert fetch.chamadas == []


@pytest.mark.parametrize(
    ("changelog", "esperado"),
    [
        ("# Changelog\n\n## [1.7.0] - 2026-09-29\n", []),
        ("## [Não publicado]\n\n## [1.8.0] - 2026-11-01\n## [1.7.0]\n", ["1.8.0 publicada"]),
        ("## [2.0.0]\n## [1.10.0]\n", ["2.0.0 publicada"]),
    ],
)
def test_componente_com_versao_nova_no_changelog(changelog, esperado):
    url = f"{RAW}/HEAD/CHANGELOG.md"
    fetch = falso({(url, "GET"): cl.Resposta(200, changelog)})
    avisos = cl.avisos_componentes({"sdd-scaffold": SCAFFOLD}, fetch)
    assert [a.mensagem.split(": ", 1)[1].split(";")[0] for a in avisos] == esperado
    assert fetch.chamadas == [(url, "GET")]


def test_componente_sem_resposta_pede_conferencia_manual():
    url = f"{RAW}/HEAD/CHANGELOG.md"
    fetch = falso({(url, "GET"): TimeoutError()})
    assert cl.avisos_componentes({"sdd-scaffold": SCAFFOLD}, fetch) == [
        cl.Aviso(
            "componente",
            "componentes.yml",
            "sdd-scaffold: CHANGELOG sem resposta (TimeoutError); confira à mão",
        )
    ]


def test_celulas_a_definir(repo_minimo):
    avisos = cl.avisos_celulas(repo_minimo, Repositorio.de([fabrica.pratica()]))
    assert len(avisos) == 47
    assert avisos[0] == cl.Aviso(
        "celula", "esquemas/espinha.yml", "construir-com-ia × enquanto-escreve"
    )


def test_relatorio_tem_uma_secao_por_categoria():
    texto = cl.relatorio([cl.Aviso("link", "referencias/a.yaml", "https://a: HTTP 404")], HOJE)
    assert texto.startswith("# Relatório de avisos de 2026-10-01\n")
    assert "## Links com erro (1)\n\n- `referencias/a.yaml`: https://a: HTTP 404\n" in texto
    assert texto.count("Nenhum.") == len(cl.CATEGORIAS) - 1


def test_main_escreve_o_relatorio_e_sai_0_mesmo_com_aviso(repo_minimo, tmp_path, capsys):
    relatorio = tmp_path / "relatorio-avisos.md"
    url = "https://exemplo.org/doc"
    fetch = falso({(url, "HEAD"): cl.Resposta(404), (url, "GET"): cl.Resposta(404)})
    argumentos = ["--raiz", str(repo_minimo), "--relatorio", str(relatorio), "--hoje", "2026-10-01"]
    assert cl.main(argumentos, fetch=fetch) == 0
    assert "## Links com erro (1)" in relatorio.read_text(encoding="utf-8")
    assert "Células a definir: 47" in capsys.readouterr().out


def test_main_sai_2_em_erro_interno(tmp_path, capsys):
    assert (
        cl.main(
            ["--raiz", str(tmp_path / "nao-existe"), "--relatorio", str(tmp_path / "r.md")],
            fetch=falso(),
        )
        == 2
    )
    assert capsys.readouterr().err.startswith("erro interno:")
