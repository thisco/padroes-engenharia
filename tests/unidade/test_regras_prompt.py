"""R27 (D19): prompt de exemplo no lugar certo, obrigatório onde o Exemplo é, e executado."""

from portal.gerador.carregar import Conteudo, Repositorio
from portal.gerador.exemplos import prompts_de
from portal.gerador.markdown import para_html
from portal.gerador.regras import Contexto, regra_prompt
from tests import fabrica

EXEMPLO = (
    "## Exemplo\n\n### Antes e depois\n\n```sql\nx;\n```\n\n"
    "### Para o agente\n\n```prompt\nFaça <b>x</b>.\n```\n\n"
)
COM_PROMPT = fabrica.CORPO_PRATICA.replace("## Como verificar", EXEMPLO + "## Como verificar")
EXECUTADO = {
    "tipo": "prompt",
    "harness": "claude-code",
    "resultado": "passou",
    "evidencia": "ok",
    "data": "2026-10-01",
}


def rodar(*conteudos, raiz):
    ctx = Contexto(raiz=raiz, componentes={}, ids_retirados=frozenset())
    return [e.valor for e in regra_prompt(Repositorio.de(conteudos), fabrica.espinha_real(), ctx)]


def registro(chave, *ids):
    execucoes = [dict(EXECUTADO, prompt=i) for i in ids]
    return fabrica.verificacao(fabrica.meta_verificacao(conteudo=chave, execucoes=execucoes))


def test_inocente_pratica_e_receita(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(status="adotar"), COM_PROMPT)
    assert [x.id for x in prompts_de(p)] == ["P1-01-prompt-1"]
    r = fabrica.receita()
    assert (
        rodar(
            p,
            registro("P1-01", "P1-01-prompt-1"),
            r,
            registro("receita-ligar-ci", "receita-ligar-ci-prompt-1"),
            raiz=tmp_path,
        )
        == []
    )


def test_pega_sem_execucao_obrigatorio_e_fora_do_lugar(tmp_path):
    sem_execucao = fabrica.pratica(fabrica.meta_pratica(status="adotar"), COM_PROMPT)
    assert rodar(sem_execucao, raiz=tmp_path) == ["P1-01-prompt-1: sem execução registrada"]
    sem_prompt = COM_PROMPT.replace("```prompt\nFaça <b>x</b>.\n```", "Cole a linha.")
    assert rodar(
        fabrica.pratica(fabrica.meta_pratica(status="adotar"), sem_prompt), raiz=tmp_path
    ) == ["prompt de exemplo obrigatório em ### Para o agente"]
    fora = fabrica.CORPO_PRATICA + "\n```prompt\nx\n```\n"
    assert "prompt fora de ## Exemplo › ### Para o agente" in rodar(
        fabrica.pratica(corpo=fora), registro("P1-01", "P1-01-prompt-1"), raiz=tmp_path
    )
    guia = Conteudo("guia", "guias/g.md", fabrica.meta_guia(), "```prompt\nx\n```\n")
    assert "prompt só em prática e receita" in rodar(guia, raiz=tmp_path)


def test_prompt_sai_escapado_com_id_e_copiar():
    html = para_html("```prompt\n<script>x</script> e ```\n```\n", chave="DAD-01")
    assert '<figure class="prompt" id="DAD-01-prompt-1">' in html
    assert "&lt;script&gt;" in html and "<script>" not in html
    assert 'class="copiar" data-copiar hidden>Copiar</button>' in html


def test_execucao_que_falhou_nao_conta_como_execucao_registrada(tmp_path):
    p = fabrica.pratica(fabrica.meta_pratica(status="adotar"), COM_PROMPT)
    falhou = dict(
        EXECUTADO, prompt="P1-01-prompt-1", resultado="falhou", motivo="defeito do prompt"
    )
    sozinha = fabrica.verificacao(fabrica.meta_verificacao(conteudo="P1-01", execucoes=[falhou]))
    assert rodar(p, sozinha, raiz=tmp_path) == ["P1-01-prompt-1: sem execução registrada"]
    execucoes = [falhou, dict(EXECUTADO, prompt="P1-01-prompt-1")]
    com_a_que_passou = fabrica.verificacao(
        fabrica.meta_verificacao(conteudo="P1-01", execucoes=execucoes)
    )
    assert rodar(p, com_a_que_passou, raiz=tmp_path) == []
