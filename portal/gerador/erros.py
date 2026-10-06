"""Erro de validação e os códigos de regra (spec §12.1 e §14).

Todo validador devolve uma lista de `Erro`; ninguém levanta exceção para erro de conteúdo.
Exceção fica reservada para falha interna, que o CLI transforma no código de saída 2.
"""

from __future__ import annotations

from dataclasses import dataclass

R_FRONTMATTER = "R-FRONTMATTER"
R_ESQUEMA = "R-ESQUEMA"
R_SECOES = "R-SECOES"
R_ESPINHA = "R-ESPINHA"
R_ID_FORMATO = "R-ID-FORMATO"
R_ID_PREFIXO = "R-ID-PREFIXO"
R_ID_DUPLICADO = "R-ID-DUPLICADO"
R_ID_RETIRADO = "R-ID-RETIRADO"
R_ID_ARQUIVO = "R-ID-ARQUIVO"
R_REF_INEXISTENTE = "R-REF-INEXISTENTE"
R_REF_CONJUNTO = "R-REF-CONJUNTO"
R_REFERENCIA = "R-REFERENCIA"
R_MECANISMO = "R-MECANISMO"
R_MECANISMO_HOSPEDADO = "R-MECANISMO-HOSPEDADO"
R_ADOTAR = "R-ADOTAR"
R_EVITAR = "R-EVITAR"
R_VERIFICACAO = "R-VERIFICACAO"
R_AGENTS = "R-AGENTS"
R_SKILL = "R-SKILL"
R_GERADO_DIVERGENTE = "R-GERADO-DIVERGENTE"
R_EXTERNO = "R-EXTERNO"
R_PRATICA_FORA = "R-PRATICA-FORA"
R_REF_MALFORMADO = "R-REF-MALFORMADO"
R_PECA = "R-PECA"
R_COMPONENTE = "R-COMPONENTE"
R_EXEMPLO = "R-EXEMPLO"
R_EXECUCAO = "R-EXECUCAO"
R_PROMPT = "R-PROMPT"
R_APRESENTACAO = "R-APRESENTACAO"

DESCRICOES: dict[str, str] = {
    R_FRONTMATTER: "frontmatter ausente ou YAML inválido",
    R_ESQUEMA: "frontmatter fora do JSON Schema do tipo",
    R_SECOES: "seções obrigatórias da prática, da receita ou do tutorial ausentes ou fora de ordem",
    R_ESPINHA: "domínio, subdomínio, momento ou pasta fora de esquemas/espinha.yml",
    R_ID_FORMATO: "ID fora do formato <PREFIXO>-<NN>",
    R_ID_PREFIXO: "prefixo do ID incoerente com o domínio",
    R_ID_DUPLICADO: "ID repetido",
    R_ID_RETIRADO: "ID listado em esquemas/ids-retirados.txt",
    R_ID_ARQUIVO: "nome do arquivo diferente do ID",
    R_REF_INEXISTENTE: "referência, prática ou caso citado que não existe",
    R_REF_CONJUNTO: "campo referencias diferente do conjunto citado no corpo",
    R_REFERENCIA: "referência com URL https inválida ou data impossível",
    R_MECANISMO: "força acima de orienta sem mecanismo resolvível",
    R_MECANISMO_HOSPEDADO: "mecanismo hospedado divergente do registro, ou script não hospedado",
    R_ADOTAR: "status adotar sem referência forte nem caso interno",
    R_EVITAR: "status evitar sem indicar a prática que substitui",
    R_VERIFICACAO: "registro de verificação ausente, defasado, incompleto ou sem revisão",
    R_AGENTS: "AGENTS.md ausente, grande demais ou com constituição divergente",
    R_SKILL: "skill fora da especificação Agent Skills ou sem PROCEDENCIA.md",
    R_GERADO_DIVERGENTE: "README.md ou ROTEAMENTO.md diferente do que o gerador produz",
    R_EXTERNO: "recurso externo em <link>, <script> ou @import",
    R_PRATICA_FORA: "prática fora de praticas/<faixa>/<ID>.md",
    R_REF_MALFORMADO: "marcador [ref: que não casa [ref:<id>]",
    R_PECA: "peça de conceito que não existe no ninho declarado",
    R_COMPONENTE: "starter fora de componentes.yml ou com versão ou repo diferente",
    R_EXECUCAO: "arquivo de exemplos/ sem execução registrada, inseguro ou com sintaxe inválida",
    R_PROMPT: "prompt de exemplo fora do lugar, ausente onde é obrigatório ou sem execução",
    R_APRESENTACAO: "apresentação sem registro ou deck, com página ausente ou recurso externo",
    R_EXEMPLO: "Exemplo ausente ou incompleto, ou bloco de código sem linguagem ou longo demais",
}


@dataclass(frozen=True, order=True)
class Erro:
    """Uma violação: onde (arquivo e campo), qual regra e o valor encontrado."""

    arquivo: str
    campo: str
    regra: str
    valor: str = ""

    def __str__(self) -> str:
        base = f"{self.arquivo}:{self.campo}: {self.regra}"
        return f"{base} ({self.valor})" if self.valor else base
