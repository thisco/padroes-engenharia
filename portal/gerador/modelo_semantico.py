"""Contrato semântico do piloto RDF (spec do piloto RDF, §2): classes, relações e propriedades.
Fonte única para o exportador e para a página visual. Não importa `Site` nem o renderizador."""

from __future__ import annotations

# Tipo original do nó (`file_type` do grafo) → nome da classe. Tipo ausente daqui vira
# `FALLBACK_CLASSE` (itens de `aplica` como skill e steering), com o tipo original preservado.
CLASSES: dict[str, str] = {
    "pratica": "Pratica",
    "dominio": "Dominio",
    "momento": "Momento",
    "celula": "Celula",
    "passo": "Passo",
    "ferramenta": "Ferramenta",
    "referencia": "Referencia",
    "conceito": "DocumentoConceito",
    "receita": "Receita",
    "trilha": "Trilha",
}
FALLBACK_CLASSE = "RecursoAplicavel"
CLASSE_COMUM = "Entidade"

DESCRICAO_CLASSES: dict[str, str] = {
    CLASSE_COMUM: (
        "Qualquer registro do grafo do catálogo: superclasse comum, da qual toda outra classe "
        "do vocabulário é subclasse."
    ),
    "Pratica": "Prática de engenharia do catálogo.",
    "Dominio": "Domínio (faixa) da espinha do catálogo.",
    "Momento": "Momento do ciclo de desenvolvimento.",
    "Celula": "Cruzamento de um domínio com um momento.",
    "Passo": "Passo de um momento da espinha.",
    "Ferramenta": (
        "Ferramenta com registro em ferramentas/, inclusive as da categoria skill. Skills e "
        "steering citados só em aplica, sem esse registro, são Recurso aplicável."
    ),
    "Referencia": "Fonte externa catalogada.",
    "DocumentoConceito": "Documento de conceito do portal, não um conceito formal.",
    "Receita": "Receita passo a passo que ensina práticas.",
    "Trilha": "Sequência de ferramentas para um objetivo.",
    FALLBACK_CLASSE: "Item aplicado por uma prática sem classe específica.",
}

# Rótulos legíveis (pt-BR) de classes e propriedades relacionais; o nome local da IRI segue ASCII.
ROTULO_CLASSES: dict[str, str] = {
    CLASSE_COMUM: "Entidade",
    "Pratica": "Prática",
    "Dominio": "Domínio",
    "Momento": "Momento",
    "Celula": "Célula",
    "Passo": "Passo",
    "Ferramenta": "Ferramenta",
    "Referencia": "Referência",
    "DocumentoConceito": "Documento de conceito",
    "Receita": "Receita",
    "Trilha": "Trilha",
    FALLBACK_CLASSE: "Recurso aplicável",
}
ROTULO_PROPRIEDADES: dict[str, str] = {
    "temCelula": "tem célula",
    "temDominio": "tem domínio",
    "temMomento": "tem momento",
    "temPasso": "tem passo",
    "aplica": "aplica",
    "usa": "usa",
    "cita": "cita",
    "relaciona": "relaciona",
    "explica": "explica",
    "ensina": "ensina",
}

# origem/destino são classes; `relacao` é o vínculo de entrada; `propriedade` é a do RDF.
# Destino `Entidade` aceita qualquer classe.
RELACOES: tuple[dict[str, str], ...] = (
    {
        "origem": "Pratica",
        "relacao": "pertence",
        "destino": "Celula",
        "propriedade": "temCelula",
        "descricao": "A prática ocupa uma célula da espinha.",
    },
    {
        "origem": "Celula",
        "relacao": "pertence",
        "destino": "Dominio",
        "propriedade": "temDominio",
        "descricao": "A célula pertence a um domínio.",
    },
    {
        "origem": "Celula",
        "relacao": "pertence",
        "destino": "Momento",
        "propriedade": "temMomento",
        "descricao": "A célula ocorre em um momento.",
    },
    {
        "origem": "Passo",
        "relacao": "pertence",
        "destino": "Momento",
        "propriedade": "temMomento",
        "descricao": "O passo faz parte de um momento.",
    },
    {
        "origem": "Ferramenta",
        "relacao": "caminho",
        "destino": "Passo",
        "propriedade": "temPasso",
        "descricao": "A ferramenta tem um caminho de uso neste passo.",
    },
    {
        "origem": "Pratica",
        "relacao": "aplica",
        "destino": "Entidade",
        "propriedade": "aplica",
        "descricao": "A prática se aplica por meio deste recurso.",
    },
    {
        "origem": "Pratica",
        "relacao": "usa",
        "destino": "Ferramenta",
        "propriedade": "usa",
        "descricao": "A prática aprova o uso desta ferramenta.",
    },
    {
        "origem": "Trilha",
        "relacao": "usa",
        "destino": "Ferramenta",
        "propriedade": "usa",
        "descricao": "A trilha inclui esta ferramenta na sequência.",
    },
    {
        "origem": "Pratica",
        "relacao": "cita",
        "destino": "Referencia",
        "propriedade": "cita",
        "descricao": "A prática cita esta fonte externa.",
    },
    {
        "origem": "Pratica",
        "relacao": "relaciona",
        "destino": "Pratica",
        "propriedade": "relaciona",
        "descricao": "A prática declara relação com outra, na direção registrada.",
    },
    {
        "origem": "DocumentoConceito",
        "relacao": "explica",
        "destino": "Pratica",
        "propriedade": "explica",
        "descricao": "O documento de conceito explica a prática.",
    },
    {
        "origem": "Receita",
        "relacao": "ensina",
        "destino": "Pratica",
        "propriedade": "ensina",
        "descricao": "A receita ensina a prática.",
    },
)

# Propriedades de dados: campo do nó → (nome, rótulo, descrição, é IRI). Ausência não é inventada.
PROPRIEDADES_DADOS: dict[str, tuple[str, str, str, bool]] = {
    "id": ("identificador", "identificador", "ID original, sem normalização.", False),
    "file_type": ("tipoOrigem", "tipo de origem", "Tipo original do nó no grafo.", False),
    "source_file": (
        "arquivoFonte",
        "arquivo de fonte",
        "Arquivo que declara o registro: vale para a entidade e para a afirmação (rdf:Statement) "
        "do vínculo, por isso não tem domínio declarado.",
        False,
    ),
    "forca": ("forca", "força", "Força normativa da prática.", False),
    "status": ("status", "status", "Estado editorial da prática.", False),
    "dominio": ("dominio", "domínio", "Slug do domínio da prática.", False),
    "momento": ("momento", "momento", "Slug do momento da prática.", False),
    "url": ("url", "URL", "Endereço da página do registro.", True),
}
# Propriedades de dados usadas também nas afirmações (rdf:Statement): ficam sem `rdfs:domain`,
# porque domínio Entidade faria de cada afirmação uma Entidade sob entailment RDFS.
PROPRIEDADES_SEM_DOMINIO = frozenset({"arquivoFonte"})
# Propriedades das afirmações (rdf:Statement) e do recorte por entidade.
PROPRIEDADE_RELACAO_ORIGEM = "relacaoOrigem"
PROPRIEDADE_RECORTE = "recorte"


def classe_de(tipo: str) -> str:
    return CLASSES.get(tipo, FALLBACK_CLASSE)


def relacao_prevista(
    relacao: str, classe_origem: str, classe_destino: str
) -> dict[str, str] | None:
    """A linha de `RELACOES` que admite a combinação, ou None se não for prevista."""
    for r in RELACOES:
        if (
            r["relacao"] == relacao
            and r["origem"] == classe_origem
            and r["destino"] in (classe_destino, CLASSE_COMUM)
        ):
            return r
    return None
