"""Regras de integridade do repositório (spec §6.5, §6.6, §11.2 e §12.1, bloqueios 1–7 e 12).

Cada regra é uma função pura `(repo, espinha, contexto) -> list[Erro]`, registrada com `@regra`.
`validar_tudo(raiz)` é o contrato da validação: carrega o repositório, roda o schema e todas as
regras registradas, e devolve todos os erros, ordenados e sem repetição. A checagem do build
(R-GERADO-DIVERGENTE e R-EXTERNO) não mora aqui: o CLI `scripts/validar.py` soma as duas.

As regras não confiam no tipo dos campos (o schema já reporta isso): leem com `_texto` e
`_lista`, que devolvem None ou lista vazia quando o campo tem o tipo errado.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

from markdown_it import MarkdownIt

from portal.gerador import erros as codigos
from portal.gerador.carregar import (
    BLOCOS,
    TIPOS_YAML_PUBLICADOS,
    Componente,
    Conteudo,
    Repositorio,
    carregar,
    carregar_componentes,
    carregar_ids_retirados,
    carregar_isencoes,
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
    secoes,
)
from portal.gerador.ninhos import PECAS


@dataclass(frozen=True)
class Contexto:
    """O que as regras precisam além do conteúdo: raiz, componentes fixados e IDs retirados."""

    raiz: Path
    componentes: dict[str, Componente]
    ids_retirados: frozenset[str]
    isentos: frozenset[str] = frozenset()


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
        isentos=carregar_isencoes(raiz),
    )


def validar_tudo(raiz: Path) -> list[Erro]:
    """Todos os erros de validação do repositório em `raiz`, ordenados e sem repetição."""
    raiz = Path(raiz)
    espinha = carregar_espinha(raiz / "esquemas" / "espinha.yml")
    repo = carregar(raiz)
    contexto = carregar_contexto(raiz)
    erros = list(repo.erros)
    erros += validar_repositorio(repo, raiz / "esquemas")
    erros += validar_componentes(raiz)
    for funcao in REGRAS:
        erros += funcao(repo, espinha, contexto)
    return sorted(set(erros))


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
    "pessoas-e-normas": {"lead", "modos", "normas"},
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
    erros: list[Erro] = []
    for p in repo.praticas:
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
        if url is not None and not url_https_valida(url):
            erros.append(Erro(r.caminho_relativo, "url", codigos.R_REFERENCIA, url))
        for campo in ("publicado_em", "verificado_em"):
            valor = _texto(r.meta, campo)
            if valor is not None and _data_impossivel(valor):
                erros.append(Erro(r.caminho_relativo, campo, codigos.R_REFERENCIA, valor))
    return erros


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

RAIZES_DE_MECANISMO = ("scripts/", "portal/", ".gitlab-ci.yml")


def normalizar_versao(versao: str) -> str:
    """`v1.6.1` e `1.6.1` são a mesma versão (§6.6 do delta)."""
    return versao[1:] if versao[:1] in ("v", "V") else versao


ID_NO_TEXTO = re.compile(r"\b[A-Z][A-Z0-9]*-[0-9]{2}\b")


@regra
def regra_mecanismo(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Força acima de `orienta` exige mecanismo; todo mecanismo declarado precisa resolver.

    Formas aceitas: caminho de arquivo dentro do repositório, ou
    `<componente>:<caminho>@<versao>` com componente e versão iguais aos de `componentes.yml`.
    """
    erros: list[Erro] = []
    for p in repo.praticas:
        forca = _texto(p.meta, "forca")
        mecanismo = _texto(p.meta, "mecanismo")
        if mecanismo is None:
            if forca is not None and forca != "orienta":
                valor = f"força {forca} sem mecanismo"
                erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
            continue
        problema = _problema_do_mecanismo(mecanismo, contexto)
        if problema:
            valor = f"{mecanismo}: {problema}"
            erros.append(Erro(p.caminho_relativo, "mecanismo", codigos.R_MECANISMO, valor))
    return erros


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
        return "caminho interno fora de scripts/, portal/ ou .gitlab-ci.yml"
    if not alvo.is_file():
        return "caminho inexistente"
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
            if exemplo_obrigatorio(p.meta) and p.chave not in contexto.isentos:
                reprovar(p, "## Exemplo obrigatório: status adotar ou força acima de orienta")
            continue
        subsecoes = _h3_da_secao(secao)
        for titulo in ("Antes e depois", "Para o agente"):
            if titulo not in subsecoes:
                reprovar(p, f"## Exemplo sem ### {titulo}")
        codigo = [b for b in blocos(p.corpo) if b.h2 == "Exemplo" and b.linguagem != "prompt"]
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


# Registro de verificação (spec §11.2; §12.1, bloqueio 7) --------------------------------------


@regra
def regra_verificacao(repo: Repositorio, espinha: Espinha, contexto: Contexto) -> list[Erro]:
    """Todo conteúdo publicado tem `verificacoes/<chave>.yaml` válido e em dia (R14, §11).

    Vale também para página e domínio sem nenhuma citação: é aí que uma afirmação factual
    escaparia da curadoria. O registro não é anterior a `revisado_em`, tem ao menos uma
    afirmação para cada id citado no corpo, nenhuma afirmação `nao-confirmada` e a
    `revisao_adversarial` registrada.
    Registro sem conteúdo correspondente também reprova: quase sempre é ID digitado errado.
    """
    erros: list[Erro] = []
    conteudos = {c.chave: c for c in repo.publicados()}
    registros: dict[str, Conteudo] = {}
    for v in repo.verificacoes:
        alvo = _texto(v.meta, "conteudo")
        if alvo is None:
            continue
        registros.setdefault(alvo, v)
        if alvo not in conteudos:
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
