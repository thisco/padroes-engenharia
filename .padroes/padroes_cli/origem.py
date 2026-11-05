"""Origem do pacote de distribuição (spec do motor §10, `--origem`; plano F4-D2).

A origem é uma pasta (a `public/pacote/` do build, ou o tarball da release extraído) ou uma URL
`https`, `file` ou `http` (este só para localhost) que serve a mesma pasta. O `manifesto.json`
lista cada arquivo com o SHA-256; nada é aceito sem a conferência de todos, e o CLI só escreve no
projeto depois dela.
Arquivo presente na pasta e fora do manifesto não entra.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

MANIFESTO = "manifesto.json"
_URL = re.compile(r"^(?:https?|file)://", re.I)
TEMPO_LIMITE = 30
# `http` sem TLS só para a máquina local (o servidor de teste, o `http.server` do portal).
LOCAIS = frozenset({"localhost", "127.0.0.1", "::1"})


class ErroDoPacote(Exception):
    """Pacote ilegível ou adulterado; a mensagem diz o arquivo e o que fazer."""


@dataclass(frozen=True)
class Pacote:
    origem: str
    manifesto: dict[str, Any]
    bruto_manifesto: bytes
    arquivos: dict[str, bytes]

    @property
    def versao(self) -> str:
        return str(self.manifesto.get("versao", ""))

    @property
    def sha256(self) -> str:
        """Identidade do pacote: o SHA-256 do `manifesto.json`, que fixa o de todo arquivo."""
        return hashlib.sha256(self.bruto_manifesto).hexdigest()

    def json(self, caminho: str) -> Any:
        return json.loads(self.arquivos[caminho].decode("utf-8"))


def e_url(origem: str) -> bool:
    return bool(_URL.match(origem))


def _caminho_seguro(relativo: str) -> bool:
    partes = PurePosixPath(relativo).parts
    return (
        bool(partes)
        and not relativo.startswith("/")
        and "\\" not in relativo
        and ".." not in partes
        and ":" not in partes[0]
    )


def _url_aceita(url: str) -> bool:
    partes = urllib.parse.urlsplit(url)
    esquema = partes.scheme.lower()
    return esquema == "https" or (esquema == "http" and partes.hostname in LOCAIS)


class _SoRedirecionamentoSeguro(urllib.request.HTTPRedirectHandler):
    """Recusa, antes de segui-lo, o redirecionamento que rebaixa para http fora da máquina."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _url_aceita(newurl):
            raise ErroDoPacote(
                f"{req.full_url}: redirecionamento para {newurl} recusado (só https, ou http "
                "em localhost); aponte --origem para a URL final em https"
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_ABRIDOR = urllib.request.build_opener(_SoRedirecionamentoSeguro)


def _leitor(origem: str):
    if e_url(origem):
        if urllib.parse.urlsplit(origem).scheme.lower() != "file" and not _url_aceita(origem):
            raise ErroDoPacote(
                f"{origem}: http sem TLS só para localhost; use https (ou a pasta do pacote)"
            )
        base = origem if origem.endswith("/") else origem + "/"

        def ler_url(relativo: str) -> bytes:
            url = base + relativo
            try:
                with _ABRIDOR.open(url, timeout=TEMPO_LIMITE) as resposta:
                    if not _url_aceita(resposta.geturl()) and not url.lower().startswith("file:"):
                        raise ErroDoPacote(f"{url}: terminou em {resposta.geturl()}, recusado")
                    return resposta.read()
            except (urllib.error.URLError, OSError) as erro:
                raise ErroDoPacote(f"{url}: não foi possível baixar ({erro})") from erro

        return ler_url
    pasta = Path(origem)

    def ler_pasta(relativo: str) -> bytes:
        caminho = pasta / relativo
        if not caminho.is_file():
            raise ErroDoPacote(f"{caminho}: arquivo do manifesto ausente na origem")
        return caminho.read_bytes()

    return ler_pasta


def abrir(origem: str, versao: str | None = None) -> Pacote:
    """Lê e confere o pacote inteiro. `versao` fixa a versão esperada (`--versao`)."""
    ler = _leitor(origem)
    try:
        bruto = ler(MANIFESTO)
    except ErroDoPacote as erro:
        raise ErroDoPacote(
            f"{erro}. Aponte --origem para a pasta do pacote (a que tem {MANIFESTO})."
        ) from erro
    try:
        manifesto = json.loads(bruto.decode("utf-8"))
        declarados = manifesto["arquivos"]
        if not isinstance(declarados, dict):
            raise TypeError
    except (ValueError, KeyError, TypeError) as erro:
        raise ErroDoPacote(f"{origem}: {MANIFESTO} ilegível ou sem 'arquivos'") from erro
    if versao is not None and str(manifesto.get("versao")) != versao:
        raise ErroDoPacote(
            f"{origem}: o pacote está na versão {manifesto.get('versao')}, não na {versao} "
            "pedida; aponte --origem para a release certa ou tire --versao"
        )
    arquivos: dict[str, bytes] = {}
    for relativo, esperado in sorted(declarados.items()):
        if not _caminho_seguro(relativo):
            raise ErroDoPacote(f"{relativo}: caminho inválido no manifesto (absoluto ou com ..)")
        dados = ler(relativo)
        real = hashlib.sha256(dados).hexdigest()
        if real != esperado:
            raise ErroDoPacote(
                f"{relativo}: sha256 {real} difere do manifesto ({esperado}); o pacote foi "
                "alterado ou baixado pela metade. Baixe de novo da origem publicada."
            )
        arquivos[relativo] = dados
    return Pacote(origem=origem, manifesto=manifesto, bruto_manifesto=bruto, arquivos=arquivos)
