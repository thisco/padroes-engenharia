"""Regras de integridade do repositório (spec §6.5, §6.6, §11.2 e §12.1, bloqueios 1–7 e 12).

Cada regra é uma função pura `(repo, espinha, contexto) -> list[Erro]`, registrada com `@regra`.
`validar_tudo(raiz)` é o contrato da validação: carrega o repositório, roda o schema e todas as
regras registradas, e devolve todos os erros, ordenados e sem repetição. A checagem do build
(R-GERADO-DIVERGENTE e R-EXTERNO) não mora aqui: o CLI `scripts/validar.py` soma as duas.

As regras não confiam no tipo dos campos (o schema já reporta isso): leem com `_texto` e
`_lista`, que devolvem None ou lista vazia quando o campo tem o tipo errado.
"""

from __future__ import annotations

import hashlib
import posixpath
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from portal.gerador import erros as codigos
from portal.gerador.apresentacoes import (
    chaves_de_verificacao,
    chaves_exigidas,
    validar_apresentacoes,
)
from portal.gerador.carregar import (
    BLOCOS,
    TIPOS_YAML_PUBLICADOS,
    Componente,
    Conteudo,
    Repositorio,
    carregar,
    carregar_componentes,
    carregar_ids_retirados,
)
from portal.gerador.citacoes import extrair, malformados
from portal.gerador.erros import Erro
from portal.gerador.espinha import Espinha, carregar_espinha
from portal.gerador.esquemas import validar_componentes, validar_repositorio
from portal.gerador.exemplos import (
    blocos,
    caminho_seguro,
    checar_sintaxe,
    inclusoes,
    prompts_de,
    secoes,
)
from portal.gerador.gatilhos import mecanismo_de, problemas_da_mensagem, problemas_dos_gatilhos
from portal.gerador.grafo import montar_catalogo
from portal.gerador.mecanismos import PASTA as PASTA_MECANISMOS
from portal.gerador.mecanismos import Mecanismo, carregar_mecanismos
from portal.gerador.ninhos import PECAS
from portal.gerador.nucleo import compor_bloco, problemas_do_bloco


@dataclass(frozen=True)
class Contexto:
    """O que as regras precisam além do conteúdo: raiz, componentes fixados e IDs retirados."""

    raiz: Path
    componentes: dict[str, Componente]
    ids_retirados: frozenset[str]


Regra = Callable[[Repositorio, Espinha, Contexto], list[Erro]]

REGRAS: list[Regra] = []


def regra(funcao: Regra) -> Regra:
    """Registra a regra em REGRAS, na ordem de definição."""
    REGRAS.append(funcao)
    return funcao


def carregar_contexto(raiz: Path) -> Contexto:
    return Contexto(
        raiz=raiz,
        componentes=carregar_componentes(raiz),
        ids_retirados=carregar_ids_retirados(raiz),
    )


def validar_tudo(raiz: Path, ignorar: frozenset[str] = frozenset()) -> list[Erro]:
    """Todos os erros de validação do repositório em `raiz`, ordenados e sem repetição.

    `ignorar` são códigos de regra descartados do resultado (o modo de prévia ignora só
    `R-PROMPT`)."""
    raiz = Path(raiz)
    espinha = carregar_espinha(raiz / "esquemas" / "espinha.yml")
    repo = carregar(raiz)
    contexto = carregar_contexto(raiz)
    erros = list(repo.erros)
    erros += validar_repositorio(repo, raiz / "esquemas")
    erros += validar_componentes(raiz)
    for funcao in REGRAS:
        erros += funcao(repo, espinha, contexto)
    return sorted({e for e in erros if e.regra not in ignorar})


def _texto(meta: dict[str, Any], campo: str) -> str | None:
    valor = meta.get(campo)
    return valor if isinstance(valor, str) else None


def _lista(meta: dict[str, Any], campo: str) -> list[str]:
    valor = meta.get(campo)
    if not isinstance(valor, list):
        return []
    return [item for item in valor if isinstance(item, str)]


def _escalar(meta: dict[str, Any], campo: str) -> list[str]:
    """O campo de texto como lista de zero ou um item (`null` e ausente dão lista vazia)."""
    valor = meta.get(campo)
    return [valor] if isinstance(valor, str) else []


def _pasta(conteudo: Conteudo) -> str:
    return PurePosixPath(conteudo.caminho_relativo).parent.name


def _nome(conteudo: Conteudo) -> str:
    return PurePosixPath(conteudo.caminho_relativo).stem


# Espinha e IDs (spec §6.5, regras 1 e 2) ---------------------------------------------------

ID_PRATICA = re.compile(r"^(?P<prefixo>[A-Z][A-Z0-9]*)-(?P<numero>[0-9]{2})$")


@regra
def regra_espinha(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Domínio, subdomínio e momento existem na espinha, e cada arquivo está na pasta da faixa."""
    erros: list[Erro] = []
    for p in repo.praticas:
        dominio = _texto(p.meta, "dominio")
        momento = _texto(p.meta, "momento")
        subdominio = _texto(p.meta, "subdominio")
        faixa = espinha.faixa(dominio) if dominio else None
        if dominio is not None and faixa is None:
            erros.append(Erro(p.caminho_relativo, "dominio", codigos.R_ESPINHA, dominio))
        if momento is not None and espinha.momento(momento) is None:
            erros.append(Erro(p.caminho_relativo, "momento", codigos.R_ESPINHA, momento))
        if faixa is not None and faixa.subdominios and subdominio not in faixa.subdominios:
            esperado = ", ".join(faixa.subdominios)
            valor = f"{subdominio or 'ausente'}; esperado um de: {esperado}"
            erros.append(Erro(p.caminho_relativo, "subdominio", codigos.R_ESPINHA, valor))
        if faixa is not None and not faixa.subdominios and subdominio is not None:
            valor = f"{subdominio}; {dominio} não tem subdomínio"
            erros.append(Erro(p.caminho_relativo, "subdominio", codigos.R_ESPINHA, valor))
        if dominio is not None and _pasta(p) != dominio:
            valor = f"{dominio} fora da pasta praticas/{dominio}/"
            erros.append(Erro(p.caminho_relativo, "dominio", codigos.R_ESPINHA, valor))
    for d in repo.dominios:
        faixa = espinha.faixa(_pasta(d))
        grupo = _texto(d.meta, "grupo")
        if faixa is None:
            erros.append(Erro(d.caminho_relativo, "pasta", codigos.R_ESPINHA, _pasta(d)))
        elif grupo is not None and grupo != faixa.grupo:
            valor = f"{grupo}; a espinha diz {faixa.grupo}"
            erros.append(Erro(d.caminho_relativo, "grupo", codigos.R_ESPINHA, valor))
    for r in repo.referencias:
        for dominio in _lista(r.meta, "dominios"):
            if espinha.faixa(dominio) is None:
                erros.append(Erro(r.caminho_relativo, "dominios", codigos.R_ESPINHA, dominio))
    return erros


@regra
def regra_ids(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Formato <PREFIXO>-<NN>, prefixo da faixa, sem duplicata, sem ID retirado, arquivo = ID."""
    erros: list[Erro] = []
    vistos: dict[str, str] = {}
    for p in repo.praticas:
        id_ = _texto(p.meta, "id")
        if id_ is None:
            continue
        casamento = ID_PRATICA.match(id_)
        dominio = _texto(p.meta, "dominio")
        faixa = espinha.faixa(dominio) if dominio else None
        if casamento is None:
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_FORMATO, id_))
        elif faixa is not None and not espinha.prefixo_valido(
            faixa.slug, _texto(p.meta, "subdominio"), casamento["prefixo"]
        ):
            valor = f"{id_}; {faixa.slug} usa {', '.join(faixa.prefixos)}"
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_PREFIXO, valor))
        if id_ in contexto.ids_retirados:
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_RETIRADO, id_))
        if id_ in vistos:
            valor = f"{id_}; já usado em {vistos[id_]}"
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_DUPLICADO, valor))
        else:
            vistos[id_] = p.caminho_relativo
        if _nome(p) != id_:
            valor = f"{id_}; o arquivo se chama {_nome(p)}.md"
            erros.append(Erro(p.caminho_relativo, "id", codigos.R_ID_ARQUIVO, valor))
    for r in repo.referencias:
        id_ = _texto(r.meta, "id")
        if id_ is not None and _nome(r) != id_:
            valor = f"{id_}; o arquivo se chama {_nome(r)}.yaml"
            erros.append(Erro(r.caminho_relativo, "id", codigos.R_ID_ARQUIVO, valor))
    for v in repo.verificacoes:
        alvo = _texto(v.meta, "conteudo")
        if alvo is not None and _nome(v) != alvo:
            valor = f"{alvo}; o arquivo se chama {_nome(v)}.yaml"
            erros.append(Erro(v.caminho_relativo, "conteudo", codigos.R_ID_ARQUIVO, valor))
    return erros


# Referências e citações (spec §6.2 e §6.3; §12.1, bloqueios 3 e 6) ----------------------------

DATA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


CAMPOS_DE_TEXTO = (
    "resumo",
    "linha",
    "definicao",
    "onde_mora",
    "erro_comum",
    "objetivo",
    "resultado_esperado",
    "subtitulo",
)


@regra
def regra_citacoes(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo `[ref:id]` e todo item de `referencias:` existe, e os dois conjuntos são iguais.

    Confere também os vínculos internos: `relacionadas` e `casos` da prática e `praticas` do
    conceito apontam para conteúdo que existe.
    """
    erros: list[Erro] = []
    ids_referencia = {r.chave for r in repo.referencias}
    ids_pratica = {p.chave for p in repo.praticas}
    slugs_caso = {c.chave for c in repo.casos}
    for c in repo.publicados():
        texto = c.texto_citavel
        for trecho in malformados(texto):
            erros.append(Erro(c.caminho_relativo, "corpo", codigos.R_REF_MALFORMADO, trecho))
        for campo in CAMPOS_DE_TEXTO:
            for trecho in malformados(str(c.meta.get(campo) or "")):
                erros.append(Erro(c.caminho_relativo, campo, codigos.R_REF_MALFORMADO, trecho))
        citados = set(extrair(texto))
        declarados = set(c.referencias_declaradas)
        for id_ in sorted(citados | declarados):
            if id_ not in ids_referencia:
                erros.append(
                    Erro(c.caminho_relativo, "referencias", codigos.R_REF_INEXISTENTE, id_)
                )
        partes = []
        if citados - declarados:
            partes.append("citadas e não declaradas: " + ", ".join(sorted(citados - declarados)))
        if declarados - citados and c.tipo not in TIPOS_YAML_PUBLICADOS:
            partes.append("declaradas e não citadas: " + ", ".join(sorted(declarados - citados)))
        if partes:
            valor = "; ".join(partes)
            erros.append(Erro(c.caminho_relativo, "referencias", codigos.R_REF_CONJUNTO, valor))
    vinculos = [(p, "relacionadas", ids_pratica) for p in repo.praticas]
    vinculos += [(p, "casos", slugs_caso) for p in repo.praticas]
    vinculos += [(c, "praticas", ids_pratica) for c in repo.conceitos]
    for conteudo, campo, existentes in vinculos:
        for alvo in _lista(conteudo.meta, campo):
            if alvo not in existentes:
                erros.append(
                    Erro(conteudo.caminho_relativo, campo, codigos.R_REF_INEXISTENTE, alvo)
                )
    return erros


# Vínculos entre tipos (delta §6.5, regras 8, 9 e 11) -----------------------------------------

BLOCOS_POR_PAGINA = {
    "inicio": {"lead", "fatos", "caminhos"},
    "o-problema": {
        "lead",
        "elos",
        "falhas",
        "numeros",
        "disciplinas",
        "momentos",
        "principios",
        "escada",
    },
    "pessoas-e-normas": {"lead", "modos", "normas", "trabalho"},
}
PAGINAS_RESERVADAS = frozenset(
    {
        "index",
        "espinha",
        "conceitos",
        "referencias",
        "como-fazer",
        "comece-aqui",
        "prompts",
        "ferramentas",
        "glossario",
        "casos",
        "guias",
    }
)


def _ausentes(conteudo: Conteudo, campo: str, alvos: list[str], existentes: set[str]) -> list[Erro]:
    """Um R-REF-INEXISTENTE por alvo de `campo` que não está entre os `existentes`."""
    return [
        Erro(conteudo.caminho_relativo, campo, codigos.R_REF_INEXISTENTE, alvo)
        for alvo in alvos
        if alvo not in existentes
    ]


def _na_espinha(
    conteudo: Conteudo, espinha: Espinha, dominio: Any, momento: Any, campo: str = ""
) -> list[Erro]:
    """R-ESPINHA para `dominio` e `momento` que não existem; `campo` é o prefixo do caminho."""
    erros: list[Erro] = []
    if isinstance(dominio, str) and espinha.faixa(dominio) is None:
        erros.append(Erro(conteudo.caminho_relativo, f"{campo}dominio", codigos.R_ESPINHA, dominio))
    if isinstance(momento, str) and espinha.momento(momento) is None:
        erros.append(Erro(conteudo.caminho_relativo, f"{campo}momento", codigos.R_ESPINHA, momento))
    return erros


def _starter_fixado(starter: Conteudo, contexto: Contexto) -> list[Erro]:
    """Regra 11: o starter é componente de `componentes.yml`, com a mesma versão e o mesmo repo."""
    caminho = starter.caminho_relativo
    id_ = _texto(starter.meta, "id") or ""
    componente = contexto.componentes.get(id_)
    if componente is None:
        valor = f"{id_}: componente fora de componentes.yml"
        return [Erro(caminho, "id", codigos.R_COMPONENTE, valor)]
    erros: list[Erro] = []
    versao = _texto(starter.meta, "versao") or ""
    if normalizar_versao(versao) != componente.versao:
        valor = f"versão {versao} difere da fixada ({componente.versao})"
        erros.append(Erro(caminho, "id", codigos.R_COMPONENTE, valor))
    repo_url = _texto(starter.meta, "repo") or ""
    if repo_url != componente.repo:
        valor = f"repo {repo_url} difere do fixado"
        erros.append(Erro(caminho, "id", codigos.R_COMPONENTE, valor))
    return erros


@regra
def regra_vinculos(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Toda referência cruzada resolve; a peça existe no ninho; o starter bate com
    `componentes.yml`; a página usa só os blocos do seu template."""
    praticas = {p.chave for p in repo.praticas}
    receitas = {_nome(r) for r in repo.receitas}
    starters = {_texto(s.meta, "id") or _nome(s) for s in repo.starters}
    ferramentas = {_texto(f.meta, "id") or _nome(f) for f in repo.ferramentas}
    conceitos = {_nome(c) for c in repo.conceitos}
    guias = {_nome(g) for g in repo.guias}
    skills = {s.chave for s in repo.skills}
    erros: list[Erro] = []
    for p in repo.praticas:
        for item in _lista(p.meta, "aplica"):
            tipo, _, nome = item.partition(":")
            if tipo == "skill" and nome not in skills:
                erros.append(Erro(p.caminho_relativo, "aplica", codigos.R_REF_INEXISTENTE, item))
        erros += _ausentes(
            p, "ferramentas_aprovadas", _lista(p.meta, "ferramentas_aprovadas"), ferramentas
        )
        erros += _ausentes(p, "starter", _escalar(p.meta, "starter"), starters)
        erros += _ausentes(p, "receitas", _lista(p.meta, "receitas"), receitas)
    for r in repo.receitas:
        erros += _ausentes(
            r, "ferramentas_aprovadas", _lista(r.meta, "ferramentas_aprovadas"), ferramentas
        )
        erros += _ausentes(r, "starter", _escalar(r.meta, "starter"), starters)
        erros += _ausentes(r, "praticas", _lista(r.meta, "praticas"), praticas)
        erros += _na_espinha(r, espinha, r.meta.get("dominio"), r.meta.get("momento"))
    for s in repo.starters:
        erros += _ausentes(s, "praticas_aplicadas", _lista(s.meta, "praticas_aplicadas"), praticas)
        erros += _ausentes(s, "receitas", _lista(s.meta, "receitas"), receitas)
        erros += _starter_fixado(s, contexto)
    for f in repo.ferramentas:
        proprio = _texto(f.meta, "id") or _nome(f)
        erros += _ausentes(f, "praticas", _lista(f.meta, "praticas"), praticas)
        erros += _ausentes(f, "receitas", _lista(f.meta, "receitas"), receitas)
        erros += _ausentes(
            f, "alternativa", _escalar(f.meta, "alternativa"), ferramentas - {proprio}
        )
    for g in repo.guias:
        erros += _ausentes(g, "starter", _escalar(g.meta, "starter"), starters)
        erros += _ausentes(g, "relacionados", _lista(g.meta, "relacionados"), praticas)
    for d in repo.dominios:
        erros += _ausentes(d, "starter", _escalar(d.meta, "starter"), starters)
        for i, candidata in enumerate(d.meta.get("candidatas") or []):
            momento = candidata.get("momento") if isinstance(candidata, dict) else None
            erros += _na_espinha(d, espinha, None, momento, f"candidatas.{i}.")
    for g in repo.glossarios:
        for i, termo in enumerate(g.meta.get("termos") or []):
            conceito = termo.get("conceito") if isinstance(termo, dict) else None
            if isinstance(conceito, str) and conceito not in conceitos:
                campo = f"termos.{i}.conceito"
                erros.append(Erro(g.caminho_relativo, campo, codigos.R_REF_INEXISTENTE, conceito))
    for c in repo.conceitos:
        ninho, peca = _texto(c.meta, "ninho"), _texto(c.meta, "peca")
        if ninho in PECAS and peca is not None and peca not in PECAS[ninho]:
            valor = f"{peca} não é peça de {ninho}"
            erros.append(Erro(c.caminho_relativo, "peca", codigos.R_PECA, valor))
    for pagina in repo.paginas:
        erros += _problemas_da_pagina(pagina, espinha, praticas, receitas, starters, guias)
    return erros


def _problemas_da_pagina(
    pagina: Conteudo,
    espinha: Espinha,
    praticas: set[str],
    receitas: set[str],
    starters: set[str],
    guias: set[str],
) -> list[Erro]:
    slug = _nome(pagina)
    caminho = pagina.caminho_relativo
    erros: list[Erro] = []
    if slug in PAGINAS_RESERVADAS:
        valor = f"{slug} é página gerada; escolha outro nome"
        erros.append(Erro(caminho, "arquivo", codigos.R_ESQUEMA, valor))
    permitidos = BLOCOS_POR_PAGINA.get(slug, {"lead"})
    for bloco in BLOCOS:
        if bloco in pagina.meta and bloco not in permitidos:
            valor = (
                f"bloco que o template {slug if slug in BLOCOS_POR_PAGINA else 'pagina'} não usa"
            )
            erros.append(Erro(caminho, bloco, codigos.R_ESQUEMA, valor))
    destinos = {"guias": guias, "receitas": receitas, "starters": starters}
    for i, falha in enumerate(_itens(pagina, "falhas")):
        pratica = falha.get("pratica")
        if isinstance(pratica, str) and pratica not in praticas:
            erros.append(Erro(caminho, f"falhas.{i}.pratica", codigos.R_REF_INEXISTENTE, pratica))
        erros += _na_espinha(pagina, espinha, falha.get("dominio"), None, f"falhas.{i}.")
    for i, disciplina in enumerate(_itens(pagina, "disciplinas")):
        erros += _na_espinha(pagina, espinha, disciplina.get("dominio"), None, f"disciplinas.{i}.")
    trabalho = pagina.meta.get("trabalho")
    ciclo = (
        [m for m in trabalho.get("ciclo", []) if isinstance(m, dict)]
        if isinstance(trabalho, dict)
        else []
    )
    for i, modo in enumerate(ciclo):
        for id_ in modo.get("praticas") or []:
            if isinstance(id_, str) and id_ not in praticas:
                campo = f"trabalho.ciclo.{i}.praticas"
                erros.append(Erro(caminho, campo, codigos.R_REF_INEXISTENTE, id_))
    for i, item in enumerate(_itens(pagina, "momentos")):
        erros += _na_espinha(pagina, espinha, None, item.get("momento"), f"momentos.{i}.")
    for i, caminho_item in enumerate(_itens(pagina, "caminhos")):
        destino = caminho_item.get("destino")
        pasta, _, resto = destino.partition("/") if isinstance(destino, str) else ("", "", "")
        if pasta in destinos and resto not in destinos[pasta]:
            erros.append(Erro(caminho, f"caminhos.{i}.destino", codigos.R_REF_INEXISTENTE, destino))
    return erros


def _itens(conteudo: Conteudo, campo: str) -> list[dict[str, Any]]:
    valor = conteudo.meta.get(campo)
    return [i for i in valor if isinstance(i, dict)] if isinstance(valor, list) else []


@regra
def regra_referencias(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """URL `https://` válida e datas de calendário reais em cada referência.

    A presença de `verificado_em` e `verificacao` é exigida pelo schema (R-ESQUEMA).
    """
    erros: list[Erro] = []
    for r in repo.referencias:
        url = _texto(r.meta, "url")
        if url is not None and r.meta.get("tipo") == "portal":
            if not PAGINA_DO_PORTAL.match(url):
                erros.append(Erro(r.caminho_relativo, "url", codigos.R_REFERENCIA, url))
        elif url is not None and not url_https_valida(url):
            erros.append(Erro(r.caminho_relativo, "url", codigos.R_REFERENCIA, url))
        for campo in ("publicado_em", "verificado_em"):
            valor = _texto(r.meta, campo)
            if valor is not None and _data_impossivel(valor):
                erros.append(Erro(r.caminho_relativo, campo, codigos.R_REFERENCIA, valor))
    return erros


PAGINA_DO_PORTAL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*\.html$")


def url_https_valida(url: str) -> bool:
    """`https://` com host que tem domínio (contém ponto) e sem espaço em lugar nenhum."""
    if any(caractere.isspace() for caractere in url):
        return False
    try:
        partes = urlsplit(url)
        host = partes.hostname or ""
    except ValueError:
        return False
    return partes.scheme == "https" and "." in host.strip(".")


def _data_impossivel(texto: str) -> bool:
    """Texto no formato YYYY-MM-DD que não é uma data do calendário (ex.: 2026-02-30)."""
    if not DATA.match(texto):
        return False
    try:
        date.fromisoformat(texto)
    except ValueError:
        return True
    return False


# Força, mecanismo e status (spec §6.5, regras 4 e 5; §6.6; §12.1, bloqueios 4 e 5) -----------

MECANISMO_EXTERNO = re.compile(
    r"^(?P<componente>[a-z0-9][a-z0-9-]*):(?P<caminho>[^@\s]+)@(?P<versao>[^@\s]+)$"
)
TIPOS_FORTES = frozenset({"normativo", "vendor", "padrao-aberto"})

RAIZES_DE_MECANISMO = ("scripts/", "portal/", "verificadores/", ".gitlab-ci.yml")


def normalizar_versao(versao: str) -> str:
    """`v1.7.0` e `1.7.0` são a mesma versão (§6.6 do delta)."""
    return versao[1:] if versao[:1] in ("v", "V") else versao


ID_NO_TEXTO = re.compile(r"\b[A-Z][A-Z0-9]*-[0-9]{2}\b")


@regra
def regra_mecanismo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Força acima de `orienta` exige mecanismo; todo verificador declarado precisa resolver.

    Formas do verificador: caminho de arquivo dentro do repositório, ou
    `<componente>:<caminho>@<versao>` com componente e versão iguais aos de `componentes.yml`.
    O bloco estruturado pode não ter verificador: os gatilhos bastam (ADR 0009).
    """
    erros: list[Erro] = []
    for p in repo.praticas:
        forca = _texto(p.meta, "forca")
        m = mecanismo_de(p.meta)
        if m is None:
            if forca is not None and forca != "orienta":
                valor = f"força {forca} sem mecanismo"
                erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
            continue
        if m.verificador is None:
            continue
        problema = _problema_do_mecanismo(m.verificador, contexto)
        if problema:
            valor = f"{m.verificador}: {problema}"
            erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
    return erros


@regra
def regra_gatilhos(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-GATILHO (spec do motor §6.1): força dura exige gatilho de harness e de Git ou CI;
    cada gatilho é coerente (ferramenta, comando, caminhos, repetição)."""
    erros: list[Erro] = []
    for p in repo.praticas:
        m = mecanismo_de(p.meta)
        if m is None:
            continue
        for problema in problemas_dos_gatilhos(_texto(p.meta, "forca"), m):
            erros.append(
                Erro(p.caminho_relativo, "mecanismo.gatilhos", codigos.R_GATILHO, problema)
            )
    return erros


@regra
def regra_mensagem(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-MENSAGEM (spec do motor §6.1): o que o agente lê ao ser bloqueado."""
    erros: list[Erro] = []
    for p in repo.praticas:
        m = mecanismo_de(p.meta)
        if m is None:
            continue
        for problema in problemas_da_mensagem(p.chave, m):
            erros.append(
                Erro(p.caminho_relativo, "mecanismo.mensagem", codigos.R_MENSAGEM, problema)
            )
    return erros


@regra
def regra_nucleo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-NUCLEO (spec do motor §7.1): o bloco do perfil mais completo cabe no limite."""
    catalogo = montar_catalogo(repo, espinha)
    bloco = compor_bloco(catalogo, "0.0.0", [f.slug for f in espinha.faixas])
    return [Erro("praticas/", "nucleo", codigos.R_NUCLEO, p) for p in problemas_do_bloco(bloco)]


def _problema_do_mecanismo(mecanismo: str, contexto: Contexto) -> str:
    externo = MECANISMO_EXTERNO.match(mecanismo)
    if externo:
        componente = contexto.componentes.get(externo["componente"])
        if componente is None:
            return "componente fora de componentes.yml"
        if normalizar_versao(externo["versao"]) != componente.versao:
            return f"versão diferente da fixada ({componente.versao})"
        return ""
    raiz = contexto.raiz.resolve()
    alvo = (raiz / mecanismo).resolve()
    if not alvo.is_relative_to(raiz):
        return "caminho fora do repositório"
    relativo = alvo.relative_to(raiz).as_posix()
    if not any(relativo == r or relativo.startswith(r) for r in RAIZES_DE_MECANISMO):
        return "caminho interno fora de scripts/, portal/, verificadores/ ou .gitlab-ci.yml"
    if not alvo.is_file():
        return "caminho inexistente"
    if relativo.startswith("verificadores/"):
        teste = raiz / "tests" / "verificadores" / f"test_{alvo.stem}.py"
        if not teste.is_file():
            return f"sem teste em tests/verificadores/test_{alvo.stem}.py"
    return ""


@regra
def regra_adotar(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`adotar` exige uma referência forte ([V] e tipo normativo, vendor ou padrao-aberto)
    ou um caso interno existente em `casos/`, citado no campo `casos`."""
    erros: list[Erro] = []
    referencias = {r.chave: r.meta for r in repo.referencias}
    slugs_caso = {c.chave for c in repo.casos}
    for p in repo.praticas:
        if _texto(p.meta, "status") != "adotar":
            continue
        fortes = [
            id_
            for id_ in _lista(p.meta, "referencias")
            if referencias.get(id_, {}).get("tipo") in TIPOS_FORTES
            and referencias.get(id_, {}).get("verificacao") == "V"
        ]
        casos = [slug for slug in _lista(p.meta, "casos") if slug in slugs_caso]
        if not fortes and not casos:
            valor = "adotar sem referência forte [V] nem caso interno"
            erros.append(Erro(p.caminho_relativo, "status", codigos.R_ADOTAR, valor))
    return erros


@regra
def regra_evitar(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`evitar` descreve um anti-padrão e o corpo cita, pelo ID, a prática que o substitui."""
    erros: list[Erro] = []
    ids_pratica = {p.chave for p in repo.praticas}
    for p in repo.praticas:
        if _texto(p.meta, "status") != "evitar":
            continue
        substitutas = set(ID_NO_TEXTO.findall(p.corpo)) & (ids_pratica - {p.chave})
        if not substitutas:
            valor = "o corpo não cita o ID de uma prática existente que substitui esta"
            erros.append(Erro(p.caminho_relativo, "status", codigos.R_EVITAR, valor))
    return erros


# Seções obrigatórias da prática (spec §6.1; §12.1, bloqueio 1) --------------------------------

SECOES_PRATICA = (
    "O que fazer",
    "Como aparece quando falta",
    "Como aplicar",
    "Exemplo",
    "Como verificar",
)
SECOES_RECEITA = (
    "Resultado",
    "Antes de começar",
    "Passos",
    "Com o agente",
    "Confira",
    "Se der errado",
)
_MARKDOWN = MarkdownIt("commonmark")


def titulos_h2(corpo: str) -> list[str]:
    """Títulos de nível 2 do corpo, como o Markdown os entende (ignora `## ` dentro de código)."""
    tokens = _MARKDOWN.parse(corpo)
    return [
        tokens[i + 1].content.strip()
        for i, token in enumerate(tokens)
        if token.type == "heading_open" and token.tag == "h2"
    ]


@regra
def regra_secoes(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """A prática tem as 5 seções do §6.1 (ou as 4 sem `Exemplo`, que a regra 6 cobra à parte), a
    receita tem as 6 do §6.4 e o guia `tutorial` tem `## Passos`."""
    erros: list[Erro] = []
    sem_exemplo = tuple(s for s in SECOES_PRATICA if s != "Exemplo")
    for p in repo.praticas:
        titulos = titulos_h2(p.corpo)
        if tuple(titulos) not in (SECOES_PRATICA, sem_exemplo):
            valor = "encontradas: " + (" | ".join(titulos) or "nenhuma")
            erros.append(Erro(p.caminho_relativo, "corpo", codigos.R_SECOES, valor))
    for g in repo.guias:
        if g.meta.get("tipo") == "tutorial" and "Passos" not in titulos_h2(g.corpo):
            valor = "tutorial sem a seção ## Passos"
            erros.append(Erro(g.caminho_relativo, "corpo", codigos.R_SECOES, valor))
    for r in repo.receitas:
        titulos = titulos_h2(r.corpo)
        if tuple(titulos) != SECOES_RECEITA:
            valor = "encontradas: " + (" | ".join(titulos) or "nenhuma")
            erros.append(Erro(r.caminho_relativo, "corpo", codigos.R_SECOES, valor))
    return erros


# Exemplo obrigatório e blocos de código (delta §6.5, regra 6; §12.1, bloqueio 13) ---------------

LIMITE_BLOCO = 15


def exemplo_obrigatorio(meta: dict[str, Any]) -> bool:
    """O Exemplo é obrigatório quando o status é `adotar` ou a força não é `orienta`."""
    return meta.get("status") == "adotar" or meta.get("forca") != "orienta"


def _h3_da_secao(texto: str) -> set[str]:
    tokens = _MARKDOWN.parse(texto)
    return {
        tokens[i + 1].content.strip()
        for i, t in enumerate(tokens)
        if t.type == "heading_open" and t.tag == "h3"
    }


@regra
def regra_exemplo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """A prática tem `## Exemplo` com antes/depois, prompt e código; os blocos têm linguagem."""
    erros: list[Erro] = []

    def reprovar(c: Conteudo, valor: str) -> None:
        erros.append(Erro(c.caminho_relativo, "corpo", codigos.R_EXEMPLO, valor))

    for p in repo.praticas:
        secao = dict(secoes(p.corpo)).get("Exemplo")
        if secao is None:
            if exemplo_obrigatorio(p.meta):
                reprovar(p, "## Exemplo obrigatório: status adotar ou força acima de orienta")
            continue
        subsecoes = _h3_da_secao(secao)
        for titulo in ("Antes e depois", "Para o agente"):
            if titulo not in subsecoes:
                reprovar(p, f"## Exemplo sem ### {titulo}")
        codigo = [
            b
            for b in blocos(p.corpo)
            if b.h2 == "Exemplo" and b.linguagem != "prompt" and b.texto.strip()
        ]
        if not codigo and not inclusoes(secao):
            reprovar(p, "## Exemplo sem bloco de código")
    for c in [*repo.praticas, *repo.receitas]:
        for bloco in blocos(c.corpo):
            if not bloco.linguagem:
                reprovar(c, f"bloco de código sem linguagem (linha {bloco.linha})")
            elif bloco.linguagem != "prompt" and bloco.texto.count("\n") > LIMITE_BLOCO:
                valor = (
                    f"bloco com {bloco.texto.count(chr(10))} linhas (linha {bloco.linha}); "
                    f"arquivo com mais de {LIMITE_BLOCO} linhas mora em exemplos/"
                )
                reprovar(c, valor)
    return erros


# Exemplos executados (delta §6.5, regra 7; §11.4; §12.1, bloqueio 14) -------------------------


@regra
def regra_execucao(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo arquivo de `exemplos/` existe, é seguro, tem sintaxe válida e execução registrada.

    Vale para prática e receita. A inclusão `<!-- incluir: -->` só lê dentro de `exemplos/` e o
    arquivo incluído precisa estar declarado em `exemplos:`. Nada aqui executa o arquivo.
    """
    registros = {_texto(v.meta, "conteudo"): v for v in repo.verificacoes}
    erros: list[Erro] = []
    for c in [*repo.praticas, *repo.receitas]:
        registro = registros.get(c.chave)
        executados = {
            e.get("arquivo")
            for e in (registro.meta.get("execucoes") or [] if registro else [])
            if isinstance(e, dict)
        }
        declarados = _lista(c.meta, "exemplos")

        def reprovar(caminho: str, problema: str, c: Conteudo = c) -> None:
            valor = f"{caminho}: {problema}"
            erros.append(Erro(c.caminho_relativo, "exemplos", codigos.R_EXECUCAO, valor))

        for caminho in declarados:
            alvo = caminho_seguro(contexto.raiz, caminho)
            if alvo is None:
                reprovar(caminho, "fora de exemplos/")
                continue
            if not alvo.is_file():
                reprovar(caminho, "inexistente")
                continue
            problema = checar_sintaxe(alvo)
            if problema:
                reprovar(caminho, problema)
            if caminho not in executados:
                reprovar(caminho, f"sem execução registrada em verificacoes/{c.chave}.yaml")
        for caminho in inclusoes(c.corpo):
            if caminho_seguro(contexto.raiz, caminho) is None:
                reprovar(caminho, "inclusão fora de exemplos/")
            elif caminho not in declarados:
                reprovar(caminho, "incluído e não declarado em exemplos")
    return erros


# Prompts de exemplo (delta D19, R27) ---------------------------------------------------------

LUGAR_DO_PROMPT = {
    "pratica": ("Exemplo", "Para o agente", "## Exemplo › ### Para o agente"),
    "receita": ("Com o agente", "", "## Com o agente"),
}


@regra
def regra_prompt(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """O prompt de exemplo mora em `Exemplo › Para o agente` (prática) ou `Com o agente`
    (receita), é obrigatório onde o Exemplo é e só publica com execução registrada."""
    registros = {_texto(v.meta, "conteudo"): v for v in repo.verificacoes}
    erros: list[Erro] = []
    for c in repo.markdown():
        achados = prompts_de(c)

        def reprovar(valor: str, c: Conteudo = c) -> None:
            erros.append(Erro(c.caminho_relativo, "corpo", codigos.R_PROMPT, valor))

        if c.tipo not in LUGAR_DO_PROMPT:
            if achados:
                reprovar("prompt só em prática e receita")
            continue
        h2, h3, descricao = LUGAR_DO_PROMPT[c.tipo]
        for achado in achados:
            if (achado.h2, achado.h3) != (h2, h3):
                reprovar(f"prompt fora de {descricao}")
        obrigatorio = c.tipo == "receita" or exemplo_obrigatorio(c.meta)
        if obrigatorio and not any((a.h2, a.h3) == (h2, h3) for a in achados):
            reprovar(f"prompt de exemplo obrigatório em {descricao.split(' › ')[-1]}")
        registro = registros.get(c.chave)
        executados = {
            e.get("prompt")
            for e in (registro.meta.get("execucoes") or [] if registro else [])
            if isinstance(e, dict) and e.get("tipo") == "prompt" and e.get("resultado") != "falhou"
        }
        for achado in achados:
            if achado.id not in executados:
                reprovar(f"{achado.id}: sem execução registrada")
    return erros


# Registro de verificação (spec §11.2; §12.1, bloqueio 7) --------------------------------------


@regra
def regra_verificacao(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo conteúdo publicado tem `verificacoes/<chave>.yaml` válido e em dia (R14, §11).

    Vale também para página e domínio sem nenhuma citação: é aí que uma afirmação factual
    escaparia da curadoria. O registro não é anterior a `revisado_em`, tem ao menos uma
    afirmação para cada id citado no corpo, nenhuma afirmação `nao-confirmada` e a
    `revisao_adversarial` registrada.
    Registro sem conteúdo correspondente também reprova: quase sempre é ID digitado errado.
    O registro de uma apresentação (`apresentacao-<slug>`) tem a pasta como conteúdo, e toda
    pasta com `apresentacao.yml` precisa dele.
    """
    erros: list[Erro] = []
    conteudos = {c.chave: c for c in repo.publicados()}
    registros: dict[str, Conteudo] = {}
    apresentacoes = chaves_de_verificacao(contexto.raiz)
    for v in repo.verificacoes:
        alvo = _texto(v.meta, "conteudo")
        if alvo is None:
            continue
        registros.setdefault(alvo, v)
        if alvo not in conteudos and alvo not in apresentacoes:
            valor = f"{alvo}: nenhum conteúdo com essa chave"
            erros.append(Erro(v.caminho_relativo, "conteudo", codigos.R_VERIFICACAO, valor))
    for chave, c in conteudos.items():
        citados = extrair(c.texto_citavel)
        if c.tipo in TIPOS_YAML_PUBLICADOS:
            citados = list(dict.fromkeys(citados + c.referencias_declaradas))
        v = registros.get(chave)
        if v is None:
            valor = f"sem registro em verificacoes/{chave}.yaml"
            erros.append(Erro(c.caminho_relativo, "verificacao", codigos.R_VERIFICACAO, valor))
            continue
        erros += _problemas_do_registro(v, c, citados)
    for chave in sorted(chaves_exigidas(contexto.raiz) - registros.keys()):
        valor = f"sem registro em verificacoes/{chave}.yaml"
        pasta = f"apresentacoes/{chave.removeprefix('apresentacao-')}"
        erros.append(Erro(pasta, "verificacao", codigos.R_VERIFICACAO, valor))
    return erros


def _problemas_do_registro(v: Conteudo, c: Conteudo, citados: list[str]) -> list[Erro]:
    erros: list[Erro] = []
    verificado_em = _texto(v.meta, "verificado_em")
    revisado_em = _texto(c.meta, "revisado_em")
    if verificado_em and revisado_em and verificado_em < revisado_em:
        valor = f"{verificado_em} é anterior ao revisado_em {revisado_em} de {c.caminho_relativo}"
        erros.append(Erro(v.caminho_relativo, "verificado_em", codigos.R_VERIFICACAO, valor))
    bruto = v.meta.get("afirmacoes")
    afirmacoes = [a for a in bruto if isinstance(a, dict)] if isinstance(bruto, list) else []
    cobertas = {a.get("ref") for a in afirmacoes}
    for id_ in citados:
        if id_ not in cobertas:
            valor = f"nenhuma afirmação conferida para [ref:{id_}]"
            erros.append(Erro(v.caminho_relativo, "afirmacoes", codigos.R_VERIFICACAO, valor))
    for i, afirmacao in enumerate(afirmacoes):
        if afirmacao.get("resultado") == "nao-confirmada":
            campo = f"afirmacoes.{i}.resultado"
            valor = f"nao-confirmada: {afirmacao.get('texto')}"
            erros.append(Erro(v.caminho_relativo, campo, codigos.R_VERIFICACAO, valor))
    if not isinstance(v.meta.get("revisao_adversarial"), dict):
        valor = "revisao_adversarial ausente"
        erros.append(Erro(v.caminho_relativo, "revisao_adversarial", codigos.R_VERIFICACAO, valor))
    return erros


# AGENTS.md e constituição (spec §8; §12.1, bloqueio 12) ---------------------------------------

LIMITE_AGENTS = 30 * 1024
INICIO_CONSTITUICAO = re.compile(r"<!--\s*constituicao:inicio\s+(?P<versao>[\w.\-]+)\s*-->")
FIM_CONSTITUICAO = "<!-- constituicao:fim -->"


@regra
def regra_agents(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`AGENTS.md` existe, tem menos de 30 KB e traz, entre os marcadores, a constituição
    idêntica (após strip) a `constituicao/<versao>.md`."""
    caminho = contexto.raiz / "AGENTS.md"
    if not caminho.is_file():
        return [Erro("AGENTS.md", "arquivo", codigos.R_AGENTS, "ausente")]
    erros: list[Erro] = []
    dados = caminho.read_bytes()
    if len(dados) >= LIMITE_AGENTS:
        valor = f"{len(dados)} bytes; o limite é {LIMITE_AGENTS}"
        erros.append(Erro("AGENTS.md", "tamanho", codigos.R_AGENTS, valor))
    texto = dados.decode("utf-8", errors="replace")
    inicio = INICIO_CONSTITUICAO.search(texto)
    if inicio is None or FIM_CONSTITUICAO not in texto[inicio.end() :]:
        valor = "marcadores <!-- constituicao:inicio <versao> --> e <!-- constituicao:fim -->"
        erros.append(Erro("AGENTS.md", "constituicao", codigos.R_AGENTS, f"faltam {valor}"))
        return erros
    versao = inicio["versao"]
    bloco = texto[inicio.end() :].split(FIM_CONSTITUICAO, 1)[0]
    canonica = contexto.raiz / "constituicao" / f"{versao}.md"
    if not canonica.is_file():
        valor = f"constituicao/{versao}.md não existe"
        erros.append(Erro("AGENTS.md", "constituicao", codigos.R_AGENTS, valor))
    elif bloco.strip() != canonica.read_text(encoding="utf-8").strip():
        valor = f"o bloco inline difere de constituicao/{versao}.md"
        erros.append(Erro("AGENTS.md", "constituicao", codigos.R_AGENTS, valor))
    return erros


# Skills (spec §10 e §11.1; formato Agent Skills) ----------------------------------------------

NOME_SKILL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILLS_NASCIDAS_AQUI = frozenset({"curadoria-de-pratica"})


@regra
def regra_skills(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """`skills/<pasta>/SKILL.md`: `name` igual à pasta, em `[a-z0-9-]` com até 64 caracteres;
    `description` com 1 a 1024 caracteres; `PROCEDENCIA.md` ao lado, salvo nas skills que
    nascem neste repositório."""
    erros: list[Erro] = []
    for s in repo.skills:
        pasta = _pasta(s)
        nome = s.meta.get("name")
        if nome != pasta:
            valor = f"{nome!r} difere da pasta {pasta}"
            erros.append(Erro(s.caminho_relativo, "name", codigos.R_SKILL, valor))
        if not isinstance(nome, str) or len(nome) > 64 or not NOME_SKILL.match(nome):
            valor = f"{nome!r}: use [a-z0-9-], sem hífen nas pontas, até 64 caracteres"
            erros.append(Erro(s.caminho_relativo, "name", codigos.R_SKILL, valor))
        descricao = s.meta.get("description")
        if not isinstance(descricao, str) or not descricao.strip() or len(descricao) > 1024:
            tamanho = len(descricao) if isinstance(descricao, str) else 0
            valor = f"{tamanho} caracteres; esperado de 1 a 1024"
            erros.append(Erro(s.caminho_relativo, "description", codigos.R_SKILL, valor))
        procedencia = contexto.raiz / "skills" / pasta / "PROCEDENCIA.md"
        if pasta not in SKILLS_NASCIDAS_AQUI and not procedencia.is_file():
            valor = "cópia sem PROCEDENCIA.md (repositório, versão, commit e origem)"
            erros.append(Erro(f"skills/{pasta}/PROCEDENCIA.md", "arquivo", codigos.R_SKILL, valor))
    return erros


LIMITE_DESCRICAO_SKILL = 1024
LIMITE_SOMA_DESCRICOES = 6000


@regra
def regra_skills_orcamento(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """R-SKILL-ORCAMENTO (spec do motor §8.1, regra 16): o que os harnesses carregam sempre."""
    erros: list[Erro] = []
    soma = 0
    for s in repo.skills:
        descricao = _texto(s.meta, "description") or ""
        soma += len(descricao)
        if len(descricao) > LIMITE_DESCRICAO_SKILL:
            valor = f"{len(descricao)} caracteres; o limite é {LIMITE_DESCRICAO_SKILL}"
            erros.append(Erro(s.caminho_relativo, "description", codigos.R_SKILL_ORCAMENTO, valor))
    if soma > LIMITE_SOMA_DESCRICOES:
        valor = f"soma de {soma} caracteres; o limite é {LIMITE_SOMA_DESCRICOES}"
        erros.append(Erro("skills/", "description", codigos.R_SKILL_ORCAMENTO, valor))
    return erros


# Apresentações (delta das apresentações, R4) ---------------------------------------------------


@regra
def regra_apresentacoes(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Cada pasta de `apresentacoes/` tem `apresentacao.yml` válido, `index.html`, as páginas e o
    roteiro que o registro cita e nenhum recurso externo; as referências citadas existem."""
    return validar_apresentacoes(contexto.raiz, frozenset(r.chave for r in repo.referencias))


# Links internos (B.5, T1b) -------------------------------------------------------------------

_ESQUEMA_URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


SAIDAS_FIXAS = (
    "llms.txt",
    "llms-full.txt",
    "busca.json",
    "catalogo.json",
    "roteamento.json",
    "prompts.json",
    "README.md",
    "ROTEAMENTO.md",
)


def _arquivos_de_apresentacoes(raiz: Path) -> set[str]:
    """O roteiro gerado e os arquivos que o build copia de cada `apresentacoes/<slug>/`."""
    from portal.gerador.apresentacoes import carregar_apresentacoes  # tardia: ver acima

    publicados: set[str] = set()
    if not (raiz / "apresentacoes").is_dir():
        return publicados
    for a in carregar_apresentacoes(raiz):
        if a.roteiro:
            publicados.add(a.caminho_roteiro)
        pasta = raiz / "apresentacoes" / a.slug
        for arquivo in pasta.rglob("*"):
            relativo = arquivo.relative_to(pasta)
            if arquivo.is_file() and not arquivo.is_symlink() and a.publicado(relativo):
                publicados.add(f"apresentacoes/{a.slug}/{relativo.as_posix()}")
    return publicados


def _paginas_geradas(repo: Repositorio, espinha: Espinha, raiz: Path) -> frozenset[str]:
    """Os caminhos que o build publica: páginas de conteúdo, domínios, listagens, roteiros, os
    arquivos das apresentações e as saídas para agentes (`llms.txt`, `catalogo.json`...)."""
    # importação tardia: renderizar importa avisos, que importa este módulo (ciclo)
    from portal.gerador.renderizar import PAGINAS_GERADAS, caminho_de

    conteudos = {
        caminho_de(c).split("#")[0] for c in repo.publicados() if c.tipo not in ("dominio",)
    }
    dominios = {f"dominios/{f.slug}.html" for f in espinha.faixas}
    fixas = {caminho for caminho, _ in PAGINAS_GERADAS}
    return frozenset(
        conteudos | dominios | fixas | set(SAIDAS_FIXAS) | _arquivos_de_apresentacoes(raiz)
    )


def _links_relativos(corpo: str) -> list[tuple[int, str]]:
    """Os links do corpo que são relativos: (linha do corpo, base 1; destino sem âncora).

    Ficam de fora o link com esquema (`https:`, `mailto:`), o absoluto na raiz do site, o que é só
    âncora e o que está em bloco ou trecho de código (o parser nem o reconhece como link)."""
    linhas = corpo.splitlines()
    achados: list[tuple[int, str]] = []
    for token in MarkdownIt("commonmark").parse(corpo):
        if token.type != "inline" or not token.map:
            continue
        inicio, fim = token.map
        for filho in token.children or []:
            href = str(
                filho.attrGet({"link_open": "href", "image": "src"}.get(filho.type, "")) or ""
            )
            destino = unquote(href.split("#")[0].split("?")[0])
            if not destino or destino.startswith("/") or _ESQUEMA_URL.match(href):
                continue
            linha = next((i for i in range(inicio, fim) if destino in linhas[i]), inicio)
            achados.append((linha + 1, destino))
    return achados


@regra
def regra_link_interno(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo link relativo do corpo Markdown aponta para a página (ou o `.md` gêmeo dela) ou outra
    saída que o build publica: `exemplos/`, roteiros e arquivos das apresentações, `llms.txt`,
    `catalogo.json`... Arquivo que só existe na fonte, como `AGENTS.md` ou `paginas/x.md`, não
    vale, porque o site não o tem. O destino é resolvido a partir da pasta da página gerada, que é
    onde o leitor está (`praticas/` para uma prática da faixa `ci-cd`). Âncora não é conferida;
    pasta não conta, porque o site não tem índice dela. O erro traz o arquivo, a linha e o
    destino."""
    from portal.gerador.renderizar import caminho_de  # tardia: ver `_paginas_geradas`

    geradas = _paginas_geradas(repo, espinha, contexto.raiz)
    erros: list[Erro] = []
    for c in repo.markdown():
        pasta_da_pagina = posixpath.dirname(caminho_de(c).split("#")[0])
        deslocamento = _linhas_antes_do_corpo(contexto.raiz / c.caminho_relativo, c.corpo)
        for linha, destino in _links_relativos(c.corpo):
            alvo = posixpath.normpath(posixpath.join(pasta_da_pagina, destino))
            gerado = alvo.removesuffix(".md") + ".html" if alvo.endswith(".md") else alvo
            publicado = (alvo.startswith("exemplos/") and (contexto.raiz / alvo).is_file()) or (
                gerado in geradas
            )
            if alvo.startswith("..") or not publicado:
                campo = f"linha {deslocamento + linha}"
                erros.append(
                    Erro(
                        c.caminho_relativo,
                        campo,
                        codigos.R_LINK_INTERNO,
                        f"{destino}: alvo não existe",
                    )
                )
    return erros


def _linhas_antes_do_corpo(arquivo: Path, corpo: str) -> int:
    """Quantas linhas do arquivo vêm antes do corpo (o frontmatter e o que o carregador descarta);
    zero se o arquivo não está em disco."""
    try:
        texto = arquivo.read_text(encoding="utf-8")
    except OSError:
        return 0
    return texto.count("\n") - corpo.count("\n") if texto.endswith(corpo) else 0


# Mecanismos hospedados (spec delta 1.7, R3) -----------------------------------------------------


@regra
def regra_mecanismos_hospedados(
    repo: Repositorio, espinha: Espinha, contexto: Contexto
) -> list[Erro]:
    """Os scripts de `mecanismos/` batem com o registro e com `componentes.yml`, e todo
    mecanismo externo de prática aponta para um arquivo hospedado.

    Reprova quando o SHA-256 do arquivo difere do `PROCEDENCIA.md`, quando a versão ou o commit
    registrados diferem dos fixados em `componentes.yml` e quando `<componente>:<caminho>@<versao>`
    não tem o caminho entre os arquivos de origem hospedados."""
    erros: list[Erro] = []
    hospedados = carregar_mecanismos(contexto.raiz)
    vistos: set[str] = set()
    for m in hospedados:
        registro = f"{PASTA_MECANISMOS}/{m.componente}/PROCEDENCIA.md"
        if m.componente not in vistos:
            vistos.add(m.componente)
            componente = contexto.componentes.get(m.componente)
            if componente is None:
                erros.append(
                    Erro(
                        registro,
                        "componente",
                        codigos.R_MECANISMO_HOSPEDADO,
                        "fora de componentes.yml",
                    )
                )
            else:
                if m.versao != componente.versao:
                    valor = f"versão {m.versao} difere da fixada ({componente.versao})"
                    erros.append(Erro(registro, "versao", codigos.R_MECANISMO_HOSPEDADO, valor))
                if m.commit != componente.commit:
                    valor = f"commit {m.commit} difere do fixado ({componente.commit})"
                    erros.append(Erro(registro, "commit", codigos.R_MECANISMO_HOSPEDADO, valor))
        real = hashlib.sha256(m.conteudo).hexdigest()
        if real != m.sha256:
            valor = f"sha256 do arquivo é {real}, o registro diz {m.sha256}"
            erros.append(Erro(registro, m.arquivo, codigos.R_MECANISMO_HOSPEDADO, valor))
    origens = {(m.componente, m.origem) for m in hospedados}
    for p in repo.praticas:
        m = mecanismo_de(p.meta)
        mecanismo = m.verificador if m else None
        externo = MECANISMO_EXTERNO.match(mecanismo) if mecanismo else None
        if externo and (externo["componente"], externo["caminho"]) not in origens:
            valor = f"{mecanismo}: arquivo não hospedado em {PASTA_MECANISMOS}/"
            erros.append(
                Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO_HOSPEDADO, valor)
            )
    arquivos = {(m.componente, m.arquivo) for m in hospedados}
    for caminho, texto in _textos_com_citacoes(repo, contexto.raiz):
        for citado in sorted(set(_citacoes_hospedadas(texto))):
            if citado not in arquivos:
                valor = f"{_PREFIXO_HOSPEDADO}/{citado[0]}/{citado[1]}: arquivo não hospedado em "
                valor += f"{PASTA_MECANISMOS}/"
                erros.append(Erro(caminho, "mecanismo", codigos.R_MECANISMO_HOSPEDADO, valor))
        for arquivo, citado, esperado in _sha256_divergentes(texto, hospedados):
            valor = f"{arquivo}: sha256 citado é {citado}, o registro diz {esperado}"
            erros.append(Erro(caminho, "sha256", codigos.R_MECANISMO_HOSPEDADO, valor))
    return erros


SHA256_LITERAL = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{64}(?![0-9a-fA-F])")
_JANELA_SHA256 = 3


def _sha256_divergentes(texto: str, hospedados: list[Mecanismo]) -> list[tuple[str, str, str]]:
    """Hashes de 64 hex citados junto ao nome de um script hospedado que divergem do registro.

    O nome é procurado na própria linha do hash e, se não houver, nas três linhas anteriores
    (a mais próxima vence). Hash sem nome de script por perto não é conferido."""
    linhas = texto.splitlines()
    achados: list[tuple[str, str, str]] = []
    for i, linha in enumerate(linhas):
        for hash_ in SHA256_LITERAL.findall(linha):
            for j in range(i, max(i - _JANELA_SHA256, 0) - 1, -1):
                nomes = [
                    m
                    for m in hospedados
                    if re.search(rf"(?<![\w.-]){re.escape(m.arquivo)}(?![\w-])", linhas[j])
                ]
                if nomes:
                    if all(hash_ != m.sha256 for m in nomes):
                        achados.append((nomes[0].arquivo, hash_, nomes[0].sha256))
                    break
    return achados


_PREFIXO_HOSPEDADO = ".well-known/mecanismos"
CITACAO_HOSPEDADA = re.compile(
    r"\.well-known/mecanismos/(?P<componente>[a-z0-9][a-z0-9-]*)/(?P<arquivo>[A-Za-z0-9_][\w.-]*)"
)


BASE_DEFINIDA = re.compile(r"\bBASE=")
BASE_HOSPEDADA = re.compile(
    r"""\bBASE=(?:"[^"]*?|'[^']*?|[^\s"'#]*?)"""
    r"\.well-known/mecanismos/(?P<componente>[a-z0-9][a-z0-9-]*)/?(?![\w/.-])"
)
CITACAO_POR_BASE = re.compile(r"\$\{?BASE\}?/(?P<arquivo>[A-Za-z0-9_][\w.-]*)")
_JANELA_BASE = 3


def _citacoes_por_base(texto: str) -> list[tuple[str, str]]:
    """Os pares (componente, arquivo) citados como `$BASE/<arquivo>` ou `${BASE}/<arquivo>`.

    O `BASE=` vale quando está na própria linha ou numa das três anteriores (a mais próxima
    vence) e termina em `/.well-known/mecanismos/<componente>/`; `BASE` sem definição por perto ou
    definido em outro lugar (o GitHub na tag, por exemplo) não é conferido."""
    linhas = texto.splitlines()
    achados: list[tuple[str, str]] = []
    for i, linha in enumerate(linhas):
        for uso in CITACAO_POR_BASE.finditer(linha):
            for j in range(i, max(i - _JANELA_BASE, 0) - 1, -1):
                alvo = linhas[j][: uso.start()] if j == i else linhas[j]
                definicoes = list(BASE_DEFINIDA.finditer(alvo))
                if definicoes:
                    hospedada = BASE_HOSPEDADA.match(alvo, definicoes[-1].start())
                    if hospedada:
                        achados.append((hospedada["componente"], uso["arquivo"].rstrip(".")))
                    break
    return achados


def _citacoes_hospedadas(texto: str) -> list[tuple[str, str]]:
    """Os pares (componente, arquivo) citados como `/.well-known/mecanismos/<c>/<arquivo>` ou,
    com `BASE` definido na janela, como `$BASE/<arquivo>`."""
    diretas = [
        (m["componente"], m["arquivo"].rstrip(".")) for m in CITACAO_HOSPEDADA.finditer(texto)
    ]
    return diretas + _citacoes_por_base(texto)


def _textos_com_citacoes(repo: Repositorio, raiz: Path) -> list[tuple[str, str]]:
    """Corpo das práticas e receitas e os arquivos de `exemplos/`, com o caminho relativo."""
    textos = [(c.caminho_relativo, c.corpo) for c in (*repo.praticas, *repo.receitas)]
    for arquivo in sorted((raiz / "exemplos").rglob("*")):
        if arquivo.is_file():
            relativo = arquivo.relative_to(raiz).as_posix()
            textos.append((relativo, arquivo.read_text(encoding="utf-8", errors="replace")))
    return textos
