"""Piloto RDF integrado ao build e à CLI (spec do piloto RDF, R1, R5, R6 e R8): ativação opcional,
pacote conferido pelo manifesto, descoberta por um consumidor só com a biblioteca padrão
(llms.txt → manifesto → índice → entidade → referência, em pasta local e em HTTP loopback) e os
três percursos de R6 contra a consulta atual. O rdflib entra só como parser independente."""

import ast
import hashlib
import http.server
import inspect
import json
import re
import socket
import sys
import threading
import urllib.parse
import urllib.request
from pathlib import Path

import pytest
from rdflib import Graph, URIRef

from portal.gerador import consultar
from portal.gerador.build import construir
from portal.gerador.pacote import PASTA_PACOTE, verificar_pacote
from portal.gerador.semantica import montar_semantica
from scripts import gerar as cli
from tests import fabrica

BASE = "https://example.org/padroes/"
PARAMETROS = {
    "versao": "0.1.0",
    "commit": "0" * 40,
    "data": "2026-10-01",
    "url_base": "http://localhost:8000",
}
BUILD = ["--commit", fabrica.COMMIT, "--data", "2026-10-01"]
SEMANTICA = f"{PASTA_PACOTE}/semantica"
CATALOGO_COMPLETO = ("catalogo.ttl", "catalogo.jsonld", "../grafo/graph.json")

# R8: durante o teste, nenhuma conexão sai da máquina; o teste HTTP libera só o loopback.
_PERMITIDOS: set[str] = set()


@pytest.fixture(autouse=True)
def sem_rede_externa(monkeypatch):
    original = socket.socket.connect

    def conectar(self, endereco):
        if self.family == socket.AF_UNIX:
            return original(self, endereco)
        if not isinstance(endereco, tuple) or endereco[0] not in _PERMITIDOS:
            raise AssertionError(f"conexão de rede bloqueada no teste: {endereco!r}")
        return original(self, endereco)

    monkeypatch.setattr(socket.socket, "connect", conectar)
    _PERMITIDOS.clear()
    yield
    _PERMITIDOS.clear()


@pytest.fixture
def loopback():
    _PERMITIDOS.add("127.0.0.1")


def gerar_site(repo, saida, **extra):
    erros = construir(repo, saida, **PARAMETROS, **extra)
    assert erros == [], erros
    return saida


def hashes_do_manifesto(saida):
    manifesto = json.loads((saida / PASTA_PACOTE / "manifesto.json").read_text("utf-8"))
    return manifesto["arquivos"]


# ---- R1: ativação e compatibilidade ----


def test_r1_sem_opcao_nao_ha_semantica_nem_anuncio(repo_minimo, tmp_path):
    saida = gerar_site(repo_minimo, tmp_path / "public")
    assert not (saida / PASTA_PACOTE / "semantica").exists()
    assert not any(c.startswith("semantica/") for c in hashes_do_manifesto(saida))
    assert "semantica" not in (saida / "llms.txt").read_text("utf-8")


def test_r1_com_opcao_os_arquivos_estao_no_manifesto_com_o_hash_certo(repo_minimo, tmp_path):
    saida = gerar_site(repo_minimo, tmp_path / "public", base_rdf=BASE)
    pasta = saida / PASTA_PACOTE
    semantica = {c: h for c, h in hashes_do_manifesto(saida).items() if c.startswith("semantica/")}
    for obrigatorio in ("manifesto.json", "indice.json", "vocabulario.ttl", "catalogo.ttl"):
        assert f"semantica/{obrigatorio}" in semantica
    assert any(c.startswith("semantica/entidades/") for c in semantica)
    for caminho, hash_ in semantica.items():
        assert hashlib.sha256((pasta / caminho).read_bytes()).hexdigest() == hash_
    assert verificar_pacote(pasta) == []
    assert "[Manifesto semântico](pacote/semantica/manifesto.json)" in (
        saida / "llms.txt"
    ).read_text("utf-8")


def test_r1_ativar_nao_altera_o_que_ja_existia(repo_minimo, tmp_path):
    inativo = gerar_site(repo_minimo, tmp_path / "inativo")
    ativo = gerar_site(repo_minimo, tmp_path / "ativo", base_rdf=BASE)
    pacote_inativo = {
        p.relative_to(inativo).as_posix(): p.read_bytes()
        for p in (inativo / PASTA_PACOTE).rglob("*")
        if p.is_file() and p.name != "manifesto.json"
    }
    pacote_ativo = {
        p.relative_to(ativo).as_posix(): p.read_bytes()
        for p in (ativo / PASTA_PACOTE).rglob("*")
        if p.is_file() and p.name != "manifesto.json" and "semantica" not in p.parts
    }
    assert pacote_ativo == pacote_inativo
    anterior = {c: h for c, h in hashes_do_manifesto(ativo).items() if "semantica" not in c}
    assert anterior == hashes_do_manifesto(inativo)
    llms_ativo = (ativo / "llms.txt").read_text("utf-8")
    llms_inativo = (inativo / "llms.txt").read_text("utf-8")
    assert llms_ativo != llms_inativo
    assert re.sub(r"## Modelo semântico\n\n.*\n\n", "", llms_ativo) == llms_inativo
    assert (ativo / "catalogo.json").read_bytes() == (inativo / "catalogo.json").read_bytes()


def test_r1_dois_builds_dao_os_mesmos_bytes_semanticos(repo_minimo, tmp_path):
    a = gerar_site(repo_minimo, tmp_path / "a", base_rdf=BASE)
    b = gerar_site(repo_minimo, tmp_path / "b", base_rdf=BASE)
    for arquivo in sorted((a / SEMANTICA).rglob("*")):
        if arquivo.is_file():
            assert arquivo.read_bytes() == (b / arquivo.relative_to(a)).read_bytes()


def test_r1_cli_com_base_valida_gera_o_pacote_semantico(repo_minimo, tmp_path):
    saida = tmp_path / "site"
    argumentos = ["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD]
    assert cli.main([*argumentos, "--base-rdf", BASE]) == 0
    assert (saida / SEMANTICA / "manifesto.json").is_file()
    assert cli.main(argumentos) == 0
    assert not (saida / SEMANTICA).exists()


@pytest.mark.parametrize(
    "base",
    [
        "http://example.org/padroes/",
        "https://example.org/padroes",
        "https://u:s@example.org/padroes/",
        "https://example.org/padroes/?q=1",
        "https://example.org/padroes/#frag",
        "padroes/",
        "",
    ],
)
def test_r1_base_invalida_e_erro_de_uso_antes_de_qualquer_escrita(
    repo_minimo, tmp_path, capsys, base
):
    saida = tmp_path / "site"
    saida.mkdir()
    (saida / "index.html").write_text("anterior", encoding="utf-8")
    antes = sorted(p.name for p in tmp_path.iterdir())
    with pytest.raises(SystemExit) as saida_do_cli:
        cli.main(["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD, "--base-rdf", base])
    assert saida_do_cli.value.code == 2
    assert "base RDF inválida" in capsys.readouterr().err
    assert (saida / "index.html").read_text(encoding="utf-8") == "anterior"
    assert sorted(p.name for p in tmp_path.iterdir()) == antes
    assert not (repo_minimo / "README.md").exists()


def test_r1_erro_de_exportacao_na_cli_sai_1_com_id_campo_e_fonte(repo_minimo, tmp_path, capsys):
    # Entrada real, sem injeção: URL do portal não ASCII vira `url` de prática no grafo.
    saida = tmp_path / "site"
    saida.mkdir()
    (saida / "index.html").write_text("anterior", encoding="utf-8")
    argumentos = ["--raiz", str(repo_minimo), "--saida", str(saida), *BUILD]
    codigo = cli.main([*argumentos, "--base-rdf", BASE, "--url-base", "https://exemplo.org/pç"])
    saida_padrao = capsys.readouterr()
    assert codigo == 1
    assert "R-SEMANTICA" in saida_padrao.out
    assert "url inválida em 'P1-01'" in saida_padrao.out
    assert "praticas/construir-com-ia/P1-01.md" in saida_padrao.out
    assert saida_padrao.err == "1 erro(s); nada foi gerado.\n"
    assert (saida / "index.html").read_text(encoding="utf-8") == "anterior"
    assert not (tmp_path / "site.tmp").exists()
    assert not (repo_minimo / "README.md").exists()


# ---- consumidor independente (R5): só biblioteca padrão, sem importar o gerador ----


class Consumidor:
    """Lê o que um agente leria: `llms.txt`, manifesto, índice e recortes. `origem` é uma pasta
    ou uma URL http; todo byte lido fica registrado em `lidos`."""

    def __init__(self, origem):
        self.origem = origem
        self.lidos = {}

    def ler(self, relativo):
        if self.origem.startswith("http://"):
            with urllib.request.urlopen(urllib.parse.urljoin(self.origem, relativo)) as resposta:
                dados = resposta.read()
        else:
            dados = (Path(self.origem) / relativo).read_bytes()
        self.lidos[relativo] = len(dados)
        return dados

    def manifesto(self):
        llms = self.ler("llms.txt").decode("utf-8")
        achado = re.search(r"\]\(([^)\s]*semantica/manifesto\.json)\)", llms)
        assert achado, "llms.txt não anuncia o manifesto semântico"
        self.caminho_manifesto = achado.group(1)
        return json.loads(self.ler(self.caminho_manifesto))

    def relativo_ao_manifesto(self, caminho):
        return urllib.parse.urljoin(self.caminho_manifesto, caminho)

    def entidade(self, manifesto, id_):
        indice = json.loads(
            self.ler(self.relativo_ao_manifesto(manifesto["artefatos"]["indice"]["caminho"]))
        )
        achado = [e for e in indice if e["id"] == id_]
        assert len(achado) == 1, f"{id_!r} não está no índice"
        return self._recorte(self.relativo_ao_manifesto(achado[0]["caminho"]))

    def _recorte(self, relativo):
        return {"caminho": relativo, "dados": json.loads(self.ler(relativo))}

    def vizinhos(self, entidade, propriedade, direcao):
        """Vínculos de `propriedade` a partir da entidade focal. `direcao` é `saida` (a entidade
        é o sujeito) ou `entrada` (ela é o objeto). Devolve (id vizinho, relação original, fonte)
        e só olha as afirmações do recorte."""
        grafo = entidade["dados"]["@graph"]
        por_iri = {no["@id"]: no for no in grafo if "identificador" in no}
        focal = grafo[0]["@id"]
        achados = []
        for no in grafo:
            if no.get("@type") != "rdf:Statement" or no["predicado"] != f"pe:{propriedade}":
                continue
            if direcao == "saida" and no["sujeito"] == focal:
                outro = no["objeto"]
            elif direcao == "entrada" and no["objeto"] == focal:
                outro = no["sujeito"]
            else:
                continue
            achados.append(
                (por_iri[outro]["identificador"], no["relacaoOrigem"], no["arquivoFonte"])
            )
        return sorted(achados)

    def seguir(self, entidade, id_vizinho):
        grafo = entidade["dados"]["@graph"]
        no = next(n for n in grafo if n.get("identificador") == id_vizinho and "recorte" in n)
        pasta = entidade["caminho"].rsplit("/", 1)[0]
        return self._recorte(f"{pasta}/{no['recorte']}")


def test_consumidor_so_usa_a_biblioteca_padrao():
    modulo = ast.parse(inspect.getsource(sys.modules[__name__]))
    consumidor = next(
        n for n in modulo.body if isinstance(n, ast.ClassDef) and n.name == "Consumidor"
    )
    nomes = {n.id for n in ast.walk(consumidor) if isinstance(n, ast.Name)}
    importados = {
        (a.asname or a.name).split(".")[0]
        for n in modulo.body
        if isinstance(n, ast.Import | ast.ImportFrom)
        for a in n.names
    }
    usados = nomes & importados
    assert usados == {"Path", "json", "re", "urllib"}
    assert not any("portal" in n for n in nomes)


def _percurso_de_referencia(consumidor):
    manifesto = consumidor.manifesto()
    pratica = consumidor.entidade(manifesto, "P1-01")
    citadas = consumidor.vizinhos(pratica, "cita", "saida")
    assert [c[0] for c in citadas] == ["ref:ref-forte"]
    referencia = consumidor.seguir(pratica, "ref:ref-forte")
    alvo = referencia["dados"]["@graph"][0]
    return manifesto, citadas, alvo


def _afirmar_referencia(citadas, alvo):
    assert citadas == [("ref:ref-forte", "cita", "praticas/construir-com-ia/P1-01.md")]
    assert alvo["identificador"] == "ref:ref-forte"
    assert alvo["@type"] == ["Entidade", "Referencia"]
    assert alvo["rotulo"] == "Documento de exemplo"


def test_r5_descoberta_em_pasta_local_sem_ler_o_catalogo(repo_minimo, tmp_path):
    saida = gerar_site(repo_minimo, tmp_path / "public", base_rdf=BASE)
    consumidor = Consumidor(str(saida))
    manifesto, citadas, alvo = _percurso_de_referencia(consumidor)
    _afirmar_referencia(citadas, alvo)
    assert manifesto["base_rdf"] == BASE
    assert list(consumidor.lidos)[:2] == ["llms.txt", f"{SEMANTICA}/manifesto.json"]
    for caminho in consumidor.lidos:
        assert not any(caminho.endswith(c.removeprefix("../")) for c in CATALOGO_COMPLETO)


def test_r5_descoberta_por_http_loopback(repo_minimo, tmp_path, loopback):
    saida = gerar_site(repo_minimo, tmp_path / "public", base_rdf=BASE)
    pedidos = []

    class Manipulador(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(saida), **kwargs)

        def do_GET(self):
            pedidos.append(self.path)
            super().do_GET()

        def log_message(self, *args):
            pass

    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
    fio = threading.Thread(target=servidor.serve_forever, daemon=True)
    fio.start()
    try:
        consumidor = Consumidor(f"http://127.0.0.1:{servidor.server_port}/")
        _, citadas, alvo = _percurso_de_referencia(consumidor)
    finally:
        servidor.shutdown()
        servidor.server_close()
        fio.join()
    _afirmar_referencia(citadas, alvo)
    assert pedidos[0] == "/llms.txt"
    assert not any(p.endswith(("catalogo.ttl", "catalogo.jsonld", "graph.json")) for p in pedidos)


def test_r5_o_manifesto_semantico_aponta_caminhos_reais_do_pacote(repo_minimo, tmp_path):
    saida = gerar_site(repo_minimo, tmp_path / "public", base_rdf=BASE)
    pasta = saida / SEMANTICA
    manifesto = json.loads((pasta / "manifesto.json").read_text("utf-8"))
    alvos = [manifesto["grafo"]["caminho"], manifesto["consulta"]["caminho"]]
    alvos += [a["caminho"] for k, a in manifesto["artefatos"].items() if k != "entidade"]
    for alvo in alvos:
        assert (pasta / alvo).resolve().is_file(), alvo
    assert (
        pasta / manifesto["consulta"]["caminho"]
    ).resolve() == saida / PASTA_PACOTE / "consultar.py"


# ---- R6: três percursos com fixture de resultado conhecido, e a consulta atual ----


def _no(id_, tipo, label, fonte, rationale="", **extra):
    return {
        "id": id_,
        "label": label,
        "file_type": tipo,
        "source_file": fonte,
        "rationale": rationale,
        **extra,
    }


def _liga(origem, destino, relacao, fonte):
    return {"source": origem, "target": destino, "relation": relacao, "source_file": fonte}


GRAFO_CONHECIDO = {
    "nodes": [
        _no(
            "DAD-01",
            "pratica",
            "DAD-01 Migration aplicada não se edita",
            "praticas/DAD-01.md",
            "Corrija com migration nova.",
            forca="bloqueia",
            dominio="dados",
            momento="merge",
        ),
        _no(
            "DAD-02",
            "pratica",
            "DAD-02 Migration de rollback",
            "praticas/DAD-02.md",
            "Migration de rollback revisada.",
            forca="orienta",
            dominio="dados",
            momento="merge",
        ),
        _no(
            "ref:flyway-doc", "referencia", "Documentação do Flyway", "referencias/flyway-doc.yaml"
        ),
        _no("conceito:migration", "conceito", "Migration", "conceitos/migration.md"),
        _no("ferramenta:flyway", "ferramenta", "Flyway migration", "ferramentas/flyway.yml"),
        _no(
            "ferramenta:liquibase",
            "ferramenta",
            "Liquibase migration",
            "ferramentas/liquibase.yml",
            "Migration de rollback com Liquibase.",
        ),
        _no("celula:dados|merge", "celula", "Dados · Merge", "esquemas/espinha.yml"),
        _no("dominio:dados", "dominio", "Dados", "esquemas/espinha.yml"),
        _no("momento:merge", "momento", "Merge", "esquemas/espinha.yml"),
    ],
    "links": [
        _liga("DAD-01", "ref:flyway-doc", "cita", "praticas/DAD-01.md"),
        _liga("conceito:migration", "DAD-01", "explica", "conceitos/migration.md"),
        _liga("DAD-01", "ferramenta:flyway", "usa", "praticas/DAD-01.md"),
        _liga("DAD-01", "celula:dados|merge", "pertence", "praticas/DAD-01.md"),
        _liga("celula:dados|merge", "dominio:dados", "pertence", "esquemas/espinha.yml"),
        _liga("celula:dados|merge", "momento:merge", "pertence", "esquemas/espinha.yml"),
    ],
}


@pytest.fixture
def pacote_conhecido(tmp_path):
    """Pasta com llms.txt, `semantica/` exportada da fixture e o `graph.json` ao lado, como o
    pacote publicado (llms.txt na raiz, o restante em `pacote/`)."""
    pacote = tmp_path / "site" / PASTA_PACOTE
    arquivos = montar_semantica(GRAFO_CONHECIDO, base_rdf=BASE, versao="1.0.0", commit="abc")
    for relativo, conteudo in arquivos.items():
        (pacote / relativo).parent.mkdir(parents=True, exist_ok=True)
        (pacote / relativo).write_bytes(conteudo)
    (pacote / "grafo").mkdir()
    (pacote / "grafo" / "graph.json").write_text(json.dumps(GRAFO_CONHECIDO), encoding="utf-8")
    (tmp_path / "site" / "llms.txt").write_text(
        "# Portal\n\n## Modelo semântico\n\n"
        "- [Manifesto semântico](pacote/semantica/manifesto.json): entrada\n",
        encoding="utf-8",
    )
    return tmp_path / "site"


def test_r6_pratica_para_referencia(pacote_conhecido):
    c = Consumidor(str(pacote_conhecido))
    pratica = c.entidade(c.manifesto(), "DAD-01")
    assert c.vizinhos(pratica, "cita", "saida") == [
        ("ref:flyway-doc", "cita", "praticas/DAD-01.md")
    ]
    # Direção: a referência não cita a prática, e a outra prática não cita nada.
    referencia = c.seguir(pratica, "ref:flyway-doc")
    assert c.vizinhos(referencia, "cita", "saida") == []
    assert c.vizinhos(referencia, "cita", "entrada") == [("DAD-01", "cita", "praticas/DAD-01.md")]
    assert c.vizinhos(c.entidade(c.manifesto(), "DAD-02"), "cita", "saida") == []


def test_r6_conceito_para_pratica_para_ferramenta(pacote_conhecido):
    c = Consumidor(str(pacote_conhecido))
    manifesto = c.manifesto()
    conceito = c.entidade(manifesto, "conceito:migration")
    explicadas = c.vizinhos(conceito, "explica", "saida")
    assert explicadas == [("DAD-01", "explica", "conceitos/migration.md")]
    pratica = c.seguir(conceito, "DAD-01")
    assert c.vizinhos(pratica, "explica", "entrada") == [
        ("conceito:migration", "explica", "conceitos/migration.md")
    ]
    assert c.vizinhos(pratica, "usa", "saida") == [
        ("ferramenta:flyway", "usa", "praticas/DAD-01.md")
    ]
    # Ausência: Liquibase fala de migration e rollback, mas nenhuma prática declara usá-lo.
    assert "ferramenta:liquibase" not in str(pratica["dados"]["@graph"])
    assert c.vizinhos(c.entidade(manifesto, "DAD-02"), "usa", "saida") == []
    liquibase = c.entidade(manifesto, "ferramenta:liquibase")
    assert c.vizinhos(liquibase, "usa", "entrada") == []


def test_r6_pratica_para_celula_para_dominio_e_momento(pacote_conhecido):
    c = Consumidor(str(pacote_conhecido))
    pratica = c.entidade(c.manifesto(), "DAD-01")
    celulas = c.vizinhos(pratica, "temCelula", "saida")
    assert celulas == [("celula:dados|merge", "pertence", "praticas/DAD-01.md")]
    celula = c.seguir(pratica, "celula:dados|merge")
    assert c.vizinhos(celula, "temDominio", "saida") == [
        ("dominio:dados", "pertence", "esquemas/espinha.yml")
    ]
    assert c.vizinhos(celula, "temMomento", "saida") == [
        ("momento:merge", "pertence", "esquemas/espinha.yml")
    ]
    assert c.vizinhos(celula, "temCelula", "entrada") == [
        ("DAD-01", "pertence", "praticas/DAD-01.md")
    ]


def test_r6_mede_o_que_foi_lido_e_compara_com_a_consulta_atual(pacote_conhecido, capsys):
    c = Consumidor(str(pacote_conhecido))
    manifesto = c.manifesto()
    conceito = c.entidade(manifesto, "conceito:migration")
    pratica = c.seguir(conceito, "DAD-01")
    resposta = json.dumps(
        {
            "explica": c.vizinhos(conceito, "explica", "saida"),
            "usa": c.vizinhos(pratica, "usa", "saida"),
        },
        ensure_ascii=False,
    )
    assert not any(k.endswith(("catalogo.ttl", "catalogo.jsonld", "graph.json")) for k in c.lidos)
    grafo = json.loads(
        (pacote_conhecido / PASTA_PACOTE / "grafo" / "graph.json").read_text("utf-8")
    )
    texto = consultar.buscar(grafo["nodes"], grafo["links"], "migration aplicada rollback")
    # A consulta atual segue intacta: ponteiros de práticas com vizinhos, sem fonte nem direção.
    assert texto.splitlines()[0].startswith("DAD-01")
    assert "ferramenta:flyway" in texto
    assert "praticas/DAD-01.md" not in texto
    medida = {
        "semantica_arquivos_lidos": len(c.lidos),
        "semantica_bytes_lidos": sum(c.lidos.values()),
        "semantica_caracteres_devolvidos": len(resposta),
        "consulta_arquivos_lidos": 1,
        "consulta_bytes_lidos": (pacote_conhecido / PASTA_PACOTE / "grafo" / "graph.json")
        .stat()
        .st_size,
        "consulta_caracteres_devolvidos": len(texto),
    }
    assert all(v > 0 for v in medida.values())
    assert medida["semantica_arquivos_lidos"] == 5
    capsys.readouterr()


# ---- R8: dados hostis e ausência de rede ----

HOSTIL = 'Aspas "x" <b>html</b> & ação 日本 {{ 7*7 }}'


def test_r8_strings_hostis_ficam_como_dados_e_a_pagina_escapa(repo_minimo, mutar, tmp_path):
    mutar(
        "praticas/construir-com-ia/P1-01.md",
        "Classificar toda mudança em tier antes de codar",
        HOSTIL,
    )
    saida = gerar_site(repo_minimo, tmp_path / "public", base_rdf=BASE)
    pasta = saida / SEMANTICA
    c = Consumidor(str(saida))
    pratica = c.entidade(c.manifesto(), "P1-01")["dados"]["@graph"][0]
    assert pratica["rotulo"] == f"P1-01 {HOSTIL}"
    ttl = Graph().parse(data=(pasta / "catalogo.ttl").read_text("utf-8"), format="turtle")
    iri = URIRef(f"{BASE}id/P1-01")
    rotulos = {
        str(o) for o in ttl.objects(iri, URIRef("http://www.w3.org/2000/01/rdf-schema#label"))
    }
    assert rotulos == {f"P1-01 {HOSTIL}"}
    pagina = (saida / "praticas" / "P1-01.html").read_text("utf-8")
    assert "<b>html</b>" not in pagina
    assert "&lt;b&gt;html&lt;/b&gt;" in pagina


def test_r8_a_rede_externa_esta_bloqueada_neste_arquivo():
    with pytest.raises(AssertionError, match="conexão de rede bloqueada"):
        socket.create_connection(("93.184.216.34", 80), timeout=1)
    with pytest.raises(AssertionError, match="conexão de rede bloqueada"):
        socket.create_connection(("127.0.0.1", 9), timeout=1)
